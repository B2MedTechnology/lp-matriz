"""Monta a pasta de um cliente NOVO para o motor: a base da casa (a página aprovada do página-base: molde, CSS, JS, fontes) com a
identidade da FICHA, as imagens recortadas das fotos do cliente, a paleta do logo, e o conteúdo da IA por cima.
Tudo o que faltar aparece como "(a confirmar)" na prévia e na lista "falta decidir" — nunca um valor inventado."""
import json, pathlib, re, secrets, shutil, subprocess, sys, unicodedata, urllib.parse
from . import imagens

AQUI = pathlib.Path(__file__).resolve().parent.parent
BASE_CASA = AQUI / "exemplos" / "clinica-exemplo"   # o molde aprovado (cliente fictício); a base da casa
FALTA = "(a confirmar)"

CONSELHOS = {
    "medico": ("CRM", "Conselho Regional de Medicina", "consulta médica", "Resolução CFM nº 2.336/2023"),
    "dentista": ("CRO", "Conselho Regional de Odontologia", "consulta odontológica", "Resolução CFO nº 196/2019"),
    "fisioterapeuta": ("CREFITO", "Conselho Regional de Fisioterapia e Terapia Ocupacional", "avaliação fisioterapêutica",
                       "Resolução COFFITO nº 532/2021"),
    "advogado": ("OAB", "Ordem dos Advogados do Brasil", "consulta jurídica", "Provimento nº 205/2021 do CFOAB"),
}
TIPO_ORG = {"medico": "MedicalClinic", "dentista": "Dentist", "fisioterapeuta": "MedicalClinic", "advogado": "LegalService"}
UF_NOME = {"AM": "do Amazonas", "SP": "de São Paulo", "RJ": "do Rio de Janeiro", "PA": "do Pará", "RR": "de Roraima",
           "MG": "de Minas Gerais", "PR": "do Paraná", "SC": "de Santa Catarina", "RS": "do Rio Grande do Sul", "BA": "da Bahia",
           "DF": "do Distrito Federal", "GO": "de Goiás", "CE": "do Ceará", "PE": "de Pernambuco", "RO": "de Rondônia",
           "AC": "do Acre", "AP": "do Amapá", "TO": "do Tocantins", "MT": "de Mato Grosso", "MS": "de Mato Grosso do Sul",
           "ES": "do Espírito Santo", "MA": "do Maranhão", "PI": "do Piauí", "RN": "do Rio Grande do Norte", "PB": "da Paraíba",
           "AL": "de Alagoas", "SE": "de Sergipe"}


def slug(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60] or "pagina"


def fmt_tel(d):
    d = re.sub(r"\D", "", d or "")
    if d.startswith("55"):
        d = d[2:]
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return d or FALTA


def fmt_cnpj(c):
    d = re.sub(r"\D", "", c or "")
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" if len(d) == 14 else (c or "")


def _hex_rgb(h):
    h = (h or "").lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if re.fullmatch(r"[0-9a-fA-F]{6}", h) else None


def _mistura(rgb, alvo, t):
    return "#%02x%02x%02x" % tuple(round(a + (b - a) * t) for a, b in zip(rgb, alvo))


def paleta(ficha):
    """As 5 cores do CSS da casa a partir da cor do logo: marca, creme (destaque claro), tinta e profundo (escuros da marca)."""
    marca = _hex_rgb((ficha.get("PALETA") or {}).get("marca")) or (12, 95, 80)
    destaque = _hex_rgb((ficha.get("PALETA") or {}).get("destaque"))
    # a marca tem de aguentar texto branco: se for clara demais, escurece
    lum = (0.2126 * marca[0] + 0.7152 * marca[1] + 0.0722 * marca[2]) / 255
    if lum > 0.45:
        marca = tuple(int(c * 0.45 / lum) for c in marca)
    creme = _mistura(destaque, (255, 255, 255), 0.35) if destaque and sum(destaque) > 450 else _mistura(marca, (255, 244, 225), 0.85)
    return {"--marca": "#%02x%02x%02x" % marca, "--creme": creme, "--tinta": _mistura(marca, (0, 0, 0), 0.72),
            "--profundo": _mistura(marca, (0, 0, 0), 0.8), "--gelo": _mistura(marca, (250, 248, 243), 0.95)}


def nome_curto(ficha, pedido):
    return ficha.get("NOME_CURTO") or ficha.get("NOME") or pedido.get("cliente_nome") or "?"


def preparar(trabalho: pathlib.Path, pedido: dict, ficha: dict, fotos: pathlib.Path):
    """Cria trabalho/cliente/ (cliente.json + site/assets) — o que o gerador de conteúdo e o motor leem."""
    cli = trabalho / "cliente"
    if cli.exists():
        shutil.rmtree(cli)
    (cli / "site" / "assets").mkdir(parents=True)
    for sub in ("css", "js", "fonts"):
        shutil.copytree(BASE_CASA / "site" / "assets" / sub, cli / "site" / "assets" / sub)
    img = cli / "site" / "assets" / "img"
    img.mkdir()
    (cli / "insumos").mkdir()

    area = pedido.get("area") or "medico"
    sigla, conselho, consulta, norma = CONSELHOS[area]
    F = ficha.get("FOTOS") or {}
    foco = ficha.get("FOCO") or {}
    fo = lambda n: tuple((foco.get(n) or [0.5, 0.35])[:2]) if n else (0.5, 0.35)
    desc = ficha.get("DESCRICOES") or {}
    pend = list(ficha.get("PENDENCIAS") or [])

    # ── imagens ─────────────────────────────────────────────────────────────────────────────────
    if F.get("capa"):
        imagens.capa(fotos / F["capa"], img, fo(F["capa"]))
    quem = F.get("quem") or F.get("retrato") or F.get("capa")
    if quem:
        imagens.vertical(fotos / quem, img, "quem", fo(quem), grande=True)
    retrato = F.get("retrato") or quem
    if retrato:
        imagens.vertical(fotos / retrato, img, "retrato-principal", fo(retrato), grande=False)
    espacos = [x for x in (F.get("espaco") or []) if x][:5]
    for i, e in enumerate(espacos, 1):
        imagens.espaco(fotos / e, img, f"espaco-{i}", fo(e))
    if F.get("logo"):
        logo, lw, lh = imagens.logo_branco(fotos / F["logo"], img)
    else:
        logo, lw, lh = None, 0, 0
        pend.append("logo: a pasta não tem o logo — a prévia usa o nome em texto")
    pal = paleta(ficha)
    if logo:
        imagens.icones(fotos / F["logo"], img, pal["--marca"])
    else:
        imagens.icones_texto(nome_curto(ficha, pedido), img, pal["--marca"])

    # ── CSS: a paleta da marca e a proporção do logo ────────────────────────────────────────────
    css = cli / "site" / "assets" / "css" / "estilo.css"
    t = css.read_text(encoding="utf-8")
    for var, cor in pal.items():
        t = re.sub(rf"({re.escape(var)}:)\s*[^;]+;", rf"\g<1>{cor};", t, count=1)
    if logo:
        t = t.replace("aspect-ratio:837.2/164.1", f"aspect-ratio:{lw}/{lh}")
    css.write_text(t, encoding="utf-8")
    js = cli / "site" / "assets" / "js" / "pagina.js"
    end = ficha.get("ENDERECO") or {}
    nome = ficha.get("NOME") or pedido.get("cliente_nome") or FALTA
    j = js.read_text(encoding="utf-8").replace(
        "Mapa com a localização da clínica",
        f"Mapa com a localização de {nome}, {end.get('rua') or ''} {end.get('bairro') or ''} {end.get('cidade') or ''}".strip())
    js.write_text(j, encoding="utf-8")

    # ── identidade ──────────────────────────────────────────────────────────────────────────────
    base = json.loads((BASE_CASA / "cliente.json").read_text(encoding="utf-8"))
    termo = (pedido.get("termo") or "").strip()
    can = slug(termo) or "pagina"
    resp = ficha.get("RESPONSAVEL") or {}
    cidade, uf = end.get("cidade") or "", (end.get("uf") or "").upper()
    rua_linha = ", ".join(x for x in [end.get("rua"), end.get("bairro")] if x)
    uma_linha = " - ".join(x for x in [rua_linha, f"{cidade} - {uf}".strip(" -"), end.get("cep")] if x) or FALTA
    zap = ficha.get("WHATSAPP") or ""
    tel = ficha.get("TELEFONE") or zap
    if not zap:
        pend.append("WhatsApp: o número não está no briefing — o botão da prévia não funciona até ele entrar")
    registro = (pedido.get("conselho_registro") or "").strip() or resp.get("registro") or ""
    crm = resp.get("registro") or registro or FALTA
    rqe = resp.get("rqe") or ""
    tipo = ficha.get("TIPO") or "clinica"
    oficio = ficha.get("OFICIO") or {"medico": "médico", "dentista": "dentista", "fisioterapeuta": "fisioterapeuta",
                                     "advogado": "advogado"}[area]
    previa = f"lp-{slug(nome)[:40]}-previa"
    mensagem = f"Olá! Vim pelo site e gostaria de agendar uma {consulta}."

    novo = {
        "NOME": nome, "BASE": f"https://{previa}.vercel.app", "DOMINIO_DO_SITE": f"{previa}.vercel.app",
        "HOST_PRINCIPAL": f"{previa}.vercel.app", "PREVIA_HOST": f"{previa}.vercel.app", "SITE_ATUAL": "",
        "SUBDOMINIOS": {}, "ANTIGOS_GREATPAGES": [], "REDIRECIONAR_PREVIA": False,
        "ENDERECO_RUA": end.get("rua") or FALTA, "ENDERECO_BAIRRO": end.get("bairro") or "", "ENDERECO_CIDADE": cidade or FALTA,
        "ENDERECO_UF": uf, "ENDERECO_CEP": end.get("cep") or "", "ENDERECO_REFERENCIA": end.get("referencia") or "",
        "ENDERECO_UMA_LINHA": uma_linha, "GEO": None, "CID_GOOGLE": "", "PLACE_ID": "", "NOTA_GOOGLE": "", "TOTAL_GOOGLE": "",
        "AVALIACOES_SEMENTE": [], "TELEFONE": tel, "TEL_FMT": fmt_tel(tel), "WHATSAPP": zap, "ZAP_FMT": fmt_tel(zap),
        "EMAIL": ficha.get("EMAIL") or "", "INSTAGRAM": ficha.get("INSTAGRAM") or pedido.get("instagram") or "",
        "HORARIOS": ficha.get("HORARIOS") or [["Horário", FALTA]], "HORARIOS_LD": ficha.get("HORARIOS_LD") or [],
        "CNPJ": fmt_cnpj(ficha.get("CNPJ")) or FALTA, "RAZAO_SOCIAL": ficha.get("RAZAO_SOCIAL") or FALTA,
        "DIRETORA": resp.get("nome") or FALTA, "DIRETORA_NOME": resp.get("nome_sem_titulo") or resp.get("nome") or FALTA,
        "CRM": crm, "RQE": rqe, "CRM_INSTITUTO": None, "RT_ROTULO": "Responsável técnico" if area != "advogado" else "Responsável",
        "DIRETOR_ID": slug(resp.get("nome_sem_titulo") or resp.get("nome") or "responsavel"), "DIRETOR_CARGO": "",
        "ESPECIALIDADE_NOME": ficha.get("ESPECIALIDADE_NOME") or FALTA, "OFICIO": oficio,
        "CONSELHO_SIGLA_UF": f"{sigla}-{uf}" if uf else sigla, "CONSELHO_NOME": f"{conselho} {UF_NOME.get(uf, '')}".strip(),
        "TIPO_ORG": TIPO_ORG[area], "SITE_NOME_SUFIXO": termo[:1].upper() + termo[1:], "ALT_SUFIXO": termo.lower(),
        "AREAS_EXTRA": [], "GTM_ID": "", "GTM_HEAD": base["GTM_HEAD"], "GTM_BODY": "", "INDEXAR": False,
        "INDEXNOW_CHAVE": secrets.token_hex(16), "CANONICA": can, "CAMINHOS": {can: "/"}, "TESTES": {},
        "LOGO_ARQUIVO": logo or "", "LOGO_PNG": "logo.png", "LOGO_PNG_W": 600, "LOGO_PNG_H": 600,
        "LOGO_RODAPE": logo or "", "LOGO_RODAPE_W": lw or 376, "LOGO_RODAPE_H": lh or 361,
        "LOGO_RODAPE_ALT": nome,
        "CAPA_ALT": desc.get(F.get("capa") or "", "") or f"{nome}, {termo}",
        "CATALOGO_ETIQUETA": "O que a clínica trata" if tipo == "clinica" else f"O que {resp.get('nome') or 'o profissional'} trata",
        "CORPO_HEAD": f"Quem atende no {nome}." if tipo == "clinica" else f"Quem atende.",
        "ONDE_HEAD": f"Onde fica: {end.get('rua')}, {end.get('bairro')}." if end.get("rua") and end.get("bairro") else "Onde fica.",
        "RODAPE_AVISO": (f"Esta página tem caráter informativo e não substitui a {consulta}. Conteúdo publicado em conformidade "
                         f"com a {norma}."),
        "ICONES": {k: v["svg"] for k, v in json.loads((AQUI / "motor" / "icones.json").read_text(encoding="utf-8")).items()},
        "MENSAGEM": mensagem, "MEDICA_MOTIVOS": [], "MEDICA_BIO": "", "MENSAGEM_MEDICA": mensagem,
        "_FICHA_PENDENCIAS": pend,
        "_FOTOS_ESPACO": [f"espaco-{i}" for i in range(1, len(espacos) + 1)],
        "_DESCRICOES": {**{f"espaco-{i}": desc.get(e, "") for i, e in enumerate(espacos, 1)},
                        "quem": desc.get(quem or "", ""), "retrato-principal": desc.get(retrato or "", "")},
    }
    base.update(novo)
    padrao = dict(base["PADRAO_PAGINA"])
    padrao.update({"ASSINA_NOME": nome, "OG_IMAGEM": "og.jpg", "OG_ALT": novo["CAPA_ALT"],
                   "_QUEM_FOTO": {"__t": ["quem", desc.get(quem or "", "") or nome]}, "_PERFIL": "instituto"})
    base["PADRAO_PAGINA"] = padrao
    base["VARIANTES"] = {can: {"TERMO": termo, "CAPA_CLASSE": " capa--exame", "H1_HTML": termo, "TITLE": termo,
                               "DESCRICAO": termo, "LEAD": ""}}
    (cli / "cliente.json").write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
    return cli


def aplicar_conteudo(cli: pathlib.Path, conteudo: dict, cards_fotos: dict, fotos: pathlib.Path, ficha: dict):
    """O conteúdo da IA por cima da base; as fotos dos cards recortadas com o ícone escolhido; roda o motor."""
    base = json.loads((cli / "cliente.json").read_text(encoding="utf-8"))
    for k in ["MARCA_LINHA", "NUMEROS", "QUEM_HEAD", "MOTIVOS", "CORPO_LEAD", "CORPO_CLINICO", "GRUPOS", "FILTRO", "PASSOS",
              "ESPACO", "SALA_HEAD", "SALA_TEXTO", "FAQ", "BAIRROS", "SERVICOS", "CONDICOES", "SABERES", "JSONLD_DESCRICAO"]:
        if k in conteudo:
            base[k] = conteudo[k]
    base["FOTOS_CARDS"] = {ico: alt for ico, (arq, alt) in cards_fotos.items()}
    img = cli / "site" / "assets" / "img"
    # ESPACO: só fotos que existem; o que a IA nomeou errado vira a próxima foto de espaço, com a descrição da ficha
    existentes = [x for x in base.get("_FOTOS_ESPACO", []) if (img / f"{x}.jpg").exists()]
    usadas, espaco = set(), []
    for item in base.get("ESPACO") or []:
        nomef, leg = item[0], item[1]
        if nomef not in existentes or nomef in usadas:
            livres = [x for x in existentes if x not in usadas]
            if not livres:
                continue
            nomef, leg = livres[0], (base.get("_DESCRICOES") or {}).get(livres[0]) or leg
        usadas.add(nomef)
        espaco.append([nomef, leg])
    for x in existentes:
        if x not in usadas:
            espaco.append([x, (base.get("_DESCRICOES") or {}).get(x, "")])
    base["ESPACO"] = espaco
    foco = ficha.get("FOCO") or {}
    for ico, (arq, alt) in cards_fotos.items():
        imagens.card(fotos / arq, img, ico, tuple((foco.get(arq) or [0.5, 0.4])[:2]))
    # corpo clínico: só a foto que existe (o retrato principal); os outros ficam sem foto até o cliente mandar
    for m in base.get("CORPO_CLINICO") or []:
        if not (img / f"{m.get('foto')}.jpg").exists():
            m["foto"] = "retrato-principal" if (img / "retrato-principal.jpg").exists() and m is base["CORPO_CLINICO"][0] else "quem"
    base["PADRAO_PAGINA"] = {**base["PADRAO_PAGINA"],
                             **{k: v for k, v in (conteudo.get("PADRAO_PAGINA") or {}).items() if not k.startswith("_")}}
    base["PADRAO_PAGINA"]["_MOTIVOS"] = conteudo.get("MOTIVOS", base["PADRAO_PAGINA"].get("_MOTIVOS"))
    can = base["CANONICA"]
    base["VARIANTES"] = {can: {**base["VARIANTES"][can], **(conteudo.get("PAGINA_PRINCIPAL") or {})}}
    # a frase do filtro é UMA constante (doutrina: "igual nos três lugares")
    if base.get("FILTRO") and base.get("PASSOS"):
        base["PASSOS"][0][2] = base["FILTRO"]
        if base.get("FAQ") and not base["FAQ"][0][1].startswith(base["FILTRO"]):
            base["FAQ"][0][1] = base["FILTRO"] + " " + base["FAQ"][0][1].split(". ", 1)[-1]
    base["ZAP"] = ("https://wa.me/" + base["WHATSAPP"] + "?text=" + urllib.parse.quote(base["MENSAGEM"])) if base["WHATSAPP"] else "#"
    (cli / "cliente.json").write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
    (cli / ".versao").write_text("1")
    r = subprocess.run([sys.executable, str(AQUI / "motor" / "gerar.py"), str(cli)], capture_output=True, text=True,
                       env={"PYTHONHASHSEED": "0", "PATH": "/usr/bin:/bin:/usr/local/bin"})
    if r.returncode != 0:
        raise RuntimeError("o motor recusou a página: " + (r.stderr or r.stdout)[-600:])
    return vercel_previa(cli / "site", can)


def vercel_previa(site: pathlib.Path, principal: str):
    """A prévia não herda roteamento de site real: "/" mostra a página principal e tudo sai com noindex."""
    vj = json.loads((site / "vercel.json").read_text(encoding="utf-8"))
    previa = {"$schema": vj.get("$schema"), "cleanUrls": True, "trailingSlash": True,
              "rewrites": [{"source": "/", "destination": f"/{principal}/"}],
              "headers": [h for h in vj.get("headers", []) if h.get("source", "").startswith("/assets/")]
                         + [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]}]}
    (site / "vercel.json").write_text(json.dumps(previa, ensure_ascii=False, indent=1), encoding="utf-8")
    return site
