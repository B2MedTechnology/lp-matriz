#!/usr/bin/env python3
"""
A IA escreve o CONTEÚDO da página (números com fonte, quem é, catálogo, filtro, passos, espaço, FAQ, eixo/H1, SEO) seguindo o
GUIA — a doutrina da matriz compilada por área (ia/guia.py). NAP, domínio, GTM e imagens vêm do sistema (cliente.json).
Modelo padrão: Gemini 2.5 Pro pelo OpenRouter (validado contra páginas aprovadas: ~US$ 0,45–0,57 e 5–8 min por página).

    OPENROUTER_API_KEY=… python3 ia/gerar-conteudo.py --dir <pasta do cliente> --insumos <insumos.md> --area medico

· --dir: a pasta do cliente (cliente.json + site/assets) — a infra que a prévia usa. Fica FORA do repositório.
· --exemplo: um cliente.json de página APROVADA, dado como exemplo de forma, tom e nível (padrão: o cliente fictício
  exemplos/clinica-exemplo). Nunca o próprio cliente.
Saída: saidas/<cliente>/<carimbo>/ com prompt (sha), respostas, revisor, conteudo.json e uso (tokens e custo).
"""
import argparse, datetime, re, hashlib, json, os, pathlib, subprocess, sys, time, urllib.request, urllib.error

AQUI = pathlib.Path(__file__).resolve().parent.parent
CAMPOS = [  # o que a IA escreve; o resto (NAP, GTM, domínio, imagens) vem do sistema
    "MARCA_LINHA", "NUMEROS", "NUMEROS_FONTES", "QUEM_HEAD", "MOTIVOS", "CORPO_LEAD", "CORPO_CLINICO",
    "GRUPOS", "FOTOS_CARDS", "FILTRO", "PASSOS", "ESPACO", "SALA_HEAD", "SALA_TEXTO", "FAQ", "BAIRROS",
    "PADRAO_PAGINA", "PAGINA_PRINCIPAL", "MENSAGEM", "SERVICOS", "CONDICOES", "SABERES", "JSONLD_DESCRICAO",
    "PENDENCIAS",
]

def dados_anotados(caminho):
    """O conteúdo de uma página aprovada (os campos que a IA escreve), como exemplo de forma, tom e nível."""
    d = json.loads(pathlib.Path(caminho).read_text(encoding="utf-8"))
    return json.dumps({k: d[k] for k in CAMPOS if k in d}, ensure_ascii=False, indent=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=""); ap.add_argument("--exemplo", default=str(AQUI / "exemplos" / "clinica-exemplo" / "cliente.json"))
    ap.add_argument("--insumos", required=True); ap.add_argument("--area", default="medico")
    ap.add_argument("--modelo", default="google/gemini-2.5-pro"); ap.add_argument("--temperatura", type=float, default=0.4)
    ap.add_argument("--rotulo", default="")
    # cliente NOVO (a fábrica): a pasta de trabalho no lugar de clientes/<ref>, a saída fixa e os ícones da biblioteca do motor
    ap.add_argument("--dir", default=""); ap.add_argument("--saida", default="")
    a = ap.parse_args()

    sys.path.insert(0, str(AQUI / "ia")); from guia import montar_guia
    guia = montar_guia(a.area)
    regras = (AQUI / "ia" / "regras-de-saida.md").read_text(encoding="utf-8")
    exemplo = dados_anotados(a.exemplo)
    base_cli = pathlib.Path(a.dir).resolve() if a.dir else AQUI / "exemplos" / (a.ref or "clinica-exemplo")
    if pathlib.Path(a.exemplo).resolve() == (base_cli / "cliente.json").resolve():
        sys.exit("o exemplo não pode ser o próprio cliente")
    a.ref = a.ref or base_cli.name
    ref = json.loads((base_cli / "cliente.json").read_text(encoding="utf-8"))
    img = base_cli / "site" / "assets" / "img"
    fotos = sorted({re.sub(r"-\d{3,4}$", "", p.stem) for p in list(img.glob("*.jpg")) + list(img.glob("*.webp"))})
    icones = sorted(ref.get("ICONES", {}).keys())
    biblioteca = json.loads((AQUI / "motor" / "icones.json").read_text(encoding="utf-8")) if a.dir else None
    if biblioteca:
        icones = sorted(biblioteca)
    insumos = pathlib.Path(a.insumos).read_text(encoding="utf-8")

    sistema = (
        "Você é a FÁBRICA DE LANDING PAGES da agência. Escreve o CONTEÚDO de uma landing page de cliente seguindo, "
        "sem exceção, o GUIA abaixo — a doutrina da agência (padrão, anatomia da página, insumos, copy, SEO, componentes, "
        "lições aprendidas e a regra do conselho). Onde o guia e o exemplo divergirem, o GUIA manda.\n\n"
        + regras + "\n\n==================== GUIA ====================\n" + guia
        + "\n\n==================== EXEMPLO ANOTADO (outro cliente, página aprovada) ====================\n"
        "Conteúdo de uma página aprovada (cliente fictício). Use como referência de FORMA, TOM e NÍVEL — "
        "nunca copie fatos, números ou textos dele.\n```json\n" + exemplo + "\n```"
    )
    usuario = (
        "==================== INSUMOS DO CLIENTE ====================\n" + insumos
        + "\n\n==================== FATOS FIXOS (do sistema — não altere) ====================\n"
        + json.dumps({k: ref.get(k) for k in ["NOME", "ENDERECO_RUA", "ENDERECO_BAIRRO", "ENDERECO_CIDADE", "ENDERECO_UF",
                                              "ENDERECO_CEP", "ZAP_FMT", "TEL_FMT", "HORARIOS", "NOTA_GOOGLE", "TOTAL_GOOGLE"]},
                     ensure_ascii=False)
        + "\n\nFOTOS DISPONÍVEIS (nomes de arquivo; os cards usam as que começam com card-, o espaço as que começam com espaco- ou sala-): "
        + ", ".join(fotos)
        + ("\n\nÍCONES DOS CARDS disponíveis (cada um tem a foto card-<ícone> e o desenho do sinal): " + ", ".join(icones)
           if not biblioteca else
           "\n\nÍCONES DOS CARDS (biblioteca — escolha o que corresponde ao ASSUNTO do card; a foto do card o sistema escolhe "
           "depois, entre as fotos do cliente; FOTOS_CARDS pode ficar {}): "
           + "; ".join(f"{k} = {v['desc']}" for k, v in sorted(biblioteca.items())))
        + ". Todo card usa um destes; o mesmo ícone não se repete."
        + "\n\nDevolva SÓ o objeto JSON com as chaves: " + ", ".join(CAMPOS)
    )
    # As fotos vão junto: alt e legenda descrevem o que a IA VÊ, não o nome do arquivo.
    import base64
    def menor(stem):
        vs = sorted(img.glob(stem + "-*.webp")) + sorted(img.glob(stem + "-*.jpg")) + [img / (stem + e) for e in (".webp", ".jpg") if (img / (stem + e)).exists()]
        vs = [v for v in vs if re.fullmatch(re.escape(stem) + r"(-\d+)?\.(webp|jpg)", v.name)]
        return min(vs, key=lambda v: v.stat().st_size) if vs else None
    vistas = [f for f in fotos if f.startswith(("card-", "espaco-", "sala-", "medic", "instituto-equipe", "quem", "retrato"))][:24]
    partes = [{"type": "text", "text": usuario + "\n\nAS FOTOS SEGUEM ABAIXO, cada uma precedida do nome. O alt de cada card "
               "(FOTOS_CARDS) e a legenda de cada foto do ESPACO descrevem SÓ o que se vê na imagem — nada de nome de aparelho, "
               "diagnóstico ou pessoa que a imagem não mostre com clareza. Quem é cada médico na foto NÃO se deduz da imagem."}]
    for f in vistas:
        m = menor(f)
        if not m: continue
        tipo = "image/webp" if m.suffix == ".webp" else "image/jpeg"
        partes += [{"type": "text", "text": f"foto: {f}"},
                   {"type": "image_url", "image_url": {"url": f"data:{tipo};base64," + base64.b64encode(m.read_bytes()).decode()}}]
    corpo = {"model": a.modelo, "temperature": a.temperatura, "response_format": {"type": "json_object"},
             "usage": {"include": True},
             "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": partes}]}
    dest = pathlib.Path(a.saida) if a.saida else AQUI / "saidas" / a.ref / (datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + (f"-{a.rotulo}" if a.rotulo else ""))
    dest.mkdir(parents=True, exist_ok=True)
    _leve = json.loads(json.dumps(corpo))
    for m in _leve["messages"]:
        if isinstance(m["content"], list):
            m["content"] = [x if x["type"] == "text" else {"type": "image_url", "image_url": "<imagem omitida>"} for x in m["content"]]
    (dest / "prompt.json").write_text(json.dumps(_leve, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.path.insert(0, str(AQUI / "ia")); from validar import validar
    def chamar(msgs, modelo=None):
        c = dict(corpo, messages=msgs, **({"model": modelo} if modelo else {}))
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(c).encode(),
                                     headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                                              "Content-Type": "application/json", "X-Title": "lp-matriz"})
        for tentativa in range(3):   # a Google às vezes devolve finish_reason=error sem conteúdo: tenta de novo
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    resp = json.loads(r.read())
            except (ConnectionError, TimeoutError, urllib.error.URLError) as e:
                print(f"  rede caiu ({e}), tentando de novo", file=sys.stderr); time.sleep(10); resp = {}; continue
            if (resp.get("choices") or [{}])[0].get("message", {}).get("content"): return resp
            print(f"  resposta vazia ({(resp.get('choices') or [{}])[0].get('finish_reason')}), tentando de novo", file=sys.stderr)
            time.sleep(5)
        return resp
    def ler(resp):
        tx = resp["choices"][0]["message"]["content"].strip()
        if tx.startswith("```"): tx = tx.split("\n", 1)[1].rsplit("```", 1)[0]
        return tx, json.loads(tx)
    fixos = json.dumps({k: ref.get(k) for k in ["NOME", "ENDERECO_RUA", "ENDERECO_BAIRRO", "ENDERECO_CIDADE", "ENDERECO_UF",
                        "ENDERECO_CEP", "ZAP_FMT", "TEL_FMT", "HORARIOS", "NOTA_GOOGLE", "TOTAL_GOOGLE"]}, ensure_ascii=False)
    from verificar_fatos import checar_fatos as _cf
    def checar_fatos(conteudo):
        achados, custo = _cf(conteudo, insumos, fixos, lambda m, mod: chamar(m, mod), ler)
        total["cost"] += custo
        return achados
    t0 = time.time(); msgs = list(corpo["messages"]); voltas = []; total = {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
    for volta in range(3):   # 1 geração + até 2 revisões
        resp = chamar(msgs)
        u = resp.get("usage") or {}
        for k in total: total[k] += (u.get(k) or (u.get("cost_details") or {}).get("upstream_inference_cost") or 0) if k == "cost" else (u.get(k) or 0)
        (dest / f"resposta-{volta}.json").write_text(json.dumps(resp, ensure_ascii=False, indent=1), encoding="utf-8")
        texto, conteudo = ler(resp)
        probs = validar(conteudo, icones, exigir_fotos_cards=not biblioteca)
        achados = checar_fatos(conteudo)
        probs += [f"fato que não está nos insumos ({x.get('campo')}): «{x.get('trecho')}» — {x.get('por_que')}. Corte, ou mande para PENDENCIAS como pergunta ao cliente" for x in achados]
        voltas.append(len(probs))
        (dest / f"revisor-{volta}.json").write_text(json.dumps(probs, ensure_ascii=False, indent=1), encoding="utf-8")
        if not probs or volta == 2: break
        msgs += [{"role": "assistant", "content": texto},
                 {"role": "user", "content": "O REVISOR da agência recusou estes pontos:\n- " + "\n- ".join(probs)
                  + "\n\nCorrija SÓ o que foi apontado, seguindo o guia e as regras (fato concreto dos insumos no lugar do adjetivo; "
                    "o que não tiver fato, corte ou vá para PENDENCIAS). Devolva o JSON inteiro."}]
    seg = time.time() - t0
    resp = {"usage": total}
    faltam = [c for c in CAMPOS if c not in conteudo]
    # O que o revisor ainda recusa na última volta não some: vira pendência visível para quem revisa antes de publicar.
    if probs:
        conteudo["PENDENCIAS"] = list(conteudo.get("PENDENCIAS") or []) + ["REVISOR (corrigir antes de publicar): " + x for x in probs]
    (dest / "conteudo.json").write_text(json.dumps(conteudo, ensure_ascii=False, indent=1), encoding="utf-8")
    u = resp.get("usage", {})
    uso = {"modelo": a.modelo, "segundos": round(seg, 1), "entrada": u.get("prompt_tokens"), "saida": u.get("completion_tokens"),
           "custo_usd": round(u.get("cost") or 0, 4), "problemas_por_volta": voltas, "sha_prompt": hashlib.sha1(json.dumps(corpo).encode()).hexdigest()[:10], "faltam": faltam}
    (dest / "uso.json").write_text(json.dumps(uso, indent=1), encoding="utf-8")
    print(json.dumps(uso, ensure_ascii=False)); print(dest)

if __name__ == "__main__":
    main()
