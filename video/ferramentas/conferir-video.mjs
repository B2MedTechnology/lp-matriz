// PASSO 5 — O porteiro do vídeo, automático: 9 quadros (0 a 8 s) → IA de visão compara com a foto de início (e de fim) → passou/reprovou + por quê.
//   node conferir-video.mjs --id <cliente-NN> [--caderno <arq>]     (o gerar-video.mjs chama sozinho)
//   node conferir-video.mjs --video <arquivo.mp4> --inicio <foto> [--fim <foto>] [--cliente <slug>]
// Grava a conferência no caderno (é ela que ensina o próximo prompt) e monta a folha de 9 quadros para o humano ver.
// A palavra final é humana: a IA aponta, não aprova sozinha. Chave: GEMINI_API_KEY.
// Quadros: no macOS usa o Swift (binário quadros-video, se compilado, ou o script); fora do macOS, ffmpeg (no PATH).
import fs from 'node:fs'; import path from 'node:path'; import os from 'node:os'; import { execFileSync } from 'node:child_process'
import { args, parteImagem, gemini, prancha, registrar, lerCaderno, AQUI, CADERNO } from './comum.mjs'

const a = args()
let v = a.um('id') ? lerCaderno().find(r => r.tipo === 'video' && r.id === a.um('id')) : null
if (a.um('id') && !v) { console.log('id não encontrado no caderno:', a.um('id')); process.exit(1) }
v = v || { id: path.basename(a.um('video', '')).replace(/\.mp4$/, ''), arquivo: a.um('video'), inicio: a.um('inicio'), fim: a.um('fim'), cliente: a.um('cliente', '?') }
if (!v.arquivo || !v.inicio) { console.log('uso: node conferir-video.mjs --id <cliente-NN> | --video <mp4> --inicio <foto> [--fim <foto>]'); process.exit(1) }

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'lpv-quadros-'))
// Binário compilado (swiftc -O quadros-video.swift -o quadros-video) é ~1 min mais rápido que o script.
// Sem Swift (Linux/Windows): ffmpeg tira os mesmos 9 instantes (a folha é só para OLHAR; a cor exata importa no passo 6, não aqui).
const bin = path.join(AQUI, 'quadros-video')
const temSwift = (() => { try { execFileSync('swift', ['--version'], { stdio: 'ignore' }); return process.platform === 'darwin' } catch { return false } })()
let info
if (fs.existsSync(bin)) info = execFileSync(bin, [v.arquivo, pasta], { encoding: 'utf8' })
else if (temSwift) info = execFileSync('swift', [path.join(AQUI, 'quadros-video.swift'), v.arquivo, pasta], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] })
else {
  for (const t of [0, 1, 2, 3, 4, 5, 6, 7, 7.95])
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-ss', String(t), '-i', v.arquivo, '-frames:v', '1', '-q:v', '3', path.join(pasta, `f${t.toFixed(2).padStart(5, '0')}.jpg`)])
  info = 'quadros via ffmpeg'
}
const quadros = fs.readdirSync(pasta).filter(f => f.endsWith('.jpg')).sort().map(f => path.join(pasta, f))
const folha = prancha(quadros, quadros.map(q => path.basename(q).replace(/^f|\.jpg$/g, '') + ' s'), v.arquivo.replace(/\.mp4$/, ' — 9 quadros.jpg'), 3, 640)

const partes = [{ text: `Você é o porteiro de qualidade de um vídeo de 8 s gerado por IA que vai andar com a rolagem de uma landing page (o usuário para em qualquer quadro).
A 1ª imagem é a FOTO DE INÍCIO real${v.fim ? ', a 2ª é a FOTO DE FIM real' : ''}; depois vêm 9 quadros do vídeo (0 s a 8 s), em ordem.
Reprove sem dó se QUALQUER quadro tiver: rosto diferente da foto (identidade, traços, idade), mãos deformadas/dedos a mais, pessoa nova ou objeto novo,
texto/logo inventado, câmera girando ou tremendo, salto brusco entre quadros vizinhos, pessoa andando/trocando de lugar, algo entrando no lado esquerdo
(onde vai o texto)${v.fim ? ', ou o último quadro longe da foto de fim' : ''}. Avalie também se cada quadro intermediário seria uma foto aceitável parada.
Responda APENAS em JSON: {"passou":true,"nota":0,"identidade":"igual|leve diferença|outra pessoa","maos":"ok|problema em X s","terceiros_ou_objetos_novos":["..."],
"camera":"estável|problema","suavidade":"uniforme|irregular","ultimo_quadro":"bate|parecido|diferente|sem foto de fim",
"motivos":["cada problema com o segundo em que aparece"],"ajuste_no_prompt":"o que mudar no prompt para corrigir (em inglês, frase pronta)","resumo":"1 frase para o responsável"}` },
  parteImagem(v.inicio, 1024)]
if (v.fim) partes.push(parteImagem(v.fim, 1024))
quadros.forEach(q => partes.push({ text: path.basename(q) }, parteImagem(q, 1024)))
const { dados } = await gemini(partes)

registrar({ tipo: 'conferencia', id: v.id, cliente: v.cliente, cena: v.cena || '', modelo: v.modelo, resolucao: v.resolucao, seed: v.seed,
  prompt: v.prompt || '', passou: !!dados.passou, nota: dados.nota, motivos: dados.motivos || [], ajuste_no_prompt: dados.ajuste_no_prompt || '', resumo: dados.resumo, folha })
console.log(`${info.trim().split('\n').slice(0, 3).join(' | ')}
${dados.passou ? '🟢 PASSOU' : '🔴 REPROVADO'} (nota ${dados.nota}) — ${dados.resumo}
identidade: ${dados.identidade} · mãos: ${dados.maos} · câmera: ${dados.camera} · suavidade: ${dados.suavidade} · último quadro: ${dados.ultimo_quadro}
${(dados.motivos || []).map(m => '  - ' + m).join('\n')}${dados.ajuste_no_prompt ? '\najuste sugerido no prompt: ' + dados.ajuste_no_prompt : ''}
folha dos 9 quadros: ${folha}`)
try { execFileSync(process.execPath, [path.join(AQUI, 'caderno.mjs'), '--caderno', CADERNO], { stdio: 'ignore' }) } catch {}
