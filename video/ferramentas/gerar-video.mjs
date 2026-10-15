// PASSO 4 — Gera o vídeo no Google Veo 3.1 (Gemini API) com a opção que o RESPONSÁVEL aprovou.
//   node gerar-video.mjs --cliente <slug> --sugestoes <sugestoes.json> --opcao <n> --aprovado "<frase de aprovação, literal>"
//                        [--modelo fast|lite|standard] [--resolucao 1080p] [--seed 1234] [--ancora 0.35] [--destino <pasta>] [--caderno <arq>]
//   (ou --prompt <arquivo.txt> --inicio <foto> [--fim <foto>] no lugar de --sugestoes/--opcao, para refazer com prompt ajustado)
// TRAVA: sem --aprovado não gera (custa dinheiro e anima gente: decisão humana). Imprime o custo antes e grava tudo no caderno.
// Chave: GEMINI_API_KEY (a mesma da visão; precisa de faturamento ativo — o Veo não tem camada grátis).
// Depois de baixar, roda a conferência dos 9 quadros sozinho (conferir-video.mjs).
import fs from 'node:fs'; import path from 'node:path'; import { execFileSync } from 'node:child_process'
import { args, chaveGemini, b64, registrar, VEO, PRECO_VEO, hash, dolar, AQUI, lerCaderno, CADERNO } from './comum.mjs'

const a = args(), cliente = a.um('cliente'), aprovado = a.um('aprovado')
const modelo = a.um('modelo', 'fast'), resolucao = a.um('resolucao', '1080p'), seed = a.um('seed') ? +a.um('seed') : Math.floor(Math.random() * 4e9)
const ancora = +a.um('ancora', 0.35)
let inicio = a.um('inicio'), fim = a.um('fim'), prompt, titulo = 'prompt manual', cena = a.um('cena', '')
if (a.um('sugestoes')) {
  const s = JSON.parse(fs.readFileSync(a.um('sugestoes'), 'utf8')), o = s.opcoes.find(x => x.n === +a.um('opcao'))
  if (!o) { console.log('opção inexistente em', a.um('sugestoes')); process.exit(1) }
  inicio = inicio || s.inicio; fim = fim || s.fim; prompt = o.prompt; titulo = o.titulo; cena = cena || o.cena
} else if (a.um('prompt')) prompt = fs.readFileSync(a.um('prompt'), 'utf8')
if (!cliente || !inicio || !prompt) { console.log('uso: node gerar-video.mjs --cliente <slug> --sugestoes <json> --opcao <n> --aprovado "<frase de aprovação>" [--modelo fast|lite|standard]'); process.exit(1) }
if (!aprovado) { console.log('🔒 PARADO: falta --aprovado "<a frase literal de quem aprovou>". Vídeo custa e anima gente — só com OK humano.'); process.exit(2) }
if (!VEO[modelo] || !PRECO_VEO[modelo][resolucao]) { console.log(`combinação inválida: ${modelo} ${resolucao} (Lite não faz 4K)`); process.exit(1) }

const custo = PRECO_VEO[modelo][resolucao] * 8
const anteriores = lerCaderno().filter(r => r.tipo === 'video'), gastoAntes = anteriores.reduce((s, r) => s + (r.custo_usd || 0), 0)
console.log(`Vai gerar: "${titulo}" · Veo ${modelo} ${resolucao} · 8 s · seed ${seed}\nCUSTO desta tentativa: ${dolar(custo)} (gasto anterior em vídeo: ${dolar(gastoAntes)})`)

// Entradas em 16:9 (o recorte é o mesmo nas duas, para o início e o fim baterem) — ancora 0 = topo, 0,5 = centro, 1 = base
const destino = path.resolve(a.um('destino', `lp-video-${cliente}`)); fs.mkdirSync(destino, { recursive: true })
const n = anteriores.filter(r => r.cliente === cliente).length + 1, id = `${cliente}-${String(n).padStart(2, '0')}`
const preparar = (arq, nome) => {
  const out = path.join(destino, `${id}-${nome}.jpg`)
  const py = `import sys
from PIL import Image,ImageOps
i=ImageOps.exif_transpose(Image.open(sys.argv[1])).convert('RGB'); w,h=i.size; a=float(sys.argv[3])
if w/h>16/9: nw=round(h*16/9); x=round((w-nw)/2); i=i.crop((x,0,x+nw,h))
elif w/h<16/9: nh=round(w*9/16); y=round((h-nh)*a); i=i.crop((0,y,w,y+nh))
i.thumbnail((1920,1080)); i.save(sys.argv[2],'JPEG',quality=93,subsampling=0)`
  execFileSync('python3', ['-c', py, arq, out, String(ancora)]); return out
}
const ini = preparar(inicio, 'inicio'), fi = fim ? preparar(fim, 'fim') : null
const K = chaveGemini(), BASE = 'https://generativelanguage.googleapis.com/v1beta'
const inst = { prompt, image: { inlineData: { mimeType: 'image/jpeg', data: b64(ini) } } }
if (fi) inst.lastFrame = { inlineData: { mimeType: 'image/jpeg', data: b64(fi) } }
const corpo = { instances: [inst], parameters: { aspectRatio: '16:9', resolution: resolucao, durationSeconds: 8, personGeneration: 'allow_adult', seed } }

const t0 = Date.now()
let r = await fetch(`${BASE}/models/${VEO[modelo]}:predictLongRunning`, { method: 'POST', headers: { 'x-goog-api-key': K, 'Content-Type': 'application/json' }, body: JSON.stringify(corpo) })
let j = await r.json()
if (!r.ok) { console.log('ERRO Veo', r.status, JSON.stringify(j.error || j).slice(0, 500)); registrar({ tipo: 'erro', cliente, id, modelo, resolucao, erro: (j.error || {}).message }); process.exit(1) }
const op = j.name; process.stdout.write('gerando ')
while (true) {
  await new Promise(ok => setTimeout(ok, 10000)); process.stdout.write('.')
  j = await (await fetch(`${BASE}/${op}`, { headers: { 'x-goog-api-key': K } })).json()
  if (j.done) break
  if (Date.now() - t0 > 15 * 60e3) { console.log('\npassou de 15 min; operação', op); process.exit(1) }
}
const amostra = j.response?.generateVideoResponse?.generatedSamples?.[0]
if (j.error || !amostra) {
  const motivo = j.error?.message || JSON.stringify(j.response?.generateVideoResponse || j).slice(0, 400)
  console.log('\nVeo não devolveu vídeo:', motivo); registrar({ tipo: 'erro', cliente, id, modelo, resolucao, erro: motivo }); process.exit(1)
}
const mp4 = path.join(destino, `video-${id}-${modelo}-${resolucao}.mp4`)
const v = await fetch(amostra.video.uri, { headers: { 'x-goog-api-key': K }, redirect: 'follow' })
fs.writeFileSync(mp4, Buffer.from(await v.arrayBuffer()))
fs.writeFileSync(mp4.replace(/\.mp4$/, '.prompt.txt'), prompt)
const reg = registrar({ tipo: 'video', id, cliente, cena, titulo, inicio, fim: fim || null, modelo, resolucao, seed, prompt_hash: hash(prompt), prompt, aprovado,
  custo_usd: +custo.toFixed(2), segundos: Math.round((Date.now() - t0) / 1000), arquivo: mp4, mb: +(fs.statSync(mp4).size / 1e6).toFixed(1) })
console.log(`\nOK ${mp4} (${reg.mb} MB, ${reg.segundos}s) · CUSTO ${dolar(custo)} · gasto total em vídeo: ${dolar(gastoAntes + custo)}`)
execFileSync(process.execPath, [path.join(AQUI, 'conferir-video.mjs'), '--id', id, '--caderno', CADERNO], { stdio: 'inherit' })
