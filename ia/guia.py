"""
O GUIA que a IA lê: a doutrina da matriz (`doutrina/`) compilada por área, com o sha de cada arquivo.
A ordem é a de autoridade — o padrão (01) manda sobre o resto; a regra do conselho da área vem por último.
Uso direto: python3 ia/guia.py medico  (imprime o tamanho e as fontes)
"""
import hashlib, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONSELHO = {"medico": "medicina-cfm", "dentista": "odontologia-cfo", "advogado": "advocacia-oab", "fisioterapeuta": "fisioterapia-coffito"}

def fontes(area: str) -> list:
    if area not in CONSELHO:
        raise SystemExit(f"área desconhecida: {area} (use {', '.join(CONSELHO)})")
    d = RAIZ / "doutrina"
    comuns = sorted(p for p in d.glob("[0-9][0-9]-*.md"))
    return comuns + [d / "conselhos" / f"{CONSELHO[area]}.md"]

def montar_guia(area: str) -> str:
    partes, cab = [], []
    for p in fontes(area):
        t = p.read_text(encoding="utf-8")
        cab.append(f"- {p.relative_to(RAIZ)} · sha {hashlib.sha1(t.encode()).hexdigest()[:10]}")
        partes.append(f"\n\n<<<DOUTRINA: {p.relative_to(RAIZ)}>>>\n{t}\n<<<FIM>>>")
    return f"# GUIA DA MATRIZ DE LANDING PAGES — área: {area}\nFontes (a ordem é a de autoridade):\n" + "\n".join(cab) + "".join(partes)

if __name__ == "__main__":
    g = montar_guia(sys.argv[1] if len(sys.argv) > 1 else "medico")
    print(g.split("\n<<<")[0]); print(f"{len(g) // 1024} KB")
