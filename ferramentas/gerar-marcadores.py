#!/usr/bin/env python3
"""
Gera as IMAGENS-MARCADOR de um cliente de exemplo: cada peça que a página pede, nas dimensões reais, com um gradiente na
cor da marca e o nome da peça escrito — nenhuma foto real entra no repositório. Também gera os quadros da cena de rolagem
(desktop 1280x720 e celular 720x720, mesma quantidade) e os logos em SVG.

Uso: python3 ferramentas/gerar-marcadores.py exemplos/clinica-exemplo [--quadros 48] [--cor 1f5f7a]
Lê `<pasta>/marcadores.json` ({"arquivo.ext": [largura, altura]}) e escreve em `<pasta>/site/assets/`.
Numa página REAL as peças vêm das fotos do cliente (doutrina/03-insumos-e-briefing.md) e o vídeo da esteira em video/.
"""
import json, pathlib, sys
from PIL import Image, ImageDraw, ImageFont

pasta = pathlib.Path(sys.argv[1]).resolve()
arg = lambda n, d: sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d
N = int(arg("--quadros", "48"))
cor = arg("--cor", "1f5f7a")
C1 = tuple(int(cor[i:i + 2], 16) for i in (0, 2, 4))
C2 = tuple(min(255, int(c * 0.35 + 200)) for c in C1)
assets = pasta / "site" / "assets"
(assets / "img").mkdir(parents=True, exist_ok=True)
(assets / "video" / "cena").mkdir(parents=True, exist_ok=True)

def fonte(tam):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try: return ImageFont.truetype(f, tam)
        except OSError: pass
    return ImageFont.load_default()

def quadro(w, h, rotulo, t=0.0):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        k = (y / max(1, h - 1) + t) % 1.0
        c = tuple(int(C1[i] * (1 - k) + C2[i] * k) for i in range(3))
        for x in range(w): px[x, y] = c
    d = ImageDraw.Draw(im)
    f = fonte(max(12, min(w, h) // 14))
    d.text((w // 2, h // 2), rotulo, fill=(255, 255, 255), font=f, anchor="mm")
    return im

def salvar(im, destino):
    ext = destino.suffix.lower()
    if ext == ".avif": im.save(destino, "AVIF", quality=30)
    elif ext == ".webp": im.save(destino, "WEBP", quality=40)
    elif ext in (".jpg", ".jpeg"): im.save(destino, "JPEG", quality=55)
    else: im.save(destino, "PNG")

manifesto = json.loads((pasta / "marcadores.json").read_text())
for nome, (w, h) in manifesto.items():
    salvar(quadro(w, h, nome.rsplit(".", 1)[0]), assets / "img" / nome)
for i in range(N):
    t = i / N
    salvar(quadro(1280, 720, f"cena {i + 1}/{N}", t), assets / "video" / "cena" / f"cena-{i:03d}.avif")
    salvar(quadro(720, 720, f"celular {i + 1}/{N}", t), assets / "video" / "cena" / f"movel-{i:03d}.avif")
(assets / "video" / "capa-medica.mp4").write_bytes(b"")  # marcador vazio: o vídeo real vem da esteira (video/)
hexa = "#%02x%02x%02x" % C1
for nome, (w, h), cor_txt in (("logo-horizontal.svg", (320, 64), hexa), ("logo-vertical.svg", (200, 120), hexa), ("logo-vertical-creme.svg", (200, 120), "#f4efe6")):
    # forma que o motor exige (motor/gerar.py · logo_embutido): abre com <svg xmlns=…> e tem UM fill="#0c5f50", que ele
    # troca por currentColor — o logo herda a cor do texto (branco na capa, a cor da marca na barra clara)
    fill = "#0c5f50" if nome == "logo-horizontal.svg" else cor_txt
    (assets / "img" / nome).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><g fill="{fill}"><text x="50%" y="55%" text-anchor="middle" '
        f'dominant-baseline="middle" font-family="Arial, sans-serif" font-size="{h // 3}" font-weight="700" textLength="{int(w * .9)}" '
        f'lengthAdjust="spacingAndGlyphs">{"CLÍNICA DE OLHOS AURORA" if w > h * 3 else "AURORA"}</text></g></svg>')   # nome fantasia do cliente fictício
print(f"{len(manifesto)} imagens + {N}×2 quadros + 3 logos em {assets}")
