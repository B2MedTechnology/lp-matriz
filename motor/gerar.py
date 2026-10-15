#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOTOR COMUM de landing page — a montagem de uma página aprovada da casa, sem os dados do cliente: eles vêm de `cliente.json`.

    python3 motor/gerar.py <pasta do cliente>        (ex.: exemplos/clinica-exemplo)

A pasta do cliente tem: cliente.json · insumos/ · site/assets/ (css, js, fontes, img, video) · .versao
O molde da página é comum: motor/template/pagina.html. As linhas marcadas "# MOTOR:" são o que virou parâmetro.
Saída em <pasta>/site/: uma pasta por página (estática, da pessoa responsável, capa em vídeo e a cena de rolagem),
sitemap, robots e vercel.json. Prévia (INDEXAR=false) sai noindex na meta, no robots e no cabeçalho.
Doutrina: doutrina/02-anatomia-da-pagina.md e doutrina/01-padrao.md.
"""
import hashlib, html, json, pathlib, re, sys, urllib.parse

MOTOR = pathlib.Path(__file__).resolve().parent
RAIZ = pathlib.Path(sys.argv[1]).resolve()

# ═══════════════════════ OS DADOS DO CLIENTE (cliente.json) ═══════════════════════
def _dec(o):
    if isinstance(o, dict) and set(o) == {"__t"}: return tuple(_dec(x) for x in o["__t"])
    if isinstance(o, dict): return {k: _dec(v) for k, v in o.items()}
    if isinstance(o, list): return [_dec(x) for x in o]
    if o == "@cena_rolagem": return lambda molde: cena_rolagem(molde)   # a abertura trocada pela cena (definida abaixo)
    return o
_DADOS = _dec(json.loads((RAIZ / "cliente.json").read_text(encoding="utf-8")))
globals().update(_DADOS)
LOGO_ARQUIVO = _DADOS.get("LOGO_ARQUIVO", "logo-horizontal.svg")
EXCECOES = _DADOS.get("EXCECOES", {})   # {"avaliacoes": "motivo"} — só com decisão humana registrada

# ═══════════════════════ O QUE O MOTOR RECALCULA (igual ao gerador original) ═══════════════════════
def url_de(slug):
    return BASE + CAMINHOS.get(slug, f"/{slug}/")

_HOJE = __import__("datetime").date.today()
ATUALIZADO = _HOJE.isoformat()
ATUALIZADO_TXT = f"{_HOJE.day} de {MESES[_HOJE.month - 1]} de {_HOJE.year}"

vfile = RAIZ / ".versao"
VER = int(vfile.read_text().strip()) + 1 if vfile.exists() else 1
vfile.write_text(str(VER))

# ═══════════════════════ MONTAGEM ═══════════════════════
def e(t):
    return html.escape(t, quote=True)


def bloco_numeros():
    """A lista sai DUPLICADA: é o que fecha o laço sem salto. A cópia NÃO repete o `data-conta`."""
    def item(n, s, r, copia=False):
        oculto = ' aria-hidden="true"' if copia else ''
        if not re.fullmatch(r"[\d.,]+", n):
            return f'<li{oculto}><b class="palavra">{n}</b><span>{r}</span></li>'
        conta = f'<span>{n}</span>' if copia else f'<span data-conta="{n}">0</span>'
        return f'<li{oculto}><b>{conta}{f"<i>{s}</i>" if s else ""}</b><span>{r}</span></li>'
    return "".join(item(*x) for x in NUMEROS) + "".join(item(*x, copia=True) for x in NUMEROS)


def srcset_avif(nome):
    """As larguras AVIF que o ferramentas/imagens-web.py gerou. Sem nenhuma, PARA: srcset apontando para
    arquivo que não existe não dá erro visível — só a foto quebrada."""
    ws = sorted(int(m.group(1)) for p in (RAIZ / "site" / "assets" / "img").glob(f"{nome}-*.avif")
                if (m := re.fullmatch(re.escape(nome) + r"-(\d+)", p.stem)))
    if not ws:
        raise SystemExit(f"ERRO: {nome} sem AVIF — rodar python3 ferramentas/imagens-web.py")
    return ", ".join(f"../assets/img/{nome}-{w}.avif {w}w" for w in ws)


def bloco_cards():
    """§6c do modelo: card com a FOTO de fundo, véu subindo da base, sinal em linha no canto.
    `pathLength="1"` em cada traço: o CSS "desenha" o sinal com a mesma duração em qualquer traço."""
    out = []
    for gi, (grupo, itens) in enumerate(GRUPOS):
        out.append(f'<h3 class="grupo-titulo">{grupo}</h3>')
        out.append('<ul class="cards cards--foto">')
        for ci, (titulo, ico, texto, tags) in enumerate(itens):
            traco = re.sub(r"<(path|circle|line|polyline|polygon|rect|ellipse)\b", r'<\1 pathLength="1"', ICONES[ico])
            out.append(
                f'<li style="--d:{ci}">'
                f'<img class="cards__foto" src="../assets/img/card-{ico}.webp" '
                f'srcset="../assets/img/card-{ico}-400.webp 400w, ../assets/img/card-{ico}-660.webp 660w, '
                f'../assets/img/card-{ico}.webp 800w" sizes="(max-width: 640px) 92vw, (max-width: 980px) 45vw, 400px" '
                f'width="800" height="1000" loading="lazy" decoding="async" alt="{e(FOTOS_CARDS[ico])}">'
                f'<span class="cards__ico" aria-hidden="true"><svg viewBox="0 0 24 24">{traco}</svg></span>'
                f'<div class="cards__corpo"><h4>{titulo}</h4><p>{texto}</p><p class="cards__tags">{tags}</p></div></li>')
        out.append('</ul>')
    return "".join(out)


SILHUETA = ('<svg class="medico__silhueta" viewBox="0 0 64 64" aria-hidden="true">'
            '<circle cx="32" cy="23" r="11"/><path d="M11 58c2.4-12.4 11-19 21-19s18.6 6.6 21 19"/></svg>')


def bloco_corpo():
    out = []
    for i, m in enumerate(CORPO_CLINICO):
        if m["foto"]:
            foto = (f'<picture><source type="image/avif" sizes="(max-width: 980px) 46vw, 300px" '
                    f'srcset="{srcset_avif(m["foto"])}"><img src="../assets/img/{m["foto"]}.jpg" width="600" '
                    f'height="750" loading="lazy" decoding="async" alt="{e(m["alt"])}"></picture>')
            classe = "medico"
        else:
            foto, classe = SILHUETA, "medico medico--vaga"
        # CRM e RQE sem quebra no meio (erro 5e). 28-09 (a dona): sem os dois confirmados, o cartão fica SEM a linha
        # ("tira essa informação para não ficar feio"); antes dizia "CRM e RQE a confirmar".
        registro = (f'<span class="nw">{m["crm"]}</span> · <span class="nw">{m["rqe"]}</span>'
                    if m["crm"] and m["rqe"] else "")
        area = f'<p class="medico__area">{m["area"]}</p>' if m["area"] else ""
        # 22-09: o horário de atendimento de cada médico, quando a clínica passa (a dona mandou o da Dra. Teodora e o do Dr. Otávio)
        # "das 8h às 12h" sem quebrar no meio (a mesma família do erro 5e)
        agenda = (f'<p class="medico__agenda"><b>Atende</b>'
                  + re.sub(r"(das \d{1,2}h(?:\d{2})? às \d{1,2}h(?:\d{2})?)", r'<span class="nw">\1</span>', e(m["agenda"]))
                  + '</p>') if m.get("agenda") else ""
        out.append(f'<li class="{classe}" style="--d:{i}"><div class="medico__foto">{foto}</div>'
                   f'<div class="medico__corpo"><h3>{m["nome"]}</h3><p class="medico__cargo">{m["cargo"]}</p>'
                   f'{area}{agenda}' + (f'<p class="medico__reg">{registro}</p>' if registro else '') + '</div></li>')
    return "".join(out)

def bloco_passos():
    return "".join(f'<li class="{"destaque" if d else ""}"><div><h3>{t}</h3><p>{p}</p></div></li>'
                   for t, d, p in PASSOS)


def bloco_espaco():
    """A faixa do espaço em LAÇO (4ª rodada, pedido da dona): a lista sai DUPLICADA — a cópia com aria-hidden e alt vazio.
    A legenda fica só para o leitor de tela: texto passando não se lê."""
    def figura(img, leg, copia):
        oculto = ' aria-hidden="true"' if copia else ''
        alt = "" if copia else f"{e(leg)} — {NOME}, {ALT_SUFIXO}"  # MOTOR: parâmetro
        legenda = "" if copia else f'<figcaption class="so-leitor">{leg}</figcaption>'
        return (f'<figure{oculto}><picture><source type="image/avif" sizes="(max-width: 900px) 64vw, 380px" '
                f'srcset="{srcset_avif(img)}"><img src="../assets/img/{img}.jpg" width="1000" height="667" '
                f'loading="lazy" decoding="async" alt="{alt}"></picture>{legenda}</figure>')
    return "".join(figura(i, l, False) for i, l in ESPACO) + "".join(figura(i, l, True) for i, l in ESPACO)


def bloco_semente():
    return json.dumps(AVALIACOES_SEMENTE, ensure_ascii=False, indent=1).replace("</", "<\\/")


def bloco_faq():
    # telefone e CEP sem quebra no hífen — só no HTML visível; o FAQPage do JSON-LD leva o texto puro
    nw = lambda t: re.sub(r"\(\d{2}\) \d{4,5}-\d{4}|\b\d{5}-\d{3}\b", lambda m: f'<span class="nw">{m.group(0)}</span>', t)
    return "".join(f'<details><summary><h3>{p}</h3></summary><div class="faq__resp">{nw(r)}</div></details>'
                   for p, r in FAQ)


def bloco_motivos(lista):
    """Os quatro motivos da dobra 3. O número é enfeite (aria-hidden): quem numera para o leitor de tela é o <ol>."""
    return "".join(f'<li style="--d:{i}"><b class="motivos__n" aria-hidden="true">{i + 1:02d}</b>'
                   f'<h3>{titulo}</h3><p>{texto}</p></li>' for i, (titulo, texto) in enumerate(lista))


def bloco_quem_foto(nome, alt):
    """A foto do "quem é": a equipe na página do instituto, o retrato dela na página da médica (4:5, AVIF por largura)."""
    return (f'<picture><source type="image/avif" sizes="(max-width: 900px) 92vw, 530px" srcset="{srcset_avif(nome)}">'
            f'<img src="../assets/img/{nome}.jpg" width="900" height="1125" loading="lazy" decoding="async" '
            f'alt="{e(alt)}"></picture>')


def bloco_horarios():
    return "".join(f"<dt>{d}</dt><dd>{h}</dd>" for d, h in HORARIOS)


RODAPE_LEGAL = (f'{RAZAO_SOCIAL} · <span class="nw">CNPJ {CNPJ}</span><br>{RT_ROTULO}: {DIRETORA} · <span class="nw">{CRM} · {RQE}</span> ({ESPECIALIDADE_NOME})'
                + (f"<br>Inscrição do instituto no {CONSELHO_SIGLA_UF} nº {CRM_INSTITUTO}" if CRM_INSTITUTO else ""))  # MOTOR: parâmetros

# MOTOR: SERVICOS, CONDICOES e SABERES vêm do cliente.json (o mapa que Google e IAs leem)


def jsonld(slug, v):
    """O grafo que Google e IAs leem: a PÁGINA médica, o SITE, o INSTITUTO (MedicalClinic = negócio local,
    NAP idêntico ao Perfil do Google, o Perfil primeiro no sameAs) e os OFTALMOLOGISTAS (Person, com CRM e
    RQE — E-E-A-T de saúde), costurados por @id. Médico sem CRM e RQE confirmados NÃO entra.
    ⚠️ Sem `medicalSpecialty`: o schema.org não tem valor para oftalmologia (só Optometric, que é outra
    profissão). ⚠️ NUNCA aggregateRating com a nota do Google — política do Google."""
    url = url_de(slug)
    id_site, id_pag = f"{BASE}/#site", f"{url}#pagina"
    id_ins, id_med = f"{BASE}/#instituto", f"{BASE}/#{DIRETOR_ID}"  # MOTOR: parâmetro
    conselho = {"@type": "Organization", "name": CONSELHO_NOME}  # MOTOR: parâmetro

    def pessoa(m):
        titulo, nome = m["nome"].split(" ", 1)
        oficio = ("Médica" if titulo == "Dra." else "Médico") + " " + OFICIO  # MOTOR: parâmetro
        return {
            "@type": "Person", "@id": f"{BASE}/#{m['id']}", "name": nome, "alternateName": m["nome"],
            "honorificPrefix": titulo,
            "jobTitle": oficio + (DIRETOR_CARGO if m["id"] == DIRETOR_ID else ""),  # MOTOR: parâmetro
            "image": f"{BASE}/assets/img/{m['foto']}.jpg",
            "hasOccupation": {"@type": "Occupation", "name": oficio,
                              "occupationLocation": {"@type": "City", "name": ENDERECO_CIDADE}},
            "hasCredential": [
                {"@type": "EducationalOccupationalCredential", "credentialCategory": "Registro profissional (CRM)",
                 "recognizedBy": conselho, "name": m["crm"]},
                {"@type": "EducationalOccupationalCredential",
                 "credentialCategory": "Registro de Qualificação de Especialista (RQE)",
                 "recognizedBy": conselho, "name": f"{m['rqe']} — {ESPECIALIDADE_NOME}"},  # MOTOR: parâmetro
            ],
            "knowsAbout": m["saberes"],
            "worksFor": {"@id": id_ins},
        }
    # só quem tem CRM e RQE confirmados (a Dra. Teodora entra quando os dela chegarem)
    # na página da Dra. Heloísa Figueiral, só ela
    medicos = [pessoa(m) for m in CORPO_CLINICO
               if m["crm"] and m["rqe"] and (v["_PERFIL"] != "medica" or m["id"] == DIRETOR_ID)]  # MOTOR: parâmetro
    instituto = {
        "@type": TIPO_ORG, "@id": id_ins, "name": NOME, "legalName": RAZAO_SOCIAL, "taxID": CNPJ,  # MOTOR: parâmetro
        "description": JSONLD_DESCRICAO,  # MOTOR: parâmetro
        "url": url_de(CANONICA), "image": f"{BASE}/assets/img/og.jpg",
        # a versão VERTICAL do manual (quase quadrada: o Google recorta logo em quadrado), PNG transparente
        "logo": {"@type": "ImageObject", "url": f"{BASE}/assets/img/{LOGO_PNG}", "width": 600, "height": 576},  # MOTOR: parâmetro
        "telephone": "+" + WHATSAPP, "email": EMAIL,
        "priceRange": "$$", "currenciesAccepted": "BRL", "isAcceptingNewPatients": True,
        "address": {"@type": "PostalAddress", "streetAddress": ENDERECO_RUA, "addressLocality": ENDERECO_CIDADE,
                    "addressRegion": ENDERECO_UF, "postalCode": ENDERECO_CEP, "addressCountry": "BR"},
        "geo": {"@type": "GeoCoordinates", "latitude": GEO[0] if GEO else None, "longitude": GEO[1] if GEO else None},
        "hasMap": f"https://www.google.com/maps?cid={CID_GOOGLE}",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": [f"https://schema.org/{d}" for d in dias],
             "opens": abre, "closes": fecha} for dias, abre, fecha in HORARIOS_LD],
        "sameAs": [f"https://www.google.com/maps?cid={CID_GOOGLE}", INSTAGRAM, SITE_ATUAL],
        "founder": {"@id": id_med}, "employee": [{"@id": p["@id"]} for p in medicos],
        "knowsAbout": SABERES,
        "areaServed": [{"@type": "City", "name": ENDERECO_CIDADE}]
                      + [{"@type": "Place", "name": f"{b}, {ENDERECO_CIDADE}"} for b in BAIRROS]
                      + [{"@type": "AdministrativeArea", "name": a} for a in AREAS_EXTRA],  # MOTOR: parâmetro
        "availableService": [{"@type": tipo, "name": nome} for tipo, nome in SERVICOS],
    }
    # MOTOR: cliente novo sem Perfil do Google/geo, ou com dado ainda "(a confirmar)" — o campo sai do JSON-LD em vez de mentir
    if not GEO:
        instituto.pop("geo")
    if not CID_GOOGLE:
        instituto.pop("hasMap")
    instituto["sameAs"] = [s for s in instituto["sameAs"] if s and not s.endswith("cid=")]
    for k in ("legalName", "taxID", "email"):
        if not instituto.get(k) or "a confirmar" in str(instituto[k]):
            instituto.pop(k, None)
    if _DADOS.get("LOGO_PNG_W"):
        instituto["logo"].update({"width": _DADOS["LOGO_PNG_W"], "height": _DADOS["LOGO_PNG_H"]})
    if not HORARIOS_LD:
        instituto.pop("openingHoursSpecification")
    site = {"@type": "WebSite", "@id": id_site, "url": f"{BASE}/", "name": f"{NOME} — {SITE_NOME_SUFIXO}",  # MOTOR: parâmetro
            "inLanguage": "pt-BR", "publisher": {"@id": id_ins}}
    pagina = {
        "@type": "MedicalWebPage", "@id": id_pag, "url": url, "name": v["TITLE"], "description": v["DESCRICAO"],
        "inLanguage": "pt-BR", "isPartOf": {"@id": id_site},
        "mainEntity": {"@id": id_med if v["_PERFIL"] == "medica" else id_ins},
        "publisher": {"@id": id_ins},
        "about": ([{"@id": id_med}] if v["_PERFIL"] == "medica" else []) + [{"@id": id_ins}]
                 + [{"@type": "MedicalCondition", "name": c} for c in CONDICOES],
        "audience": {"@type": "MedicalAudience", "audienceType": "Patient"},
        "primaryImageOfPage": {"@type": "ImageObject", "url": f"{BASE}/assets/img/{v['OG_IMAGEM']}", "width": 1200, "height": 630},
        "dateModified": ATUALIZADO,
    }
    if REVISADO_PELO_MEDICO:
        pagina["reviewedBy"] = {"@id": id_med}
        pagina["lastReviewed"] = REVISADO_PELO_MEDICO
    faq = {"@type": "FAQPage", "@id": f"{url}#faq", "isPartOf": {"@id": id_pag},
           "mainEntity": [{"@type": "Question", "name": p, "acceptedAnswer": {"@type": "Answer", "text": r}}
                          for p, r in FAQ]}
    return json.dumps({"@context": "https://schema.org", "@graph": [site, pagina, instituto, *medicos, faq]},
                      ensure_ascii=False, separators=(",", ":"))


def hash_img(nome, pasta="img", _cache={}):
    """Hash curto do conteúdo: a URL muda só quando o ARQUIVO muda (imagem, vídeo e fonte são immutable)."""
    chave = pasta + "/" + nome
    if chave not in _cache:
        caminho = RAIZ / "site" / "assets" / pasta / nome
        if not caminho.exists():
            raise SystemExit(f"ERRO: a página aponta para assets/{chave}, que não existe")
        _cache[chave] = hashlib.sha1(caminho.read_bytes()).hexdigest()[:8]
    return _cache[chave]


def css_enxuto():
    """O estilo.css EMBUTIDO (PageSpeed): em <link> ele trava a pintura. Tira comentários e espaços em
    volta de { } ; , > — nunca em volta de + e - (o calc() precisa deles)."""
    s = (RAIZ / "site" / "assets" / "css" / "estilo.css").read_text(encoding="utf-8")
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{};,>])\s*", r"\1", s)
    return s.replace(";}", "}").strip()


CSS = css_enxuto()
tpl = (MOTOR / "template" / "pagina.html").read_text(encoding="utf-8")  # MOTOR: o molde é comum (lp-fabrica)


def logo_embutido():
    if not LOGO_ARQUIVO:   # MOTOR: cliente novo sem logo na pasta — o nome em texto, na cor do texto (pendência pede o logo)
        return f'<span class="marca__logo" style="display:block;width:auto;aspect-ratio:auto;font:600 1.25rem/48px var(--titulo);white-space:nowrap">{e(NOME)}</span>'
    if not LOGO_ARQUIVO.endswith(".svg"):   # MOTOR: cliente novo com logo em imagem (a fábrica faz a versão branca em PNG)
        # máscara na cor do texto (currentColor): branco sobre a capa, a cor da marca na barra clara — como o SVG do página-base
        url = f"../assets/img/{LOGO_ARQUIVO}"
        return (f'<span class="marca__logo" aria-hidden="true" style="display:block;background:currentColor;'
                f'-webkit-mask:url({url}) center/contain no-repeat;mask:url({url}) center/contain no-repeat"></span>')
    """O logo horizontal do manual de marca (ferramentas/logo-do-manual.py) EMBUTIDO no cabeçalho, com
    fill=currentColor: a cor vem do CSS do link. width/height reservam o lugar antes do CSS (48 px de altura)."""
    s = (RAIZ / "site" / "assets" / "img" / LOGO_ARQUIVO).read_text(encoding="utf-8")  # MOTOR: o nome do logo vem do cliente.json
    abre = '<svg xmlns="http://www.w3.org/2000/svg" '
    if s.count(' fill="#0c5f50"') != 1 or not s.startswith(abre):
        raise SystemExit("ERRO: {LOGO_ARQUIVO} não tem a forma que o logo-do-manual.py escreve")
    return (s.replace(' fill="#0c5f50"', ' fill="currentColor"')
             .replace(abre, '<svg class="marca__logo" width="245" height="48" aria-hidden="true" focusable="false" ', 1))


LOGO_SVG = logo_embutido()


def trocar(molde, nome, novo):
    padrao = re.compile(r"<!-- troca:%s -->.*?<!-- /troca:%s -->" % (nome, nome), re.S)
    saida, n = padrao.subn(lambda m: novo, molde)
    if n != 1:
        raise SystemExit(f"ERRO: marcador troca:{nome} aparece {n} vez(es) no template")
    return saida


def bloco(molde, nome):
    achados = re.findall(r"<!-- bloco:%s -->\n(.*?)\n\s*<!-- /bloco:%s -->" % (nome, nome), molde, re.S)
    if len(achados) != 1:
        raise SystemExit(f"ERRO: marcador bloco:{nome} aparece {len(achados)} vez(es) no template")
    return achados[0]


def cena_rolagem(molde):
    """A abertura da cena: capa + o instituto dentro do palco, números logo depois."""
    return (CENA_HTML.replace("[[CAPA_TEXTO]]", bloco(molde, "capa-texto"))
                     .replace("[[QUEM_TEXTO]]", bloco(molde, "quem-texto"))
            + bloco(molde, "numeros"))


_CENA = sorted((RAIZ / "site" / "assets" / "video" / "cena").glob("cena-*.avif"))
QUADROS_N = len(_CENA)
QUADROS_H = hashlib.sha1(b"".join(p.read_bytes() for p in _CENA)).hexdigest()[:8] if _CENA else "0"
_CENAM = sorted((RAIZ / "site" / "assets" / "video" / "cena").glob("movel-*.avif"))
QUADROS_HM = hashlib.sha1(b"".join(p.read_bytes() for p in _CENAM)).hexdigest()[:8] if _CENAM else "0"
if _CENAM and len(_CENAM) != QUADROS_N:
    raise SystemExit(f"ERRO: {QUADROS_N} quadros de desktop e {len(_CENAM)} de celular — têm de ser iguais")
def molde_com(trocas):
    """O template com as trocas da página, na ordem (a cena lê os blocos do molde JÁ trocado)."""
    molde = tpl
    for nome, novo in trocas.items():
        molde = trocar(molde, nome, novo(molde) if callable(novo) else novo)
    return molde


if any("abertura" in v.get("_TROCAS", {}) for v in VARIANTES.values()) and not QUADROS_N:
    raise SystemExit("ERRO: uma página usa a cena, mas não há quadros em site/assets/video/cena/")
PAGINAS = [(slug, dict(PADRAO_PAGINA, **v), molde_com(v.get("_TROCAS", {})), False) for slug, v in VARIANTES.items()]
for slug, t in TESTES.items():
    # o teste SOBRESCREVE a classe da capa da base (23-09: a base institucional tem " capa--exame"; o kwarg repetido quebrava)
    PAGINAS.append((slug, {**PADRAO_PAGINA, **VARIANTES[t["base"]], "CAPA_CLASSE": t["CAPA_CLASSE"], "_BASE": t["base"]},
                    molde_com(t["trocas"]), True))

for slug, v, molde, teste in PAGINAS:
    base_slug = v.get("_BASE", slug)
    campos = {k: val for k, val in v.items() if not k.startswith("_")}
    campos.setdefault("CAPA_CLASSE", "")
    campos.update({
        "SLUG": slug, "BASE": BASE, "VER": str(VER), "ZAP": v.get("_ZAP", ZAP), "CSS": CSS, "LOGO_SVG": LOGO_SVG,
        "GTM_HEAD": GTM_HEAD.replace("[[ID]]", GTM_ID) if GTM_ID else "",   # 16-09: a variação de teste também vai a anúncio
        "GTM_BODY": GTM_BODY.replace("[[ID]]", GTM_ID) if GTM_ID else "",
        "ROBOTS": ("index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
                   if INDEXAR and not teste else "noindex, nofollow"),
        "CANONICAL": url_de(base_slug),              # cada página é a sua; o teste aponta para a base (22-09: caminho público)
        "NOME": NOME, "MARCA_LINHA": MARCA_LINHA, "INSTAGRAM": INSTAGRAM, "EMAIL": EMAIL,
        "TEL": TELEFONE, "TEL_FMT": TEL_FMT, "ZAP_FMT": ZAP_FMT,
        "ENDERECO_RUA": ENDERECO_RUA, "ENDERECO_BAIRRO": ENDERECO_BAIRRO, "ENDERECO_CIDADE": ENDERECO_CIDADE,
        "ENDERECO_UF": ENDERECO_UF, "ENDERECO_CEP": ENDERECO_CEP, "ENDERECO_REFERENCIA": ENDERECO_REFERENCIA,
        "ENDERECO_LINHA": ENDERECO_UMA_LINHA.replace(ENDERECO_CEP, f'<span class="nw">{ENDERECO_CEP}</span>'), "HORARIOS_HTML": bloco_horarios(),
        "MAPA_Q": urllib.parse.quote(f"{NOME}, {ENDERECO_UMA_LINHA}"),
        "NUMEROS": bloco_numeros(), "MOTIVOS": bloco_motivos(v["_MOTIVOS"]), "QUEM_FOTO": bloco_quem_foto(*v["_QUEM_FOTO"]),
        "SALA_HEAD": SALA_HEAD, "SALA_TEXTO": SALA_TEXTO,
        "CORPO_LEAD": CORPO_LEAD, "CORPO_HTML": bloco_corpo(),
        "CARDS": bloco_cards(), "PASSOS": bloco_passos(), "ESPACO": bloco_espaco(),
        "SEMENTE": bloco_semente(), "NOTA_GOOGLE": NOTA_GOOGLE, "TOTAL_GOOGLE": TOTAL_GOOGLE,
        "CID_GOOGLE": CID_GOOGLE, "AVALIACOES_URL": AVALIACOES_SERVICO + "?lugar=" + PLACE_ID,
        "FAQ_HTML": bloco_faq(), "JSONLD": jsonld(base_slug, v), "RODAPE_LEGAL": RODAPE_LEGAL,
        "QUADROS_H": QUADROS_H, "QUADROS_N": str(QUADROS_N), "QUADROS_HM": QUADROS_HM,
        "ATUALIZADO_TXT": ATUALIZADO_TXT, "ATUALIZADO": ATUALIZADO,
        # MOTOR: textos que eram literais do página-base no molde (28-09) — o padrão é o texto do página-base, para a paridade
        "SITE_NOME_SUFIXO": SITE_NOME_SUFIXO, "ALT_SUFIXO": ALT_SUFIXO, "ESPECIALIDADE_NOME": ESPECIALIDADE_NOME,
        "CAPA_ALT": _DADOS.get("CAPA_ALT", "A Dra. Fulana faz o exame de retina com o retinógrafo portátil, na sala de exames do " + NOME),
        "CATALOGO_ETIQUETA": _DADOS.get("CATALOGO_ETIQUETA", "O que o instituto trata"),
        "CORPO_HEAD": _DADOS.get("CORPO_HEAD", "Os oftalmologistas do instituto."),
        "ONDE_HEAD": _DADOS.get("ONDE_HEAD", "A clínica de olhos na Rua Exemplo, no Centro."),
        "LOGO_RODAPE": _DADOS.get("LOGO_RODAPE", "logo-vertical-creme.svg"),
        "LOGO_RODAPE_W": str(_DADOS.get("LOGO_RODAPE_W", 376)), "LOGO_RODAPE_H": str(_DADOS.get("LOGO_RODAPE_H", 361)),
        "LOGO_RODAPE_ALT": _DADOS.get("LOGO_RODAPE_ALT", NOME + " — Medicina Integrada"),
        "RODAPE_AVISO": _DADOS.get("RODAPE_AVISO", "Esta página tem caráter informativo e não substitui a consulta médica. Conteúdo publicado em\n"
                                   "    conformidade com a Resolução CFM nº 2.336/2023. As fotos de exame foram feitas com a equipe do instituto; a imagem da cirurgia é ilustrativa."),
    })
    saida = molde
    if not _DADOS.get("LOGO_RODAPE", "x"):   # MOTOR: sem logo, o rodapé fica só com o nome
        saida = re.sub(r'\s*<img class="rodape__logo"[^>]*>', "", saida, count=1, flags=re.S)
    if not PLACE_ID:   # MOTOR: cliente sem Perfil do Google ligado → a dobra de avaliações sai inteira (nada de nota inventada)
        saida = re.sub(r'\n[^\n]*<section class="prova" id="avaliacoes".*?</section>\n', "\n", saida, count=1, flags=re.S)
    for k, val in campos.items():
        saida = saida.replace("{{%s}}" % k, val)

    # cache-busting das IMAGENS, vídeos e FONTES por hash do conteúdo — dentro de srcset e do CSS embutido
    saida = re.sub(r'(\.\./assets/(img|video|fonts)/([A-Za-z0-9._-]+\.(?:jpg|png|webp|avif|svg|mp4|woff2)))(?!\?)',
                   lambda m: m.group(1) + '?h=' + hash_img(m.group(3), m.group(2)), saida)

    # exceções ao padrão DECLARADAS na página, para o conferidor ler (doutrina/01-padrao): as do cliente.json (decisão humana,
    # com o motivo) e a da versão com cena, em que a cena É a capa e o "quem" (a dobra vira <div>, não <section>)
    excecoes = dict(EXCECOES)
    if not re.search(r'<section[^>]*\bid="capa"', saida) and 'class="cena' in saida:
        excecoes.setdefault("capa", "cena da versão com vídeo na rolagem")
        excecoes.setdefault("quem", "cena da versão com vídeo na rolagem")
    if excecoes:
        metas = "".join(f'\n<meta name="lp-excecao" content="{k}:{html.escape(str(m), quote=True)}">' for k, m in excecoes.items())
        saida = re.sub(r'(<meta name="robots"[^>]*>)', lambda x: x.group(1) + metas, saida, count=1)

    sobrou = re.findall(r"\{\{([A-Z_0-9]+)\}\}", saida)
    if sobrou:
        raise SystemExit(f"ERRO: placeholder sem valor em {slug}: {sorted(set(sobrou))}")
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', saida, re.S):
        json.loads(b)       # chave duplicada não dá erro visível: validar antes de ir ao ar

    destino = RAIZ / "site" / slug
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "index.html").write_text(saida, encoding="utf-8")
    print(f"  {slug}/index.html  ({len(saida)//1024} KB)")

# ── /privacidade/: página curta e factual, linkada no rodapé e no aviso de cookies. Fora do sitemap, noindex. ──
_priv = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Privacidade | {NOME}</title>
<meta name="robots" content="noindex, follow"><link rel="canonical" href="{BASE}/privacidade/">
<style>body{{margin:0;background:#F5F2EB;color:#1F2A26;font:16px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
main{{max-width:44rem;margin:0 auto;padding:2.5rem 1.2rem 4rem}}h1{{font-size:1.7rem;line-height:1.2}}h2{{font-size:1.1rem;margin-top:1.8rem}}a{{color:#1F4F42}}</style></head>
<body><main><p><a href="/">← {NOME}</a></p><h1>Privacidade</h1>
<p>Esta página explica como as páginas da {NOME} ({BASE.split('//')[1]}) tratam dados de quem as visita. Responsável: {RAZAO_SOCIAL}, CNPJ {CNPJ}.</p>
<h2>O que coletamos</h2><p>Dados de navegação por cookies e tecnologias parecidas: páginas vistas, origem da visita (por exemplo, um anúncio do Google ou do Instagram) e cliques nos botões de contato. Não pedimos nome, telefone nem dado de saúde nesta página.</p>
<h2>Para quê</h2><p>Medir quais anúncios e canais trazem pacientes, melhorar a página e o atendimento. Ferramentas usadas: Google (Tag Manager, Analytics e Ads) e Meta (Facebook e Instagram).</p>
<h2>Seus direitos</h2><p>Você pode pedir informação, correção ou exclusão dos seus dados, como prevê a Lei Geral de Proteção de Dados (Lei 13.709/2018), pelo WhatsApp {ZAP_FMT} ou pelo telefone {TEL_FMT}. Também pode apagar ou bloquear os cookies no seu navegador.</p>
<p><small>Atualizada em {ATUALIZADO_TXT}.</small></p></main></body></html>"""
(RAIZ / "site" / "privacidade").mkdir(parents=True, exist_ok=True)
(RAIZ / "site" / "privacidade" / "index.html").write_text(_priv, encoding="utf-8")

(RAIZ / "site" / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    + "".join(f'  <url><loc>{url_de(s)}</loc><lastmod>{ATUALIZADO}</lastmod><changefreq>monthly</changefreq>'
              f'<priority>{"1.0" if s == CANONICA else "0.8"}</priority>'
              f'<image:image><image:loc>{BASE}/assets/img/{VARIANTES[s].get("OG_IMAGEM", "og.jpg")}</image:loc></image:image></url>\n'
              for s in VARIANTES)
    + '</urlset>\n', encoding="utf-8")

(RAIZ / "site" / "robots.txt").write_text(
    ("# PRÉVIA — página de campanha, ainda não indexável.\n"
     "# Vira indexável trocando INDEXAR=True em gerar.py (ANTES de apontar o domínio: erro 19l).\n"
     "User-agent: *\nDisallow: /\n" if not INDEXAR else
     "# Busca e IAs liberadas. Os robôs de IA precisam estar EXPLÍCITOS: sem eles a\n"
     "# página não existe para ChatGPT, Claude, Perplexity, Gemini, Copilot e Meta AI.\n"
     "User-agent: *\nAllow: /\n\n"
     + "".join(f"User-agent: {r}\nAllow: /\n\n" for r in (
         "Googlebot", "Google-Extended", "Bingbot", "Applebot", "Applebot-Extended",
         "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
         "PerplexityBot", "Perplexity-User", "meta-externalagent", "DuckAssistBot", "Amazonbot", "CCBot"))
     + f"Sitemap: {BASE}/sitemap.xml\n"), encoding="utf-8")

(RAIZ / "site" / f"{INDEXNOW_CHAVE}.txt").write_text(INDEXNOW_CHAVE, encoding="utf-8")

# o vercel.json também sai daqui: o X-Robots-Tag acompanha o INDEXAR (erro 19g)
_imut = [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]
_cab = [{"source": "/assets/img/(.*)", "headers": _imut},
        {"source": "/assets/video/(.*)", "headers": _imut},
        {"source": "/assets/fonts/(.*)", "headers": _imut},
        {"source": "/assets/(css|js)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}]}]
_noindex = [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]
if not INDEXAR:
    _cab.append({"source": "/(.*)", "headers": _noindex})
else:
    # 22-09: indexável só no www. Os subdomínios do teste A/B e a prévia servem o MESMO html (com a canônica no www) e ficam
    # fora do índice pelo cabeçalho; os testes (vídeo em laço) também, em qualquer host.
    for _h in list(SUBDOMINIOS) + [PREVIA_HOST]:
        _cab.append({"source": "/(.*)", "has": [{"type": "host", "value": _h}], "headers": _noindex})
    for _slug in TESTES:
        for _cam in {CAMINHOS.get(_slug, f"/{_slug}/"), f"/{_slug}/"}:
            _cab.append({"source": _cam + "(.*)", "headers": _noindex})
_cab.append({"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"},
                                             {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]})
_fora_lp = [{"type": "host", "value": h} for h in SUBDOMINIOS]
_redir = [
    # a raiz sem www → www, com o caminho e a busca (o gclid do anúncio chega junto); :caminho(.*) e não :param* (erro 19j)
    {"source": "/:caminho(.*)", "has": [{"type": "host", "value": DOMINIO_DO_SITE}],
     "destination": f"https://{HOST_PRINCIPAL}/:caminho", "permanent": True},
]
if REDIRECIONAR_PREVIA:
    _redir.append({"source": "/:caminho(.*)", "has": [{"type": "host", "value": PREVIA_HOST}],
                   "destination": f"https://{HOST_PRINCIPAL}/:caminho", "permanent": True})
for _slug, _cam in CAMINHOS.items():                     # o slug antigo → o caminho público (links da prévia e das LPs)
    if _cam != f"/{_slug}/":
        _redir.append({"source": f"/{_slug}/", "missing": _fora_lp, "destination": _cam, "permanent": True})
for _antigo in ANTIGOS_GREATPAGES:
    _redir.append({"source": _antigo, "missing": _fora_lp, "destination": "/", "permanent": True})
_rewr = [{"source": "/", "has": [{"type": "host", "value": h}], "destination": f"/{slug}/"} for h, slug in SUBDOMINIOS.items()]
for _slug, _cam in CAMINHOS.items():                     # o caminho público → a pasta (o endereço da barra não muda)
    if _cam != f"/{_slug}/":
        _rewr.append({"source": _cam, "missing": _fora_lp if _cam == "/" else [], "destination": f"/{_slug}/"})
for _r in _rewr:
    if not _r.get("missing"):
        _r.pop("missing", None)
(RAIZ / "site" / "vercel.json").write_text(json.dumps({
    "$schema": "https://openapi.vercel.sh/vercel.json", "cleanUrls": True, "trailingSlash": True,
    "redirects": _redir, "rewrites": _rewr, "headers": _cab}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(RAIZ / "site" / "llms.txt").unlink(missing_ok=True)     # peso 0 no Lighthouse; mito para o Farol

print(f"\nv={VER} · {len(FAQ)} perguntas no FAQ (visível e JSON-LD, mesma lista)")
print(f"CSS embutido: {len(CSS) // 1024} KB · {sum(len(i) for _, i in GRUPOS)} cards · páginas: {', '.join(p[0] for p in PAGINAS)}")
print(f"INDEXAR={INDEXAR}" + ("" if INDEXAR else "  (prévia: noindex na meta, no robots.txt e no X-Robots-Tag)"))
