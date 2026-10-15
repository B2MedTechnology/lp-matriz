// PASSO 3 — Sugestões de movimento para o responsável escolher (2 a 4 opções, cada uma com viabilidade e o prompt pronto).
//   node sugerir-movimento.mjs --cliente <slug> --inicio <foto> [--fim <foto>] [--contexto "..."] [--n 3] [--saida <pasta>] [--caderno <arq>]
// Sai em <saida>/sugestoes.json e sugestoes.md. O vídeo só é gerado (passo 4) com a opção escolhida e a frase de aprovação humana.
// Base: o modelo de prompt aprovado (modelo-prompt.txt, com marcadores {…}) e o caderno do que já passou ou falhou.
// Chave: GEMINI_API_KEY. Custa centavos. PARE aqui: a escolha é humana.
import fs from 'node:fs'; import path from 'node:path'
import { args, parteImagem, gemini, registrar, lerCaderno, hora, AQUI } from './comum.mjs'

const a = args(), cliente = a.um('cliente'), inicio = a.um('inicio'), fim = a.um('fim'), contexto = a.um('contexto', ''), n = +a.um('n', 3)
if (!cliente || !inicio) { console.log('uso: node sugerir-movimento.mjs --cliente <slug> --inicio <foto> [--fim <foto>] [--contexto "..."] [--n 3]'); process.exit(1) }
const saida = path.resolve(a.um('saida', `lp-video-${cliente}`)); fs.mkdirSync(saida, { recursive: true })
const MODELO = fs.readFileSync(path.join(AQUI, 'modelo-prompt.txt'), 'utf8')

// O que o caderno já ensinou: prompts que passaram e motivos de reprovação (o aprendizado que reduz tentativas)
const conf = lerCaderno().filter(r => r.tipo === 'conferencia')
const aprendido = [
  ...conf.filter(r => r.passou).slice(-6).map(r => `PASSOU (${r.cena || 'cena'}): "${(r.prompt || '').slice(0, 400)}"`),
  ...conf.filter(r => !r.passou).slice(-10).map(r => `REPROVADO (${r.cena || 'cena'}): ${(r.motivos || []).join('; ')}`),
].join('\n') || '(caderno ainda vazio)'

const pedido = `Você é diretor de fotografia de uma agência. A partir ${fim ? 'das DUAS fotos (1ª = quadro INICIAL, 2ª = quadro FINAL)' : 'da foto (quadro INICIAL; não há foto final)'},
proponha ${n} opções de MOVIMENTO para um vídeo de 8 s gerado pelo Google Veo 3.1 (imagem → vídeo${fim ? ', com primeiro e último quadro travados' : ''}, 16:9, 1080p, sem áudio).
O vídeo anda COM A ROLAGEM de uma landing page: o usuário pode parar em QUALQUER quadro. ${contexto ? 'Contexto: ' + contexto + '.' : ''}

Leis da casa (vêm de vídeos que falharam):
- Movimento LENTO e distribuído por igual nos 8 s; nada de gesto rápido (vira borrão entre quadros).
- Pessoas NÃO andam, não trocam de lugar, não vão em direção à câmera. Câmera: push-in lento de 3–5% ou quase parada; nada de órbita, tremor, zoom rápido.
- O 1º quadro é a capa parada (tem de ser bonito); o último fecha o bloco "quem é" (ex.: olhar para a câmera, postura de apresentação).
- Mãos são onde a IA mais erra: gesto de mão simples, perto do corpo, longe da lente. Sem fala, sem boca mexendo, sem texto, sem pessoas novas.
- O texto da página fica à esquerda: nada pode entrar no lado esquerdo do quadro.
- Se não há foto final, a IA inventa o fim: o risco no rosto sobe — prefira movimentos mínimos (respiração, olhar, ajuste de postura) e diga isso.
- Se a foto não serve para vídeo (terceiros, dado sensível, rosto pequeno/borrado, pose impossível de animar sem deformar), diga com franqueza em "nao_recomendo".

O que o caderno da casa já aprendeu:
${aprendido}

Para cada opção, escreva o PROMPT COMPLETO EM INGLÊS seguindo a ESTRUTURA E AS PROIBIÇÕES deste modelo aprovado (preencha TODOS os
marcadores {…} com o que se vê nas fotos — pessoas, roupa, cenário, gesto de cada pessoa, estilo; nenhum marcador pode sobrar; mantenha as cláusulas de identidade, de câmera, de "every intermediate frame", a lista de "No …", "Audio: none", "~8 seconds"
e a frase final sobre o último quadro ${fim ? 'bater com a 2ª foto' : '(sem 2ª foto: descreva o fim desejado com precisão)'}):
<<<
${MODELO}
>>>

Ordene da MAIS viável para a menos. Responda APENAS em JSON:
{"leitura_da_foto":"1 frase","nao_recomendo":"vazio ou o motivo para NÃO usar esta foto",
 "opcoes":[{"titulo":"curto","o_que_acontece":"2 frases simples em português, para o responsável imaginar o vídeo","quadro_final":"como termina",
   "viabilidade":"alta|media|baixa","riscos":["..."],"por_que":"por que essa viabilidade","cena":"tipo de cena em 2-3 palavras (ex.: consultório-mesa, estúdio-dupla)",
   "prompt":"o prompt completo em inglês"}]}`

const partes = [{ text: pedido }, parteImagem(inicio)]
if (fim) partes.push(parteImagem(fim))
const { dados } = await gemini(partes, { temperatura: 0.6 })
const opcoes = (dados.opcoes || []).map((o, i) => ({ n: i + 1, ...o }))
const arq = path.join(saida, 'sugestoes.json')
fs.writeFileSync(arq, JSON.stringify({ cliente, inicio, fim: fim || null, contexto, em: new Date().toISOString(), ...dados, opcoes }, null, 2))

const COR = { alta: '🟢', media: '🟡', média: '🟡', baixa: '🔴' }
let md = `# Movimentos sugeridos — ${cliente} (${hora()})\n\nFoto inicial: ${path.basename(inicio)}${fim ? ' · final: ' + path.basename(fim) : ' · sem foto final (a IA inventa o fim)'}\n\n_${dados.leitura_da_foto || ''}_\n\n`
if (dados.nao_recomendo) md += `> ⚠️ **Não recomendo esta foto:** ${dados.nao_recomendo}\n\n`
for (const o of opcoes) md += `**${o.n}. ${o.titulo}** — ${COR[o.viabilidade] || ''} viabilidade ${o.viabilidade}\n${o.o_que_acontece} Termina: ${(o.quadro_final || "").replace(/\.+$/, "")}.\nRiscos: ${(o.riscos || []).map(x => x.replace(/\.+$/, "")).join("; ") || "—"}. ${o.por_que}\n\n`
fs.writeFileSync(path.join(saida, 'sugestoes.md'), md)
registrar({ tipo: 'sugestoes', cliente, inicio, fim: fim || null, opcoes: opcoes.map(o => ({ n: o.n, titulo: o.titulo, viabilidade: o.viabilidade })), nao_recomendo: dados.nao_recomendo || '', arquivo: arq })
console.log(md + `\n(prompts completos em ${arq})`)
