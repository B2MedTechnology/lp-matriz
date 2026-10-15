# 01 · O padrão vigente de landing page

**Em uma frase:** as regras operacionais de toda landing page de cliente, área por área (fazer · não fazer · como medir), que vencem qualquer outro documento desta matriz quando houver conflito.

---

## Como ler este padrão

- Este é o **padrão vigente**. A anatomia dobra a dobra ([02-anatomia-da-pagina.md](02-anatomia-da-pagina.md)) continua valendo em tudo o que não foi revisto aqui; **onde os dois divergirem, este vence**.
- Vale para **toda página nova** e, por migração, para as páginas que já estão no ar (cada correção vira tarefa do cliente).
- Cada área tem três partes: **fazer**, **não fazer** e **como medir**. Uma regra que não se mede não está pronta.
- Os demais arquivos detalham: [insumos](03-insumos-e-briefing.md) · [copy](04-copy.md) · [SEO e velocidade](05-seo-e-velocidade.md) · [componentes](06-componentes.md).

## Regras de casa que atravessam todas as áreas

> **Preço nunca vai na página.** Nenhum valor em R$ na landing page, em nenhuma área (saúde, advocacia, comércio, serviço): nem na faixa de números, nem no FAQ, nem como "a partir de", nem em selo. A pergunta do FAQ sobre valor responde **"informado pelo WhatsApp antes do agendamento"** — mesmo quando o briefing traz o preço. Vale também para avaliações do Google que citem preço (avisar e decidir com o cliente se a avaliação entra na semente).
> *Por quê:* preço muda, cria comparação fora de contexto, é vedado ou arriscado em vários conselhos profissionais (CFM, CFO, OAB) e fecha a conversa antes de ela começar no WhatsApp, que é onde a venda acontece.

1. **Dobra do esqueleto não se corta por falta de insumo.** Faltou foto, Perfil do Google ou texto → use a alternativa que este padrão já dá **ou** pergunte ao responsável pela conta. Nunca remover dobra, trocar o formato de card ou pular botão de pausa, privacidade ou acessibilidade por conta própria.
   *A lição:* numa página de unidade de fisioterapia, a sessão tirou a dobra de avaliações ("a unidade não tem Perfil") e trocou os cards de foto por cards de texto ("não há foto da unidade"), sem perguntar. Foi reprovada. O modelo já tinha a saída: card com foto do **tratamento** de banco livre e, sem Perfil próprio, o Perfil do grupo ou da matriz pelo `?lugar=`, com a atribuição dizendo de qual unidade é.
2. **Exceção legítima se declara na própria página**, para o conferidor automático aceitar: `<meta name="lp-excecao" content="avaliacoes:advocacia">`.
3. **O conselho profissional do cliente define travas.** Advocacia (OAB, Provimento 205/2021): sem dobra de avaliações, sem dobra do espaço físico, sem depoimento, sem "consulta grátis". Saúde (CFM 2.336/2023 e equivalentes): sem superlativo, sem promessa de resultado, sem "melhor", identificação legal completa, depoimento sóbrio.
4. **Fato não se inventa.** Número, prazo, horário, credencial e nome de pessoa só entram com fonte e confirmação (ver [copy](04-copy.md)).
5. **Publicar é decisão do responsável pela conta, não consequência do trabalho.** Toda página nasce prévia `noindex`. O fluxo é sempre **prévia → prova com o cliente → domínio → indexação** (ver [SEO](05-seo-e-velocidade.md)).
6. **Antes de mandar o link, o conferidor automático sai 0** (ver §11).

---

## 1. Insumo e decisões antes do 1º pixel

**Fazer**
- NAP (nome, endereço, telefone) **do Perfil da Empresa no Google**, não do briefing, numa **constante só** no gerador, alimentando o texto visível, o FAQ e o JSON-LD.
- Levantar o `PLACE_ID` do Perfil.
- Responder antes de desenhar: **vai indexar?** **o cliente já tem site?** **quantas URLs, e qual é a canônica?**
- Saber **quem é o revisor** do conteúdo (médico/responsável técnico) e quando ele lê — sem revisão não há `reviewedBy` nem `lastReviewed`.
- Foto real de pessoa e de lugar. **Nunca** banco de imagem para pessoa ou lugar, **nunca** IA para pessoa ou para resultado.
- Pedir o **manual de marca** (logo em vetor, fontes, cores).
- Números com **fonte** e marcados `confirmado=True` no gerador.
- O conselho profissional do cliente configura as **travas do gerador**: `R$` (sempre bloqueado — regra da casa), "grátis", `aggregateRating`, conteúdo da semente de avaliações.
- Um `DESIGN.md` por cliente, emitido pelo gerador e lintado (tokens, contraste).

**Não fazer**
- Publicar número marcado "confirmar".
- "Melhor X", superlativo em saúde, convênio no título.
- **Preço em qualquer lugar da página** (regra da casa acima).
- Depoimento em advocacia.

**Como medir** — o gerador **para** (`SystemExit`) quando encontra:
placeholder sem valor · número não confirmado · palavra proibida pelo conselho ou pela casa (`R$`, "grátis") · chave duplicada no JSON-LD · asset ausente · AVIF ausente · `<h1>` diferente de 1 · `title` > 60 caracteres · `description` > 155 · `alt` vazio sem `aria-hidden` · arquivo órfão em `assets/` · `<script>` embutido que não passa em `node --check`.

## 2. Design e 1ª dobra

**Fazer**
- **Capa de fundo** com foto real em tela cheia, véu medido (texto ≥ 4,5:1 contra o fundo **real**), texto sobre a área calma da foto, **recorte próprio em retrato** para o celular (detalhe em [anatomia §4c](02-anatomia-da-pagina.md)).
- **Um sinal de confiança verificável na capa ou na faixa 2**: nota + contagem do Google, CRM/RQE, OAB. *Por quê:* a rolagem média no celular cobre menos da metade da página (≈ 45%); a dobra de avaliações fica além disso.
- A dobra inteira (título, subtítulo, botão, aviso) **cabe em 390×725 e em 360×640**, medido por script.
- Tipografia fluida com `rem` no termo do meio do `clamp()` e teste de **zoom a 200%**.
- Linha de texto ≤ 75 caracteres.
- **Símbolo de acessibilidade em destaque no rodapé** (Lei Brasileira de Inclusão, art. 63 §1º).
- `scroll-padding-bottom` = altura da barra fixa do celular (WCAG 2.4.11: o foco não pode ficar escondido atrás dela).
- Alvo de toque ≥ 24×24 px; *skip link*; `viewport-fit=cover` com `env(safe-area-inset-bottom)`.

**Não fazer**
- Tendências de galeria: 3D, neon, neumorfismo, gamificação.
- Clichês de 1ª geração de sites feitos por IA: índigo/roxo, cards com sombra, grade de ícones, fonte Inter.
- Clichês de 2ª geração **quando não vêm da marca**: creme + serifa + terracota; preto + verde-ácido; sobrancelha em caixa-alta por padrão; "→" automático; numerar sem haver sequência; uma palavra destacada no título; *fade* em toda seção; herói com número grande.
- *Dark patterns*. Vídeo com `autoplay` na capa. Dois CTAs fixos ao mesmo tempo (flutuante e barra).

**Como medir** — script de medição da dobra (folga em 725 e 640 px de altura; eixo único em 1440, 1920 e 390 px de largura) · prints com emulação real em 320, 390 e 1000 · contraste dos tokens contra o fundo real · axe com o JSON inteiro · zoom 200% no Chrome.

## 3. Ordem das dobras e copy

**Fazer** — a ordem é funil (detalhe em [anatomia §6](02-anatomia-da-pagina.md)):

1. **Capa**
2. **Números** — 5 a 8, confirmados, **nascendo com o valor final no HTML** (sem JS, nunca "0")
3. **Quem é** — o registro profissional junto do nome
4. **Catálogo** (4b · corpo clínico, quando a clínica tem mais de um profissional)
5. **Como funciona** — o filtro vem **depois** do catálogo
6. **O espaço**
7. **Avaliações** — nota e contagem **sempre da API** pelo `?lugar=<place_id>`; "há x dias" **calculado** da data; "Fornecido pelo Google"; link "ler todas"; **nunca** `aggregateRating`; **ausente em advocacia**
8. **FAQ** real e deduplicado — `<details>`, 6 a 8 perguntas, **as mesmas** do `FAQPage`
9. **Onde e quando** — `<address>`, `<dl>`, mapa do Perfil
10. **Rodapé** — identificação legal completa, "não substitui consulta" (saúde), "página atualizada em" com `<time>`, revisor visível, link de Privacidade, símbolo de acessibilidade

- Texto no nível de leitura de 5ª a 7ª série em saúde e serviços (jurídico tolera mais). Em saúde, 355 a 1.020 palavras como referência.
- **Resposta direta no topo de cada bloco.**
- Data de atualização recente **de verdade**.
- Preço: **nunca** (regra da casa). O FAQ do valor responde "informado pelo WhatsApp antes do agendamento".

**Não fazer**
- Mensagem pré-preenchida do WhatsApp com doença ou procedimento quando a URL do clique vai ao GA4/Ads (dado de saúde — LGPD art. 5º, II; a Meta proíbe parâmetro que reflita condição).
- Bairros em lista solta no texto.
- Data que muda sem mudança de conteúdo.
- "Curadoria" de avaliações que esconda nota ou contagem.

**Como medir** — contagem de palavras e índice de legibilidade no gerador (aviso, não trava, até existir limiar validado em português) · FAQ visível = `FAQPage` (assert no gerador) · `dateModified` = `lastmod` do sitemap = data do rodapé = constante `ATUALIZADO` explícita.

## 4. Movimento

**Fazer**
- **Um evento-assinatura por cliente na capa** (ver [componentes](06-componentes.md)), em `@keyframes` só de `transform`/`opacity`, pausando fora da tela **e com botão visível de pausa** (ou assentando em ≤ 5 s).
- Manchete animada só na capa (≤ 1 s, opacidade inicial > 0) e em 1–2 dobras.
- Linha do tempo, cartões e manchetes de rolagem por `animation-timeline: view()` dentro de `@supports (animation-timeline: view())` + `@media (prefers-reduced-motion: no-preference)`; fora disso, estado final.
- `sibling-index()` com `--i` de reserva; `@starting-style` nas entradas; ouvinte de `change` do `prefers-reduced-motion` (a pessoa pode ligar com a página aberta).
- Carrossel de avaliações: anda sozinho a cada 5 s, para 9 s ao toque, para fora da tela, com movimento reduzido e no botão de pausa. *(Decisão posterior à primeira versão deste padrão, que pedia carrossel só por comando da pessoa; vale a versão automática **com** botão de pausa.)*
- Letreiro (faixa de números) com a cópia `aria-hidden` + `inert` e pausa.
- Fotos que respiram pausam fora da tela e param no botão.
- `text-wrap: balance` em `h1`/`h2`.
- **O botão de pausa para tudo:** animações CSS (`html.pausado`), todo laço de `setInterval` (a função sai cedo com `window.__pausado`) e o vídeo em laço, que não volta a tocar sozinho enquanto a página estiver pausada ([lições 5.8](10-licoes-aprendidas.md)).
- **Topo compacto só por opacidade:** fundo e sombra numa camada `::before` que muda `opacity`; padding e altura do logo trocam sem transição; barra de progresso só por `transform` ([lições 5.9](10-licoes-aprendidas.md)).
- **Foco do teclado ≥ 3:1 nas duas cores de fundo:** escuro (cor forte da marca) nas seções claras, claro só nas escuras ([lições 5.10](10-licoes-aprendidas.md)).

**Não fazer**
- JS de rolagem onde o CSS já roda; `box-shadow`, `filter`, `background`, `background-size`, `padding`, `width` ou `height` animados; `backdrop-filter` no topo ou na barra fixa; `requestAnimationFrame` perpétuo rodando parado.
- *Scrolljacking*, rolagem suave forçada, parallax em texto, polyfill de scroll-timeline.
- Biblioteca de animação quando o objeto animado não é o produto.
- Quebrar texto em `<span>` por JS na carga; ler layout antes do 1º quadro; cronômetro pós-load para terceiros.

**Como medir** — medição de rolagem por CDP (60 fps, 0 tarefas longas) · Speed Index sem laço antes do `load` · `non-composited-animations` = 0 · `aria-hidden-focus` e `button-name` limpos na categoria Agentic do Lighthouse · teste com `prefers-reduced-motion` ligado **e trocado ao vivo**.

## 5. Vídeo e cena

**Fazer — vídeo em laço**
- Pôster = **quadro 0** em AVIF, cores cruas, como `<img fetchpriority="high">` **por baixo** do vídeo.
- `<video muted loop playsinline preload="none" aria-hidden="true">` com `<source>` AV1 antes do H.264.
- `play()` no `load` + 1–1,5 s ou no 1º gesto; recusa (iPhone em Pouca Energia) **re-armada** em `touchend`/`pointerup`/`click`/`keydown`.
- Pausa fora da tela; ≤ 1–2 MB; 5–12 s; dissolução do laço **gravada no arquivo**; botão de pausa.

**Fazer — cena arrastada pela rolagem**
- Sequência AVIF desenhada em `<canvas>`; esqueleto de 1 quadro a cada 16; janela de quadros vivos com `close()`; duas telas empilhadas; suavização τ entre 0,04 e 0,11 s (medida); quadros baixando no `load` ou no 1º gesto, 6–10 em paralelo, retentativa com teto 3; pôster no mesmo recorte do canvas.
- No celular, rebaixar (pôster + laço ≤ 1 MB, ou 96–120 quadros se a medição aprovar), ≤ 40 quadros vivos, teto por memória, densidade 2× a medir.

**Fazer — mídia de IA**
- Imagem→vídeo a partir de **foto real** (8 s, 1080p ou 4K), sem trilha de áudio (`-an`), porteiro dos 9 quadros (ver [componentes](06-componentes.md)) e **declaração de uso de IA na página**.

**Não fazer** — arrastar o `<video>` pela rolagem · `autoplay` na capa · vídeo grande dentro do deploy (depoimento longo vai a um serviço de streaming) · depender de um único gerador de vídeo · usar `saveData` como única trava (não existe no Safari).

**Como medir** — tempo do LCP ao 1º `playing` · laço recusado no iPhone em Pouca Energia · atraso da cena ao dedo · LCP no celular < 2,5 s com ≈ 300 KB antes do LCP.

## 6. SEO técnico e metadados

**Fazer**
- `<head>` nesta ordem: charset · viewport · title · description · robots · canonical · GTM · Open Graph · ícones · `<style>` · JSON-LD.
- `title` ≤ 60 com termo + diferencial; `description` ≤ 155.
- `og:image` JPEG 1200×630, < 600 KB, com `?h=`.
- `canonical`, `og:url` e `og:image` **sempre numa URL que já responde 200**.
- Ao indexar: `robots` com `max-image-preview:large, max-snippet:-1, max-video-preview:-1`.
- Favicon PNG 48 e 96 + `apple-touch-icon` + `/favicon.ico` em cada hostname.
- Sitemap só com canônicas, `lastmod` verdadeiro e `image:loc`.
- **Uma URL indexável por termo**; variante de anúncio em `noindex, follow`.
- 308 do `*.vercel.app` para o domínio; `trailingSlash: true`; conferir "Search generative AI = Include" nas configurações da propriedade.
- **Mudou de host:** os dez lugares da [lição 7.11](10-licoes-aprendidas.md); todo redirecionamento vai direto à canônica indexável e a raiz responde 308.

**Não fazer** — `priority`/`changefreq` no sitemap · `meta keywords`/`geo.*` · canônicas diferentes por técnicas diferentes · duas páginas indexáveis para sinônimos · data de geração como `dateModified` · favicon `data:` · `href="#"` · HSTS/CSP "para SEO".

**Como medir** — Lighthouse SEO 100 na publicada (69 na prévia = só o `noindex`) · Inspeção de URL (canônica declarada = escolhida pelo Google) · Rich Results Test para tipos com recurso · validator.schema.org para os demais · Sharing Debugger da Meta na virada · verificação no ar com expectativa derivada do interruptor `INDEXAR`.

## 7. Dados estruturados

**Fazer**
- `@graph` com `WebSite` + `WebPage`/`MedicalWebPage` (`dateModified`; `lastReviewed` **só com** `reviewedBy`) + a entidade do **subtipo mais específico**: `IndividualPhysician` + `practicesAt` → `MedicalClinic`/`PhysiciansOffice`; `Dentist` + `MedicalClinic`; `LegalService`; `Bakery`; `HardwareStore` etc.
- `Product` só com preço publicado: `offers` dentro, `brand` como `Brand`, política de troca e frete **reais** ([lições 7.10](10-licoes-aprendidas.md)).
- Na entidade: `name`, `address`, `telephone` (= página = Perfil), `url`, `geo` com ≥ 5 casas decimais, `hasMap`, `sameAs` (o Perfil do Google **primeiro**), `openingHoursSpecification` **só se o horário for exato**, `image` 16×9/4×3/1×1, `logo` ≥ 112×112 quadrado.
- `Person` com `hasCredential` (cada uma com `name`) e `name` sem título ("Fulana de Tal", não "Dra.").
- `FAQPage` = FAQ visível, saindo da mesma lista.
- Validar com `object_pairs_hook` que levanta erro em chave duplicada.
- Sobre `priceRange`: **não usar valor em R$** (regra da casa).

**Não fazer** — `aggregateRating`/`review` próprios (a política do Google proíbe usar avaliação de terceiro como do site) · marcar o que não está visível · `VideoObject` em cena decorativa · vender schema como "otimização para IA" · `Attorney` (use `LegalService`) · valor fora da enumeração em `medicalSpecialty`.

**Como medir** — `json.loads` com `object_pairs_hook` · Rich Results Test (LocalBusiness/Organization) · Inspeção de URL.

## 8. Prévia, indexação e robôs

**Fazer**
- **Prévia = `noindex` em dois lugares** (meta + cabeçalho `X-Robots-Tag` por `has: host` no `<projeto>.vercel.app` e por caminho de teste, gerados pelo interruptor `INDEXAR`) com **`robots.txt` aberto**.
  *Por quê:* `Disallow: /` impede o Google de ler o `noindex` — a página pode aparecer na busca mesmo assim — e o `robots.txt` é a única peça com cache de até 24 h. Uma página de cliente ficou travada para indexar porque o domínio passou a responder com o `robots.txt` da prévia.
- **Virada**, nesta ordem: versão indexável no ar → CNAME → `curl -I` (200, sem `X-Robots-Tag`) → 308 → Search Console com propriedade de **domínio** (na conta da agência) → sitemap → Solicitar indexação → "Request a recrawl" do `robots.txt` se algo ficou em cache → Bing + IndexNow (chave aleatória) → Sharing Debugger → verificação final.
- `robots.txt` de produção com `User-agent: *` / `Allow: /` e, **como documentação**, os robôs de citação: OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Googlebot, Google-Extended, Bingbot, Applebot, Meta-WebIndexer, DuckAssistBot, Amzn-SearchBot, MistralAI-Index — com o comentário certo: "o `*` já libera; grupos nomeados não herdam do `*`".
- Medir no relatório de IA do Search Console e no AI Performance do Bing.

**Não fazer** — `Disallow: /` na prévia · `llms.txt`, `Content-Signal` ou WebMCP como entrega · texto oculto · menções inautênticas · bloquear "AI Bots" no firewall da Vercel · reenviar "Rastreada, mas não indexada" em série.

**Como medir** — `curl -A` com os user-agents oficiais atuais · script de verificação de buscadores · impressões em IA no Search Console · citações no Bing.

## 9. Rastreamento na página, privacidade e LGPD

**Fazer**
- Script no `<head>` com:
  - (a) **protocolo no 1º toque**: cookie `SameSite=Lax; Secure`, domínio raiz, código com ≥ 1 letra, frase **byte a byte igual** à das tags do contêiner, expressão regular sem diferenciar maiúsculas, `encodeURIComponent`. *Por quê:* quem toca no WhatsApp antes de o GTM carregar sai sem protocolo — numa medição, 5 falhas em 12 cliques sem esse bloco;
  - (b) **visita por `sendBeacon`** (protocolo, gclid/gbraid/wbraid, `gad_campaignid`, UTMs, fbclid, referrer) na pintura, no toque e no `visibilitychange → hidden`, com gravação idempotente por protocolo. Assim o GTM deixa de ser crítico para a atribuição.
- Carregador do GTM com **trava de host** (também no `noscript` e no cookie do protocolo), decidido por *feature detection* do observador de LCP (`PerformanceObserver.supportedEntryTypes`), no ocioso depois do beacon.
- `medir()` só empurra no `dataLayer`. O ouvinte do GTM ignora botões com `data-form` (abrir formulário não é contato).
- Conversão num evento só (`contato_wpp`); `agendar_click{origem}` como dimensão.
- Página `/privacidade/` gerada + link no rodapé + aviso em toda página. *Por quê:* os termos do GA, da Meta e do Google Ads exigem; sem isso é descumprimento contratual.
- **Aviso de cookies mínimo, com "Ok"**, que aparece depois do `load` e não segura tag nenhuma; no celular fica **no pé**, à direita do botão de pausa, e **sobe com a barra** — aviso e pausa vêm depois da `.barra` no HTML ([lições 2.13](10-licoes-aprendidas.md)).
- O `gtag` do GA4 e do Google Ads mora no contêiner: toda versão nova do contêiner web mede o PageSpeed do celular antes × depois ([lições 8.5](10-licoes-aprendidas.md)).
- Em saúde: banner aceitar/rejeitar **de mesmo peso** segurando pixel e remarketing (Consent API da Meta); URL enviada só com domínio; eventos com nome neutro; Meta por CAPI no servidor quando a categoria restringe.
- GTM de servidor na **mesma origem** (`/metrics` por `rewrite`) ou em zona de São Paulo, em plano que não pausa.
- RUM com `web-vitals` v6 pelo `dataLayer`.
- Testes com chave própria, `--host-resolver-rules` e filtro de agentes na automação que recebe os eventos.

**Não fazer** — `gtag`/`fbq` diretos ao lado do GTM (duplicam) · UTM na mensagem do WhatsApp · correlação por horário para subir conversão · renomear evento para burlar política · condição de saúde em URL, evento ou `custom_data` · Consent Mode avançado ou Google Signals em saúde · Partytown no ouvinte · medir Web Vitals com o modo de visualização do GTM · formulário de lead do Google em saúde.

**Como medir** — gravador de eventos (1 clique = 1 `contato_wpp`; abrir formulário = 0) · cliques × mensagens com protocolo · protocolo órfão por navegador · Lighthouse de produção com os hosts de envio **do cliente** bloqueados (senão a medição vira visita de teste na conta dele) · `validateOnly` no Data Manager e eventos de teste da Meta · INP de campo.

## 10. Performance, infraestrutura e segurança

**Fazer**
- CSS **embutido**; fontes woff2 **locais** com recorte latino (inclui U+00C0–U+00FF, ª/º, U+2013–U+201D), `font-display: swap`, fonte variável só com 3+ pesos, `preload` só da fonte do título e só se o LCP for texto.
- AVIF por largura + JPEG de reserva, `width`/`height` sempre, capa com `fetchpriority="high"` e **nunca** lazy, recorte em retrato, teto de largura.
- `?h=<hash do conteúdo>` em img, vídeo, fontes, CSS, JS e nas URLs absolutas, com `Cache-Control: immutable`; HTML com `max-age=0, must-revalidate`.
- `vercel.json` gerado com `X-Content-Type-Options: nosniff`, `Referrer-Policy` e CSP de moldura (`frame-ancestors 'self'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests`).
- `.vercelignore` em **lista de permissão** + sonda `curl` pós-deploy dos caminhos sensíveis.
- Vídeo curto no deploy, longo fora. Plano pago da hospedagem para cliente. `git` por projeto. Insumos no Drive do cliente.

**Não fazer** — plano gratuito para cliente · `no-store` · HSTS manual · COEP/COOP/Permissions-Policy · CSP estrita com hash sob GTM · Early Hints · Speculation Rules · JPEG XL · só AVIF sem reserva · otimizador de imagem da hospedagem em `<img>` comum · publicar a pasta do projeto inteira.

**Como medir** — Lighthouse local na **mesma versão do PageSpeed** · mediana de 3 rodadas na rotina e de **5** nas decisões apertadas (1–3 pontos), máquina calma, uma medição por vez · metas: **≥ 95 celular, 100 desktop, 100 acessibilidade, 100 boas práticas, 100 Agentic** · `curl -I` de cabeçalhos e caminhos sensíveis nos dois hosts · validador HTML (`vnu`) → axe/pa11y em JSON → verificador de links → sonda · CrUX quando houver; RUM antes disso.

## 11. Processo e base de código

**Fazer**
- **Uma base** de gerador e ferramentas, lendo `BASE`/`SLUG`/hosts de um único `gerar.py`. Cliente = dicionário de constantes. Fork sempre da base, nunca "do gerador mais novo" nem "do mais parecido".
- Nomes fixos em toda página: `data-origem`, `.flutuante`, `.botao`, `aoRolar()`, `trilho`.
- Toda correção registrada com "replicar em: …" até que todos os geradores a tenham.
- `LEIA-ME.md` fora de `site/`, com o estado real (índice, decisões, pendências numeradas, o que quebrou).
- A checagem do agente como gancho de fim de tarefa: prints 320/390/1000, Lighthouse ×5, axe JSON, alt revisado, `vnu`, verificador de links, sonda.
- Trace de LCP pelo DevTools quando o LCP piorar.
- **Antes de mandar o link**, o conferidor automático (`python3 ferramentas/conferir.py <url ou arquivo>`) sai 0. Ele confere: dobras e ordem; cards com foto em grupos de 3; avaliações por `?lugar=` + semente; JSON-LD válido, sem `aggregateRating`, `Product` só com `offers` e `brand` do tipo `Brand`; botão de pausa e todo laço automático obedecendo a ele; aviso de cookies e pausa depois da barra; privacidade; `<time>`; acessibilidade; `viewport-fit`; `h1`; `title`; `description`; nenhuma transição de pintura/layout nem `backdrop-filter` no topo; foco escuro no fundo claro; prévia `noindex`; favicon, robots e sitemap. Avisa (não reprova) quando falta a marca do porteiro de anatomia.
- **Página antiga: o conferidor roda antes de mexer**, e o que ela reprova vai ao responsável junto com o pedido ([lições 13.4](10-licoes-aprendidas.md)).

**Não fazer** — gerador de app React como produção · um prompt por página · copiar `ferramentas/` sem reler · builds ou dois servidores locais ao mesmo tempo em máquina modesta · docstring descrevendo a versão anterior.

**Como medir** — `diff` das ferramentas entre projetos = 0 fora das constantes · toda correção presente em N de N geradores · `LEIA-ME.md` × `gerar.py` sem contradição (`INDEXAR`, índice, curadoria).

---

## Checklist de aceite

- [ ] Nenhum valor em R$ na página; FAQ do valor = "informado pelo WhatsApp antes do agendamento".
- [ ] As 10 dobras na ordem, catálogo acima do filtro; nenhuma dobra cortada sem exceção declarada em `lp-excecao`.
- [ ] Sinal de confiança verificável na capa ou na faixa 2.
- [ ] Dobra cabe em 390×725 e 360×640 (medido); eixo único medido em 1440/1920/390.
- [ ] Números confirmados, nascendo com o valor final no HTML.
- [ ] Botão de pausa presente; tudo o que se move > 5 s para nele, **inclusive o carrossel**.
- [ ] Topo sem animar pintura/layout; foco do teclado ≥ 3:1 em seção clara e escura.
- [ ] Aviso de cookies no pé no celular, sem cobrir o botão da capa (print 390×844 e 360×640 depois do `load`).
- [ ] NAP idêntico ao Perfil do Google em texto, FAQ e JSON-LD.
- [ ] JSON-LD sem chave duplicada, sem `aggregateRating`, `reviewedBy` só com revisão real.
- [ ] Prévia com `noindex` (meta + `X-Robots-Tag`) e `robots.txt` aberto.
- [ ] `/privacidade/` linkada; protocolo no 1º toque e beacon de visita presentes; nenhuma condição de saúde em URL/evento.
- [ ] Lighthouse: ≥ 95 celular (mediana), 100 desktop, 100 acessibilidade, boas práticas e Agentic; SEO 69 na prévia com o `noindex` como única reprovada.
- [ ] Conferidor automático saiu 0.
