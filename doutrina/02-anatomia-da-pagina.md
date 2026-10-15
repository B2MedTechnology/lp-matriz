# 02 · Anatomia da página, dobra a dobra

**Em uma frase:** o que é cada dobra da landing page, por que ela existe e está naquela posição, como se constrói (com medidas e código de referência) e como se aceita — subordinado ao [padrão vigente](01-padrao.md), que vence onde houver divergência.

---

## Mapa deste arquivo

§0 como replicar uma dobra de outra página · §1 a pilha · §2 prévia antes de publicar · §3 a 1ª dobra do celular (725/640) · §4 a imagem faz parte da dobra · §4b eixo único à esquerda · §4c a capa de fundo · §5 botões e contato · §6 a ordem das dobras · §6a o mínimo de cada dobra · §6b avaliações do Google · §6c cards de catálogo · §6d mapa e Perfil da Empresa · §6e animações de cada dobra · §7 medição · §8 o que não fazer (estética "de IA") · §9 fatos não se inventam · checklist de aceite.

As seções §4c, §5, §6, §6b, §6c e §6e são **padrão universal**: valem em toda página, sem discussão por cliente — com o limite do conselho profissional (advocacia: sem avaliações e sem a dobra do espaço).

---

## 0. Como replicar uma dobra de outra página — ler antes de escrever CSS

**Por que existe:** num pedido de "refazer só a 1ª dobra no formato da página de outra cliente", houve **quatro rodadas reprovadas**, e só acertou quando chegou um print da referência. A documentação da página de origem estava boa e a mecânica foi copiada certa (mesmo arquivo 3:2 de 1800×1200, `object-fit: cover`, mesmo véu, mesmo empilhamento). **Nenhuma linha de CSS explicava a diferença.** O que quebrou foi o **insumo**: a foto da cliente nova não tinha a composição da foto de referência.

### O porteiro — checar o insumo antes de qualquer linha

Para a capa de fundo (§4c), contra o material **real e aprovado** do cliente novo:

1. A foto tem **plano geral**, com o ambiente legível em volta da pessoa?
2. Sobra **ar acima da cabeça**? (Na referência aprovada, o topo da cabeça estava a **17% da altura da dobra**; na reprovada, a 6%.)
3. **Nenhuma borda do arquivo corta a pessoa?**
4. A metade onde vai o texto tem **superfície calma** (parede, janela, estante)?

**Qualquer "não" = pare.** Diga ao responsável que o formato exige uma foto que não existe no material aprovado e pergunte se o cliente fotografa de novo ou se autoriza alargar o quadro — **antes** de gastar rodada. Alargar é plano B (§4, "afastar em vez de ampliar").

**Quando só o item 4 falha** (a pessoa está boa, mas o lado do texto tem equipamento), há uma terceira saída sem foto nova: **recuar a CAIXA, não a foto.** A foto ocupa uma caixa de **66% à direita** que dissolve pela esquerda (no celular, os **57% de cima**, dissolvendo para baixo) e o texto fica sobre o fundo escuro. Descartados: espelhar a foto (bordado do jaleco sai invertido) e alargar (borda não uniforme).

A cadeia de defeitos da lição foi toda descendente de pular o porteiro: foto errada → recorte aproximou o rosto ("cortada, muito próxima") → alargar na marra → emenda vertical ("linha feia") → máscara na emenda ("borrão feio"). Quatro queixas, **uma causa**. Consertar sintoma por sintoma na ordem em que aparecem é o erro.

### O protocolo — seis passos, nesta ordem

1. **Ler a lista de versões reprovadas da dobra de origem antes do CSS.** Cada linha é uma restrição ativa. Sair de uma delas exige dizer por quê.
2. **Rodar o porteiro** contra o material do cliente novo.
3. **Abrir a página de origem e tirar print dela** (desktop **e** celular). A referência é a página, não a memória da documentação.
4. **Construir.**
5. **Pôr os dois prints lado a lado, no mesmo tamanho, antes de mostrar.** Esse passo sozinho pega quase tudo em trinta segundos.
6. **Toda diferença deliberada se diz em voz alta** ("mudei X porque Y"). Esconder o evento dinâmico no celular por conta própria é desvio silencioso, não bug.

> "No formato de X" é **composição**, não técnica: quanto a pessoa ocupa do quadro, quanto ar sobra em volta e que fatia da largura o texto toma (numa referência, **28%**; na outra, **41%**). Isso um texto transmite mal e uma imagem transmite em um segundo — por isso **toda dobra reaproveitável carrega print de referência**.

---

## 1. A pilha (não negociável)

**HTML + CSS + JS puros. Sem framework, sem build.**

```
cliente/
  gerar.py            (constantes do cliente + gerador; a saída vai para site/)
  template/pagina.html
  LEIA-ME.md          (estado, pendências, medição, como mexer — fora de site/)
  site/
    index.html
    robots.txt
    sitemap.xml
    vercel.json       (cache dos assets + cabeçalhos, gerado)
    privacidade/index.html
    assets/
      css/estilo.css  (é o que se edita; o gerador embute no HTML)
      js/pagina.js
      img/… fonts/…
```

**Por quê:**
- Máquina modesta sofre com build local; sem build, verificar é abrir o arquivo.
- Página de campanha precisa abrir no 4G de quem clicou no anúncio: as páginas ficam **abaixo de 1 MB** e servem em **menos de 0,7 s**.
- Trocar uma foto é trocar um arquivo.

**Gerar, não duplicar.** Mais de uma variante (ex.: uma por palavra-chave, para o Índice de Qualidade)? Um `gerar.py` produz todas de um template. Ganhos:
- **FAQ visível e `FAQPage` saem da mesma lista** — acaba o erro de trocar num lugar e esquecer o outro.
- **O número do WhatsApp vive numa constante só** (`WHATSAPP`), injetada em todos os botões; o JS não guarda cópia, só mede o clique.
- O gerador **falha se sobrar placeholder** e atualiza a versão dos assets sozinho.

**Cache-busting é obrigatório.** Com `/assets/*` marcado `immutable`, nome de arquivo fixo faz o navegador **nunca** pegar a versão nova. Todo asset leva `?h=<hash do conteúdo>` (ou, no mínimo, `?v=` que sobe a cada deploy).

**Prévia local:** `python3 -m http.server 8940` na pasta `site/`. Um servidor por vez; derrubar ao terminar. Publicação: `npx vercel --prod --yes`.

**Velocidade é regra da pilha** (detalhe em [SEO e velocidade](05-seo-e-velocidade.md)): CSS embutido e fontes locais; foto na largura em que aparece; o pesado espera o 1º gesto e o terceiro espera a proximidade; medida se lê depois do quadro; contraste decidido no token. Com essas cinco regras, uma página foi de **65 para 98–100** no celular.

---

## 2. Prévia antes de publicar

Toda página nasce **prévia**: `<meta name="robots" content="noindex, nofollow">` + cabeçalho `X-Robots-Tag` no `vercel.json`, com o **`robots.txt` aberto** (nunca `Disallow: /`: ele esconde o `noindex` do Google e fica em cache por até 24 h). Sai da prévia só quando o domínio estiver decidido e o cliente aprovar.

**Sempre procurar se o cliente já tem site antes de desenhar.** Numa página de dermatologia, a cliente já tinha um site num construtor de páginas e ninguém tinha avisado; uma página nova indexada teria competido com a dela pelo mesmo nome.

Na prévia o PageSpeed dá **SEO 69** — é o número certo (ver [SEO e velocidade](05-seo-e-velocidade.md)).

---

## 3. A primeira dobra do celular — a regra mais cara de aprender

**Tudo o que decide cabe na primeira tela: título, subtítulo, botão de contato e a linha do filtro.** Sem faixa branca sobrando e sem foto cortada.

O erro que se repete: **medir num quadro generoso e declarar que coube.** Conferido em 780 px de altura, "cabia"; no aparelho real (~**725 px** úteis) e num de **640 px**, o aviso estava cortado nos dois.

**Medir, não olhar.** Uma página de teste com dois `<iframe>` — **390×725** (aparelho real comum) e **360×640** (o menor comum) — e, por JS, `viewport − rect.bottom` do último elemento da dobra. Apagar o arquivo antes do deploy.

**A dobra inteira escala com a ALTURA, não só com a largura.** Se só a foto usa `svh` e o texto é fixo, em tela baixa o texto sozinho come a dobra:

```css
.capa h1    { font-size: clamp(2.1rem, min(11.6vw, 6.2svh), 3.4rem); }
.capa .lead { font-size: clamp(.9rem,  min(4vw, 2.05svh), 1rem); }
.capa .acoes{ margin-top: min(1.05rem, 2.2svh); }
@media (max-width: 700px) and (max-height: 690px) { /* telas baixas: a foto cede */ }
```

Referência medida numa página aprovada: **20 px de folga em 725** e **23 px em 640**.

**Aceite:** folga ≥ 0 (idealmente ≥ 16 px) nas duas alturas, com a barra fixa e o botão de pausa no lugar.

---

## 4. A imagem faz parte da dobra — nunca é um quadrado flutuando

- **A primeira dobra é a foto**, não uma foto dentro da dobra. "Por que não usamos a foto como plano de fundo ao invés de um quadro com a imagem? Fica mais profissional." Receita completa em §4c.
- **Desktop:** onde houver foto em coluna (dobras internas), ela **sangra até a borda da tela**, sem moldura nem card, com bordas dissolvidas por `mask-image`. O tom do fundo da foto é amostrado e estendido num `radial-gradient` atrás do texto: os dois lados viram um ambiente.
- **Celular:** a foto sangra de ponta a ponta e desce por trás do título; onde o texto passa, véu da cor de fundo.
- **Nunca `z-index` negativo nas camadas.** Com `isolation: isolate` no pai, filho com z-index negativo vai para trás do fundo do próprio pai e a foto some **sem erro no DevTools**. Empilhar positivo.
- **Capa panorâmica exige foto horizontal.** Recortar retrato em 16:9 amplia o rosto e perde o corpo. O recorte se faz **assimétrico no arquivo**, porque `object-position` só desloca dentro da pouca sobra do `cover`.

**Afastar em vez de ampliar.** Quando o cliente pede "da cabeça até o tronco" e o recorte não permite: **estender o fundo lateralmente** (amostrar o degradê do fundo linha a linha numa coluna limpa e alargar o quadro), nunca ampliar. A pessoa fica menor num quadro maior, sem perder pixel. Script em [insumos](03-insumos-e-briefing.md). Toda a faixa inventada tem de caber no trecho transparente da máscara (§4c), senão a emenda reaparece.

**Blocos de serviço são cards com imagem de fundo**, não listas de texto ("as pessoas são visuais e querem informação rápida") — padrão em §6c.

**Especialidade sensível sem foto que sirva.** Numa página de proctologia o card com foto falhou três vezes: fotos da médica (as seis viravam a mesma cena), banco de imagem ligado ao **benefício** (desconexo) e ao **sintoma** (dramático ou explícito). Saída: card **sem foto**, com um **sinal em linha desenhado em SVG** à mão (24×24, `stroke-width: 1.25`, `fill: none`), título serifado, descrição e tags sobre fundo escuro. Nunca biblioteca de ícones genérica.

**Banco de imagem gratuito:** nunca o acervo pago "plus" do Unsplash (vem com marca d'água); só o CDN público de imagens gratuitas.

---

## 4b. Eixo único à esquerda na capa

**Etiqueta, título, subtítulo, botão e aviso começam todos no mesmo x.** Medir, não olhar:

```js
['.etiqueta','h1','.lead','.botao','.aviso-particular']
  .map(s => Math.round(document.querySelector(s).getBoundingClientRect().left))
// todos iguais, em 1440, 1920 e 390 px
```

A causa quando desalinha é quase sempre a mesma: **`margin-left: auto` tira o item de grade do `stretch`** e ele passa a caber no próprio conteúdo. Dois blocos com o mesmo `max-width` param em x diferentes porque título é mais estreito que parágrafo (numa página, 38 px de desvio que passou duas rodadas sem ser visto).

```css
/* errado: mesmo teto, larguras diferentes, eixos diferentes */
.capa__cabeca, .capa__resto { max-width: 42rem; margin-left: auto; }
/* certo: mesma LARGURA nos dois */
.capa__cabeca, .capa__resto { width: min(37rem, 100%); margin-left: auto; }
```

Onde houver margem automática, `max-width` não garante alinhamento — só `width` garante.

---

## 4c. A capa de fundo — o padrão de 1ª dobra

**A dobra é a foto em tela cheia.** Ocupa a viewport inteira, o texto vive **sobre** ela na metade esquerda, e a foto se **dissolve** no fundo escuro em vez de terminar numa borda.

**Por que é o padrão:** resolve de uma vez as quatro queixas que voltavam em todas as capas em duas colunas — espaço vazio em cima e embaixo, vão entre texto e imagem, texto espremido numa coluna estreita e a foto lida como "um quadro dentro da página". Com a foto sangrando, o cliente é o fundo.

### Esqueleto

```html
<section class="capa capa--fundo" id="capa">
  <figure class="palco" id="palco" data-lupa-min="56">
    <picture>
      <source media="(max-width: 980px)" type="image/avif"
              srcset="assets/img/capa-movel-900.avif?h=…" width="900" height="1452">
      <source media="(max-width: 980px)" srcset="assets/img/capa-movel.jpg?h=…" width="900" height="1452">
      <source type="image/avif" sizes="(max-aspect-ratio: 3/2) 150vh, 100vw"
              srcset="assets/img/capa-1200.avif?h=… 1200w, assets/img/capa-1800.avif?h=… 1800w">
      <img class="palco__base" src="assets/img/capa.jpg?h=…" width="1800" height="1200"
           fetchpriority="high" alt="(descreve a foto de verdade)">
    </picture>
    <span class="capa__veu" aria-hidden="true"></span>
    <!-- o evento dinâmico do cliente mora aqui dentro -->
  </figure>
  <div class="capa__env"><!-- etiqueta, h1, lead, botão, aviso do filtro, sinal de confiança --></div>
</section>
```

Empilhamento **sempre positivo**: foto 1 · véu 2 · efeito 4 · pontos 5 · cartões 6 · texto 7.

**A foto da capa é o que mais pesa no PageSpeed do celular:** AVIF por largura com JPEG de reserva, `fetchpriority="high"`, **nunca** `loading="lazy"`. O `sizes` vai **pela altura** quando a tela é mais estreita que a foto (ela cobre o palco pela altura e fica mais larga que a tela): foto de proporção L:A → `sizes="(max-aspect-ratio: L/A) (L÷A×100)vh, 100vw"`. Com `100vw` às cegas, o navegador baixa uma pequena demais. Recorte em retrato próprio para o celular e teto na maior largura (com `sizes` em 150–200vh, o celular chega a pedir ~5.000 px).

### As cinco medidas que fazem a capa

**1. A rampa da máscara — é ela que dissolve, não blur.**
```css
.capa--fundo .palco__base{
  object-fit: cover; object-position: var(--enquadre);   /* ex.: 62% 34% no desktop */
  mask-image: linear-gradient(to right,
    transparent 0%, transparent 44%, rgba(0,0,0,.28) 54%,
    rgba(0,0,0,.72) 63%, #000 72%); }
```
Fora da rampa a tela mostra a **cor de fundo da dobra**, não um borrão.

**2. O véu, em duas camadas.** Um degradê a 96° escurece a esquerda (onde o texto mora) e chega a zero na direita; outro, vertical, escurece topo e base para o menu e a barra fixa. O rosto nunca entra no escuro. O texto mede **≥ 4,5:1 contra o fundo real** (não contra a cor do token).
```css
.capa__veu{position:absolute;inset:0;background:
  linear-gradient(96deg, rgba(26,18,14,.93) 0%, rgba(26,18,14,.66) 40%,
                         rgba(26,18,14,.13) 70%, rgba(26,18,14,0) 100%)}
```

**3. O território do efeito dinâmico — `data-lupa-min`.** À esquerda do limite (a fronteira da coluna de texto, ex.: 56%) o cursor **não assume** o efeito; o passeio automático continua. Não é *clamp*: prender o efeito na fronteira faz ele estacionar em cima do título enquanto a pessoa lê.

**4. Âncoras em % da FOTO, nunca do palco.** `data-x`/`data-y` (e `data-x-mob`/`data-y-mob`) são % da imagem; uma função converte para px do palco no `load` e no `resize`. A foto é ~65% do palco em 1920 e ~87% em 1440 — % do palco acerta num monitor e erra no outro.

**5. O cabeçalho é herdado da página clara.** O gerador marca `<body class="fundo">` e o CSS clareia o que tem borda enquanto o cabeçalho não está compacto:
```css
body.fundo .topo:not(.compacto) .ico-link{
  color: rgba(250,247,242,.9); border-color: rgba(250,247,242,.42); }
```

### O celular é outra capa (e é onde tudo quebra)

| o que muda | valor | por quê |
|---|---|---|
| arquivo próprio, vertical | `<source media="(max-width:980px)">` | recorte de foto horizontal deixa o rosto colado na tela |
| máscara | `mask-image: none` | a dissolução lateral não faz sentido sem coluna de texto ao lado |
| véu | só começa a escurecer em **57%** da altura | escurecer antes faz a foto "terminar no queixo" |
| véu claro herdado (`.palco::after`) | `content: none` | na capa escura ele lava o pé e o texto claro some |
| texto | `justify-content: flex-end` | ancora na base; a pessoa fica inteira em cima |
| âncoras do efeito | todas **acima de ~38%** da foto | abaixo disso começa o texto e o efeito estaciona sobre ele |
| cartão/rótulo do efeito | `top: 13%; bottom: auto; left: var(--margem)` | não há espaço lateral |

**Onde pôr as âncoras no celular:** acima do texto e longe dos pousos ruins (**olho** e **boca**). Conferir medindo: centro da âncora + raio do efeito tem de ser **menor** que o topo da etiqueta da capa.

**Print de celular em modo headless mente.** `--window-size=390,844` renderiza num layout mais largo que o pedido e inventa bugs. Emular de verdade por CDP: `Emulation.setDeviceMetricsOverride {width:390, height:844, deviceScaleFactor:3, mobile:true}` → `Page.captureScreenshot`.

**Duas capas na mesma página (teste A/B)?** Gerar, não duplicar: o bloco da capa variante vive num arquivo próprio e o gerador troca só esse bloco, marca `<body class="fundo">` e reescreve `canonical`/`og:url`. A saída nunca se edita à mão.

### Checklist da capa
1. Foto **horizontal** no desktop e **vertical** no celular — nunca a mesma cortada.
2. Rampa da máscara cobrindo qualquer faixa inventada do arquivo.
3. Véu em duas camadas no desktop; vertical a partir de 57% no celular.
4. `data-lupa-min` (ou equivalente) na fronteira da coluna de texto.
5. Âncoras em % da foto, com par `-mob` medido.
6. `<body class="fundo">` para o cabeçalho.
7. Eixo único (§4b) medido em 1440/1920/390; folga do pé medida em 725 e 640.
8. Prints desktop + celular tirados com emulação real e guardados como referência.
9. Sinal de confiança verificável na capa (ou na faixa 2).

---

## 5. Botões e contato

**Pastilha lisa com canto.** `--raio: 14px` em todo botão; **pílula** (`border-radius: 999px`) nos controles do cabeçalho. **Sem sombra e sem gradiente**, maiúsculas com entreletra. (O que parecia "feito por IA" era sombra e degradê em tudo, não o canto; o canto de 2 px da primeira geração foi rejeitado como "muito quadrado".)

- **Um botão de contato em toda dobra**, cada um com o `data-origem` da dobra (`topo · capa · quem · tratamentos · avaliacoes · duvidas · onde · rodape · flutuante · barra`): a medição diz de onde partiu o clique.
- **Verde de contato + glifo do WhatsApp** em SVG (`<symbol id="ico-zap">` reusado por `<use>`): `--zap: #17754C` nos botões (família WhatsApp, sem néon); o **flutuante** usa o verde do app, `--zap-app: #5BC13B` — é o ícone que a pessoa reconhece. O glifo branco sobre esse verde mede 2,3:1 (a WCAG 1.4.11 pede 3:1 para componente gráfico): decisão consciente; mitigar com `drop-shadow` no `<svg>`.
- **O texto diz a ação da dobra:** "Agendar consulta" (padrão); no catálogo, "Falar sobre o meu caso"; no FAQ, "Minha dúvida não está aqui"; em "onde e quando", "Confirmar um horário".
- **Cabeçalho em pílulas de 42 px:** rede social num **círculo** (só o ícone), telefone numa pílula com o número (`tel:`) e **Agendar consulta** numa pílula verde. No celular o número some e fica o ícone — por isso o `aria-label` ("Ligar para (00) 00000-0000"), senão o link fica sem nome. Sem selo "somente particular" no topo: o filtro mora na capa, no passo 01, no FAQ e na barra do celular.
- **Desktop: flutuante = círculo verde do app**, 62 px, glifo de 32 px, rótulo "Agendar consulta" numa etiqueta branca que aparece no hover. **Celular: barra fixa** escura com "Atendimento somente particular" (ou o filtro do cliente) + botão verde. **Nunca os dois juntos.** Aparecem depois de **78% da capa** e somem sobre o rodapé — numa **conta só**, num `requestAnimationFrame` (dois observadores se contradizem).
- **O `href` real do `wa.me` fica escrito no HTML**, com a mensagem pré-preenchida; o JS só mede. Se o script morrer, a conversão continua.
- **Mensagem pré-preenchida sem doença nem procedimento** quando a URL do clique vai ao GA4/Ads: "Olá! Vim pelo site e gostaria de agendar uma consulta." (ou retirar a query no disparo da tag). A mensagem começa por **"Vim pelo site"** quando o receptor de mensagens usa esse marcador para gravar a origem.
- **Link de compartilhar não é contato.** Um `wa.me/?text=` sem número ("chamar quem vem comigo") não leva o atributo de medição de contato; mede-se `compartilhar` à parte. Com o atributo, cada convite a um amigo viraria conversão no Ads. Provar com gravador: zero `Contact`.
- **Regra de link de seção não pode pintar botão.** `.rodape a{color:…}` (especificidade 0,1,1) vence `.botao--zap` (0,1,0) e o botão reprova o contraste. Toda regra de link de seção leva `:not(.botao)`.

### Variante com perguntas antes do WhatsApp

Para qualificar o público (ex.: encomendas):
- Todo botão de contato ganha `data-form` e **mantém o `href` real**. O JS intercepta e abre um `<dialog>`; sem JS (ou sem `<dialog>`), o botão vai direto ao WhatsApp.
- **No máximo 4 perguntas, uma por tela, com barra de progresso.** Pergunta de uma resposta **avança sozinha** 260 ms depois do toque; a de várias pede "Continuar". Depois, nome, data e detalhe, todos **opcionais**.
- A tela final mostra o resumo e o botão é um **`<a>` de verdade** com a mensagem montada (`• Ocasião:` `• Quero:` `• Para quando:` `• Pessoas:`), começando por "Vim pelo site".
- O card do catálogo abre o formulário com o item já marcado (`data-item`).
- Resposta que pede atenção vira aviso na tela final e não barra ninguém.
- Medição: `form_abre`, `form_passo`, `form_envia` → `Lead`. **Abrir o formulário não é contato**: o ouvinte do GTM ignora `data-form`.
- `LEAD_WEBHOOK` nasce vazio; preenchido, as respostas também vão por `sendBeacon`.
- No celular (≤ 640 px) o diálogo vira **folha que sobe do pé da tela**.

### Código de referência

```css
:root{ --zap:#17754C; --zap-forte:#115C3C; --zap-app:#5BC13B; --zap-app-forte:#4BA82F; --raio:14px }
.botao{ display:inline-flex; align-items:center; gap:.55rem; font-size:.78rem; font-weight:600;
        letter-spacing:.11em; text-transform:uppercase; text-decoration:none; padding:.82rem 1.35rem;
        border:0; border-radius:var(--raio); cursor:pointer; transition:background .25s ease, transform .25s ease }
.botao--zap{ background:var(--zap); color:#fff }
.botao--zap:hover{ background:var(--zap-forte); transform:translateY(-1px) }
.botao--g{ font-size:.84rem; padding:1.02rem 1.7rem }                     /* capa e barra do celular */
.ico-link{ display:inline-flex; align-items:center; gap:.5rem; height:42px; padding:0 1.05rem;
           border:1px solid var(--fio-forte); border-radius:999px; text-decoration:none }
.ico-link:not(.ico-link--texto){ width:42px; padding:0; justify-content:center }   /* só ícone = círculo */
.topo .botao{ border-radius:999px; height:42px; padding:0 1.3rem }
.flutuante{ position:fixed; right:1.4rem; bottom:1.4rem; z-index:45; width:62px; height:62px;
            display:inline-flex; align-items:center; justify-content:center; border-radius:50%;
            background:var(--zap-app); color:#fff; box-shadow:0 12px 26px -12px rgba(0,0,0,.5);
            opacity:0; visibility:hidden; transform:translateY(14px);
            transition:opacity .35s ease, transform .35s ease, visibility .35s }
.flutuante.visivel{ opacity:1; visibility:visible; transform:none }
.flutuante__rot{ position:absolute; right:calc(100% + .7rem); top:50%; transform:translate(6px,-50%);
                 white-space:nowrap; background:#fff; color:var(--tinta); font-size:.7rem; font-weight:600;
                 letter-spacing:.08em; text-transform:uppercase; padding:.5rem .8rem; border-radius:10px;
                 opacity:0; pointer-events:none; transition:opacity .25s, transform .25s }
.flutuante:hover .flutuante__rot{ opacity:1; transform:translate(0,-50%) }
.rodape a:not(.botao){ color:var(--claro) }
.barra{ display:none }
@media (max-width:900px){
  .topo__dir .botao, .ico-link--texto span{ display:none }     /* a barra fixa assume o CTA */
  .flutuante{ display:none }                                   /* nunca os dois */
  .barra{ position:fixed; inset:auto 0 0; z-index:45; display:flex; align-items:center; gap:.7rem;
          padding:.6rem var(--margem) calc(.6rem + env(safe-area-inset-bottom));
          background:rgba(10,24,38,.97); backdrop-filter:blur(8px);
          transform:translateY(100%); transition:transform .35s ease }
  .barra.visivel{ transform:none }
  html{ scroll-padding-bottom: 4.6rem }                        /* = altura da barra (WCAG 2.4.11) */
}
```

```html
<a class="flutuante" id="flutuante" href="{{ZAP}}" data-origem="flutuante" target="_blank" rel="noopener"
   aria-label="Agendar consulta pelo WhatsApp">
  <svg width="32" height="32" aria-hidden="true"><use href="#ico-zap"></use></svg>
  <span class="flutuante__rot">Agendar consulta</span></a>
<div class="barra" id="barra">
  <span class="barra__nota">Atendimento somente particular</span>
  <a class="botao botao--zap botao--g" href="{{ZAP}}" data-origem="barra" target="_blank" rel="noopener">
    <svg width="20" height="20" aria-hidden="true"><use href="#ico-zap"></use></svg>Agendar consulta</a>
</div>
<!-- o botão de pausa vem DEPOIS da .barra (ver 06-componentes.md) -->
```

---

## 6. A ordem das dobras — o esqueleto universal

**A ordem não é gosto, é funil.** Ela responde, nesta sequência, as perguntas que a pessoa faz de cima para baixo: *quem é você → posso confiar → você resolve o MEU problema → como eu entro → como é o lugar → outros foram bem → e as minhas dúvidas → onde fica.* Trocar duas dobras troca a ordem das perguntas.

| # | Dobra | Responde | Por que está aqui | Animação (§6e) |
|---|---|---|---|---|
| 1 | **Capa** | quem é e o que faz | a única dobra que todo mundo vê; carrega o evento dinâmico, o CTA e um sinal de confiança | título acende palavra por palavra no carregamento + o evento do cliente |
| 2 | **Números** | posso confiar? | prova objetiva logo depois da promessa | faixa desfila em laço; números contam |
| 3 | **Quem é** | quem me atende | autoridade com rosto | título acende com a rolagem |
| 4 | **Catálogo** | você resolve o MEU problema? | a pergunta mais forte; vem **antes** de qualquer regra | cards entram em sequência, foto assenta, sinal se desenha |
| 4b | **Corpo clínico** (só clínica com mais de um profissional) | quem me atende | primeiro o que a clínica trata, depois quem atende | cartões em sequência |
| 5 | **Como funciona** | como eu entro | expectativa + o filtro (convênio, regra de entrada) | linha do tempo se enche com a rolagem |
| 6 | **O espaço** | como é o lugar | tira o medo do ambiente; respiro entre blocos de texto | fotos respiram, ou faixa em laço contínuo sem setas |
| 7 | **Avaliações do Google** | outros foram bem? | prova social **depois** de a pessoa já querer | carrossel anda a cada 5 s, para ao toque |
| 8 | **Perguntas frequentes** | e a minha dúvida? | tira o último obstáculo antes do contato | título acende; acordeão nativo |
| 9 | **Onde e quando** | onde fica, quando abre | endereço, horários, mapa | título acende; mapa entra perto da dobra |
| 10 | **Rodapé + flutuantes** | identificação legal | registro profissional, aviso, privacidade, acessibilidade; o CTA que não sai da tela | flutuante entra depois da capa |

**Dobra que o cliente não tem por natureza, sai** (ex.: corpo clínico de profissional individual; avaliações e espaço em advocacia) — não se inventa conteúdo para preencher posição. **Dobra que falta só por insumo, não sai**: use a alternativa deste documento ou pergunte (ver [padrão](01-padrao.md)).

**O catálogo vem antes da regra de entrada.** A ordem original tinha "Como funciona" acima do catálogo, e o erro era de argumentação: ali mora o filtro ("não atendemos convênio"), que **barrava a pessoa antes de ela saber o que a profissional resolve**. Com o catálogo antes, a sequência vira *isto é o que resolvo para você → e é assim que se entra*; quem chega no filtro já quer. **Regra geral: toda restrição — convênio, público atendido, tempo de espera, modo de pagamento — mora depois do catálogo.**

---

## 6a. O mínimo de cada dobra

**0 · Cabeçalho.** Logo (SVG com `fill="currentColor"`, para clarear sobre a capa), pílulas de 42 px (§5). Vira **compacto** depois de 40 px de rolagem (fundo claro a 94% + `blur`, logo menor).

**1 · Capa.** §4c. Foto em tela cheia (ou caixa recuada à direita, §0), texto na metade esquerda, evento dinâmico próprio do cliente, CTA, a linha que filtra e um sinal de confiança verificável. Eixo único (§4b). Cabe em 725 e 640 px (§3).

**2 · Números.** Faixa **clara** logo depois da capa escura (duas dobras escuras seguidas pesam). **5 a 8 itens, cada um do tamanho do próprio conteúdo**, separados por fio vertical — nunca item de largura fixa (sobra um vão enorme no desktop). Números **contam** ao entrar; palavra ("Online") entra como palavra. Desfila em laço a velocidade constante e pausa no hover do desktop e no botão de pausa. **O HTML nasce com o valor final** (sem JS, nunca "0"). **Sem linha de fonte na tela** — a regra não afrouxou: número que a fonte não confirma não entra; a fonte fica ao lado de cada item no gerador e no `LEIA-ME.md`. Nada de "destaque que gira" sem implementação (classe CSS sem ninguém para aplicá-la é código morto).

**3 · Quem é.** Foto **apoiada numa faixa de cor**, nunca flutuando no branco; selo curto ("Desde 20XX", só com fonte); formação em lista; **registro profissional junto do nome**; um CTA. É a dobra da pessoa, não da empresa. Na página de uma **instituição**, a dobra 3 é a da casa (foto da equipe e os motivos para escolher a clínica).

**4 · Catálogo.** Cards com a foto do tratamento de fundo, em **grupos de 3 completos**, cada grupo com título; fecha com CTA próprio ("Falar sobre o meu caso"). Padrão inteiro em §6c.

**4b · Corpo clínico.** Só quando a página é da clínica e ela tem mais de um profissional; vem **depois do catálogo** (primeiro o que a clínica trata, depois quem atende). Cartões 4:5 com foto, nome, cargo, área (só com fonte) e registro (CRM/RQE). **Profissional sem foto vira vaga marcada** (borda tracejada, silhueta desenhada, "CRM e RQE a confirmar"), nunca foto de banco de jaleco, que fingiria ser alguém da casa. Profissional sem registro confirmado fica fora do JSON-LD. Na página da clínica, os cards do catálogo também ficam **sem o rosto** de qualquer profissional: o aparelho ou objeto do tratamento.

**Instituição e profissional no mesmo site.** As duas páginas saem do **mesmo gerador**: um dicionário com o que muda (assinatura, "quem é", foto, motivos, OG, perfil do JSON-LD) e a variante do profissional sobrescrevendo. Catálogo, espaço, avaliações, FAQ e rodapé num código só. **Eixo de cada uma pela busca real** ("clínica de olhos" × "oftalmologista"), para não disputarem o mesmo termo.

**5 · Como funciona.** **Linha do tempo que se enche com a rolagem:** fundo escuro, cabeça fixa à esquerda (`sticky`), passos numerados (`01`, `02`…) à direita, um fio vertical que enche até uma linha a **60% da tela**; passo alcançado acende e fica aceso; o mais recente é o *atual* (número maior, com halo). **Passo 01 é o filtro**, escrito pelo eixo da personalização ([copy](04-copy.md)). A frase do filtro vive em **três lugares** — este passo, o FAQ visível e o `FAQPage` — e sai de **uma constante só**.

**6 · O espaço.** Carrossel horizontal com `scroll-snap-type: x proximity` (nunca `mandatory`: cancela a rolagem programada das setas), setas, marcadores e legenda que **descreve o que a foto mostra** (nunca "Foto 1"). Cada foto respira (zoom lento, duração e atraso diferentes por foto). Alternativa aprovada: faixa em laço contínuo, fotos menores e encostadas, sem setas. Enquanto as fotos reais não chegam, marcadores tracejados — nunca foto de banco fingindo ser o lugar. **Em advocacia, esta dobra sai.**

**7 · Avaliações.** §6b. Obrigatória — menos em advocacia.

**8 · Perguntas frequentes.** `<details>` com `<h3>` dentro do `<summary>`, **6 a 8 perguntas reais** (as que o atendimento responde o dia inteiro), deduplicadas, **as mesmas** do `FAQPage`. Resposta na primeira frase. CTA "Minha dúvida não está aqui". Inclui a pergunta do valor, respondida com "informado pelo WhatsApp antes do agendamento". O `FAQPage` deixou de gerar resultado enriquecido no Google, mas fica pela conversão e porque as IAs leem.

**9 · Onde e quando.** Endereço em `<address>`, horários em `<dl>`, mapa por proximidade (§6d).

**10 · Rodapé + flutuantes.** Nome completo, registro profissional (CRM + RQE quando médico; OAB quando advogado), endereço, telefone, redes, "esta página não substitui consulta" (saúde), revisor visível, **"Página atualizada em `<time datetime="AAAA-MM-DD">`"** (o mesmo dia do `dateModified`), link **Privacidade**, **símbolo de acessibilidade em destaque**. Flutuante no desktop, barra no celular, nunca os dois.

---

## 6b. A dobra de avaliações do Google

Padrão em toda página (menos advocacia: avaliação de cliente é o depoimento que os tribunais de ética da OAB tratam como captação; o Perfil pode ser linkado junto do endereço). Componente completo, serviço central e prompt de implementação em [componentes](06-componentes.md).

**O que a dobra mostra**
1. **Nota e contagem em destaque** ("5,0 · em 36 avaliações no Google") + estrelas em SVG. Vêm **sempre da API**, são fato e não têm curadoria.
2. **Botão de contato** como ação principal; "Ler as avaliações no Google" como link secundário em texto (ele tira gente da página) — mas sempre presente.
3. **Carrossel de cartões**: foto da pessoa (38 px, redonda), nome, estrelas (`role="img"` + `aria-label`), **"há x dias/meses" calculado da data** (nunca congelado no HTML), texto com corte de 6 linhas, link "Ver no Google".
4. **Barra fina de posição**, não bolinhas (28 cartões = 28 bolinhas de ruído).
5. Atribuição: "Avaliações publicadas por pacientes no perfil … · Fornecido pelo Google" — exigência dos termos da Places API.

**Carrossel:** anda sozinho a cada **5 s**, para **9 s** ao toque, para fora da tela, com movimento reduzido e no botão de pausa. Anda por **índice** (somar ao `scrollLeft` sobre rolagem suave dá passos desiguais).

**Atualização em minutos:** o serviço central lê a API do Perfil da Empresa (cache de 5 min) para os perfis que a agência gerencia; nos demais, a Places API.

**Busca pelo lugar, não pelo nome:** `?lugar=<place_id>`. Numa franquia, a busca por nome puxou outra unidade. Sem Perfil próprio, usar o Perfil do grupo/matriz pelo `?lugar=`, com a atribuição dizendo de qual unidade é.

**Recência pesa:** a maioria procura avaliações dos últimos 3 meses; por isso a ordem é da mais recente para a mais antiga e a data é calculada.

**Nunca `aggregateRating` no JSON-LD.**

---

## 6c. Os cards de catálogo — a dobra "o que trata"

**O card é a FOTO do tratamento, escura, entrando em sequência.** Três decisões fecharam o padrão: card escuro com foto de fundo (card sem diferenciação da dobra "não fica legal"); cards animados com imagem ligada ao assunto; e **a foto conecta com o TRATAMENTO, não com quem sofre** (um idoso num banco de praça no card de próstata "não conectou").

**Anatomia, de cima para baixo:** sinal em linha no canto (42×42, borda de 1 px, canto de 12 px, fundo translúcido com `blur(3px)`) · foto de fundo · véu subindo **só da base** · título serifado · duas frases · fio de 1 px · tags em caixa-alta miúda.

### A estrutura
- **Grupos de 3, completos**, cada um com um `grupo-titulo` acima (caixa-alta miúda, entreletra larga, fio de 1 px embaixo). Com 14 cards, completa-se com um tratamento **real** do cliente — nunca enchimento.
- **A ordem dos grupos segue a procura do paciente**, do mais buscado ao mais específico (ex. numa página de urologia, 15 cards em 5 grupos: Próstata · Cirurgia · Saúde sexual · Hormônios e fertilidade · Rins, bexiga e vias urinárias).
- **Grade:** 3 colunas no desktop → 2 no tablet (≤ 980 px) → 1 no celular (≤ 640 px). Card **4:5 no desktop e 5:4 no celular**, texto sempre na base. **Card com linha de CTA fica 4:5 também no celular** (em 5:4 o texto cobria ~90% da foto e caía sobre a parte clara, sem contraste).
- A dobra fecha com **um CTA da própria dobra**.

### O texto do card
- **Título** = o nome que o paciente busca ("Cálculo renal"), não o jargão.
- **Duas frases:** o que é ou o que se faz, e a conduta. Sem promessa, sem superlativo, sem termo popular.
- **Tags:** 2 ou 3 termos de busca **numa linha só** (tag que quebra desalinha a fileira).
- Tratamento que **não aparece em nenhuma fonte do cliente** entra sem citar lugar e vai para as pendências até ele confirmar.

### A foto — regras que não são estéticas
1. **Conecta com o tratamento do card:** o exame, a consulta, o procedimento, o aparelho.
2. **Nunca** o próprio profissional ilustrando uma condição, **nunca** região íntima, **nunca o rosto de outro profissional** (na página dele, quem vê lê que é ele).
3. **Planos diferentes** entre os cards — médio, aberto, detalhe. Planos parecidos viram "a mesma cena seis vezes".
4. **Recorte 4:5 com o assunto a 25–40% da altura:** o véu cobre a metade de baixo e, no celular (5:4), o card mostra só a faixa de 18% a 82% da foto. Conferir numa prancha 4:5 + 5:4 **com o véu**.
5. **Três larguras** — 400 (colunas do desktop), 660 (celular), 800 (retina) — com `srcset` + `sizes`. Com uma só, de 800, o desktop baixava o dobro do que mostra.
6. **O `alt` descreve a foto de verdade**, escrito **depois** de escolhê-la.
7. **De onde vem:** banco de licença livre sem atribuição obrigatória (ex.: Pexels). Folha de candidatas → escolher olhando → recorte e prancha por script.
8. **Negócio de produto: a foto é só do próprio cliente.** Na clínica a foto ilustra um tratamento; na confeitaria a foto **é a promessa**, e bolo de banco anuncia o que a casa não faz. Fontes: o feed do Instagram do cliente pela Graph API (com autorização) e as imagens da biblioteca de anúncios da conta (até 2048 px). O card inteiro é clicável e abre o formulário (§5) com o produto marcado.

**Especialidade sensível:** card **sem foto** (§4), só sinal desenhado, título, texto e tags sobre fundo escuro.

### Código de referência

```python
# gerar.py — GRUPOS = [(grupo, [(título, ícone, texto, tags), …]), …]; FOTOS_CARDS = {ícone: alt}
def bloco_cards():
    out = []
    for gi, (grupo, itens) in enumerate(GRUPOS):
        out.append(f'<h3 class="grupo-titulo">{grupo}</h3>')
        out.append(f'<ul class="cards cards--foto cards--t{gi % 2}">')
        for ci, (titulo, ico, texto, tags) in enumerate(itens):
            # pathLength="1" em cada traço: o CSS "desenha" o sinal com a mesma duração em qualquer traço
            traco = re.sub(r"<(path|circle|line|polyline|polygon|rect|ellipse)\b", r'<\1 pathLength="1"', ICONES[ico])
            out.append(
                f'<li style="--d:{ci}">'
                f'<img class="cards__foto" src="../assets/img/card-{ico}.webp" '
                f'srcset="../assets/img/card-{ico}-400.webp 400w, ../assets/img/card-{ico}-660.webp 660w, '
                f'../assets/img/card-{ico}.webp 800w" sizes="(max-width: 640px) 92vw, (max-width: 980px) 45vw, 400px" '
                f'width="800" height="1000" loading="lazy" decoding="async" alt="{e(FOTOS_CARDS[ico])}">'
                f'<span class="cards__ico" aria-hidden="true"><svg viewBox="0 0 24 24">{traco}</svg></span>'
                f'<div class="cards__corpo"><h4>{titulo}</h4><p>{texto}</p><p class="cards__tags">{tags}</p></div></li>')
        out.append('</ul>')
    return "".join(out)
```

Os ícones são desenhados à mão num dicionário `ICONES` (24×24, `fill: none`, `stroke-width: 1.25`), **abstratos de propósito** — especialidades como urologia e proctologia não comportam desenho anatômico numa peça aberta.

```css
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:1.05rem;list-style:none;margin:0 0 2.9rem}
.cards li{position:relative;isolation:isolate;overflow:hidden;display:flex;flex-direction:column;
          justify-content:flex-end;color:#E7F0F8}
.cards--foto li{padding:1.35rem;aspect-ratio:4/5;border-radius:var(--raio);background:var(--profundo)}
.cards--foto li::after{content:"";position:absolute;inset:0;z-index:-1;          /* o véu sobe SÓ da base */
  background:linear-gradient(to top, rgba(8,18,30,.97) 0%, rgba(8,18,30,.9) 30%,
    rgba(8,18,30,.55) 52%, rgba(8,18,30,.12) 74%, rgba(8,18,30,0) 90%)}
.cards__foto{position:absolute;inset:0;z-index:-2;width:100%;height:100%;object-fit:cover;
  transform:scale(1.02);transition:transform 1.4s cubic-bezier(.2,.7,.2,1)}
.cards--foto li:hover .cards__foto{transform:scale(1.07)}                        /* scale SÓ na foto */
.cards__ico{position:absolute;top:1.2rem;left:1.35rem;width:42px;height:42px;display:grid;place-items:center;
            border:1px solid rgba(186,227,248,.42);background:rgba(8,18,30,.45);backdrop-filter:blur(3px);border-radius:12px}
.cards__ico svg{width:24px;height:24px;fill:none;stroke:var(--claro);stroke-width:1.25;stroke-linecap:round}
.cards__ico svg *{stroke-dasharray:1;stroke-dashoffset:0}
.cards--foto .cards__corpo{margin-top:auto}
/* entrada (só com JS: .vivo / .dentro) — ver §6e */
.tratamentos.vivo .cards li{opacity:0;transform:translateY(34px);
  transition:opacity .8s ease, transform .9s cubic-bezier(.2,.7,.2,1);transition-delay:calc(var(--d,0) * 110ms)}
.tratamentos.vivo .cards li .cards__foto{transform:scale(1.16)}
.tratamentos.vivo .cards li .cards__ico svg *{stroke-dashoffset:1;transition:stroke-dashoffset 1.3s ease .35s}
.tratamentos.vivo .cards li.dentro{opacity:1;transform:none}
.tratamentos.vivo .cards li.dentro .cards__foto{transform:scale(1.02)}
.tratamentos.vivo .cards li.dentro .cards__ico svg *{stroke-dashoffset:0}
@media (max-width:980px){ .cards{grid-template-columns:repeat(2,1fr)} }
@media (max-width:900px){ .cards--foto li{aspect-ratio:5/4} }
@media (max-width:640px){ .cards{grid-template-columns:1fr} }
@media (prefers-reduced-motion: reduce){ .tratamentos.vivo .cards li{opacity:1;transform:none;transition:none} }
```

---

## 6d. O mapa e o Perfil da Empresa no Google

### O mapa entra tarde, e por conta própria
O `<iframe>` do Google pesa e abre conexão de terceiro: **não vai no HTML**. Fica um `data-mapa` no contêiner e o JS injeta o iframe quando a pessoa chega perto.

```html
<div class="mapa" id="mapa"
     data-mapa="https://www.google.com/maps?q=<nome do Perfil + endereço, urlencoded>&amp;output=embed">
  <div class="mapa__vazio" id="mapa-vazio">
    <span class="mapa__pino"></span>
    <b>Edifício Exemplo · Torre 1</b>
    <span>Av. Exemplo, 000 — Bairro, Cidade</span>
  </div>
  <a class="mapa__abrir" target="_blank" rel="noopener" data-ir="mapa"
     href="https://www.google.com/maps/dir/?api=1&destination=<endereço>">Traçar rota no Google Maps</a>
</div>
```

- `?q=…&output=embed` dispensa chave de API. A busca é **o nome do Perfil + o endereço do Perfil**: o alfinete sai com o nome. Plus Code só se a busca comprovadamente não achar (ele tira o nome do alfinete).
- **O cartão de endereço fica no HTML por baixo** e continua legível se o iframe não carregar. O endereço nunca depende do Google.
- `/maps/dir/?api=1&destination=…` abre a rota no app do celular — o link que mais converte da dobra, medido (`data-ir="mapa"`).
- Injetar com `IntersectionObserver` de `rootMargin: '600px 0px'` (até 900) **mais rede de segurança pela rolagem** (a cada rolagem, se o mapa está a menos da margem, monta), porque o observador pode não entregar. **Nunca por tempo**: `setTimeout(montar, 2500)` pós-load puxa o iframe para dentro do PageSpeed de quem nem rolou.
- `insertBefore` do iframe **antes** do link de rota (`appendChild` joga o mapa para baixo do botão).
- O placeholder só some no `load` do iframe — nunca há buraco branco.
- No iframe: `loading="lazy"`, `title` descritivo, `referrerPolicy="no-referrer-when-downgrade"`.
- **Print automatizado não prova mapa quebrado**: na página inteira o iframe do Google às vezes não termina de desenhar. Testar a URL num iframe isolado do tamanho do cartão, com 15 s de espera, e confirmar no aparelho.

### O que fica no site × no Perfil
| dado | mora onde | por quê |
|---|---|---|
| endereço, telefone, nome, especialidade | **site** (`<address>` + JSON-LD) e Perfil, **idênticos** | é identificação, e o Google lê |
| avaliações e nota | **Perfil**, puxadas por API | não se copia avaliação para o HTML como se fosse do site |
| horário de funcionamento | **Perfil** (no site, só se exato) | ver abaixo |
| fotos do lugar | os dois, **as mesmas** | foto diferente confunde quem compara |

**`openingHoursSpecification` só se o horário for exato.** Se o briefing diz "à noite" para três dias, declarar só os dias com horário exato faz o Google entender que **fecha** nos outros — pior que não declarar. Ir ao ar sem, de propósito, com comentário no HTML. Quem responde horário na busca local é o Perfil, e é lá que se corrige.

**O Perfil é dono da prova social; a página é inquilina.** Melhorar a nota é trabalho no Perfil. O `?lugar=` precisa apontar para o Perfil real. Resposta do dono a uma avaliação não é avaliação.

---

## 6e. As animações de cada dobra

**Uma animação por dobra, e ela realça o que a dobra já diz** — o número conta, o passo acende, a foto do tratamento assenta. Nada de efeito genérico repetido em tudo, e nada que dispute com o evento dinâmico da capa.

### As regras — valem para todas
1. **Estado base legível.** Sem JS, com `prefers-reduced-motion` ou com o script morto, tudo aparece parado e inteiro. A classe que apaga (`.vivo`) quem põe é o JS.
2. **Só `opacity` e `transform`** (o compositor anima sem redesenhar). Exceção: o traço do ícone do card (`stroke-dashoffset`), pequeno e uma vez só.
3. **Rolagem: CSS primeiro.** Manchetes, linha do tempo e entrada de cartões por `animation-timeline: view()` dentro de `@supports (animation-timeline: view()) { @media (prefers-reduced-motion: no-preference) {…} }` — nativo nos navegadores atuais de desktop e celular; fora disso, **estado final**. JS de rolagem só quando o efeito carrega informação, e então **um `requestAnimationFrame` por evento**, nunca `IntersectionObserver` sozinho (pode não entregar e a seção fica invisível), com **todas as leituras antes de todas as escritas**.
4. **O que APAGA texto só se arma na 1ª rolagem.** Antes dela, quem não rola — leitor de tela, robô, PageSpeed — lê tudo com contraste cheio; ao armar, o que já está na tela fica aceso de vez. (Texto a 16% antes de rolar reprovou contraste em dezenas de elementos.)
5. **Medida de inicialização só depois do quadro:** `requestAnimationFrame(() => setTimeout(fn, 0))`. Ler no meio do script força o layout inteiro (tarefa longa no celular).
6. **Começa em 0,16, nunca em 0** (manchetes); `animation-fill-mode: backwards`, nunca `both` (o último quadro-chave venceria o estilo do JS).
7. **Tudo o que se move sozinho por mais de 5 s** (evento da capa, letreiro, carrossel, fotos que respiram, vídeo em laço) **tem botão visível de pausa** ou para em ≤ 5 s (WCAG 2.2.2, nível A). Pausar no hover ou no foco **não** conta como mecanismo, e `prefers-reduced-motion` não é técnica suficiente. Laço infinito também pausa **fora da tela**. Receita do botão em [componentes](06-componentes.md). Ouvir o `change` do `prefers-reduced-motion`.
8. **Efeito de rolagem se aprova medindo**, não por print: intervalo entre quadros e tarefas longas (meta: 60 fps, 0 tarefas longas).
9. `sibling-index()` para o escalonamento, com `--i` de reserva; `@starting-style` nas entradas; `text-wrap: balance` em `h1`/`h2`. Manchete animada só na capa e em 1–2 dobras.

### O mapa, dobra por dobra
| dobra | a animação | gatilho |
|---|---|---|
| todas (até 2) | `h2` acende palavra por palavra conforme sobe, de 92% a 50% da tela | rolagem (armada na 1ª) |
| 0 · Cabeçalho | vira compacto — fundo claro a 94% + `blur`, logo menor | rolagem > 40 px |
| 1 · Capa | título acende palavra por palavra (0,8 s cada, 110 ms entre elas, total ≤ 1 s de percepção) + evento dinâmico | carregamento |
| 2 · Números | faixa desfila em laço (**38 px/s**, constante); números contam de 0 ao valor (1,4 s, cúbica) — o HTML já tem o valor final | sempre / ao entrar |
| 3 · Quem é | título acende | rolagem |
| 4 · Catálogo | cards sobem 34 px em sequência (110 ms entre eles), foto assenta (1,16 → 1,02), sinal se desenha | card a 90% da tela |
| 5 · Como funciona | linha do tempo se enche até 60% da tela; passo alcançado acende; o atual ganha halo | rolagem (armada na 1ª) |
| 6 · O espaço | cada foto respira (1,005 → 1,08, de 21 a 30 s, atrasos diferentes) | sempre (pausa fora da tela e no botão) |
| 7 · Avaliações | carrossel anda a cada 5 s, para 9 s ao toque; barra de posição acompanha | com a dobra na tela |
| 8 · Perguntas | título acende; `<details>` nativo | rolagem |
| 9 · Onde e quando | título acende; mapa entra perto | rolagem |
| 10 · Flutuantes | círculo verde aparece depois de 78% da capa; some sobre o rodapé | rolagem |

### Código de referência

Tudo num `pagina.js` com `defer`, dentro de um `(function(){ … })()`, com `var reduzido = matchMedia('(prefers-reduced-motion: reduce)').matches` no topo e:

```js
function depoisDoQuadro(fn) { requestAnimationFrame(function () { setTimeout(fn, 0); }); }
```

**Título da capa** (o padrão vigente prefere não quebrar texto em `<span>` por JS na carga; se o gerador já emitir os `<span class="pl" style="--i:n">`, o CSS basta):
```css
.pl{display:inline-block}
.capa h1 .pl{animation:pl-entra .8s cubic-bezier(.2,.7,.2,1) backwards;
             animation-delay:calc(var(--i) * 110ms + 120ms)}
@keyframes pl-entra{from{opacity:.16;transform:translateY(.32em)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion: reduce){ .capa h1 .pl{animation:none} }
```

**Faixa de números** — a lista sai **duplicada** do gerador (a cópia com `aria-hidden="true"`, `inert` e **sem** `data-conta`, senão conta duas vezes). Duas condições para o laço fechar sem salto: a **metade** do trilho cobre a vitrine e o trilho é feito de duas metades iguais; anima-se `translateX(0 → -50%)`.
```css
.numeros__vitrine{overflow:hidden;mask-image:linear-gradient(to right,transparent 0,#000 6%,#000 94%,transparent 100%)}
.numeros__lista{display:flex;list-style:none;width:max-content;animation:desliza var(--dur,60s) linear infinite}
.numeros__lista li{flex:0 0 auto;padding:0 clamp(1.8rem,3.4vw,3.2rem);border-left:1px solid var(--fio);text-align:center}
.numeros__vitrine:hover .numeros__lista{animation-play-state:paused}
@keyframes desliza{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media (prefers-reduced-motion: reduce){ .numeros__lista{animation:none} }
```
```js
var trilho = document.querySelector('.numeros__lista');
if (trilho && !reduzido) {
  var montaFaixa = function () {                  // repete as cópias até cobrir; velocidade CONSTANTE de 38 px/s
    var itens = [].slice.call(trilho.children), k = itens.length / 2, metade = 0;
    for (var i = 0; i < k; i++) metade += itens[i].getBoundingClientRect().width;
    var vit = trilho.parentNode.getBoundingClientRect().width;
    if (metade && metade < vit * 1.05) {
      var copias = itens.slice(k), vezes = Math.ceil((vit * 1.05) / metade) - 1;
      for (var v = 0; v < vezes; v++) {
        copias.forEach(function (c) { trilho.insertBefore(c.cloneNode(true), itens[k]); });
        copias.forEach(function (c) { trilho.appendChild(c.cloneNode(true)); });
      }
      metade *= (vezes + 1);
    }
    if (metade) trilho.style.setProperty('--dur', Math.max(24, metade / 38).toFixed(1) + 's');
  };
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { depoisDoQuadro(montaFaixa); });
  else depoisDoQuadro(montaFaixa);
}
function contar(el) {                              // 0 → valor em 1,4 s, cúbica, vírgula decimal
  var alvo = el.getAttribute('data-conta'), num = parseFloat(alvo.replace(',', '.'));
  if (isNaN(num) || reduzido) { el.textContent = alvo; return; }
  var casas = alvo.indexOf(',') > -1 ? 1 : 0, t0 = performance.now();
  (function passo(t) {
    var p = Math.max(0, Math.min(1, (t - t0) / 1400)), v = num * (1 - Math.pow(1 - p, 3));
    el.textContent = casas ? v.toFixed(1).replace('.', ',') : Math.round(v).toLocaleString('pt-BR');
    if (p < 1) requestAnimationFrame(passo); else el.textContent = alvo;
  })(t0);
}
// dispara quando 40% do número entra na tela; rede de segurança aos 3,2 s compara com o VALOR FINAL
// (se o rAF morrer no meio, "2" não fica onde era "20")
```

**Cards do catálogo** — mede antes de pôr o `.vivo` e marca na mesma passada o que já está na tela (nenhum card visível pisca apagado):
```js
var sec = document.querySelector('.tratamentos'), lis = [].slice.call(document.querySelectorAll('.tratamentos .cards li'));
if (sec && lis.length && !reduzido) {
  var checa = function () {
    var vh = window.innerHeight;
    var tops = lis.map(function (li) { return li.classList.contains('dentro') ? null : li.getBoundingClientRect().top; });
    lis.forEach(function (li, k) { if (tops[k] !== null && tops[k] < vh * 0.9) li.classList.add('dentro'); });
  };
  depoisDoQuadro(function () {
    var vh = window.innerHeight, tops = lis.map(function (li) { return li.getBoundingClientRect().top; });
    sec.classList.add('vivo');
    lis.forEach(function (li, k) { if (tops[k] < vh * 0.9) li.classList.add('dentro'); });
    window.addEventListener('scroll', checa, { passive: true });
    window.addEventListener('resize', checa);
  });
}
```

**Linha do tempo do "Como funciona"** (quando não houver `animation-timeline`):
```css
.passos{list-style:none;counter-reset:p;position:relative}
.passos::before,.passos::after{content:"";position:absolute;left:1.02rem;top:2.1rem;bottom:2.1rem;width:2px;border-radius:2px}
.passos::before{background:rgba(186,227,248,.16)}                                   /* o trilho */
.passos::after{background:linear-gradient(to bottom,var(--claro),var(--ciano));      /* o fio que enche */
  transform-origin:top center;transform:scaleY(var(--prog,1))}
.passos li{counter-increment:p;position:relative;display:grid;grid-template-columns:3.1rem 1fr;gap:.6rem;
           padding:1.25rem 0;border-bottom:1px solid rgba(186,227,248,.2)}
.passos li::before{content:counter(p,decimal-leading-zero);width:2.15rem;height:2.15rem;border-radius:50%;
  display:grid;place-items:center;font-size:.68rem;font-weight:600;color:var(--claro);background:var(--profundo);
  border:1px solid rgba(186,227,248,.38);transition:background .45s, color .45s, transform .45s cubic-bezier(.2,.7,.2,1)}
.passos.vivo li{opacity:.4;transform:translateY(8px);transition:opacity .5s ease, transform .6s cubic-bezier(.2,.7,.2,1)}
.passos.vivo li.passou{opacity:1;transform:none}
.passos.vivo li.passou::before{background:var(--claro);color:var(--profundo);border-color:var(--claro)}
.passos.vivo li.atual::before{transform:scale(1.14);box-shadow:0 0 0 6px rgba(186,227,248,.12)}
@media (prefers-reduced-motion: reduce){ .passos.vivo li{opacity:1;transform:none;transition:none} }
```
```js
var lista = document.querySelector('.passos'), passos = lista ? [].slice.call(lista.children) : [];
if (passos.length && !reduzido) {
  var pendP = false, armouP = false;
  var pintaPassos = function () {                 // a régua é uma linha a 60% da altura da tela
    pendP = false;
    var vh = window.innerHeight, r = lista.getBoundingClientRect(), linha = vh * 0.6;
    var tops = passos.map(function (li) { return li.getBoundingClientRect().top; });   // lê tudo antes de escrever
    lista.style.setProperty('--prog', Math.max(0, Math.min(1, (linha - r.top) / r.height)).toFixed(4));
    var atual = -1;
    passos.forEach(function (li, i) { var passou = tops[i] < linha; li.classList.toggle('passou', passou); if (passou) atual = i; });
    passos.forEach(function (li, i) { li.classList.toggle('atual', i === atual); });
  };
  var pedeP = function () {
    if (!armouP) { armouP = true; lista.classList.add('vivo'); }       // o .vivo entra na 1ª rolagem
    if (!pendP) { pendP = true; requestAnimationFrame(pintaPassos); }
  };
  window.addEventListener('scroll', pedeP, { passive: true });
  window.addEventListener('resize', function () { if (armouP) pedeP(); });
}
```

**O espaço — cada foto respira**, com durações e atrasos diferentes (senão pulsam juntas):
```css
.carrossel{display:flex;gap:1rem;overflow-x:auto;scroll-snap-type:x proximity;scroll-behavior:smooth}
.carrossel figure{flex:0 0 min(58%,600px);scroll-snap-align:start;margin:0;overflow:hidden}
.carrossel img{width:100%;aspect-ratio:3/2;object-fit:cover;animation:respira 24s ease-in-out infinite alternate}
.carrossel figure:nth-child(2) img{animation-duration:28s;animation-delay:-7s}
.carrossel figure:nth-child(3) img{animation-duration:21s;animation-delay:-13s}
.carrossel figure:nth-child(4) img{animation-duration:26s;animation-delay:-4s}
.carrossel figure:nth-child(5) img{animation-duration:23s;animation-delay:-16s}
.carrossel figure:nth-child(6) img{animation-duration:30s;animation-delay:-9s}
@keyframes respira{from{transform:scale(1.005)}to{transform:scale(1.08) translate3d(-1.4%,-1%,0)}}
@media (max-width:900px){ .carrossel figure{flex:0 0 82%} }
@media (prefers-reduced-motion: reduce){ .carrossel img{animation:none} }
```

**Avaliações — o carrossel que anda sozinho:**
```js
function andarProva() {           // anda por ÍNDICE
  if (window.__pausado || Date.now() < pausaAte) return;
  var cards = trilhoProva.querySelectorAll('.depos'); if (cards.length < 2) return;
  iProva = (iProva + 1) % cards.length;
  trilhoProva.scrollTo({ left: iProva ? cards[iProva].offsetLeft - trilhoProva.offsetLeft : 0, behavior: 'smooth' });
}
['pointerdown', 'touchstart', 'wheel'].forEach(function (ev) {
  trilhoProva.addEventListener(ev, function () { pausaAte = Date.now() + 9000; }, { passive: true }); });
// o setInterval(andarProva, 5000) liga com a dobra na tela e desliga fora dela
```

**Cabeçalho compacto, flutuante e barra — uma conta só:**
```js
var topo = document.getElementById('topo'), flut = document.getElementById('flutuante'),
    barra = document.getElementById('barra'), capa = document.getElementById('capa'),
    rodape = document.querySelector('.rodape'), pendente = false;
function aoRolar() {
  if (pendente) return; pendente = true;
  requestAnimationFrame(function () {
    pendente = false;
    var y = window.scrollY || document.documentElement.scrollTop;
    if (topo) topo.classList.toggle('compacto', y > 40);
    var passouCapa = capa ? y > capa.offsetHeight * 0.78 : y > 500;
    var sobreRodape = rodape ? rodape.getBoundingClientRect().top < window.innerHeight - 60 : false;
    var mostrar = passouCapa && !sobreRodape;
    if (flut) flut.classList.toggle('visivel', mostrar);
    if (barra) barra.classList.toggle('visivel', mostrar);
  });
}
window.addEventListener('scroll', aoRolar, { passive: true });
window.addEventListener('resize', aoRolar);
aoRolar();
```

---

## 7. Medição

Regras completas no [padrão §9](01-padrao.md). Na página:
- Bloco comentado `══ MEDIÇÃO ══` no `<head>`: o **protocolo no 1º toque** e a **visita por `sendBeacon`**, depois o carregador do GTM com trava de host, no ocioso, depois que a capa pinta. (Com o snippet padrão do GTM, uma página caiu de ~100 para 67 no celular; com o carregamento depois da pintura, 86 sem perder rastreio.)
- `medir(nome, dados)` só empurra no `dataLayer`. Nada de `gtag`/`fbq` diretos (duplicariam o contêiner).
- Eventos que sempre valem: `contato_wpp` (a conversão, um evento só), `agendar_click` **com a dobra de origem**, um evento do elemento dinâmico da capa (diz se a ideia prendeu alguém), `pausa_animacoes`, `compartilhar` (à parte de contato), `form_*` quando houver formulário.
- Página `/privacidade/` e aviso em toda página com GTM, Ads ou pixel.

---

## 8. O que NÃO fazer — a estética "de IA"

Rejeitada explicitamente: "você tem um estilo padrão de criar sites que eu não quero que você siga".
- Gradiente roxo/azul, glassmorphism, cards arredondados **com sombra** em tudo (canto de 14 px sem sombra é o padrão).
- Grade de três cards "ícone + título + parágrafo" de caixa branca com ícone de biblioteca.
- Emoji na interface. "Eleve o seu…". Adjetivo em cascata.
- Botão com sombra ou gradiente.
- Os clichês de 1ª e 2ª geração listados no [padrão §2](01-padrao.md).
- **Faz:** hierarquia editorial — display grande contra micro-caixa-alta, fios de 1 px, assimetria.

**Tipografia por cliente, nunca a mesma** (exemplos de pares já usados: Fraunces + Karla; Space Grotesk + IBM Plex Sans + IBM Plex Mono; Cormorant Garamond + Jost).

**Quando chega o manual de marca, ele manda:**
- A **fonte do manual substitui o par escolhido**. Fonte paga sem licença web do cliente não entra: usa-se a fonte livre do próprio manual — de preferência a que está **dentro do logo** — e a paga fica como proposta. Nunca uma "parecida" grátis (letra quase igual ao lado do logo destoa).
- **O logo sai do PDF em vetor**, não de print: os traços preenchidos da página viram SVG (ex.: PyMuPDF) e o SVG se confere pixel a pixel contra outra página do manual com a mesma arte. No cabeçalho, embutido com `fill="currentColor"`.
- **A cor do desenho do logo pode não ser a da paleta impressa.** O PDF guarda em CMYK: conferir a conversão comparando as amostras com os hex impressos.
- Favicon: o monograma do manual, na cor do desenho. JSON-LD `logo`: a versão mais quadrada, em PNG ≥ 112×112.

---

## 9. Fatos não se inventam

Número é afirmação, não enfeite. Faltaram três números numa página médica e **a faixa foi ao ar com quatro, não com sete**, com o pedido registrado no `LEIA-ME.md`. Vale para prazo, "opções veganas", horário, credencial — qualquer coisa que a fonte não confirme. Quando duas fontes do próprio cliente se contradizem, **buscar a terceira** (um CRM aparecia com dois dígitos trocados entre o Instagram e uma arte; o site oficial decidiu — e revelou que havia arte circulando com o número errado). Detalhe em [copy](04-copy.md).

---

## Checklist de aceite

**Estrutura**
- [ ] Ordem das dobras da §6; catálogo **acima** do filtro.
- [ ] Nenhuma dobra cortada por falta de insumo; exceção legítima declarada em `<meta name="lp-excecao">`.
- [ ] Avaliações puxando do Perfil por `?lugar=` (menos advocacia).
- [ ] Clínica com mais de um profissional: dobra 4b depois do catálogo, vaga marcada para quem não tem foto.

**Primeira dobra**
- [ ] Capa de fundo com foto horizontal no desktop e vertical no celular (ou caixa recuada à direita).
- [ ] Eixo único medido em 1440, 1920 e 390.
- [ ] Cabe em 725 e 640 px de altura, com folga medida.
- [ ] Efeito dinâmico preso fora da coluna de texto; âncoras do celular medidas.
- [ ] `<body class="fundo">` e cabeçalho claro sobre a foto escura.
- [ ] Sinal de confiança verificável na capa ou na faixa 2.

**Conteúdo**
- [ ] Nenhum número sem fonte; nenhum valor em R$.
- [ ] Frase do filtro igual nos três lugares.
- [ ] Nenhuma frase trata quem lê como custo.
- [ ] Legendas e `alt` descrevem o que a foto mostra.
- [ ] Saúde: registro profissional no rodapé e junto do nome, "não substitui consulta", regras do conselho conferidas.

**Botões e animação**
- [ ] Canto de 14 px; pílulas no cabeçalho; flutuante no desktop, barra no celular, nunca os dois.
- [ ] Um CTA por dobra, cada um com `data-origem`.
- [ ] Faixa de números com 5–8 itens do tamanho do conteúdo, valor final no HTML, sem linha de fonte na tela.
- [ ] Catálogo em grupos de 3 completos; foto do tratamento em 3 larguras; tags numa linha.
- [ ] Estado base legível; o que apaga texto armado só na 1ª rolagem; `prefers-reduced-motion` respeitado e ouvido ao vivo; botão de pausa parando tudo o que se move > 5 s; rolagem medida (60 fps, 0 tarefas longas).

**Técnica** — ver o checklist de [SEO e velocidade](05-seo-e-velocidade.md).

**Documentação**
- [ ] Prints desktop e celular com emulação real guardados como referência da página.
- [ ] O que quebrou nesta página virou lição registrada para as próximas.
