"""A FICHA do cliente novo: a IA olha o briefing e TODAS as fotos da pasta e devolve o que a página precisa e que não é texto
de venda — identidade e contato (só o que os insumos dizem), responsável técnico, as cores do logo, e qual foto vai em cada
lugar (capa pelo PORTEIRO da doutrina, "quem é", espaço, retratos), com a descrição do que se vê em cada foto.
Nada é inventado: o que faltar vira PENDENCIA (e o sistema põe um marcador visível na prévia)."""
import base64, io, json, pathlib, time, urllib.request
from PIL import Image, ImageOps

SISTEMA = """Você é o PREPARADOR DE INSUMOS da fábrica de landing pages da agência. Recebe os INSUMOS de um cliente (briefing,
pedido do assessor) e as FOTOS da pasta dele. Devolve a FICHA em JSON. Leis:
1. NADA INVENTADO. Endereço, telefone, WhatsApp, e-mail, horários, CNPJ, razão social, registro no conselho (CRM/RQE, CRO,
   OAB, CREFITO) e nome do responsável SÓ se estiverem nos insumos, escritos. Faltou → string vazia "" e uma linha em PENDENCIAS.
2. Telefones só com dígitos, com 55 e DDD (ex.: "5500900000000"). Se houver um número de WhatsApp e outro de ligação, separe.
3. HORARIOS = [["Segunda a sexta", "8h às 17h"], ["Sábado", "8h às 12h"]] e HORARIOS_LD no formato schema.org
   [[["Monday","Tuesday"], "08:00", "17:00"], …]. Sem horário nos insumos → listas vazias + pendência.
4. PALETA a partir do LOGO: "marca" = a cor principal do logo (hex escuro/saturado o bastante para texto branco por cima);
   "destaque" = uma cor clara de apoio que combine (hex). Sem logo → tons neutros elegantes e pendência.
5. FOTOS — use SÓ nomes de arquivo da lista. Para cada foto, DESCRICOES[nome] = o que se vê, em uma frase concreta (quem,
   onde, fazendo o quê, que aparelho) — nunca o que a foto "transmite". Quem é a pessoa NÃO se deduz da imagem.
   · "logo": o arquivo do logo (ou "").
   · "capa": a foto da capa, escolhida pelo PORTEIRO da casa: (1) plano geral com o ambiente legível em volta da pessoa;
     (2) ar acima da cabeça; (3) nenhuma borda corta a pessoa; (4) um lado com superfície calma para o texto.
     Em "capa_porteiro" diga quais dos 4 itens a escolhida cumpre. Se nenhuma cumpre todos, escolha a melhor e ponha em
     PENDENCIAS "capa: nenhuma foto passa no porteiro (itens que falham…) — pedir foto em plano geral".
   · "quem": foto do profissional ou da equipe no consultório (vertical de preferência) para a dobra "quem é".
   · "retrato": o melhor retrato individual do profissional responsável (ou "").
   · "espaco": 3 a 5 fotos do ambiente/atendimento (sala, recepção, aparelho, consulta) — sem repetir a capa.
   · "cards": até 12 fotos que sirvam de ilustração de serviço/exame/tratamento (aparelho, procedimento, detalhe), com o
     assunto de cada uma em CARDS_ASSUNTO[nome].
   Foto com paciente identificável em situação sensível, documento, tela com dado de paciente, ou print de rede social: não use.
6. TIPO: "clinica" (clínica/instituto com equipe) ou "profissional" (um profissional com consultório).
7. FOCO[nome] = [x, y] com 0–1 (fração da largura e da altura) do ponto que não pode sair do recorte — o rosto da pessoa
   principal, ou o aparelho/detalhe quando não houver pessoa — para toda foto escolhida (capa, quem, retrato, espaço, cards).
Responda SÓ o JSON com as chaves: NOME, NOME_CURTO, TIPO, ESPECIALIDADE_NOME, OFICIO, RESPONSAVEL {nome, nome_sem_titulo,
cargo, registro, rqe}, RAZAO_SOCIAL, CNPJ, ENDERECO {rua, bairro, cidade, uf, cep, referencia}, TELEFONE, WHATSAPP, EMAIL,
INSTAGRAM, HORARIOS, HORARIOS_LD, PALETA {marca, destaque}, FOTOS {logo, capa, capa_porteiro, quem, retrato, espaco, cards},
DESCRICOES, CARDS_ASSUNTO, FOCO, PENDENCIAS."""


def miniatura(p: pathlib.Path, lado=640):
    """JPEG pequeno para a IA ver (a IA não precisa de 2400 px para escolher a capa)."""
    if p.suffix.lower() == ".svg":
        return None
    im = ImageOps.exif_transpose(Image.open(p))
    if im.mode in ("RGBA", "LA", "P"):
        fundo = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        fundo.paste(im, mask=im.split()[-1])
        im = fundo
    im = im.convert("RGB")
    im.thumbnail((lado, lado))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=80)
    return base64.b64encode(b.getvalue()).decode()


def gerar_ficha(insumos: str, fotos: list, chave: str, modelo="google/gemini-2.5-pro"):
    partes = [{"type": "text", "text": "INSUMOS:\n" + insumos + "\n\nFOTOS DA PASTA (cada uma precedida do nome):"}]
    for f in fotos:
        m = miniatura(f)
        if m:
            partes += [{"type": "text", "text": f"foto: {f.name} ({Image.open(f).size[0]}×{Image.open(f).size[1]})"},
                       {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + m}}]
        else:
            partes += [{"type": "text", "text": f"arquivo vetorial: {f.name} (provável logo)"}]
    corpo = {"model": modelo, "temperature": 0.2, "response_format": {"type": "json_object"}, "usage": {"include": True},
             "messages": [{"role": "system", "content": SISTEMA}, {"role": "user", "content": partes}]}
    ultimo = None
    for tentativa in range(3):
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(corpo).encode(),
                                         headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json",
                                                  "X-Title": "lp-matriz ficha"})
            with urllib.request.urlopen(req, timeout=600) as r:
                resp = json.loads(r.read())
            tx = ((resp.get("choices") or [{}])[0].get("message") or {}).get("content")
            if not tx:
                ultimo = f"resposta vazia ({(resp.get('choices') or [{}])[0].get('finish_reason')})"
                time.sleep(5)
                continue
            tx = tx.strip()
            if tx.startswith("```"):
                tx = tx.split("\n", 1)[1].rsplit("```", 1)[0]
            u = resp.get("usage") or {}
            custo = u.get("cost") or (u.get("cost_details") or {}).get("upstream_inference_cost") or 0
            ficha = json.loads(tx)
            validar_ficha(ficha, {f.name for f in fotos})
            return ficha, custo
        except (ValueError, OSError) as e:
            ultimo = str(e)
            time.sleep(5)
    raise RuntimeError(f"a ficha não saiu depois de 3 tentativas: {ultimo}")


def validar_ficha(f, nomes):
    """Nome de foto que não existe vira vazio (a IA às vezes 'corrige' o nome do arquivo)."""
    fotos = f.setdefault("FOTOS", {})
    for k in ("logo", "capa", "quem", "retrato"):
        if fotos.get(k) and fotos[k] not in nomes:
            f.setdefault("PENDENCIAS", []).append(f"foto «{fotos[k]}» indicada para {k} não existe na pasta")
            fotos[k] = ""
    for k in ("espaco", "cards"):
        fotos[k] = [x for x in (fotos.get(k) or []) if x in nomes]
    # telefones: a IA às vezes devolve lista; o 1º vira WhatsApp e o 2º, o telefone da recepção
    for k in ("WHATSAPP", "TELEFONE"):
        if isinstance(f.get(k), list):
            lista = [str(x) for x in f[k] if x]
            f[k] = lista[0] if lista else ""
            if k == "WHATSAPP" and len(lista) > 1 and not f.get("TELEFONE"):
                f["TELEFONE"] = lista[1]
        f[k] = "".join(ch for ch in str(f.get(k) or "") if ch.isdigit())
        if f[k] and not f[k].startswith("55"):
            f[k] = "55" + f[k]
    if not f.get("TELEFONE"):
        f["TELEFONE"] = f.get("WHATSAPP", "")
    if not fotos.get("capa"):
        f.setdefault("PENDENCIAS", []).append("capa: a pasta não tem foto utilizável para a capa")
    return f
