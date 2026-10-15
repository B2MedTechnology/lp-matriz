"""A foto de cada CARD do catálogo: a IA (só texto, barata) casa o assunto de cada card com as fotos do cliente pelas
descrições que a FICHA já fez (o que se vê em cada foto). O alt é o que se vê — nunca o nome do arquivo."""
import json, time, urllib.request

SISTEMA = """Você escolhe a FOTO de cada card do catálogo de uma landing page. Recebe os CARDS (título, ícone, texto) e as
FOTOS disponíveis com a descrição do que se vê em cada uma. Para cada card, escolha a foto que melhor ilustra o assunto:
aparelho do exame, procedimento, detalhe, ou o profissional atendendo. Não repita foto enquanto houver foto não usada
que sirva. O "alt" descreve o que se VÊ na foto escolhida, em uma frase concreta (sem nome de pessoa, sem diagnóstico).
Responda JSON {"cards": {"<ícone>": {"foto": "<nome do arquivo>", "alt": "<o que se vê>"}}}."""


def escolher(grupos, descricoes, candidatas, chave, modelo="google/gemini-2.5-flash"):
    cards = [{"icone": c[1], "titulo": c[0], "texto": c[2] if len(c) > 2 else ""} for _, lista in grupos for c in lista]
    fotos = {n: descricoes.get(n, "") for n in candidatas}
    corpo = {"model": modelo, "temperature": 0.2, "response_format": {"type": "json_object"}, "usage": {"include": True},
             "messages": [{"role": "system", "content": SISTEMA},
                          {"role": "user", "content": "CARDS:\n" + json.dumps(cards, ensure_ascii=False)
                           + "\n\nFOTOS:\n" + json.dumps(fotos, ensure_ascii=False)}]}
    custo, escolha = 0, {}
    for _ in range(3):
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(corpo).encode(),
                                         headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json",
                                                  "X-Title": "lp-matriz cards"})
            with urllib.request.urlopen(req, timeout=300) as r:
                resp = json.loads(r.read())
            u = resp.get("usage") or {}
            custo += u.get("cost") or (u.get("cost_details") or {}).get("upstream_inference_cost") or 0
            tx = ((resp.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
            tx = tx.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
            escolha = json.loads(tx).get("cards", {})
            break
        except (ValueError, OSError):
            time.sleep(4)
    # rede de segurança: card sem foto válida recebe a próxima candidata (em rodízio), com a descrição dela como alt
    usadas, saida, i = set(), {}, 0
    for c in cards:
        e = escolha.get(c["icone"]) or {}
        foto = e.get("foto") if e.get("foto") in fotos else None
        if not foto:
            livres = [n for n in candidatas if n not in usadas] or list(candidatas)
            foto = livres[i % len(livres)]
            i += 1
        usadas.add(foto)
        saida[c["icone"]] = (foto, (e.get("alt") or fotos.get(foto) or c["titulo"]).strip())
    return saida, custo
