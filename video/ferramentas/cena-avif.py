#!/usr/bin/env python3
"""
PASSO 6b — Os dois conjuntos de quadros da cena, em AVIF (desktop: quadro inteiro; celular: quadrado recortado na pessoa).

  python3 cena-avif.py <pasta-dos-png> <foco-celular> [--saida site/assets/video/cena] [--poster site/assets/img] [--desk 1280x720] [--q 72]

  <pasta-dos-png>  saída do sequencia-video.swift (q000.png, q001.png, …), com as cores CRUAS
  <foco-celular>   onde a pessoa está no quadro (0 = esquerda, 1 = direita) — o MESMO --foco do CSS do celular

Sai: cena-000.avif … (desktop) e movel-000.avif … (celular), mesmo número nos dois; e em --poster, capa-video.avif e
capa-video-movel.avif (o quadro 0 = o poster).
Precisa de Pillow >= 11.2 (python3 -c "from PIL import features; print(features.check('avif'))" tem de dar True).
"""
import argparse, glob, pathlib, shutil
from PIL import Image

a = argparse.ArgumentParser()
a.add_argument("pasta"); a.add_argument("foco", type=float)
a.add_argument("--saida", default="site/assets/video/cena")
a.add_argument("--poster", default="site/assets/img")
a.add_argument("--desk", default="1280x720")
a.add_argument("--q", type=int, default=72)
a = a.parse_args()

SAIDA = pathlib.Path(a.saida); SAIDA.mkdir(parents=True, exist_ok=True)
DESK = tuple(int(x) for x in a.desk.lower().split("x"))
quadros = sorted(glob.glob(str(pathlib.Path(a.pasta) / "*.png")))
if not quadros:
    raise SystemExit("nenhum PNG em " + a.pasta)
for i, f in enumerate(quadros):
    im = Image.open(f).convert("RGB")
    im = Image.frombytes("RGB", im.size, im.tobytes())          # tira o perfil ICC (o convert() o MANTÉM)
    d = im if im.size == DESK else im.resize(DESK, Image.LANCZOS)
    d.save(SAIDA / f"cena-{i:03d}.avif", "AVIF", quality=a.q, speed=6)
    lado = d.height; x0 = round((d.width - lado) * a.foco)
    d.crop((x0, 0, x0 + lado, lado)).save(SAIDA / f"movel-{i:03d}.avif", "AVIF", quality=a.q, speed=6)

def mb(padrao):
    return sum(p.stat().st_size for p in SAIDA.glob(padrao)) / 1e6

# o poster é o próprio quadro 0, nos dois recortes (a troca poster → canvas não pode mudar um pixel)
POSTER = pathlib.Path(a.poster); POSTER.mkdir(parents=True, exist_ok=True)
shutil.copy(SAIDA / "cena-000.avif", POSTER / "capa-video.avif")
shutil.copy(SAIDA / "movel-000.avif", POSTER / "capa-video-movel.avif")
print(f"{len(quadros)} quadros em cada conjunto · desktop {mb('cena-*.avif'):.2f} MB · celular {mb('movel-*.avif'):.2f} MB (alvo: até ~7 MB cada)")
print("confira no 1º e no último quadro do celular que a pessoa cabe no quadrado (a câmera avança).")
