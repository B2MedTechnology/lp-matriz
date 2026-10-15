// O CADERNO — cada geração, conferência e veredito humano, em Markdown legível (é ele que faz acertar na 1ª tentativa com o tempo).
//   node caderno.mjs [--caderno <arq.jsonl>] [--md <arq.md>]            → reescreve o caderno.md a partir do caderno.jsonl
//   node caderno.mjs --id <cliente-NN> --humano aprovou|reprovou [--motivo "..."]   → grava o veredito humano (vale mais que o da IA)
// O .md sai ao lado do .jsonl (caderno.md), a menos que --md diga outro lugar.
import fs from 'node:fs'; import path from 'node:path'
import { args, registrar, lerCaderno, dolar, hora, CADERNO } from './comum.mjs'

const NOTA = path.resolve(args().um('md', CADERNO.replace(/\.jsonl$/, '') + '.md'))
const a = args()
const veredito = a.um('humano') || a.um('dono')            // --dono aceito por compatibilidade
if (veredito) {
  if (!a.um('id') || !['aprovou', 'reprovou'].includes(veredito)) { console.log('uso: node caderno.mjs --id <cliente-NN> --humano aprovou|reprovou [--motivo "..."]'); process.exit(1) }
  registrar({ tipo: 'dono' /* veredito humano; nome mantido por compatibilidade */, id: a.um('id'), veredito, motivo: a.um('motivo', '') })
}

const C = lerCaderno(), videos = C.filter(r => r.tipo === 'video')
const conf = id => C.filter(r => r.tipo === 'conferencia' && r.id === id).at(-1)
const humano = id => C.filter(r => r.tipo === 'dono' && r.id === id).at(-1)
const final = v => humano(v.id)?.veredito === 'aprovou' ? true : humano(v.id)?.veredito === 'reprovou' ? false : conf(v.id)?.passou ?? null
const gastoVideo = videos.reduce((s, v) => s + (v.custo_usd || 0), 0)
const gastoAjuste = C.filter(r => r.tipo === 'ajuste').reduce((s, r) => s + (r.custo_usd || 0), 0)

// Tentativas até o 1º vídeo aprovado, por cliente (o indicador que tem de cair)
const porCliente = {}
for (const v of videos) (porCliente[v.cliente] ||= []).push(v)
const tentativas = Object.entries(porCliente).map(([c, vs]) => { const i = vs.findIndex(v => final(v) === true); return { c, n: vs.length, ate: i < 0 ? null : i + 1, gasto: vs.reduce((s, v) => s + v.custo_usd, 0) } })
const comAcerto = tentativas.filter(t => t.ate)
const media = comAcerto.length ? (comAcerto.reduce((s, t) => s + t.ate, 0) / comAcerto.length).toFixed(1).replace('.', ',') : '—'

let md = `<!-- gerado por caderno.mjs a partir de ${path.basename(CADERNO)} — não editar à mão: é reescrito a cada geração -->
# Caderno — Vídeos de LP por IA (cada geração)

> Cada vídeo gerado pela esteira (veja README.md): o prompt, o modelo, o custo, a conferência da IA e o **veredito humano**
> (vale mais que o da IA). É daqui que o \`sugerir-movimento\` tira o que já passou e o que já falhou — o caminho para
> acertar na 1ª tentativa. Atualizado em ${hora()}.

## Placar
- Vídeos gerados: **${videos.length}** · gasto em vídeo: **${dolar(gastoVideo)}** · ajustes de foto: ${dolar(gastoAjuste)}
- **Tentativas até o 1º vídeo aprovado (média por página): ${media}** — meta: 1
${tentativas.map(t => `- ${t.c}: ${t.n} tentativa(s), ${t.ate ? 'aprovado na ' + t.ate + 'ª' : 'nenhum aprovado ainda'}, ${dolar(t.gasto)}`).join('\n')}

## Todas as gerações
| id | quando | cena | modelo | seed | custo | IA | humano | motivos |
|---|---|---|---|---|---|---|---|---|
${videos.map(v => { const k = conf(v.id), d = humano(v.id); return `| ${v.id} | ${hora(new Date(v.em))} | ${v.cena || '—'} | ${v.modelo} ${v.resolucao} | ${v.seed} | ${dolar(v.custo_usd)} | ${k ? (k.passou ? '🟢 ' : '🔴 ') + k.nota : '—'} | ${d ? (d.veredito === 'aprovou' ? '🟢' : '🔴') + (d.motivo ? ' ' + d.motivo : '') : 'pendente'} | ${(k?.motivos || []).join('; ').replace(/\|/g, '/') || '—'} |` }).join('\n') || '| — | | | | | | | | |'}

## Prompts aprovados (ponto de partida da próxima página do mesmo tipo de cena)
${videos.filter(v => final(v) === true).map(v => `### ${v.id} · ${v.cena || 'cena'} · ${v.titulo}\n\`\`\`text\n${v.prompt}\n\`\`\``).join('\n\n') || '_nenhum ainda_'}

## O que reprovou (não repetir)
${videos.filter(v => final(v) === false).map(v => `- **${v.id}** (${v.cena || 'cena'}, ${v.modelo}): ${[...(conf(v.id)?.motivos || []), humano(v.id)?.motivo].filter(Boolean).join('; ')}${conf(v.id)?.ajuste_no_prompt ? ' → ajuste: _' + conf(v.id).ajuste_no_prompt + '_' : ''}`).join('\n') || '_nada ainda_'}
`
fs.writeFileSync(NOTA, md)
console.log(`caderno em ${NOTA}: ${videos.length} vídeo(s), ${dolar(gastoVideo)}, média até o 1º aprovado: ${media}`)
