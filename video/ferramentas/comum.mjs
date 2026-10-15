// Peças comuns da esteira "LP com vídeo na rolagem": chaves, imagens, Gemini, preços e o caderno.
// Processo completo: ../README.md. Chaves SÓ por variável de ambiente (veja .env.exemplo).
import fs from 'node:fs'; import path from 'node:path'; import os from 'node:os'; import crypto from 'node:crypto'
import { execFileSync } from 'node:child_process'

export const AQUI = path.dirname(new URL(import.meta.url).pathname)
export const MODELO_VISAO = process.env.LPV_MODELO_VISAO || 'gemini-3.6-flash'          // leitura das fotos e dos quadros
export const MODELO_FOTO = process.env.LPV_MODELO_FOTO || 'gpt-image-2.5-sunburst'      // edição de imagem (OpenAI)
export const VEO = { lite: 'veo-3.1-lite-generate-preview', fast: 'veo-3.1-fast-generate-preview', standard: 'veo-3.1-generate-preview' }
// US$ por segundo, Gemini API (ai.google.dev/gemini-api/docs/pricing, lido em 05-10-2026). Sem camada grátis. Atualize quando o Google mudar.
export const PRECO_VEO = { lite: { '720p': 0.05, '1080p': 0.08 }, fast: { '720p': 0.10, '1080p': 0.12, '4k': 0.30 }, standard: { '720p': 0.40, '1080p': 0.40, '4k': 0.60 } }
// US$ por 1M tokens da API de imagens da OpenAI (tabela de 30-09-2026). Atualize quando mudar.
export const PRECO_FOTO = { texto: 5, imagem_in: 8, imagem_out: 30 }

export function args(lista = process.argv.slice(2)) {
  const um = (k, d) => { const i = lista.indexOf('--' + k); return i >= 0 && lista[i + 1] && !lista[i + 1].startsWith('--') ? lista[i + 1] : d }
  const varios = k => lista.flatMap((x, i) => x === '--' + k ? [lista[i + 1]] : [])
  const tem = k => lista.includes('--' + k)
  return { um, varios, tem }
}

// O caderno (1 linha JSON por análise, ajuste, vídeo, conferência e veredito humano).
// Ordem: --caderno <arquivo> → variável LPV_CADERNO → ./caderno.jsonl da pasta de trabalho.
export const CADERNO = path.resolve(args().um('caderno', process.env.LPV_CADERNO || 'caderno.jsonl'))
// Livro de gastos da OpenAI (ajustes de foto). --livro-openai <arquivo> → LPV_LIVRO_OPENAI → ./gastos-openai.jsonl
export const LIVRO_OPENAI = path.resolve(args().um('livro-openai', process.env.LPV_LIVRO_OPENAI || 'gastos-openai.jsonl'))

// Chaves: SÓ variáveis de ambiente. Aceita nomes alternativos (o primeiro que existir vale).
// Dica: `node --env-file=.env ferramenta.mjs …` (Node 20.6+) carrega um arquivo .env sem código extra.
export function chave(...nomes) {
  for (const n of nomes) if (process.env[n] && process.env[n].trim()) return process.env[n].trim()
  console.error(`falta a variável de ambiente ${nomes.join(' ou ')} (veja ferramentas/.env.exemplo)`); process.exit(3)
}
export const chaveGemini = () => chave('GEMINI_API_KEY', 'GOOGLE_API_KEY')   // a mesma chave serve à visão e ao Veo 3.1
export const chaveOpenAI = () => chave('OPENAI_API_KEY')

export const IMAGEM = /\.(jpe?g|png|heic|webp|tiff?)$/i
export function listarFotos(entradas) {
  return entradas.flatMap(e => fs.statSync(e).isDirectory()
    ? fs.readdirSync(e).filter(f => IMAGEM.test(f) && !f.startsWith('.')).sort().map(f => path.join(e, f)) : [e])
}

// Largura × altura sem abrir a imagem inteira (respeita a rotação do EXIF)
export function medidas(arq) {
  const py = 'import sys;from PIL import Image;from PIL import ImageOps;i=ImageOps.exif_transpose(Image.open(sys.argv[1]));print(i.width,i.height)'
  const [w, h] = execFileSync('python3', ['-c', py, arq], { encoding: 'utf8' }).trim().split(' ').map(Number)
  return { w, h, mb: +(fs.statSync(arq).size / 1e6).toFixed(1) }
}

// Cópia em JPEG com o lado maior limitado (para mandar à IA sem estourar o limite do pedido) — respeita a rotação do EXIF
export function jpeg(arq, lado = 1600, q = 88) {
  const saida = path.join(os.tmpdir(), 'lpv-' + crypto.createHash('md5').update(arq + lado + q + fs.statSync(arq).mtimeMs).digest('hex').slice(0, 12) + '.jpg')
  if (!fs.existsSync(saida)) {
    const py = 'import sys;from PIL import Image,ImageOps;i=ImageOps.exif_transpose(Image.open(sys.argv[1])).convert("RGB");i.thumbnail((int(sys.argv[3]),)*2);i.save(sys.argv[2],"JPEG",quality=int(sys.argv[4]),subsampling=0)'
    execFileSync('python3', ['-c', py, arq, saida, String(lado), String(q)])
  }
  return saida
}
export const b64 = arq => fs.readFileSync(arq).toString('base64')
export const parteImagem = (arq, lado = 1600) => ({ inlineData: { mimeType: 'image/jpeg', data: b64(jpeg(arq, lado)) } })

// Gemini com resposta em JSON (visão). `partes`: [{text}|{inlineData}]. 3 tentativas (rede instável, 429/500/503).
export async function gemini(partes, { modelo = MODELO_VISAO, temperatura = 0.2 } = {}) {
  const K = chaveGemini()
  const corpo = { contents: [{ role: 'user', parts: partes }], generationConfig: { responseMimeType: 'application/json', temperature: temperatura } }
  for (let t = 1; t <= 3; t++) {
    let r, j
    try {
      r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${modelo}:generateContent`, {
        method: 'POST', headers: { 'x-goog-api-key': K, 'Content-Type': 'application/json' }, body: JSON.stringify(corpo) })
      j = await r.json()
    } catch (e) {                                   // queda de rede (ECONNRESET) com pedido grande: tenta de novo
      if (t === 3) throw e
      await new Promise(ok => setTimeout(ok, 5000 * t)); continue
    }
    if (r.ok) {
      const txt = (j.candidates?.[0]?.content?.parts || []).map(p => p.text || '').join('')
      try { return { dados: JSON.parse(txt), uso: j.usageMetadata } } catch { if (t === 3) throw new Error('Gemini não devolveu JSON: ' + txt.slice(0, 300)) }
    } else if (t === 3 || ![429, 500, 503].includes(r.status)) throw new Error(`Gemini ${r.status}: ${JSON.stringify(j.error || j).slice(0, 300)}`)
    await new Promise(ok => setTimeout(ok, 4000 * t))
  }
}

export function registrar(reg) { fs.appendFileSync(CADERNO, JSON.stringify({ em: new Date().toISOString(), ...reg }) + '\n'); return reg }
export const lerCaderno = () => fs.existsSync(CADERNO) ? fs.readFileSync(CADERNO, 'utf8').trim().split('\n').filter(Boolean).map(l => JSON.parse(l)) : []
export const hash = s => crypto.createHash('sha1').update(s).digest('hex').slice(0, 8)
// Fuso dos horários impressos: LPV_FUSO (padrão America/Sao_Paulo)
export const hora = (d = new Date()) => d.toLocaleString('pt-BR', { timeZone: process.env.LPV_FUSO || 'America/Sao_Paulo', dateStyle: 'short', timeStyle: 'short' })
export const dolar = v => 'US$ ' + v.toFixed(2).replace('.', ',')

// Folha de contato com legenda (para a IA e o humano olharem de uma vez)
export function prancha(arquivos, legendas, saida, colunas = 3, lado = 640) {
  const py = `
import sys,json
from PIL import Image,ImageOps,ImageDraw,ImageFont
arqs,legs,saida,col,lado=json.loads(sys.argv[1]),json.loads(sys.argv[2]),sys.argv[3],int(sys.argv[4]),int(sys.argv[5])
ims=[ImageOps.exif_transpose(Image.open(a)).convert('RGB') for a in arqs]
for i in ims: i.thumbnail((lado,lado))
h=max(i.height for i in ims)+44; lin=(len(ims)+col-1)//col
fol=Image.new('RGB',(col*(lado+12)+12,lin*(h+12)+12),(250,250,248)); d=ImageDraw.Draw(fol)
f=None
for fonte in ['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','C:/Windows/Fonts/arial.ttf']:
  try: f=ImageFont.truetype(fonte,22); break
  except Exception: pass
if f is None: f=ImageFont.load_default()
for n,(im,lg) in enumerate(zip(ims,legs)):
  x=12+(n%col)*(lado+12); y=12+(n//col)*(h+12); fol.paste(im,(x,y)); d.text((x+4,y+im.height+8),lg[:60],fill=(20,40,38),font=f)
fol.save(saida,'JPEG',quality=85)`
  execFileSync('python3', ['-c', py, JSON.stringify(arquivos), JSON.stringify(legendas), saida, String(colunas), String(lado)])
  return saida
}
