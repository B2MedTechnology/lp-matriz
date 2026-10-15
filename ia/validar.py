#!/usr/bin/env python3
"""O REVISOR mecânico: o que dá para conferir sem gosto. Devolve a lista de problemas (vazia = passou)."""
import json, re, sys

# vocabulário genérico que o Guia de copy e o padrão v3 recusam ("estética de IA", superlativo vazio) — rodada 2, 28-09
PROIBIDAS = ["humanizad", "excelência", "de ponta", "o que há de mais moderno", "mais moderno", "jornada", "liberdade visual",
             "transformar vidas", "transforma vidas", "qualidade de vida", "atendimento diferenciado", "referência em", "cuidado integral",
             "garantindo", "garantir", "garantia", "melhor resultado", "melhores resultados", "previsibilidade", "precisão e agilidade",
             "com excelência", "de excelência", "comprometid", "compromisso com", "inovação", "inovador", "de qualidade",
             "tecnologia avançada", "equipamentos modernos", "ambiente moderno", "sinta-se", "sinta seguro", "sem dor", "indolor",
             "rápida recuperação", "recuperação rápida", "100% seguro", "mais seguros", "totalmente seguro", "resultado garantido",
             "o melhor", "a melhor", "os melhores", "as melhores", "único em", "pioneir",
             "acolh", "cuidado completo", "cuidado oftalmológico completo", "tecnologia e ", "experiência prática", "experiência tranquila"]
NUMEROS_ABSTRATOS = ["pilar", "foco", "em foco", "tipos de", "categorias", "etapas", "valores"]

def textos(o):
    if isinstance(o, str): yield o
    elif isinstance(o, list):
        for x in o: yield from textos(x)
    elif isinstance(o, dict):
        for x in o.values(): yield from textos(x)

def validar(c, icones=None, exigir_fotos_cards=True):
    p = []
    # preço nunca na página (regra da dona, 28-09-2026): qualquer R$ em qualquer campo de texto é recusado
    com_preco = sorted({s.strip()[:90] for s in textos({k: v for k, v in c.items() if k not in ("PENDENCIAS", "NUMEROS_FONTES")}) if re.search(r"R\$\s*\d|\d+\s*reais", s)})
    if com_preco:
        p.append(f"preço na página (proibido: o valor é sempre informado pelo WhatsApp): {com_preco[:3]}")
    if c.get("FILTRO") and c.get("FAQ") and not c["FAQ"][0][1].startswith(c["FILTRO"]):
        p.append("a 1ª resposta do FAQ tem de começar com a frase do FILTRO, idêntica")
    if icones is not None:
        usados = [x[1] for g in c.get('GRUPOS', []) for x in g[1]]
        ruins = [u for u in usados if u not in icones]
        if ruins: p.append(f'card com ícone fora da lista disponível: {ruins} (use só: {", ".join(icones)})')
        if len(usados) != len(set(usados)): p.append('ícone de card repetido')
        falta_alt = [u for u in usados if u not in c.get('FOTOS_CARDS', {})] if exigir_fotos_cards else []
        if falta_alt: p.append(f'FOTOS_CARDS sem o texto da foto de: {falta_alt}')
    pp = c.get("PAGINA_PRINCIPAL", {})
    if len(re.sub("<[^>]+>", "", pp.get("TITLE", ""))) > 60: p.append(f"TITLE com {len(pp.get('TITLE',''))} caracteres (máximo 60): {pp.get('TITLE')}")
    if len(pp.get("DESCRICAO", "")) > 155: p.append(f"DESCRICAO com {len(pp.get('DESCRICAO',''))} caracteres (máximo 155)")
    n, f = c.get("NUMEROS", []), c.get("NUMEROS_FONTES", [])
    if len(n) != len(f): p.append("NUMEROS e NUMEROS_FONTES com quantidades diferentes")
    if not 5 <= len(n) <= 8: p.append(f"NUMEROS com {len(n)} itens (o padrão pede 5–8 — se faltam fatos, registre em PENDENCIAS)")
    for x in n:
        r = (x[2] if len(x) > 2 else "").lower()
        if any(a in r for a in NUMEROS_ABSTRATOS): p.append(f"número abstrato (não decide a escolha do paciente): {x}")
    if len(c.get("MOTIVOS", [])) != 4: p.append("MOTIVOS precisa de exatamente 4")
    if not 6 <= len(c.get("FAQ", [])) <= 8: p.append(f"FAQ com {len(c.get('FAQ', []))} perguntas (6–8)")
    if not str(c.get("MENSAGEM", "")).startswith("Olá! Vim pelo site"): p.append("MENSAGEM não começa por 'Olá! Vim pelo site'")
    tudo = " \n ".join(textos({k: v for k, v in c.items() if k not in ("PENDENCIAS", "NUMEROS_FONTES")})).lower()
    achadas = sorted({w for w in PROIBIDAS if w in tudo})
    if achadas:
        exemplos = []
        for w in achadas:
            i = tudo.find(w); exemplos.append(f"«{w}» em: …{tudo[max(0, i-60):i+60].strip()}…")
        p.append("vocabulário genérico/promessa (trocar por fato concreto do atendimento, ou cortar): " + " | ".join(exemplos))
    return p

if __name__ == "__main__":
    c = json.load(open(sys.argv[1], encoding="utf-8"))
    r = validar(c); print(json.dumps(r, ensure_ascii=False, indent=1)); sys.exit(1 if r else 0)
