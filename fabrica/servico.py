"""A FÁBRICA no servidor: pega o próximo pedido da fila (lp_pedidos, intel/0186), gera a página e publica a prévia.

    python3 -m fabrica.servico            # laço (o contêiner)
    python3 -m fabrica.servico --um 12    # só o pedido 12 (teste)

Etapas (a barra do dash acompanha): fotos do Drive → ficha (a IA vê fotos e briefing) → base → conteúdo (Gemini 2.5 Pro,
revisor + verificador de fatos, até 3 voltas) → foto de cada card → montagem (motor) → Vercel. Qualquer falha vira
status "erro" com a frase para o assessor; nada é publicado pela metade."""
import argparse, json, os, pathlib, shutil, subprocess, sys, time, traceback
from . import banco, drive, ficha as ficha_mod, montar_novo, cards, vercel

AQUI = pathlib.Path(__file__).resolve().parent.parent
TRABALHO = pathlib.Path(os.environ.get("FABRICA_TRABALHO", "/tmp/fabrica"))
EXEMPLO = AQUI / "exemplos" / "clinica-exemplo" / "cliente.json"   # página aprovada (fictícia) dada à IA como exemplo de forma


def etapa(pid, texto, pct):
    print(f"[pedido {pid}] {pct:3d}% {texto}", flush=True)
    banco.atualizar_pedido(pid, etapa=texto, progresso=pct)


def insumos_do_pedido(p):
    linhas = [f"# Insumos — {p['cliente_nome']} (pedido nº {p['id']} pelo painel)", "", "## Pedido do assessor",
              f"- Termo principal da campanha: {p['termo']}", f"- Área: {p['area']}"]
    for rot, k in (("Instagram", "instagram"), ("Perfil do Google", "perfil_google"),
                   ("Registro no conselho", "conselho_registro"), ("Observações para a página", "observacoes")):
        if p.get(k):
            linhas.append(f"- {rot}: {p[k]}")
    linhas += ["", "## Briefing do cliente", p.get("briefing") or "(sem briefing)"]
    return "\n".join(linhas)


def gerar(p, chave, vercel_token, vercel_time=None):
    pid = p["id"]
    t0 = time.time()
    dir_ = TRABALHO / f"pedido-{pid}"
    if dir_.exists():
        shutil.rmtree(dir_)
    fotos = dir_ / "fotos"
    custo = 0.0

    etapa(pid, "Baixando as fotos e o logo do Drive", 6)
    if not p.get("drive_url"):
        raise ValueError("Falta o link da pasta do Drive com as fotos e o logo.")
    arquivos = drive.baixar(p["drive_url"], fotos, limite=40)
    if len(arquivos) < 3:
        raise ValueError(f"A pasta do Drive tem só {len(arquivos)} foto(s) — mande pelo menos a capa, o profissional e o espaço.")

    etapa(pid, f"Olhando as {len(arquivos)} fotos e lendo o briefing", 15)
    insumos = insumos_do_pedido(p)
    (dir_ / "insumos.md").write_text(insumos, encoding="utf-8")
    fi, c = ficha_mod.gerar_ficha(insumos, arquivos, chave)
    custo += c
    (dir_ / "ficha.json").write_text(json.dumps(fi, ensure_ascii=False, indent=1), encoding="utf-8")

    etapa(pid, "Preparando a base da página (capa, cores do logo, espaço)", 35)
    cli = montar_novo.preparar(dir_, p, fi, fotos)

    etapa(pid, "Escrevendo a página seguindo o padrão da casa", 40)
    saida = dir_ / "conteudo"
    cmd = [sys.executable, str(AQUI / "ia" / "gerar-conteudo.py"), "--ref", "novo", "--exemplo", str(EXEMPLO),
           "--insumos", str(dir_ / "insumos.md"), "--area", p.get("area") or "medico", "--dir", str(cli), "--saida", str(saida)]
    cfg = banco.ler_config() or {}
    if cfg.get("modelo"):
        cmd += ["--modelo", cfg["modelo"]]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            env={**os.environ, "OPENROUTER_API_KEY": chave})
    vistos = 0
    while proc.poll() is None:
        n = len(list(saida.glob("revisor-*.json"))) if saida.exists() else 0
        if n != vistos:
            vistos = n
            etapa(pid, ["Escrevendo a página seguindo o padrão da casa", "Revisão: o revisor e o verificador de fatos leram a 1ª versão",
                        "Corrigindo o que o revisor apontou", "Última revisão"][min(n, 3)], 40 + min(n, 3) * 11)
        time.sleep(3)
    log = proc.stdout.read() if proc.stdout else ""
    if proc.returncode != 0 or not (saida / "conteudo.json").exists():
        raise RuntimeError("a IA não terminou o texto: " + log[-400:])
    conteudo = json.loads((saida / "conteudo.json").read_text(encoding="utf-8"))
    uso = json.loads((saida / "uso.json").read_text(encoding="utf-8"))
    custo += float(uso.get("custo_usd") or 0)

    etapa(pid, "Escolhendo a foto de cada serviço", 78)
    F = fi.get("FOTOS") or {}
    candidatas = [x for x in (F.get("cards") or []) + (F.get("espaco") or []) if x] or [F.get("capa")]
    mapa, c = cards.escolher(conteudo.get("GRUPOS") or [], fi.get("DESCRICOES") or {}, candidatas, chave)
    custo += c

    etapa(pid, "Montando a página", 86)
    site = montar_novo.aplicar_conteudo(cli, conteudo, mapa, fotos, fi)

    etapa(pid, "Publicando a prévia (sem indexação no Google)", 93)
    nome_proj = json.loads((cli / "cliente.json").read_text(encoding="utf-8"))["PREVIA_HOST"].split(".")[0]
    if vercel_token == "CLI-LOCAL":   # só no teste no Mac: publica com o login local da Vercel CLI
        r = subprocess.run(["npx", "vercel", "deploy", "--prod", "--yes", "--name", nome_proj], cwd=site, capture_output=True, text=True)
        url = next((l.split()[-1] for l in (r.stdout + r.stderr).splitlines() if "Aliased" in l), None)
        if not url:
            raise RuntimeError("Vercel CLI: " + (r.stderr or r.stdout)[-300:])
    else:
        url = vercel.publicar(site, nome_proj, vercel_token, vercel_time)

    pend = [x for x in (fi.get("PENDENCIAS") or []) + (conteudo.get("PENDENCIAS") or []) if x]
    banco.atualizar_pedido(pid, status="pronta", etapa="Prévia pronta", progresso=100, previa_url=url,
                           pendencias=pend, custo_usd=round(custo, 4), concluido_em=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print(f"[pedido {pid}] pronta em {round(time.time() - t0)} s · US$ {custo:.3f} · {url}", flush=True)
    shutil.rmtree(fotos, ignore_errors=True)
    return url


def frase_de_erro(e):
    t = str(e)
    if isinstance(e, ValueError):
        return t
    if "Vercel" in t:
        return "A página ficou pronta, mas a publicação na Vercel falhou. A Diretoria foi avisada pela caixa de erros; tente de novo em alguns minutos."
    return "A geração parou no meio (" + t[:160] + "). Tente “Gerar de novo”; se repetir, a Diretoria vê o detalhe."


def rodar_um(p):
    chave = banco.segredo_do_cofre("OPENROUTER_API_KEY")
    token = banco.segredo_do_cofre("VERCEL_TOKEN")
    time_id = banco.segredo_do_cofre("VERCEL_TEAM_ID")
    try:
        if not chave:
            raise RuntimeError("OPENROUTER_API_KEY ausente no Cofre")
        if not token:
            raise ValueError("A fábrica ainda não tem a chave da Vercel (VERCEL_TOKEN no Cofre) — a Diretoria precisa cadastrar.")
        gerar(p, chave, token, time_id)
    except Exception as e:
        traceback.print_exc()
        banco.atualizar_pedido(p["id"], status="erro", erro=frase_de_erro(e), etapa="Não terminou")


def laco():
    # pedido que ficou "gerando" num reinício do contêiner não vai terminar sozinho
    for p in banco._req("GET", "/rest/v1/lp_pedidos?status=eq.gerando&select=id") or []:
        banco.atualizar_pedido(p["id"], status="erro", etapa="Não terminou",
                               erro="A fábrica reiniciou no meio da geração. Peça “Gerar de novo”.")
    print("fábrica de landing pages: esperando pedidos", flush=True)
    while True:
        try:
            pegos = banco.rpc("lp_pedido_pegar") or []
            for p in pegos:
                rodar_um(p)
            if not pegos:
                time.sleep(15)
        except Exception:
            traceback.print_exc()
            time.sleep(30)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--um", type=int)
    a = ap.parse_args()
    if a.um:
        rodar_um(banco.ler_pedido(a.um))
    else:
        laco()
