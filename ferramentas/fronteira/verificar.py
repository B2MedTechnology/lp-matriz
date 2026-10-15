#!/usr/bin/env python3
"""FRONTEIRA (06-10-2026): este repositório é da B2MedTechnology e não recebe cliente nem dado da GHOT Mídia ou da Focus
Marketing. Compara cada sequência de 1 a 6 palavras com ghot-focus.sha (só hashes) e recusa pastas que são só da GHOT.
Roda no CI (.github/workflows/fronteira.yml) e à mão: python3 ferramentas/fronteira/verificar.py"""
import hashlib, pathlib, re, subprocess, sys, unicodedata
RAIZ = pathlib.Path(__file__).resolve().parents[2]
import os
# 15-10-2026 — repositório PÚBLICO: sal e lista são segredos (FRONTEIRA_SAL/FRONTEIRA_LISTA no CI, ou ~/.config/lp-matriz/).
_c = pathlib.Path.home() / ".config/lp-matriz"
SAL = (os.environ.get("FRONTEIRA_SAL") or ((_c / "sal").read_text() if (_c / "sal").exists() else "")).strip()
_l = os.environ.get("FRONTEIRA_LISTA") or ((_c / "ghot-focus.sha").read_text() if (_c / "ghot-focus.sha").exists() else "")
if not (SAL and _l): print("⛔ fronteira: segredo ausente (FRONTEIRA_SAL / FRONTEIRA_LISTA) — recusado"); sys.exit(1)
LISTA = {l.strip() for l in _l.splitlines() if l.strip() and not l.startswith("#")}
CAMINHOS = re.compile(r"(^|/)ferramentas/ghot/|(^|/)ops/db/ghot-\d+-seed|ESCOPO-GHOT\.json$|n8n-[a-z]+-mapa-waba")
def norm(s): return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())
def h(s): return hashlib.sha256((SAL + "|" + s).encode()).hexdigest()[:20]
achados = []
for f in subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True).stdout.split("\n"):
    if not f or f.endswith("ghot-focus.sha"): continue
    if CAMINHOS.search(f): achados.append(f"{f}: pasta/arquivo da GHOT"); continue
    try: t = (RAIZ / f).read_text(encoding="utf-8")
    except Exception: continue
    for n, linha in enumerate(t.split("\n"), 1):
        p = norm(linha).split()
        if any(h(" ".join(p[i:i + k])) in LISTA for i in range(len(p)) for k in range(1, 7) if i + k <= len(p)):
            achados.append(f"{f}:{n}: cita cliente da GHOT/Focus")
for a in achados[:60]: print("✗", a)
if achados: print(f"\n{len(achados)} achado(s): isto é da GHOT/Focus e vai para o GitHub da GHOT (tavaresfx), não para a B2MedTechnology."); sys.exit(1)
print("✓ fronteira: nada da GHOT/Focus neste repositório")
