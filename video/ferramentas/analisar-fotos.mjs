// PASSO 1 — Análise das fotos do cliente para a LP com vídeo (portão 2 da receita da cena de rolagem, por IA de visão).
//   node analisar-fotos.mjs --cliente <slug> --fotos <pasta|arquivo> [--fotos ...] [--contexto "dermatologista em consultório, capa da LP"] [--saida <pasta>] [--caderno <arq>]
// Sai em <saida> (padrão: ./lp-video-<cliente>): analise.json, analise.md (para o humano) e prancha.jpg (todas as fotos com nota).
// Nada é gerado nem gasto além da leitura (Gemini, centavos). Chave: GEMINI_API_KEY. A decisão de qual foto usar é HUMANA — PARE aqui.
import fs from 'node:fs'; import path from 'node:path'
import { args, listarFotos, medidas, parteImagem, gemini, prancha, registrar, hora } from './comum.mjs'

const a = args(), cliente = a.um('cliente'), contexto = a.um('contexto', '')
if (!cliente || !a.varios('fotos').length) { console.log('uso: node analisar-fotos.mjs --cliente <slug> --fotos <pasta|arquivo> [--contexto "..."] [--saida <pasta>]'); process.exit(1) }
const saida = path.resolve(a.um('saida', `lp-video-${cliente}`)); fs.mkdirSync(saida, { recursive: true })
const fotos = listarFotos(a.varios('fotos'))
if (!fotos.length) { console.log('nenhuma foto encontrada'); process.exit(1) }

const RUBRICA = `Você é o diretor de arte de uma agência que faz landing pages com um VÍDEO QUE ANDA COM A ROLAGEM.
A foto vai virar o 1º quadro (ou o último) de um vídeo de 8 s gerado por IA (Google Veo, imagem → vídeo, 16:9).
O 1º quadro é a capa da página (fica parado na tela); o texto da capa fica à ESQUERDA, por cima do vídeo.
No celular, só aparece um QUADRADO do meio do quadro. A câmera vai avançar devagar (push-in), então quem está no quadro cresce.
${contexto ? 'Contexto do cliente: ' + contexto + '\n' : ''}
Avalie a foto com rigor pelos PORTÕES da casa (todos vêm de vídeos que falharam de verdade):
1. Horizontal (paisagem). Vertical só serve se der para recortar 16:9 sem cortar cabeça/mãos.
2. A(s) pessoa(s) idealmente no terço DIREITO, ocupando no máximo ~40% da largura; centro é aceitável se houver área calma à esquerda.
3. Área calma (sem detalhe forte, de preferência mais escura) à ESQUERDA, onde o texto vai morar.
4. NENHUM terceiro: porta-retratos com pessoas, pacientes, outras pessoas ao fundo, reflexos de pessoas. (Num caso real, porta-retratos de família na estante apareceram em todo o vídeo e ele foi descartado.)
5. NENHUM dado sensível: telas com nomes/prontuários, papéis legíveis, crachás, placas de carro. (Num caso real, quase foi ao ar o nome e o prontuário de um paciente numa tela de ultrassom.)
6. Nenhuma marca de terceiro em destaque (logos de outras empresas).
7. Nitidez e resolução suficientes para um vídeo 1080p (rosto nítido, sem ruído forte).
8. Mãos: mãos grandes, perto da câmera ou em posição complicada são o ponto em que a IA mais deforma.
9. Serve de capa PARADA (é bonita e profissional mesmo sem movimento)?
10. Publicidade: se for profissional de saúde/advocacia, nada sensacionalista, nada de paciente identificável.

Para cada problema, diga se a IA de edição de imagem consegue consertar NA FOTO (apagar objeto, escurecer/limpar a parede da esquerda,
ampliar o cenário para 16:9 / dar espaço à esquerda) — consertar no vídeo depois NÃO funciona, porque a câmera se move.
Atenção: edição de IA pode alterar o rosto; ajuste no rosto/corpo da pessoa é sempre "não ajustável".

Responda APENAS em JSON:
{"descricao":"o que se vê, 1 frase","pessoas":0,"posicao_pessoa":"esquerda|centro|direita|nenhuma","ocupacao_largura_pct":0,
 "lado_esquerdo_calmo":true,"terceiros":["..."],"dados_sensiveis":["..."],"marcas_terceiros":["..."],"nitidez":"boa|media|ruim",
 "risco_maos":"baixo|medio|alto","serve_de_capa_parada":true,
 "problemas":[{"problema":"...","gravidade":"bloqueia|atrapalha|detalhe","ajuste_sugerido":"o pedido exato de edição, em português","ajustavel_por_ia":true}],
 "papel_sugerido":"inicio|fim|qualquer|nenhum","veredito":"usar|usar com ajuste|nao usar","motivo":"1 frase para o responsável","nota":0}
"nota" de 0 a 10 = quão boa é para virar o vídeo da capa.`

const resultado = []
for (const [i, f] of fotos.entries()) {
  const m = medidas(f)
  process.stdout.write(`(${i + 1}/${fotos.length}) ${path.basename(f)} ${m.w}×${m.h} ${m.mb} MB … `)
  const { dados } = await gemini([{ text: RUBRICA }, parteImagem(f)])
  const tecnico = []
  if (m.w < m.h) tecnico.push('vertical')
  if (Math.max(m.w, m.h) < 1920) tecnico.push(`resolução baixa (${m.w}×${m.h}; o vídeo é 1080p)`)
  resultado.push({ arquivo: f, ...m, tecnico, ...dados })
  console.log(`${dados.veredito} · nota ${dados.nota}`)
}

// Pares de início/fim: fotos do MESMO ensaio, mesmo enquadramento, pose diferente (a técnica que mais acerta: as pontas são fotos reais)
let pares = []
// só as 12 melhores entram na busca de pares (o pedido leva todas as imagens juntas)
const candidatas = [...resultado].filter(r => r.veredito !== 'nao usar').sort((x, y) => (y.nota || 0) - (x.nota || 0)).slice(0, 12)
if (candidatas.length >= 2) {
  const partes = [{ text: `Estas são ${candidatas.length} fotos de um cliente (numeradas na ordem). Encontre PARES que sirvam de quadro INICIAL e FINAL
do mesmo vídeo de 8 s: mesmo ensaio, mesmo cenário e enquadramento quase igual, mesmas pessoas no mesmo lugar, mudando SÓ a pose ou o gesto
(ex.: mãos no bolso → ajusta o paletó). Pares com câmera em outro lugar ou pessoas trocando de posição NÃO servem (a IA inventaria um meio caótico).
Responda APENAS em JSON: {"pares":[{"inicio":1,"fim":2,"o_que_muda":"...","qualidade":"otimo|bom|arriscado","por_que":"..."}]} — lista vazia se não houver.` }]
  candidatas.forEach((r, n) => partes.push({ text: `Foto ${n + 1}: ${path.basename(r.arquivo)}` }, parteImagem(r.arquivo)))
  const { dados } = await gemini(partes)
  pares = (dados.pares || []).map(p => ({ ...p, inicio: candidatas[p.inicio - 1]?.arquivo, fim: candidatas[p.fim - 1]?.arquivo })).filter(p => p.inicio && p.fim)
}

resultado.sort((x, y) => (y.nota || 0) - (x.nota || 0))
fs.writeFileSync(path.join(saida, 'analise.json'), JSON.stringify({ cliente, contexto, em: new Date().toISOString(), fotos: resultado, pares }, null, 2))
prancha(resultado.map(r => r.arquivo), resultado.map(r => `${r.nota}/10 ${r.veredito} · ${path.basename(r.arquivo)}`), path.join(saida, 'prancha.jpg'), 4, 480)

const VER = { usar: '🟢 usar', 'usar com ajuste': '🟡 usar com ajuste', 'nao usar': '🔴 não usar' }
let md = `# Análise das fotos — ${cliente} (${hora()})\n\n${contexto ? '_Contexto: ' + contexto + '_\n\n' : ''}`
const todasVerticais = resultado.every(r => r.tecnico.includes('vertical'))
if (todasVerticais) { md += `> Todas as fotos são **verticais**: para 16:9, ou se amplia o cenário por IA (passo 2) ou se recorta (perde cabeça/pernas).\n\n`; resultado.forEach(r => r.tecnico = r.tecnico.filter(x => x !== 'vertical')) }
md += `| Nota | Foto | Veredito | Por quê | Ajuste sugerido |\n|---|---|---|---|---|\n`
for (const r of resultado.slice(0, 12)) {
  const aj = (r.problemas || []).filter(p => p.ajustavel_por_ia && p.gravidade !== 'detalhe').map(p => p.ajuste_sugerido).join(' · ') || '—'
  md += `| ${r.nota} | ${path.basename(r.arquivo)} | ${VER[r.veredito] || r.veredito} | ${r.motivo}${r.tecnico.length ? ' (' + r.tecnico.join('; ') + ')' : ''} | ${aj} |\n`
}
md += resultado.length > 12 ? `\n_(+${resultado.length - 12} fotos com nota menor em analise.json)_\n` : ''
md += `\n## Pares de início e fim (mesmo ensaio, só a pose muda)\n`
md += pares.length ? pares.map(p => `- **${path.basename(p.inicio)} → ${path.basename(p.fim)}** (${p.qualidade}): ${p.o_que_muda}. ${p.por_que}`).join('\n') : '- nenhum par encontrado: o vídeo parte de 1 foto (a IA inventa o fim — mais risco no rosto), ou se cria o fim por edição da mesma foto.'
md += `\n\n## Problemas que bloqueiam\n` + (resultado.slice(0, 12).flatMap(r => (r.problemas || []).filter(p => p.gravidade === 'bloqueia' && !(todasVerticais && /vertical|retrato|16:9/i.test(p.problema))).map(p => `- ${path.basename(r.arquivo)}: ${p.problema}${p.ajustavel_por_ia ? ' → dá para consertar na foto: ' + p.ajuste_sugerido : ' → **não** se conserta por IA'}`)).join('\n') || '- nenhum')
fs.writeFileSync(path.join(saida, 'analise.md'), md + '\n')
registrar({ tipo: 'analise', cliente, fotos: resultado.length, pares: pares.length, melhores: resultado.slice(0, 3).map(r => path.basename(r.arquivo)), pasta: saida })
console.log(`\n${md}\nprancha: ${path.join(saida, 'prancha.jpg')}`)
