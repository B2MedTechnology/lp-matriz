"""As imagens da página no formato que o motor espera (os mesmos tamanhos e nomes da página aprovada do página-base):
capa (2400×1895 + AVIF por largura) e capa do celular (1000×1053), "quem é" 4:5, retratos 4:5, espaço 3:2, cards 4:5 em WebP,
og 1200×630, e o logo em branco (cabeçalho e rodapé sobre o fundo escuro) + favicons na cor da marca."""
import pathlib, re
from PIL import Image, ImageOps, ImageChops


def abrir(p):
    im = ImageOps.exif_transpose(Image.open(p))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        fundo = Image.new("RGB", im.size, (255, 255, 255))
        fundo.paste(im, mask=im.split()[-1])
        return fundo
    return im.convert("RGB")


def recorte(im, w, h, foco=(0.5, 0.35)):
    """Recorta na proporção w:h mantendo o FOCO (x, y em 0–1, normalmente o rosto) dentro do quadro, e redimensiona."""
    W, H = im.size
    alvo = w / h
    if W / H > alvo:
        cw, ch = int(H * alvo), H
    else:
        cw, ch = W, int(W / alvo)
    fx, fy = foco
    x = min(max(0, int(fx * W - cw / 2)), W - cw)
    y = min(max(0, int(fy * H - ch * 0.42)), H - ch)   # o foco um pouco acima do meio: sobra ar acima da cabeça
    im = im.crop((x, y, x + cw, y + ch))
    # o molde pede o tamanho exato (os srcset têm as larguras fixas); foto menor é ampliada — até ~1,3× não se nota
    return im.resize((w, h), Image.LANCZOS)


def _salvar(im, destino, fmt, **kw):
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, fmt, **kw)


def variantes(im, pasta, nome, larguras_avif, jpg=None, webp=None):
    """Salva <nome>-<w>.avif para cada largura, e a base em JPG (ou WebP)."""
    for w in larguras_avif:
        if im.width >= w * 0.98:
            _salvar(im.resize((w, round(im.height * w / im.width)), Image.LANCZOS), pasta / f"{nome}-{w}.avif", "AVIF", quality=58)
    if jpg:
        _salvar(im, pasta / f"{nome}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
    if webp:
        for w in webp:
            alvo = im if w == im.width else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
            _salvar(alvo, pasta / (f"{nome}.webp" if w == im.width else f"{nome}-{w}.webp"), "WEBP", quality=78)


def capa(src, pasta, foco):
    im = abrir(src)
    g = recorte(im, 2400, 1895, foco)
    variantes(g, pasta, "capa", [1000, 1500, 2100, 2400], jpg=True)
    m = recorte(im, 1000, 1053, foco)
    variantes(m, pasta, "capa-movel", [800, 1000], jpg=True)
    og = recorte(im, 1200, 630, foco)
    _salvar(og, pasta / "og.jpg", "JPEG", quality=84, optimize=True)


def vertical(src, pasta, nome, foco, grande=True):
    """4:5 — "quem é" (900×1125, AVIF 480–900) ou retrato do corpo clínico (600×750, AVIF 400/600)."""
    im = abrir(src)
    if grande:
        variantes(recorte(im, 900, 1125, foco), pasta, nome, [480, 600, 720, 900], jpg=True)
    else:
        variantes(recorte(im, 600, 750, foco), pasta, nome, [400, 600], jpg=True)


def espaco(src, pasta, nome, foco):
    variantes(recorte(abrir(src), 1000, 667, foco), pasta, nome, [600, 1000], jpg=True)


def card(src, pasta, ico, foco):
    variantes(recorte(abrir(src), 800, 1000, foco), pasta, f"card-{ico}", [], webp=[800, 660, 400])


def logo_branco(src, pasta, nome="logo-branco.png", altura=192):
    """O logo como silhueta BRANCA (o cabeçalho e o rodapé ficam sobre o fundo escuro da marca). Fundo branco/transparente
    vira transparência; o resto vira branco. Devolve (arquivo, largura, altura)."""
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGBA")
    r, g, b, a = im.split()
    # fundo quase branco sem transparência (JPG/PNG chapado) → alfa pelo contraste com o branco
    if a.getextrema() == (255, 255):
        cinza = ImageOps.grayscale(im.convert("RGB"))
        a = ImageOps.invert(cinza).point(lambda v: 0 if v < 28 else min(255, int(v * 1.6)))
    caixa = a.getbbox()
    if caixa:
        a = a.crop(caixa)
    branco = Image.new("RGBA", a.size, (255, 255, 255, 0))
    branco.putalpha(a)
    w = round(branco.width * altura / branco.height)
    branco = branco.resize((w, altura), Image.LANCZOS)
    _salvar(branco, pasta / nome, "PNG", optimize=True)
    return nome, w, altura


def icones(src, pasta, cor_marca):
    """favicon 48/96 e apple-touch 180: o logo branco sobre um quadrado na cor da marca; logo.png (≥112, fundo branco) p/ JSON-LD."""
    base = Image.open(pasta / "logo-branco.png").convert("RGBA")
    for lado, nome in ((48, "favicon-48.png"), (96, "favicon-96.png"), (180, "apple-touch-icon.png")):
        q = Image.new("RGBA", (lado, lado), cor_marca)
        m = base.copy()
        m.thumbnail((int(lado * 0.8), int(lado * 0.8)), Image.LANCZOS)
        q.alpha_composite(m, ((lado - m.width) // 2, (lado - m.height) // 2))
        _salvar(q.convert("RGB") if nome.startswith("apple") else q, pasta / nome, "PNG", optimize=True)
    lg = abrir(src)
    lado = max(lg.size)
    q = Image.new("RGB", (lado, lado), (255, 255, 255))
    q.paste(lg, ((lado - lg.width) // 2, (lado - lg.height) // 2))
    q.thumbnail((600, 600))
    _salvar(q, pasta / "logo.png", "PNG", optimize=True)


def icones_texto(nome, pasta, cor_marca):
    """Sem logo: as iniciais em branco sobre a cor da marca (favicons, apple-touch e o logo.png do JSON-LD)."""
    from PIL import ImageDraw, ImageFont
    palavras = [w for w in re.split(r"\s+", nome) if w[:1].isalpha() and w.lower() not in ("de", "da", "do", "dos", "das", "e", "dr.", "dra.")]
    ini = "".join(w[0] for w in palavras[:2]).upper() or "?"
    for lado, arq in ((48, "favicon-48.png"), (96, "favicon-96.png"), (180, "apple-touch-icon.png"), (600, "logo.png")):
        q = Image.new("RGB", (lado, lado), cor_marca)
        d = ImageDraw.Draw(q)
        try:
            f = ImageFont.truetype("DejaVuSans-Bold.ttf", int(lado * 0.42))
        except OSError:
            f = ImageFont.load_default(size=int(lado * 0.42))
        l, t_, r, b = d.textbbox((0, 0), ini, font=f)
        d.text(((lado - (r - l)) / 2 - l, (lado - (b - t_)) / 2 - t_), ini, fill="white", font=f)
        _salvar(q, pasta / arq, "PNG", optimize=True)
