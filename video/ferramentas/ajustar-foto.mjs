// PASSO 2 — Ajuste da foto ANTES do vídeo (API de imagens da OpenAI), com conferência de que a pessoa continua a mesma.
//   node ajustar-foto.mjs --cliente <slug> --foto <arquivo> --pedido "apagar os porta-retratos da estante" [--saida <pasta>]
//                         [--tamanho 2048x1152] [--qualidade high] [--modelo <modelo de imagem>] [--versao a1]
//                         [--caderno <arq>] [--livro-openai <arq>]
// Também serve para criar o QUADRO FINAL a partir da mesma foto (ex.: --pedido "ela levanta o olhar para a câmera, sorriso leve"),
// quando não há um 2º clique do mesmo ensaio — mais arriscado: a conferência diz se o rosto mudou.
// Chaves: OPENAI_API_KEY (edição) e GEMINI_API_KEY (conferência). Toda peça informa quanto custou; se OPENAI_CREDITO_USD
// estiver definida, informa também quanto resta (o livro de gastos é ./gastos-openai.jsonl, ou --livro-openai).
// Nada vai para página nem para vídeo sem o responsável aprovar o antes/depois — PARE aqui.
import fs from 'node:fs'; import path from 'node:path'
import { args, chaveOpenAI, jpeg, parteImagem, gemini, prancha, registrar, LIVRO_OPENAI, MODELO_FOTO, PRECO_FOTO, dolar } from './comum.mjs'

const a = args(), cliente = a.um('cliente'), foto = a.um('foto'), pedido = a.um('pedido')
if (!cliente || !foto || !pedido) { console.log('uso: node ajustar-foto.mjs --cliente <slug> --foto <arquivo> --pedido "..." [--tamanho 2048x1152] [--qualidade high]'); process.exit(1) }
const saida = path.resolve(a.um('saida', `lp-video-${cliente}`)); fs.mkdirSync(saida, { recursive: true })
const modelo = a.um('modelo', MODELO_FOTO), tamanho = a.um('tamanho', '2048x1152'), qualidade = a.um('qualidade', 'high'), versao = a.um('versao', 'a1')

const prompt = `Edit this photograph. Make ONLY this change: ${pedido}.
Everything else must stay exactly as in the original photo: the same person (identical face, facial features, skin texture, hair, expression unless the change asks otherwise, body, hands, clothing, accessories), the same lighting, colors, camera angle, lens and framing.
Photorealistic, natural photographic look, no beauty retouching, no CGI look. Do not add people, text, logos or new objects.
Output a 16:9 horizontal photograph; if the canvas needs to grow, extend the existing scene naturally (same wall, same room), never stretch the person.`

const ref = jpeg(foto, 2048, 95)
const fd = new FormData()
fd.append('model', modelo); fd.append('prompt', prompt); fd.append('size', tamanho); fd.append('quality', qualidade); fd.append('n', '1')
fd.append('image[]', new Blob([fs.readFileSync(ref)], { type: 'image/jpeg' }), path.basename(ref))
const t0 = Date.now()
const r = await fetch('https://api.openai.com/v1/images/edits', { method: 'POST', headers: { Authorization: 'Bearer ' + chaveOpenAI() }, body: fd })
const j = await r.json()
if (!r.ok) { console.log('ERRO OpenAI', r.status, JSON.stringify(j.error || j).slice(0, 400)); process.exit(1) }
const u = j.usage || {}, det = u.input_tokens_details || {}
const custo = ((det.text_tokens || 0) * PRECO_FOTO.texto + (det.image_tokens || 0) * PRECO_FOTO.imagem_in + (u.output_tokens || 0) * PRECO_FOTO.imagem_out) / 1e6
const base = path.basename(foto).replace(/\.[^.]+$/, '')
const final = path.join(saida, `${base} — ajustada ${versao}.png`)
fs.writeFileSync(final, Buffer.from(j.data[0].b64_json, 'base64'))

// Livro de gastos da OpenAI: se outras ferramentas usam a mesma conta, aponte todas para o mesmo arquivo (--livro-openai)
fs.appendFileSync(LIVRO_OPENAI, JSON.stringify({ em: new Date().toISOString(), cliente, conceito: 'lp-video-ajuste', versao, modelo, tamanho, qualidade, refs: 1, usage: u, custo_usd: +custo.toFixed(4), segundos: Math.round((Date.now() - t0) / 1000), arquivo: final }) + '\n')
const credito = process.env.OPENAI_CREDITO_USD ? +process.env.OPENAI_CREDITO_USD : null
const gasto = fs.readFileSync(LIVRO_OPENAI, 'utf8').trim().split('\n').reduce((s, l) => s + (JSON.parse(l).custo_usd || 0), 0)

// Conferência: a IA de edição mexe na fisionomia — compara original × ajustada
const { dados: conf } = await gemini([{ text: `Compare a foto ORIGINAL (1ª) com a EDITADA (2ª). O pedido de edição foi: "${pedido}".
Responda APENAS em JSON: {"pedido_atendido":true,"mesma_pessoa":true,"mudancas_no_rosto":"nenhuma|leves|fortes","outras_mudancas_indesejadas":["..."],
"artefatos":["mãos, bordas, texto, objetos estranhos..."],"aprovaria":true,"resumo":"1 frase em português para o responsável"}` }, parteImagem(foto), parteImagem(final)])

const lado = prancha([foto, final], ['ANTES · ' + path.basename(foto), 'DEPOIS · ' + versao], path.join(saida, `${base} — antes e depois ${versao}.jpg`), 2, 900)
registrar({ tipo: 'ajuste', cliente, foto, pedido, modelo, tamanho, qualidade, custo_usd: +custo.toFixed(4), arquivo: final, conferencia: conf })
console.log(`OK ${final}
antes/depois: ${lado}
conferência: ${conf.aprovaria ? '🟢' : '🔴'} ${conf.resumo} (rosto: ${conf.mudancas_no_rosto}; pedido atendido: ${conf.pedido_atendido ? 'sim' : 'não'})${(conf.outras_mudancas_indesejadas || []).length ? '\n  mudou também: ' + conf.outras_mudancas_indesejadas.join('; ') : ''}
CUSTO deste ajuste: ${dolar(custo)} · gasto total no livro: ${dolar(gasto)}${credito != null ? ` · RESTA ~${dolar(credito - gasto)} de ${dolar(credito)}` : ''}`)
