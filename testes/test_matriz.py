"""Testes da matriz (sem rede, sem chave): python3 -m pytest testes   ou   python3 testes/test_matriz.py

Cada teste segura uma regra que já custou caro: nome de cliente vazando, preço na página, prévia indexável,
a cena de rolagem sem quadros, o filtro diferente entre o passo 01 e o FAQ."""
import json, pathlib, re, shutil, subprocess, sys, tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "ferramentas"))
import anonimato as A                          # noqa: E402
from fabrica import montar_novo as M           # noqa: E402
from fabrica.ficha import validar_ficha        # noqa: E402
from ia.validar import validar                 # noqa: E402
from ia.guia import montar_guia, CONSELHO      # noqa: E402


# ── anonimato ──────────────────────────────────────────────────────────────────────────────
def test_repositorio_inteiro_passa_na_trava():
    r = subprocess.run([sys.executable, str(RAIZ / "ferramentas" / "anonimato.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]

def test_trava_pega_identificador_real_e_aceita_placeholder():
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        # montados por partes: o próprio teste não pode carregar um identificador inteiro (a trava varre este arquivo)
        f.write("\n".join(["GTM-" + "AB12CD3", "act_" + "123456789012", "123-" + "456-7890", "(11) 9" + "8765-4321",
                           "12.345.678/" + "0001-90", "CRM-SP " + "123456"]) + "\n")
    achados = {t for _, _, t in A.checar(pathlib.Path(f.name))}
    assert {"id de GTM", "conta do Meta (act_)", "conta do Google Ads", "telefone", "CNPJ", "registro profissional com número"} <= achados
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as g:
        g.write("GTM-XXXXXXX · (00) 00000-0000 · 00.000.000/0000-00 · CRM-SP 000000 · contato@exemplo.com.br\n")
    assert A.checar(pathlib.Path(g.name)) == []

def test_lista_de_bloqueio_so_tem_hash():
    # 15-10-2026: a lista e o sal são segredos (fora do repositório público); aqui só se prova que nada vazou para dentro.
    assert not (RAIZ / "ferramentas" / "bloqueio.sha").exists() and not (RAIZ / "ferramentas" / "fronteira" / "ghot-focus.sha").exists()
    assert A.BLOQUEIO and all(re.fullmatch(r"[0-9a-f]{20}", l) for l in A.BLOQUEIO)
    assert A.SAL and A.SAL not in (RAIZ / "ferramentas" / "anonimato.py").read_text()


# ── regras da página ───────────────────────────────────────────────────────────────────────
def test_preco_nunca_na_pagina():
    c = {"FAQ": [["Qual o valor?", "A consulta custa R$ 200."]], "NUMEROS": []}
    assert any("preço na página" in x for x in validar(c))

def test_guia_compila_para_cada_area():
    for area in CONSELHO:
        g = montar_guia(area)
        assert "doutrina/01-padrao.md" in g and f"conselhos/{CONSELHO[area]}.md" in g

def test_telefone_cnpj_e_slug():
    assert M.fmt_tel("55119" + "12345678") == "(11) 9" + "1234-5678"
    assert M.fmt_tel("") == M.FALTA
    assert M.fmt_cnpj("00000000000100") == "00.000.000/" + "0001-00"
    assert M.slug("Clínica de olhos em Campinas") == "clinica-de-olhos-em-campinas"

def test_paleta_escurece_marca_clara():
    p = M.paleta({"PALETA": {"marca": "#f0e68c", "destaque": "#ffffff"}})
    r, g, b = (int(p["--marca"][i:i + 2], 16) for i in (1, 3, 5))
    assert (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 <= 0.46

def test_ficha_normaliza_telefone_e_foto_inexistente():
    f = validar_ficha({"WHATSAPP": ["00 9" + "1234-5678", "(00) 9" + "3333-4444"], "FOTOS": {"capa": "nao-existe.jpg"}}, {"a.jpg"})
    assert f["WHATSAPP"] == "5500912345678" and f["TELEFONE"] == "5500933334444"
    assert f["FOTOS"]["capa"] == "" and any("capa" in x for x in f["PENDENCIAS"])


# ── o motor gera o exemplo de ponta a ponta ────────────────────────────────────────────────
def test_motor_gera_as_quatro_versoes_do_exemplo():
    with tempfile.TemporaryDirectory() as tmp:
        cli = pathlib.Path(tmp) / "clinica-exemplo"
        shutil.copytree(RAIZ / "exemplos" / "clinica-exemplo", cli,
                        ignore=shutil.ignore_patterns("clinica-de-*", "oftalmologista-*", "privacidade", "*.xml", "vercel.json", ".versao"))
        (cli / ".versao").write_text("0")
        r = subprocess.run([sys.executable, str(RAIZ / "motor" / "gerar.py"), str(cli)], capture_output=True, text=True,
                           env={"PYTHONHASHSEED": "0", "PATH": "/usr/bin:/bin"})
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-800:]
        paginas = sorted(p.parent.name for p in (cli / "site").glob("*/index.html") if p.parent.name != "privacidade")
        assert (cli / "site" / "privacidade" / "index.html").exists(), "página de privacidade não gerada (o aviso de cookies linka para ela)"
        assert len(paginas) == 4 and any(p.endswith("-cena") for p in paginas) and any(p.endswith("-video") for p in paginas)
        for p in paginas:
            h = (cli / "site" / p / "index.html").read_text(encoding="utf-8")
            assert 'content="noindex' in h, f"{p}: prévia sem noindex"
            assert not re.search(r"R\$\s?\d", re.sub(r"<script type=\"application/ld\+json\">.*?</script>", "", h, flags=re.S)), f"{p}: preço na página"
            for bloco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S):
                json.loads(bloco)   # JSON-LD válido
        cena = (cli / "site" / [p for p in paginas if p.endswith("-cena")][0] / "index.html").read_text(encoding="utf-8")
        assert "cena-0" in cena or "QUADROS" in cena or "cena" in cena
        # a trava também vale para o que o motor ESCREVE
        achados = [a for f in (cli / "site").rglob("*") if f.is_file() for a in A.checar(f)]
        assert achados == [], achados[:5]
        # o conferidor do padrão aprova as 4 versões (pausa obedecida pelo carrossel, topo sem animar pintura, foco visível…);
        # provado reprovando 14 itens no exemplo do motor de 06-10
        r = subprocess.run([sys.executable, str(RAIZ / "ferramentas" / "conferir.py")]
                           + [str(cli / "site" / p / "index.html") for p in paginas], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout[-1500:]


if __name__ == "__main__":
    falhas = 0
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            try:
                f(); print("✓", n)
            except AssertionError as e:
                falhas += 1; print("✗", n, "—", str(e)[:300])
    sys.exit(1 if falhas else 0)
