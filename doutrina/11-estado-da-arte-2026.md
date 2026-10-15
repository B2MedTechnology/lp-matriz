# Estado da arte 2026 — o que a casa faz, o que a evidência diz e o que muda

Síntese de uma varredura (setembro de 2026) que comparou o jeito de construir landing pages desta matriz — doutrina,
código de cerca de dez páginas e páginas no ar — com a documentação oficial (Google, W3C, Vercel, Meta, WebKit,
schema.org) e estudos datados de 2026. Graus usados: **FATO** (doc oficial, lei, código, medição direta) ·
**FORTE** (estudo com método) · **CORRELAÇÃO** · **FRACO** · **MITO**.

Ver também: [padrão](01-padrao.md) · [anatomia](02-anatomia-da-pagina.md) · [SEO e velocidade](05-seo-e-velocidade.md) ·
[componentes](06-componentes.md) · [lições](10-licoes-aprendidas.md) · [conselhos](conselhos/).

> **Veredito em uma linha:** o jeito de **construir** está certo; o jeito de **manter** estava errado. As páginas são
> rápidas e à frente do mercado; o problema era cada página nascer copiando a anterior, com as correções sem voltar para
> as outras. Daí esta matriz: uma base única.

---

## 1. O que a casa já faz bem (confirmado pela evidência)

| Prática | Por que está certa |
|---|---|
| HTML/CSS/JS puros, gerados por Python, sem framework | HTTP Archive (ago/2026, celular): geradores estáticos têm **71–78%** das origens com Core Web Vitals bons; Next.js 35% (19% no Brasil); construtores de app por IA ~19% (5% no Brasil). A pilha decide, não a hospedagem (FORTE) |
| CSS embutido, woff2 local recortado, `swap` | HTML inteiro em ~26–30 KB comprimido; FCP 3,5 → 1,5 s ao trocar Google Fonts por fonte local (FATO) |
| AVIF por largura + JPEG de reserva, capa `fetchpriority="high"` e nunca lazy | AVIF com ~95% de suporte; a imagem de LCP é AVIF em só 0,7% das páginas — a casa está na ponta (FATO) |
| Capa com foto real, véu medido (≥ 4,5:1), texto em área calma | WCAG 1.4.3; foto real da equipe recebe mais atenção que banco de imagem (FORTE) |
| 1ª dobra medida em 390×725 e 360×640 com `min(vw, svh)` | 360 px soma ~7% das telas do Brasil; 57% da atenção fica acima da dobra (FATO/FORTE) |
| Um CTA por dobra; barra fixa no celular **ou** círculo no desktop | Componente fixo vence mais no celular; o Google aceita banner pequeno (CORRELAÇÃO/FATO) |
| `href` real do `wa.me` com mensagem pronta; JS só mede | Formato oficial do WhatsApp; se o script morrer, a conversão continua (FATO) |
| Avaliações com nota, contagem, data e link; **nunca** `aggregateRating` | Autoavaliação é inelegível para estrelas no Google (FATO) |
| FAQ em `<details>` nativo com as dúvidas reais da secretária | Acordeão condensa no celular; `<details name>` é Baseline (FORTE/FATO) |
| Mapa e APIs só perto da dobra ("fachada") | Padrão documentado para embeds de terceiros (FATO) |
| GTM depois da pintura da capa + protocolo garantido no 1º toque | Snippet padrão derrubava o celular de ~100 para 67; o contêiner custa ~1 s de execução no celular (FATO) |
| Sequência de quadros em `<canvas>` (não `<video>` arrastado), janela de bitmaps com `close()` | Arrastar `currentTime` não é preciso; 192 quadros decodificados = ~708 MB sem janela (FATO) |
| `play()` tratado e re-armado em `touchend/pointerup/click/keydown` | `touchstart` e `scroll` não geram ativação; o iOS rejeita o `play()` sem ela (FATO) |
| Lighthouse local, máquina calma, uma rodada por vez | Doc de variabilidade do Lighthouse (FATO) |
| `?h=`/`?v=` nas URLs de assets | O navegador guarda por URL completa; na Vercel, `?h=` funciona (FATO) — "query string não é cacheada" é **mito** lá |
| Sem `llms.txt` | O Google diz que não afeta nada; 97% dos arquivos tiveram zero tráfego em maio/2026 (FATO/FORTE) |
| Sem otimização "especial para IA" (chunking, Markdown, schema mágico) | Guia oficial do Google para IA (jul/2026); schema não moveu citação em IA num estudo com 1.885 páginas (FORTE) |
| JSON-LD em `@graph`, subtipo mais específico, NAP igual ao perfil, credenciais | Doc de LocalBusiness/Organization (FATO) |
| Anti-"estética de IA" (gradiente índigo, cards com sombra, grade de ícones, Inter) | Reconhecido como marca de página gerada (FATO) |

## 2. O que a evidência de 2026 diz — por área

### Design e conversão
- **Rolagem média no celular: ~45% da página**; as pessoas raramente passam da terceira tela. A prova social da dobra 7
  fica além do que a maioria vê → **um sinal de confiança verificável na capa ou na faixa 2** (nota + contagem do Google
  para saúde; registro do conselho; OAB para advocacia). É a troca de maior potencial e menor custo — testar por variante.
- **Régua de conversão** (Unbounce, edição 2024, ainda a vigente): saúde 5,1% (odontologia 4,3%), jurídico 6,3%,
  serviços 6,1%. Ressalva: clique no WhatsApp **não é lead** — comparar só separando clique, conversa e agendamento.
- **Legibilidade:** texto no nível de 5ª–7ª série converte mais em saúde e serviços; faixas de referência: saúde
  355–1.020 palavras, serviços 275–745, jurídico ~600 (CORRELAÇÃO; limiar em português desconhecido).
- **Clichês de 2ª geração de página gerada por IA:** sobrancelha em CAIXA-ALTA espaçada, metadados com "·", filetes de
  1 px em diagramação de jornal, creme + serifa de alto contraste + terracota, uma palavra destacada no título,
  numerar 01/02/03 sem sequência, fade em toda seção, herói com número grande. Regra: esses recursos só entram quando
  vêm da marca do cliente, e a ousadia se gasta **em um lugar só**.
- Tendências de galeria (3D, neon, neumorfismo, gamificação) não têm prova e custam desempenho.

### Movimento
- **WCAG 2.2.2 (nível A):** o que se move sozinho por mais de 5 s ao lado de outro conteúdo exige **mecanismo visível**
  de pausar. Pausa no hover/foco não conta; `prefers-reduced-motion` não é técnica do critério.
- Animação de rolagem por CSS (`animation-timeline: view()/scroll()`) roda nativa no Chrome 115+ e Safari 26+ (no
  compositor desde 26.4) — **~95% do celular brasileiro**. JS de rolagem vira plano B.
- Manchete acendendo palavra por palavra em todas as dobras: a NN/g desaconselha em sites de tarefa (cita médico) e
  pede evitar fade de rolagem no celular → só na capa e em 1–2 dobras.
- Carrossel que anda sozinho tira o controle (~1% clica em destaque de carrossel). Se andar sozinho, tem pausa que fica
  pausada.
- `navigator.connection.saveData`/`deviceMemory` **não existem no Safari** — no iPhone a trava nunca dispara.
- Rolagem suave/scrolljacking desorienta; parallax em texto enjoa; polyfill de scroll-timeline não compensa.
- Movimento aumentar conversão: **nenhuma fonte primária** — é linguagem de marca, não alavanca.

### SEO técnico
- O Google exige pouco: 200, sem `noindex`, robots liberado, HTML útil, versão de celular completa, HTTPS. Elegibilidade
  a AI Overviews/AI Mode = estar indexado e elegível a snippet.
- Title ≤ 60 e um `<h1>` são **boas heurísticas de redação**, não exigência (o Google corta pela largura).
- `priority`/`changefreq` no sitemap são ignorados; `meta keywords` e `geo.*` não são usados.
- **Resultado enriquecido de FAQ acabou em 07-05-2026.** `FAQPage` fica como semântica barata (Bing, IAs).
- `lastmod`/`dateModified` só valem se verdadeiros; data que muda sem mudança de conteúdo é sinal ruim.
- Duas páginas indexáveis para sinônimo puro são "substancialmente similares" sem ganho: variante de anúncio em
  `noindex, follow` (o AdsBot ignora `noindex`).
- Favicon só conta como arquivo (PNG/ICO/…) rastreável por hostname — `data:` SVG fica fora.
- Cabeçalhos de segurança (CSP, HSTS, COOP) pesam **0** no Lighthouse e não são SEO.
- E-E-A-T é fundamento, não fator; em saúde os sistemas dão "ainda mais peso".

### Prévia e indexação
- **`Disallow: /` na prévia esconde o `noindex`** ("the crawler will never see the noindex rule") e é a única peça com
  cache de até 24 h. Prévia = `noindex` em dois lugares (meta + `X-Robots-Tag`) com robots.txt aberto.
- Grupos nomeados do robots.txt **não herdam** do `*`: se o `*` ganhar `Disallow`, repetir em cada grupo.
- Produção em `*.vercel.app` é indexável por padrão: `noindex` por host ou 308 para o domínio.

### Posicionamento em IA
- O que decide para negócio local: **perfil do Google, avaliações recentes, HTML visível com fatos verificáveis**, NAP
  idêntico em diretórios. No Gemini, o site do negócio é ~50% das citações; no ChatGPT, ~10% (diretórios dominam) —
  dados dos EUA.
- Robôs de OpenAI, Anthropic e Perplexity não executam JS (telemetria de dez/2024): fatos no HTML inicial.
- `* / Allow: /` já libera todos; a lista nominal é documentação. **Google-Extended** também controla o grounding do app
  Gemini — bloqueá-lo tira citação. Claude-User respeita robots.txt.
- `llms.txt`, `Content-Signal` e WebMCP **não** são entrega. Nenhuma técnica de "otimização para IA" tem efeito causal
  estável entre plataformas (revisão de 45 estudos). "Preço explícito e data recente" ajudam citação em laboratório.
- Medição: relatório de IA generativa do Search Console (impressões) + AI Performance do Bing (citações). Estudo
  brasileiro com método (set/2026): menção de marca em português — Gemini 21,6% · Claude 17,1% · Perplexity 16,4% ·
  ChatGPT 11,9%.

### Rastreamento na página e privacidade
- Protocolo curto (9 caracteres, alfabeto sem 0/1/I/L/O, ≥ 1 letra) no texto do `wa.me`: o protocolo longo de 28
  dígitos perdia 53% (medição própria).
- Consent Mode **não** é exigência no Brasil (a política vale para EEE, Reino Unido e Suíça).
- Meta classifica "saúde e bem-estar" como categoria restrita: nome de evento, URL, público e `custom_data` não podem
  refletir condição. Na página: só domínio na URL, eventos neutros desde o nascimento (`contato_wpp`).
- Cookie "2 anos": 400 dias no Chrome; 7 dias (24 h com clique decorado) no Safari para cookie de script.
- GTM servidor por CNAME para terceiro não ganha durabilidade no Safari (7 dias); a **mesma origem** (`/metrics` por
  rewrite) é a melhor prática.
- "iOS 26 apaga o gclid antes de carregar": mito na navegação normal (só privada, Mail, Mensagens).

### Performance e infra
- Lighthouse: mediana de 5 é duas vezes mais estável que 1; versão local alinhada à do PageSpeed.
- O CLI da Vercel publica tudo da pasta exceto uma lista fixa (sem README, ferramentas, `.env.production`) e não lê
  `.gitignore`.
- AVIF-only quebra para ~1 em 20; JPEG XL tem 0% de suporte pleno (mito como próximo formato).
- Vídeo grande não vai no deploy; vídeo longo vai para serviço de streaming.

## 3. O que muda — as regras e decisões que valem a partir daqui

1. **Base única.** Toda página nasce da base da matriz; toda correção entra na base. Nunca "o gerador mais novo" ou
   "o mais parecido".
2. **Preço nunca vai na página**, de nenhuma área (regra da casa, acima de normas que permitem). Item de catálogo sem
   preço é `Service` no JSON-LD.
3. **Sinal de confiança na capa** (selo "★ 5,0 · N avaliações no Google" abaixo do botão; registro do conselho junto do
   nome). Em advocacia, só a OAB.
4. **Botão de pausa** por página para tudo que se move sozinho > 5 s; o estado pausado = estado do reduced-motion.
5. **`/privacidade/` gerada** + link no rodapé de toda página + aviso; em saúde, banner "aceitar/rejeitar" de mesmo peso
   segurando pixel e remarketing (Consent API da Meta). Base legal do cookie do protocolo: decisão jurídica.
6. **Prévia:** `noindex` (meta + `X-Robots-Tag` por host e por caminho de teste) com robots.txt **aberto**.
7. **Ordem da virada de domínio:** (1) versão indexável no ar com canônica/`og:*` no domínio e robots aberto; (2) só
   então o DNS; (3) `curl -I`: 200 e sem `X-Robots-Tag`; (4) 308 `vercel.app` → domínio; (5) Search Console de domínio
   → sitemap → solicitar indexação → "Request a recrawl" do robots.txt se preciso; Bing + IndexNow (Amazon, Bing,
   Naver, Seznam, Yandex, Yep — não Google); (6) depurador de compartilhamento da Meta.
8. **Animação de rolagem em CSS** com `@supports`; manchete animada só na capa e em 1–2 dobras; ouvir a mudança do
   `prefers-reduced-motion` ao vivo.
9. **Fato não confirmado não vai à página** (`confirmado=True` por número; "aberto agora" só com horário confirmado).
10. **Contador nasce com o valor final**; avaliações com "há x dias" calculado.
11. **Datas verdadeiras:** `ATUALIZADO` explícito alimentando `lastmod`, `dateModified` e o rodapé (`<time datetime>`).
12. **Uma URL indexável por termo**; variante de anúncio em `noindex, follow`.
13. **Favicon PNG/ICO** por hostname; canônica/`og:*` só na URL que já responde.
14. **Mídia de IA declarada** na página; pessoa e resultado sempre reais.
15. **Mensagem do WhatsApp sem doença** quando a URL do clique vai ao GA4/Ads.
16. **Ouvinte do GTM ignora `data-form`**; só um evento converte.
17. **Visita por `sendBeacon`** no script do `<head>` (protocolo, gclid/gbraid/wbraid, `gad_campaignid`, UTMs, fbclid,
    referrer) na pintura, no toque e no `visibilitychange → hidden` — aí o GTM deixa de ser crítico e pode ir para o
    ocioso.
18. **Higiene de teste:** chave própria de "não rastrear", `--host-resolver-rules` em todo laboratório, filtro de agentes
    (AdsBot, Googlebot, GoogleOther, Google-InspectionTool, facebookexternalhit, meta-external*, HeadlessChrome).
19. **Checagens que param o gerador:** placeholder, número não confirmado, palavra proibida do conselho, chave duplicada
    no JSON-LD, asset ausente, `<h1>` ≠ 1, title > 60, description > 155, alt vazio sem `aria-hidden`, órfão em
    `assets/`, `<script>` que não passa em `node --check`.
20. **`.vercelignore` em lista de permissão** + sonda pós-deploy; `vercel.json` gerado com `nosniff`,
    `Referrer-Policy` e CSP "de moldura" (`frame-ancestors 'self'; base-uri 'self'; object-src 'none';
    upgrade-insecure-requests` — não toca em script, risco zero para o GTM).
21. **Acessibilidade de nível A como padrão:** símbolo de acessibilidade em destaque no rodapé (Lei 13.146/2015, art. 63,
    §1º), `scroll-padding-bottom` = altura da barra fixa, alvo ≥ 24×24 px, skip link, `viewport-fit=cover`, teste de
    zoom a 200% nos títulos (tipo fluido com `rem` no termo do meio).
22. **Git por projeto**, insumos grandes fora do repositório.

## 4. Riscos (não são pendências de conforto)

| Risco | O que diz a fonte | Consequência | O que fazer |
|---|---|---|---|
| **Plano gratuito da hospedagem proíbe uso comercial** | Vercel Hobby: "non-commercial personal use only"; receber pagamento para hospedar ou anunciar serviço é uso comercial (FATO) | `503 DEPLOYMENT_PAUSED`, que não volta sozinho — no meio de campanha paga; o Hobby não permite comprar uso extra | Conta Pro (US$ 20/mês por assento que publica) em nome da titular da agência; conferir a franquia de requisições na tela de cobrança (doc e preços divergem: 1M × 10M) |
| **Política de privacidade ausente** | Termos do Google Analytics §7; Termos de Ferramentas de Negócios da Meta (aviso em cada página com pixel); Google Ads exige política com remarketing (FATO) | Quebra contratual e restrição de plataforma, antes de qualquer multa. A ANPD não sancionou ninguém por banner até aqui ("já multou por banner" é mito) | `/privacidade/` + link + aviso em toda página; banner de mesmo peso em saúde |
| **Peças em movimento sem pausa** | WCAG 2.2.2 nível A + LBI art. 63 (FATO) | Risco jurídico e de acessibilidade; reprova auditoria | Botão de pausa (ver §3, item 4) |
| **Dado de saúde na URL ou no evento** | LGPD art. 5º, II; política da Meta para categoria restrita (FATO) | Restrição de otimização e de dados na conta | URL só domínio, eventos neutros, mensagem genérica |
| **Arquivos internos publicados** | CLI publica a pasta inteira (FATO) | Notas internas, ids de fluxo e mídias descartadas acessíveis no domínio do cliente | `.vercelignore` em lista de permissão + sonda |
| **Copiar ferramentas entre projetos** | Achado da varredura | Mede o cliente errado, bloqueia os hosts errados e manda visita de teste para a conta do cliente | Ferramentas lendo a configuração do projeto |
| **Canônica ou `og:image` em host que não responde** | Doc do Google e da Meta (FATO/FORTE) | Página com anúncio compartilhada no WhatsApp sem imagem | Trocar só no deploy da virada |
| **Pixel no navegador em clínica** | Categoria restrita; ~0,5 s de thread (FATO) | Peso sem benefício e risco de dado sensível | Conferir a categoria; se restrita, Meta só por API de conversões no servidor |
| **Servidor GTM gratuito** | Plano gratuito de terceiros pausa ao estourar a cota e não reabre (FATO) | GTM mandando dados para destino morto | Plano que não pausa; mesma origem |
| **Mídia de IA não declarada** | Proveniência C2PA/SynthID chegando ao Search e ao Chrome; penalidade de confiança maior em saúde quando revelado (FATO/FORTE) | Perda de confiança exatamente onde a página existe para construí-la | Pessoa e resultado reais; linha de declaração |

## 5. O que não fazer (2026)

- Dark patterns em saúde e direito: cronômetro ou "últimas vagas" falsos, avaliação filtrada para esconder as ruins,
  caixa pré-marcada, banner só com "aceitar" (CDC art. 37; guia de cookies da ANPD).
- Vídeo `autoplay` na capa; vídeo arrastado pela rolagem; biblioteca de animação quando o objeto animado não é o produto.
- `Cache-Control: no-store` (mata o bfcache), `COEP: require-corp` (quebra mapa e YouTube), `Referrer-Policy:
  no-referrer` (apaga a origem da atribuição), CSP estrita com hash sob GTM, HSTS manual em subdomínio do cliente.
- "AI Bots" da Vercel em `deny` (bloqueia também os robôs de busca das IAs); bloquear Google-Extended num cliente que
  quer aparecer no Gemini.
- Construtores de app por IA como produção (entregam React com runtime próprio; 5% de CWV bom no Brasil); um prompt por
  página; Tailwind por CDN.
- Formulário de lead do Google em saúde (vetado); Consent Mode avançado/Google Signals em saúde (supérfluo);
  renomear evento para burlar categoria.
- Lista de bairros como bloco (keyword stuffing); "melhor X"; perseguir rankings de "melhor médico".
- Resubmeter "rastreada, mas não indexada"; robots.txt como mecanismo de remoção.
- Partytown no ouvinte do protocolo; UTM no texto da mensagem.

## 6. Supérfluo (inofensivo, mas não vender como resultado)

`priority`/`changefreq`; `meta geo.*`; `VideoObject` em cena decorativa; `hasCredential`, `knowsAbout`, `areaServed`,
`alumniOf`, `availableService`, `reviewedBy` sem efeito documentado no Google (manter por consistência de entidade, sem
prometer); grupos nomeados com só `Allow: /` no robots.txt (documentação); HSTS manual; `Permissions-Policy`;
`manifest.webmanifest`; JS de rolagem onde o CSS já roda; comentários que vão ao ar; raio de 14 px e caixa-alta nos
botões (assinatura, não alavanca de conversão).

## 7. O que a casa acreditava × o que a evidência diz

| Crença | Evidência de 2026 |
|---|---|
| Prévia com `noindex` em três lugares, incluindo `Disallow: /` | O `Disallow` esconde o `noindex` e é a única peça com cache de 24 h — dois lugares + robots aberto |
| `FAQPage` aparece direto no resultado | Descontinuado em 07-05-2026 |
| `priority` no sitemap ajuda | Ignorado |
| "O laço nunca pausa no hover" basta | Pausa visível obrigatória para > 5 s (nível A) |
| Rolagem só por JS num rAF | CSS scroll-driven nativo em ~95% do celular no Brasil |
| `saveData` desliga a cena no celular | Não existe no Safari nem no Firefox |
| Robôs de IA precisam estar explícitos no robots.txt | `* / Allow: /` cobre; grupos nomeados não herdam do `*` |
| Google-Extended = só treino | Também controla o grounding do app Gemini |
| Claude-User ignora robots.txt | Respeita |
| Schema ajuda a ser citado por IA | Sem ganho relevante medido |
| `llms.txt` "nunca" recebe acesso / peso 0 | 97% sem tráfego em maio/2026; mal formado **derruba** a categoria Agentic (peso 1 por auditoria) |
| Sem política de privacidade é "esperado" | Quebra os termos do GA, da Meta e do Ads |
| Consent Mode necessário no Brasil | Só EEE/Reino Unido/Suíça |
| `gtm.<domínio>` por CNAME = cookie durável | 7 dias no Safari; mesma origem é a melhor prática |
| Filtro `/Lighthouse/i` pega o teste | O UA do Lighthouse 13 não contém "Lighthouse" |
| Observador de LCP dispara em todo Safari | Só no Safari ≥ 26.2 — decidir por detecção da API |
| `json.loads` acusa chave duplicada | Não acusa (fica a última) |
| "Vercel = página rápida" | A pilha decide; origens na Vercel: 43% de CWV bom no mundo, 29% no Brasil |
| Plano gratuito serve para cliente | Uso comercial proibido |
| JPEG XL é o próximo formato | 0% de suporte pleno |
| Title ≤ 60 e um `<h1>` são exigência | Heurísticas de redação |
| CSP/HSTS contam para SEO | Peso 0 |
| Mediana de 3 basta | Mediana de 5 é duas vezes mais estável que 1 (use 5 nas decisões apertadas) |
| "53% abandonam em 3 s" | Página-fonte aposentada; usar casos atuais do web.dev |
| Movimento aumenta conversão | Sem fonte primária — mito como regra |
| APCA como critério de contraste | Fora do rascunho do WCAG 3; usar WCAG 2 |

## 8. Conclusão

O que faltava não era técnica, era **sistema**: a casa já resolvia com medição própria problemas que a maioria das
páginas da web ainda tem no LCP, e perdia correções na cópia. A segunda mudança é de risco: privacidade e plano de
hospedagem são descumprimentos contratuais com consequência operacional, e a acessibilidade de nível A (pausa, símbolo
da LBI, foco sob a barra) virou exigência — no exato ponto em que os concorrentes são mais fracos, o que a transforma em
argumento de venda. O que pesa de verdade para negócio local continua simples: perfil do Google, avaliações recentes,
HTML visível com fatos verificáveis e um sinal de confiança na primeira tela.
