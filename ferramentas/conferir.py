#!/usr/bin/env python3
"""CONFERIDOR do padrão da matriz numa landing page — publicada (URL) ou gerada (arquivo local).

Por que existe: o padrão escrito não basta. Página saiu com cards sem foto, sem a dobra de avaliações, sem o botão de pausa,
com o carrossel andando com a página pausada e com o foco do teclado invisível no fundo claro — cada caso passou por quem
"seguiu o padrão de cabeça". Nenhum link vai ao cliente sem este conferidor saindo 0.

Uso:
  python3 ferramentas/conferir.py https://www.exemplo.com.br/           (página no ar)
  python3 ferramentas/conferir.py exemplos/clinica-exemplo/site/inicio/index.html   (página gerada, antes do deploy)
Sai 1 se algo reprovar. Exceção decidida pelo dono da página: <meta name="lp-excecao" content="avaliacoes:motivo">
(vira aviso, não reprovação). A doutrina de cada item está em doutrina/ (01-padrao, 02-anatomia-da-pagina, 05-seo-e-velocidade).
"""
import json, pathlib, re, sys, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (lp-matriz-conferir)"}
ORDEM = ["capa", "quem", "tratamentos", "consulta", "sala", "avaliacoes", "duvidas", "onde"]   # doutrina/02-anatomia-da-pagina


def ler(alvo, rel=None):
    """(status, texto, cabeçalhos) de uma URL ou de um arquivo; `rel` resolve caminho relativo ao alvo."""
    if rel:
        alvo = urllib.parse.urljoin(alvo, rel) if re.match(r"https?://", alvo) else str((pathlib.Path(alvo).parent / rel.split("?")[0]).resolve())
    if re.match(r"https?://", alvo):
        r = urllib.request.urlopen(urllib.request.Request(alvo, headers=UA), timeout=30)
        return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    p = pathlib.Path(alvo)
    return (200, p.read_text(encoding="utf-8"), {}) if p.exists() else (404, "", {})


def regras_de_css(css):
    """Blocos `seletor{…}` de topo nível e de dentro de @media (o suficiente para as checagens abaixo)."""
    sem_coment = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return re.findall(r"([^{}@]+)\{([^{}]*)\}", sem_coment)


def conferir(alvo):
    ok, falhas, avisos = [], [], []
    st, h, hdr = ler(alvo)
    exc = dict(x.split(":", 1) for x in re.findall(r'<meta name="lp-excecao" content="([^"]+)"', h))

    def f(cond, msg, dobra=None):
        if cond: ok.append(msg)
        elif dobra and dobra in exc: avisos.append(f"{msg} (exceção declarada: {exc[dobra]})")
        else: falhas.append(msg)

    f(st == 200, "página responde 200")
    # ── dobras e conteúdo (doutrina/02-dobras) ──
    ids = re.findall(r'<section[^>]*\bid="([^"]+)"', h)
    for d in ORDEM: f(d in ids, f"dobra '{d}' presente", d)
    pos = [ids.index(d) for d in ORDEM if d in ids]
    f(pos == sorted(pos), "ordem das dobras (catálogo antes do filtro)")
    f('class="numeros' in h, "faixa de números")
    cards = re.findall(r"<li\b[^>]*>(?:(?!</li>).)*?cards__corpo", h, re.S)   # \b: sem ele '<link' contava como card
    semfoto = [c for c in cards if "cards__foto" not in c]
    f(cards and not semfoto, f"cards do catálogo com foto: {len(cards) - len(semfoto)}/{len(cards)}", "cards")
    grupos = re.findall(r'<ul class="cards[^"]*">(.*?)</ul>', h, re.S)
    f(grupos and all(g.count("<li") % 3 == 0 for g in grupos), "grupos de 3 completos (card que sai pede o que completa)")
    m = re.search(r'id="avaliacoes"[^>]*data-avaliacoes="([^"]+)"', h)
    f(bool(m) and "lugar=" in (m.group(1) if m else ""), "avaliações pelo serviço central com ?lugar=", "avaliacoes")
    sem = re.search(r'id="prova-semente">(.*?)</script>', h, re.S)
    try: n = len(json.loads(sem.group(1).replace("<\\/", "</"))) if sem else 0
    except Exception: n = 0
    f(n > 0, f"semente de avaliações no HTML ({n})", "avaliacoes")

    # ── dados estruturados (doutrina/05-seo-e-velocidade) ──
    blocos = re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
    grafo, jsonld_ok = [], True
    for b in blocos:
        try:
            o = json.loads(b.replace("<\\/", "</"))
            grafo += o.get("@graph", [o]) if isinstance(o, dict) else o
        except Exception: jsonld_ok = False
    f(blocos and jsonld_ok, "JSON-LD válido")
    f(not any("aggregateRating" in b for b in blocos), "sem aggregateRating no JSON-LD (avaliação autosservida)")
    produtos = [x for x in grafo if isinstance(x, dict) and "Product" in ([x.get("@type")] if isinstance(x.get("@type"), str) else x.get("@type") or [])]
    f(all(p.get("offers") for p in produtos), f"todo Product com offers dentro ({len(produtos)}); sem preço publicado o item é Service")
    f(all(isinstance(p.get("brand"), dict) and p["brand"].get("@type") == "Brand" and p["brand"].get("name") for p in produtos if "brand" in p),
      "brand do Product é {@type: Brand, name}")

    # ── cabeça, acessibilidade e LGPD (doutrina/01-padrao) ──
    f(len(re.findall(r"<h1[\s>]", h)) == 1, "um <h1> só")
    t = re.search(r"<title>(.*?)</title>", h, re.S); f(t and len(t.group(1)) <= 60, "title ≤ 60")
    dsc = re.search(r'<meta name="description" content="([^"]*)"', h); f(dsc and len(dsc.group(1)) <= 155, "description ≤ 155")
    f("viewport-fit=cover" in h, "viewport-fit=cover")
    f('fetchpriority="high"' in h, "capa com fetchpriority=high")
    f('id="pausa"' in h and "aria-pressed" in h, "botão de pausa (WCAG 2.2.2)")
    f("aviso-cookies" in h, "aviso de cookies mínimo, com Ok")
    p = h.find('id="pausa"'), h.find('class="barra"'), h.find('id="aviso-cookies"')
    f(-1 not in p and p[1] < p[0] and p[1] < p[2], "pausa e aviso DEPOIS da .barra (sobem com ela no celular)")
    pr = re.search(r'href="([^"]*privacidade[^"]*)"', h)
    f(pr is not None, "link Privacidade")
    f("<time datetime=" in h, "'página atualizada em' com <time>")
    f(re.search(r"acess[ií]vel|acessibilidade", re.sub(r"<!--.*?-->", "", h, flags=re.S), re.I) is not None, "menção de acessibilidade no rodapé")
    f("wa.me/" in h, "botão de agendar pelo WhatsApp")

    # ── prévia × domínio do cliente ──
    meta_noindex = re.search(r'<meta name="robots" content="[^"]*noindex', h) is not None
    host = urllib.parse.urlparse(alvo).netloc if re.match(r"https?://", alvo) else ""
    if host.endswith(".vercel.app"):
        f(meta_noindex and "noindex" in (hdr.get("X-Robots-Tag") or hdr.get("x-robots-tag") or "").lower(), "prévia: noindex na meta e no X-Robots-Tag")
    elif host:
        f(not meta_noindex, "domínio do cliente: indexável (sem noindex)")
        f("GTM-" in h, "GTM do cliente na página")
    elif not meta_noindex and "GTM-XXXXXXX" in h:
        avisos.append("página indexável com o GTM de exemplo (GTM-XXXXXXX): troque pelo do cliente antes do deploy")

    # ── o que só o CSS e o JS servidos mostram (doutrina/01-padrao §movimento e §foco) ──
    css_src = re.search(r'<link rel="stylesheet" href="([^"]*estilo\.css[^"]*)"', h)
    css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", h, re.S))
    if css_src:
        try: css += ler(alvo, css_src.group(1))[1]
        except Exception: pass
    js_src = re.search(r'<script src="([^"]*pagina\.js[^"]*)"', h)
    js = ""
    if js_src:
        try: js = ler(alvo, js_src.group(1))[1]
        except Exception: pass
    if css:
        regras = regras_de_css(css)
        proib = [s.strip()[:40] for s, c in regras if re.search(r"transition:[^;}]*\b(box-shadow|padding|margin|width|height|top|left|filter)\b", c)]
        f(not proib, "nenhuma transição de pintura/layout (box-shadow, padding, width, filter…)" + (f" — em: {proib[:4]}" if proib else ""))
        topo_filtro = [s.strip()[:40] for s, c in regras if re.search(r"\.(topo|barra)\b", s) and "backdrop-filter" in c]
        f(not topo_filtro, "sem backdrop-filter no topo e na barra" + (f" — em: {topo_filtro}" if topo_filtro else ""))
        raiz_foco = [c for s, c in regras if s.strip() == ":focus-visible"]
        f(raiz_foco and "--claro" not in raiz_foco[0] and "#fff" not in raiz_foco[0].lower(),
          "foco do teclado escuro no fundo claro (o claro só nas seções escuras, ≥ 3:1)")
    else:
        falhas.append("CSS não lido (estilo.css) — as checagens de movimento e foco não rodaram")
    if js:
        intervalos = re.findall(r"setInterval\(\s*([A-Za-z_$][\w$]*)", js)
        sem_pausa = []
        for nome in set(intervalos):
            corpo = re.search(r"function\s+" + re.escape(nome) + r"\s*\([^)]*\)\s*\{(.{0,400})", js, re.S)
            if not corpo or "__pausado" not in corpo.group(1): sem_pausa.append(nome)
        f(not sem_pausa, "todo laço automático (setInterval) obedece ao botão de pausa (window.__pausado)" + (f" — falta em: {sem_pausa}" if sem_pausa else ""))
    else:
        falhas.append("JS não lido (pagina.js) — a checagem do carrossel × pausa não rodou")

    # ── porteiro de anatomia: a marca só é escrita depois da conferência a 100% das fotos com pessoa ──
    if re.search(r'<meta name="lp-porteiro" content="aprovado', h): ok.append("porteiro de anatomia: fotos de pessoa aprovadas a 100%")
    else: avisos.append("sem a marca lp-porteiro: confira a 100% mãos, rostos, pele e equipamento de cada foto com pessoa (doutrina/01-padrao, porteiro de anatomia) antes de publicar")

    # ── arquivos do site ──
    if re.match(r"https?://", alvo):
        base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(alvo))
        for c in ("/favicon.ico", "/robots.txt", "/sitemap.xml"):
            try: f(ler(base + c)[0] == 200, f"{c} 200")
            except Exception: falhas.append(f"{c} não responde")
        if pr:
            try: f(ler(alvo, pr.group(1))[0] == 200, "página de privacidade 200")
            except Exception: falhas.append("página de privacidade não responde")
    else:
        site = pathlib.Path(alvo).resolve().parent.parent
        for c in ("robots.txt", "sitemap.xml", "privacidade/index.html"):
            f((site / c).exists(), f"{c} gerado")

    print(f"\n{alvo}\n  ✅ {len(ok)} ok" + "".join(f"\n  ⚠️ {a}" for a in avisos) + "".join(f"\n  ❌ {x}" for x in falhas))
    return not falhas


if __name__ == "__main__":
    alvos = sys.argv[1:]
    if not alvos: sys.exit(__doc__)
    r = [conferir(a) for a in alvos]
    sys.exit(0 if all(r) else 1)
