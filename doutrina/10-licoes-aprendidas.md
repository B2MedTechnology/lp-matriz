# Lições aprendidas — regras que nasceram de falhas reais

Cada regra abaixo custou pelo menos uma rodada de retrabalho, uma reprovação do cliente ou um dado errado numa conta de
anúncio. Estão destiladas do diário de construção de dezenas de páginas, sem data nem cliente. Formato:

- **Regra** — o que fazer (ou nunca fazer).
- **Por quê** — a falha que a gerou, contada de forma genérica.
- **Como conferir** — o teste que prova que está certo.

Antes de depurar algo do zero, procure o sintoma aqui. Regras de norma profissional estão em [conselhos/](conselhos/);
o padrão de construção em [01-padrao.md](01-padrao.md); as dobras em [02-anatomia-da-pagina.md](02-anatomia-da-pagina.md).

Sumário: [Medição](#1-medição-e-verificação) · [Capa](#2-capa-e-primeira-dobra) · [Fotos](#3-fotos-e-imagens) ·
[CSS e JS](#4-css-e-javascript-que-mordem) · [Movimento](#5-movimento-vídeo-e-acessibilidade) · [Copy](#6-copy-e-fatos) ·
[SEO](#7-seo-metadados-e-dados-estruturados) · [Velocidade](#8-velocidade) · [Rastreamento](#9-rastreamento) ·
[Publicação](#10-publicação-e-hospedagem) · [IA](#11-ia-na-produção) · [Formulário](#12-formulário) ·
[Processo](#13-processo-e-base)

---

## 1. Medição e verificação

### 1.1 Medir na tela real, não na confortável
**Regra:** a primeira dobra do celular se mede em **390×725 e 360×640** antes de dizer que coube; a dobra inteira (foto
**e** texto) escala com `min(vw, svh)`.
**Por quê:** a capa foi conferida num quadro de 780 px e declarada "cabe tudo"; na altura real do aparelho (~725 px
úteis) e em 640 px o aviso de "somente particular" estava cortado 16 e 62 px. Só a foto escalava; o texto era fixo.
**Como conferir:** script de medição da dobra nos dois tamanhos; a folga que denuncia texto grande demais é a de
**cima** (pé do cabeçalho → começo do texto), não a de baixo — com capa ancorada embaixo, a folga de baixo é só o padding.

### 1.2 O resumo da auditoria esconde o resto
**Regra:** auditoria de acessibilidade se lê no **JSON inteiro**, não no resumo.
**Por quê:** o PageSpeed listava só as primeiras palavras de baixo contraste; consertadas, apareceram mais 18
reprovações (etiquetas, datas, rodapé) que sempre estiveram abaixo do corte do resumo.
**Como conferir:** axe/pa11y ou o JSON do Lighthouse, contando todos os nós reprovados.

### 1.3 Uma rodada de PageSpeed não diz nada
**Regra:** celular = **mediana de 3 rodadas** na rotina e **5** nas decisões apertadas (1–3 pontos); uma medição por vez;
máquina calma (`uptime`; carga alta invalida o TBT).
**Por quê:** a mesma página, sem mudar uma linha, deu 97, 100 e 100 (Speed Index de 1,1 a 4,2 s). Noutra, uma "queda
causada pelo GTM" (73) era a máquina sobrecarregada por outras sessões — com a máquina calma deu 95.
**Como conferir:** registrar a carga da máquina junto do número; nunca rodar dois Chrome ao mesmo tempo.

### 1.4 SEO 69 na prévia é o `noindex`
**Regra:** ao reportar a nota de SEO de uma prévia, conferir que a única auditoria reprovada é "bloqueada para
indexação" e dizer isso junto do número.
**Por quê:** o cliente estranhou 69 depois de uma rodada inteira de SEO; o `noindex` proposital vale 4 dos 13 pontos.
**Como conferir:** a mesma página com indexação ligada dá 100.

### 1.5 Print automatizado não prova defeito
**Regra:** print de navegador sem interface, aba oculta ou painel escondido **não é prova de bug**. Confirmar em
viewport real (emulação por CDP: `Emulation.setDeviceMetricsOverride`) ou no aparelho antes de consertar.
**Por quê:** `--window-size=390,844` renderizou o layout num quadro maior e gerou um "transbordo" que não existia;
transições e vídeos congelam em aba oculta (`getComputedStyle` devolve o valor do início); `IntersectionObserver` e
`requestAnimationFrame` não disparam em aba automatizada; o print da página inteira com recorte além da janela sai sem
as imagens `lazy`; o iframe do mapa não termina de desenhar no print e o alfinete "some". Em um caso a busca do mapa
foi "consertada" sem prova e o conserto foi desfeito.
**Como conferir:** `document.visibilityState`, `el.getAnimations()`; prova por um estado que só existe se a coisa rodou
(um quadro do vídeo que o pôster não tem); no script de print, trocar `loading` para `eager` e esperar cada imagem;
mapa estranho → testar a URL num iframe isolado do mesmo tamanho, com 15 s de espera.

### 1.6 Efeito que responde ao dedo se mede em atraso
**Regra:** além de fps, medir **quanto o efeito fica atrás do dedo** e quanto o vídeo demora a começar.
**Por quê:** uma cena de rolagem passava em tudo (60 fps, PageSpeed 99) e foi reprovada na mão: "muito delay". Com
suavização τ = 0,11 s ficava 17–21 quadros atrás (quase 1 s); com τ = 0,04 s, 6–8. O vídeo em laço esperava 1,5 s
para tocar depois da capa.
**Como conferir:** script que simula um gesto real e mede quadros de atraso; script que mede LCP → primeiro `playing`.

### 1.7 Cache com janela se prova contando
**Regra:** todo cache de objetos caros (bitmaps de quadro) se prova **contando o que está vivo** depois de rolar a
página inteira.
**Por quê:** a folga da janela aplicada também ao "esqueleto" fixo prendeu 115 bitmaps (~425 MB) contra ~40 esperados.
A leitura do código não pegou.
**Como conferir:** interceptar `createImageBitmap` e `close` e contar.

### 1.8 Verificação com cache vazio é cega para bug de cache
**Regra:** depois de trocar CSS/JS/imagem numa página que já esteve no ar, "certo no meu print" não prova nada. Quando
alguém diz "continua quebrado" e o print frio está certo, **a primeira hipótese é cache**, não layout.
**Por quê:** todo print sobe um navegador com perfil limpo, que nunca tem o arquivo velho. O cliente viu HTML novo com
CSS velho na primeira tentativa; duas rodadas foram gastas caçando defeito de CSS inexistente.
**Como conferir:** URL versionada (§10.2) e conferência num navegador que já tinha aberto a página.

### 1.9 Laço de medição não engole erro
**Regra:** listar arquivos para medir com `find` ou `pathlib.glob`, nunca com glob do shell calado por `2>/dev/null`.
**Por quê:** no zsh, um padrão sem arquivo aborta o laço inteiro; a saída foi uma tabela vazia que parecia "nada a medir".

### 1.10 Comparar com a referência, lado a lado
**Regra:** ao replicar uma dobra de outra página, tirar print da origem (desktop **e** celular) e pôr ao lado do seu
**antes** de mostrar a alguém. Toda diferença deliberada se diz em voz alta.
**Por quê:** a cópia foi entregue com quatro defeitos que trinta segundos de comparação pegariam; um elemento escondido
no celular "por conta própria" virou reclamação de desvio silencioso.

### 1.11 "Reprovado" é restrição ativa
**Regra:** cada linha de uma lista de versões reprovadas pelo cliente é uma restrição. Sair de uma exige dizer por quê,
antes de entregar.
**Por quê:** uma versão reprovada ("dois arquivos, um para celular e outro para desktop") foi refeita igual na página
seguinte, por acidente.

---

### 1.12 PageSpeed pode devolver análise guardada
**Regra:** em toda medição, o `analysisUTCTimestamp` muda entre as rodadas e é posterior ao deploy; rodada com carimbo
repetido não conta. Marca diferente por rodada na URL (`?psi=<marca>`).
**Por quê:** "3 rodadas" responderam em 2 s com o mesmo carimbo: a mediana era um número só, e o antes × depois de uma
mudança comparava análises velhas.
**Como conferir:** imprimir o carimbo de cada rodada ao lado da nota.

## 2. Capa e primeira dobra

### 2.1 A capa tem porteiro de insumo
**Regra:** antes de qualquer CSS, a foto da capa passa por quatro perguntas: plano geral? ar acima da cabeça? a borda
não corta a pessoa? metade do quadro calma para o texto? Qualquer "não" **para** e vira conversa com o cliente.
**Por quê:** a mesma mecânica de capa, copiada certa, deu resultado ruim porque a foto nova era plano médio (cabeça a 6%
do topo, figura preenchendo metade) e a de origem era plano geral (cabeça a 17%). Foto errada → recorte aproximou →
quadro alargado na marra → emenda → máscara para esconder → borrão no celular. Quatro rodadas, uma causa.
**Como conferir:** prancha com as candidatas e a grade de 10%; ver [insumos](03-insumos-e-briefing.md).

### 2.2 Trocar a foto da capa não é trocar o `src`
**Regra:** orçar a troca de foto como trabalho: reabrir pontos ancorados, máscara, posição de cartões e zoom.
**Por quê:** a troca de retratos de IA pela sessão real quebrou cinco coisas: coordenadas caindo no fundo desfocado,
cartão tapando o rosto, cartão translúcido sumindo sobre camisa branca, máscara dissolvendo o lado errado, zoom de 1,9×
grotesco num retrato fechado.

### 2.3 Folga acima da cabeça no celular
**Regra:** no recorte do celular, ~12% de folga acima da cabeça; elemento sobre a foto sai em telas baixas (≤ 760 px).
**Por quê:** com 6%, o cabeçalho fixo cobria a testa; em 360×640 o texto subiu até o meio da foto e o cartão bateu na
assinatura.

### 2.4 Coordenada sobre rosto se mede
**Regra:** ponto ou efeito sobre a foto é **medido** (`getBoundingClientRect`), nos dois eixos, com o raio do efeito
abaixo do teto do texto. Num rosto, mirar testa e bochechas.
**Por quê:** escolhido "no olhômetro" pelo print, o ponto caiu em cima do texto, na boca e no olho, em três tentativas.

### 2.5 O que é ancorado numa imagem mede a imagem
**Regra:** coordenadas em % se calculam sobre a caixa **da imagem**, não do contêiner, e se remedem em `load`,
`document.fonts.ready` e `resize`. Conferir em 1440 **e** 1920.
**Por quê:** em 1440 a foto ocupava 87% do palco; em 1920, 65% — o ponto da testa aterrissou no cabelo e a lupa
ampliava esticado.

### 2.6 Letreiro de uma linha se mede em três larguras
**Regra:** `white-space: nowrap` no letreiro e teto do `clamp` calculado pela largura da coluna; medir em 1280, 1440 e
1920.
**Por quê:** uma fonte ultracondensada a 10vw coube em 1440 e quebrou em duas linhas em 1920.

### 2.7 Cabeçalho compartilhado e variantes herdam cores e pseudoelementos
**Regra:** ao criar variante que reaproveita classes da original, procurar `::before`/`::after` (sobretudo dentro de
media queries) e as cores do cabeçalho pensadas para outro fundo.
**Por quê:** a variante de capa escura herdou um véu marfim do `@media` do celular da capa clara e o aviso ficou
ilegível; o selo e os ícones do cabeçalho, escuros, sumiram sobre a foto escura (e, clareados sem `:not(.compacto)`,
ficavam branco no branco depois da rolagem).
**Como conferir:** `grep -n '::after\|::before' estilo.css` antes de entregar; rolar a página olhando o cabeçalho.

### 2.8 Linha com separadores se decide, não se deixa quebrar
**Regra:** em linhas com "·", decidir as quebras no celular (rótulo em bloco, separador some); telefone, CEP, CNPJ e
"CRM · RQE" dentro de `white-space: nowrap`.
**Por quê:** o navegador quebrou o horário no meio, pendurou o "·" no fim da linha e partiu "(00) 00000-" de "0000".
**Como conferir:** print em 390 e 360 px.

### 2.9 Elemento novo na capa nasce como teste
**Regra:** dobra nova ou elemento novo na capa (ex.: selo "★ 5,0 · N avaliações no Google" abaixo do botão) nasce numa
página de teste `noindex`, e o cliente vê o print antes de virar padrão.
**Por quê:** a rolagem média no celular é ~45% da página; o sinal de confiança precisa subir, mas cabe em 390×725 só
se medido.

### 2.10 Título sem `<br>` e com `&nbsp;` preservado
**Regra:** o H1 se escreve sem `<br>`; o divisor de palavras das manchetes animadas separa por `[ \t\n\r]+`, nunca `\s`.
**Por quê:** `<br>` deixou um "e" sozinho na linha do celular; `\s` casa com o nbsp e desfez o `&nbsp;`, derrubando a
última palavra para uma terceira linha.

### 2.11 Glifo da fonte igual ao do logo
**Regra:** conferir "&", números e aspas da fonte do título contra o logo; se divergir, trocar só o caractere por
`unicode-range` (ex.: `U+0026`), sem trocar a fonte.
**Por quê:** o "&" cursivo da fonte do título contrastava com o "&" clássico do logo, e o cliente reprovaria.

---

### 2.12 A maior frase da capa é a busca que paga a página
**Regra:** em página que recebe anúncio de pesquisa, a frase grande da capa (a que se lê primeiro, não só o `<h1>`
técnico) e o `<title>` trazem a palavra principal do grupo de anúncios ("Oftalmologista em <cidade>"). Slogan e conceito
vão para o apoio ou para uma dobra de baixo.
**Por quê:** na mesma página, as palavras cujo termo estava no título tinham a nota de "experiência na página" na média;
as que não estavam, abaixo — justamente a palavra que levava ~80% do gasto.
**Como conferir:** a nota de página por palavra que gasta (`post_click_quality_score`) cruzada com o termo no `<title>` e
no `<h1>`; "abaixo" só onde o termo falta = este defeito.

### 2.13 Aviso de cookies no pé, subindo com a barra
**Regra:** no celular o aviso fica no **pé** (`bottom: env(safe-area-inset-bottom) + .6rem`), à direita do botão de pausa
(`left: 44px`), e sobe junto com a barra fixa (`.barra.visivel ~ .aviso-cookies`) — por isso ele e a pausa vêm **depois**
da `.barra` no HTML.
**Por quê:** a 84 px do pé, o aviso cobria o botão da capa no celular; a prova da 1ª dobra não via porque o aviso só
aparece depois do `load`.
**Como conferir:** print em 390×844 e 360×640 **depois do `load`**; o conferidor cobra a ordem pausa/aviso depois da barra.

## 3. Fotos e imagens

### 3.1 Foto real; banco só provisório e declarado
**Regra:** foto real da pessoa e do lugar. Enquanto a real não chega, foto de banco **gratuita**, sem rosto visível,
com o selo "Imagem ilustrativa" — nunca apresentar desconhecido como profissional da casa. Nos bancos gratuitos, fotos
"patrocinadas" são pagas e vêm com marca d'água.

### 3.2 Varrer o quadro inteiro
**Regra:** antes de recortar, procurar terceiros (porta-retratos, pessoas ao fundo) e texto (rótulos, telas). Deslocar
o recorte em vez de borrar.
**Por quê:** fotos do consultório tinham porta-retratos da família; uma bolsa de soro de banco de imagem tinha rótulo em
língua estrangeira, ilegível na prancha e legível no card do celular.
**Como conferir:** triagem no **print do celular**, onde o card é maior que na coluna do desktop.

### 3.3 Arquivo de mesmo tamanho não é a mesma imagem
**Regra:** achar arquivo por tamanho, nome ou data é hipótese — abrir e olhar antes de usar.
**Por quê:** procurando a foto de uma médica pelas dimensões, entrou na prancha um anúncio de **outra** clínica com o
mesmo tamanho.

### 3.4 Logo vem do cliente e se lê
**Regra:** logo vem do cliente ou do perfil oficial, com o **manual de marca**; ler o nome escrito no logo antes de
aplicar. Montagem com peças do site antigo é provisória e se refaz quando o manual chega.
**Por quê:** o profissional tinha dois sites e o logo baixado era de outra marca; a montagem tinha proporção 4,29 contra
5,10 da versão oficial.

### 3.5 Cor do logo é a do desenho, não a da página de paleta
**Regra:** tirar a cor do **desenho** do logo; PDFs de design guardam CMYK — bater as amostras contra os hex impressos.
**Por quê:** a página de paleta trazia a cor do fundo da aplicação, não a do símbolo.

### 3.6 SVG extraído de PDF se confere pixel a pixel
**Regra:** ao converter traços em `d` de SVG com arredondamento, calcular cada delta a partir do ponto **já
arredondado**; conferir redesenhando no tamanho de outra página do manual.
**Por quê:** a partir do ponto exato o erro soma e a letra não fecha. (PyMuPDF renderiza e entrega os vetores.)

### 3.7 Alt depois da foto
**Regra:** o `alt` se escreve olhando a foto **final**, nunca a planejada.
**Por quê:** os alts descreviam "médico explicando um exame" e as fotos escolhidas eram coleta e microscópio.

### 3.8 Uma largura por tela, com `sizes` verdadeiro
**Regra:** AVIF/WebP por largura com `srcset` + `sizes` real; recorte próprio em retrato para o celular
(`<source media="(orientation: portrait)">`) e teto na maior largura.
**Por quê:** logo de 720 px aparecendo com 150; cards de 800 px em colunas de 400; capa que cobre pela altura com
`sizes="100vw"` escolhe pequeno demais, e com `150vh` pede ~5.000 px no celular para mostrar 23%.

### 3.9 Variante de logo mantém a razão exata
**Regra:** larguras de variante múltiplas da razão do arquivo (logo 1030×240 → 206, 309, 412…).
**Por quê:** 200×47 (46,6 arredondado) deu "proporção incorreta" no Lighthouse.

### 3.10 Comprimir na escala em que a tela mostra
**Regra:** comparar compressão na ampliação real (retina amplia 2–3×). Para quadros de vídeo, AVIF q~72; no canvas,
`imageSmoothingQuality = "high"` a **cada** redimensionamento.
**Por quê:** WebP q68 passava a 100% e virava pele plastificada ampliada.

### 3.11 Quadro de vídeo sai com valores crus
**Regra:** quadro extraído de vídeo para a web sai com os valores **crus do decodificador**, marcado sRGB sem conversão,
e gravado sem perfil ICC.
**Por quê:** a extração com conversão de gama clareou os meios-tons (rosto pálido: brilho 120,7 contra 111,8 no
`<video>`); o Pillow `convert('RGB')` carrega o ICC junto.

### 3.12 Estender fundo só onde é fundo
**Regra:** para alargar uma foto, esticar só colunas de **fundo puro** da borda, borrar, colar a foto com rampa larga
(~220–240 px) e alargar só pelo lado que o véu escurece. Margem inventada fica inteira dentro do trecho que a máscara
dissolve. Foto com painel ou coluna branca na borda não serve.
**Por quê:** amostrar uma borda tocada pela roupa criou um vinco claro; a média das colunas virou bloco com emenda reta;
a faixa inventada maior que o degradê chegou nítida.

### 3.13 Recorte de assunto limpa a franja
**Regra:** recorte de objeto recua a máscara 2 px, suaviza 1 px e troca a cor da franja pela do interior.
**Por quê:** a borda semitransparente trazia a cor da mesa e virou contorno sobre o creme.
**Como conferir:** prancha 1:1 em fundo claro **e** escuro.

### 3.14 `og:image` de vídeo do Instagram vem com o ▶
**Regra:** de post em vídeo, baixar a mídia (`/p/<código>/media/?size=l`), não a `og:image`.

### 3.15 Imagens públicas de alta do construtor antigo
**Regra:** cliente com página em construtor visual costuma ter os **originais** das imagens públicos em alta resolução
no HTML publicado (a miniatura é outra URL). Resolve logo e fotos quando o briefing não chega.

### 3.16 Foto 360° do perfil serve só de ambiente
**Regra:** vistas planas tiradas de fotos 360° do perfil do Google servem de **ambiente sob véu forte**, nunca de herói
nítido (~530 px reais num campo de 80°). Conferir quem publicou cada uma: foto de cliente não entra.

---

### 3.17 O porteiro olha a 100%, quadro a quadro
**Regra:** toda imagem com pessoa passa a 100% (mãos, rosto, pele, equipamento) antes de entrar; em página com cena por
quadros, amostrar **≥ 9 quadros ao longo da cena** e conferir **cada imagem de card**, não só o pôster. Foto de centro
cirúrgico: olhar luva, pele do paciente, monitor e equipe. Vídeo gravado em pé no celular sai deitado na leitura crua
(o leitor ignora a rotação gravada): girar antes de cortar.
**Por quê:** a miniatura escondeu mãos de IA numa capa, sangue na luva numa foto de cirurgia, dois quadros da cena e um
card de IA — e um card "de tratamento" que era, a 100%, uma vacina veterinária com rótulo em espanhol.
**Como conferir:** a marca `lp-porteiro` só é escrita depois da folha aprovada; sem ela o conferidor avisa.

### 3.18 Remédio pelo nome genérico, também nas avaliações
**Regra:** nunca nome comercial de medicamento em lugar nenhum da página ("toxina botulínica", não a marca); as
avaliações ao vivo passam por filtro fixo de nome comercial **e** de e-mail no nome do autor, no navegador.
**Por quê:** uma marca comercial dentro de uma avaliação travou o anúncio de saúde da conta inteira; o serviço central de
avaliações não filtra nenhum dos dois.
**Como conferir:** nas primeiras 24 h de anúncio novo, ler os tópicos de política do anúncio.

## 4. CSS e JavaScript que mordem

### 4.1 `overflow-x: clip` no `html`, não `hidden` no `body`
**Por quê:** `hidden` no `body` cria contêiner de rolagem — `scrollY` para, o cabeçalho não encolhe, a barra do celular
não aparece; `clip` nos dois travou o `scrollTo`. A regra é literal.

### 4.2 `img { height: auto }` sempre
**Por quê:** `width`/`height` no HTML vencem o `aspect-ratio`; uma capa renderizou com 1176 px de altura.

### 4.3 Elemento substituído posicionado tem largura explícita
**Regra:** `canvas`, `img` e `video` com `left`/`right` levam `width: 100%`, nunca `auto`.
**Por quê:** o canvas ficou com 962 px numa tela de 390 (300×150 é o padrão do elemento).
**Como conferir:** `getBoundingClientRect()` da caixa antes de desconfiar da conta que desenha dentro.

### 4.4 `transform` no ancestral captura o `position: fixed`
**Regra:** centralizar por margem quando houver filho posicionado.

### 4.5 Especificidade: variante, seção e tag vencem o componente
**Regra:** ao sobrescrever no media query, incluir a variante no seletor; regra de layout que a variante sobrescreve
leva a própria versão de celular; regra de tag dentro de seção (`.rodape a`, `.rodape p`) leva `:not(.botao)` ou o
componente repete a seção no seletor; `li > span` para filho direto.
**Por quê:** cartão em x = −420 numa tela de 390; texto numa coluna de 150 px; botão verde com texto azul (4,2:1);
aviso encostado na borda; contador de 46 px caindo para 15 px.

### 4.6 Alinhamento se garante com `width`
**Por quê:** `margin-left: auto` desliga o `stretch` do item de grade; etiqueta e título ficaram 38 px fora do eixo e
passaram por duas revisões.

### 4.7 Máscaras: sem `-webkit-mask-composite`, redeclarar o composite no media query
**Por quê:** o prefixado usa outro vocabulário e deixou a foto **invisível** no Chrome; trocar `mask-image` no celular
sem redeclarar `mask-composite` sumiu a foto de novo, só no celular. Mesmo sintoma, duas causas.
**Regra extra:** a rampa da máscara começa transparente **dentro** do palco (`transparent 0%, transparent 5%, …`);
degradê se confere medindo a coluna de pixels na borda.

### 4.8 `scroll-snap-type: x proximity`
**Por quê:** `mandatory` cancela a rolagem programada, principalmente no iOS.

### 4.9 Laço contínuo não depende de transbordo
**Regra:** faixa "nunca estática" = trilho duplicado animando `translateX(0 → -50%)`; o conjunto cobre o contêiner e o
trilho é esse conjunto **duas** vezes; velocidade em px/s.
**Por quê:** a guarda "só anda se transborda" nunca disparava numa grade de 4 colunas; a faixa ficou parada semanas.

### 4.10 Uma conta só, no mesmo quadro
**Por quê:** dois observadores independentes mandavam mostrar e esconder a mesma barra.

### 4.11 Estado base é o legível — e inclui o número
**Regra:** o que a animação apenas realça nasce legível; contador nasce com o **valor final** no HTML (o JS anima a
partir dele); rede de segurança compara com o valor final, não com o vazio; efeito de revelação só se arma na primeira
rolagem.
**Por quê:** sem observador, a lista ficou esmaecida; o `rAF` morreu no meio e a faixa mostrou "2h" em vez de "24h";
robô e leitor de tela liam "0 anos"; palavras a 16% de opacidade reprovaram o contraste para quem não rola.

### 4.12 Interpolação com piso e teto
**Regra:** `Math.max(0, Math.min(1, p))`.
**Por quê:** durante a pausa `p` ficou negativo e a lente saiu da foto.

### 4.13 Leitura de layout espera um quadro
**Regra:** toda leitura de medida na inicialização por `requestAnimationFrame(() => setTimeout(fn, 0))`.
**Por quê:** ler `getBoundingClientRect` com o script rodando forçou layout de 69 ms e somou TBT de 210 ms.

### 4.14 Rede de segurança pela rolagem, não pelo tempo
**Regra:** mapa, API e iframe montam quando a pessoa chega perto; nunca por cronômetro pós-load.
**Por quê:** o `setTimeout` injetava o mapa e chamava a API para todo mundo, inclusive para o PageSpeed.

### 4.15 Elemento que segue o cursor não estaciona na fronteira
**Regra:** fora do território permitido o cursor **não assume**: volta o passeio automático.
**Por quê:** limitar o `x` deixou a lupa parada em cima da manchete.

### 4.16 `insertBefore`, não `appendChild`
**Por quê:** o iframe do mapa caiu abaixo do link "Traçar rota".

### 4.17 `aria-label` só com papel
**Regra:** `<span aria-label>` leva `role="img"`; carrossel com `aria-label` leva `role="region"`.
**Por quê:** reprovou acessibilidade **e** a categoria de agentes do Lighthouse.

### 4.18 CSS zumbi se apaga
**Regra:** ao trocar o mecanismo de uma dobra, `grep` da classe antiga em HTML, CSS e JS; classe que só existe num deles
é zumbi — apagar ou implementar. Docstring e comentário descrevem a versão atual.
**Por quê:** um comentário explicava um realce que nada mais acionava e mandaria o próximo caçar um bug inexistente.

### 4.19 JS dentro de string Python
**Regra:** JS embutido no gerador em `r"""…"""` (ou `\\n`); o gerador roda `node --check` em todo `<script>` embutido
e para com erro.
**Por quê:** `\n` virou quebra real, o script do protocolo morreu com `SyntaxError` e ninguém viu por horas porque o
GTM mascarava.

### 4.20 Logo empilhado não usa a máscara do horizontal
**Regra:** `aspect-ratio` da caixa do logo = proporção do arquivo.

---

### 4.21 A base traz cor fixa fora das variáveis
**Regra:** ao trocar a paleta de uma página que nasceu de outra, procurar `rgba(` e `#` no CSS **inteiro**, não só o
`:root`; e ler o texto visível inteiro da página gerada antes de mandar o link.
**Por quê:** 70 cores fixas da página-base deixaram a página nova com a cor do cliente anterior; a busca por lista de
palavras não pegou um nome de unidade de outro cliente no meio de uma frase.
**Como conferir:** `grep -oE "rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}" estilo.css | sort | uniq -c` contra os tokens.

## 5. Movimento, vídeo e acessibilidade

### 5.1 Animação de rolagem no compositor
**Regra:** efeitos de rolagem em CSS (`animation-timeline: scroll()/view()`) dentro de `@supports` e
`prefers-reduced-motion: no-preference`; JS só como plano B, escrevendo **um** `transform` por quadro.
**Por quê:** animação pela thread principal fica atrás do dedo no iOS.

### 5.2 Misturar quadros sem redesenhar
**Regra:** duas telas empilhadas com `opacity` na de cima; o compositor mistura.
**Por quê:** misturar com `globalAlpha` dobrou os `drawImage` e a rolagem caiu a 30 fps — e passou em todos os prints.
**Como conferir:** intervalo entre quadros e tarefas longas.

### 5.3 `filter`, `backdrop-filter` e `box-shadow` não se animam
**Por quê:** foram a maior parte do custo de quadro no celular; `box-shadow` em laço pinta a cada quadro na dobra do LCP.

### 5.4 `play()` recusado se trata
**Regra:** todo `play()` automático trata a recusa e re-arma no próximo evento de **ativação** (`touchend`,
`pointerup`, `click`, `keydown` — **não** `touchstart` nem `scroll`), destravando as outras cópias no mesmo toque. O
pôster (quadro 0) segura a dobra até lá.
**Por quê:** no iPhone em Modo de Pouca Energia o Safari recusa `play()` sem toque; o código engolia a recusa com
`.catch(function(){})` e a capa ficou parada para sempre. Nenhum medidor via (todos rodam em Chrome com autoplay mudo).
**Como conferir:** script que simula a regra do iPhone (play sem ativação → `NotAllowedError`) e confere: parado sem
toque, tocando após 1 toque, tocando após uma volta do laço. "Reduzir movimento" ligado deixa o pôster de propósito.

### 5.5 Vídeo com autoplay na capa derruba o celular
**Por quê:** `autoplay` passa por cima do `preload="none"`; um vídeo de 4,7 MB no topo deu 28/100 e LCP de 20,6 s.
**Regra:** `muted loop playsinline preload="none"`, `play()` por JS depois do load/LCP.

### 5.6 Tudo que se move sozinho por mais de 5 s tem pausa
**Regra:** um botão de pausa por página (24 px, canto inferior esquerdo, `aria-pressed`, `aria-label` que troca entre
"Pausar" e "Retomar"); a classe de pausa **repete o estado do `prefers-reduced-motion`** (estado final, não congelado no
meio); laços de JS escutam o evento de pausa; a escolha fica no `localStorage`.
**Por quê:** WCAG 2.2.2 (nível A): pausa no hover não conta e reduced-motion não é técnica do critério. Congelar no meio
deixou uma luz atravessada no rosto. O botão nasceu alto demais para fugir da barra fixa e encostou no aviso da capa —
conserto: baixo, e sobe só quando a barra aparece.
**O que não entra:** o que só se move com o dedo (cena de rolagem, manchetes que acendem ao rolar).

### 5.7 Servidor local que não atende `Range` não busca vídeo
**Regra:** teste que busca tempo num vídeo usa servidor que responde **206**.

---

### 5.8 A pausa vale para o carrossel também
**Regra:** todo laço automático (`setInterval` do carrossel, vídeo em laço, letreiro) obedece ao botão de pausa: a função
do laço sai cedo com `window.__pausado`, o CSS para com `html.pausado`, e o vídeo da capa não volta a tocar sozinho
(nem ao reentrar na tela) enquanto a página estiver pausada.
**Por quê:** com a página pausada, o carrossel de avaliações seguia andando a cada 5 s (WCAG 2.2.2) em mais de uma página;
o conferidor via o botão existir, não que cada laço o obedecesse.
**Como conferir:** o conferidor lê o JS servido e reprova `setInterval` cuja função não leia `__pausado`.

### 5.9 Topo compacto anima só opacidade
**Regra:** o fundo e a sombra do cabeçalho compacto moram numa camada (`::before`) que só muda `opacity`; o padding e a
altura do logo trocam **sem** transição; sem `backdrop-filter` no topo nem na barra; barra de progresso só por
`transform`.
**Por quê:** `transition: background, box-shadow` + `transition: padding` + `backdrop-filter` estavam na página-base e
em mais de uma dezena de páginas — repintura a cada quadro de rolagem, contra a própria regra de movimento.
**Como conferir:** o conferidor reprova transição de `box-shadow`/`padding`/`width`/`height`/`filter` e `backdrop-filter`
em `.topo`/`.barra`.

### 5.10 O foco do teclado tem 3:1 nas duas cores de fundo
**Regra:** o anel de foco é escuro (cor forte da marca) nas seções claras e claro só nas escuras; medir ≥ 3:1 contra o
fundo de cada seção.
**Por quê:** o foco claro/ciano dava 1,55:1 no fundo claro — quem navega por teclado não via onde estava (WCAG 2.4.11).
**Como conferir:** o conferidor reprova `:focus-visible` raiz com o token claro; contraste medido por seção.

### 5.11 Animação da capa depois do `load` (em prova)
**Regra (ainda em prova, confirmar numa 2ª página antes de virar regra):** ligar o ciclo CSS da capa só depois do `load`
e em ociosidade (`requestIdleCallback`, teto 2,5 s).
**Por quê:** com a animação ligando no 1º quadro, o TBT do celular foi de 644 para 280 ms (mediana de 3) só com essa
troca — mas uma rodada avulsa repetiu a nota antiga.

## 6. Copy e fatos

### 6.1 Preço nunca vai na página
**Regra:** nenhum valor em R$ — nem nos números, nem no FAQ, nem "a partir de". FAQ do valor: *"informado pelo WhatsApp
antes do agendamento"*, mesmo com preço no briefing.
**Por quê:** a IA, com o valor no briefing, publicou preço em páginas cujas versões aprovadas já tinham escolhido
"valor pelo WhatsApp". O revisor automático recusa qualquer `R$`. Ver [conselhos/](conselhos/).

### 6.2 Fato não confirmado não vai à página
**Regra:** cada número e cada oferta ("entrega grátis", parcelamento, horário) tem `confirmado=True` ou não sai;
"aberto agora" só com horário confirmado; parcelado sempre com o total a prazo.
**Por quê:** "entrega grátis" marcada "confirmar" foi publicada (oferta vincula — CDC art. 30); parcela sem total fere o
Decreto 5.903/2006; um "aberto agora" era calculado de horário que a própria página tratava como não confirmado.

### 6.3 Avaliação não se esconde sem pedido
**Regra:** levantar o ponto (sobrenome de parente, regra do conselho) **uma vez** e seguir a decisão do cliente; a
dobra de avaliações tem cards passando e atualização automática.
**Por quê:** uma primeira versão escondeu avaliações por sobrenome e ficou parada; o cliente reprovou.

### 6.4 O link da bio diz o que a página precisa resolver
**Regra:** ler a página de links do Instagram do cliente: cada botão é uma demanda (ex.: "não sei qual tamanho comprar"
virou uma dobra).

### 6.5 Franquia: busca pelo ID exato
**Regra:** cliente de rede ou franquia → perfil do Google pelo `place_id` exato, nunca pelo nome; nome da página e do
JSON-LD com a unidade; rodapé diz que é rede.
**Por quê:** a busca pelo nome devolveu outra unidade (212 avaliações contra 3) e teria puxado avaliações de outra empresa.

### 6.6 Mapa pelo embed do próprio perfil
**Regra:** em prédio com mais de um negócio, o mapa usa o embed `pb=` do perfil e a rota por `destination_place_id`;
conferir o alfinete com os olhos.
**Por quê:** "nome + endereço" marcou a farmácia do térreo.

---

## 7. SEO, metadados e dados estruturados

### 7.1 JSON-LD se valida pelo que o gerador escreve
**Regra:** `json.loads(..., object_pairs_hook=…)` que **levanta** em chave repetida; validar cada bloco; conferir o
`@type` montado.
**Por quê:** um `sameAs` duplicado foi ao ar e ficou semanas; `json.loads` puro fica com a última chave, sem erro.

### 7.2 Sem preço publicado não existe `Product`
**Regra:** item de catálogo sem preço é `Service`; com preço publicado (loja), `Product` com `offers` **dentro** e o
preço do JSON-LD saindo da mesma constante do visível. Nunca `aggregateRating`/`review` para "passar" no teste.
**Por quê:** `OfferCatalog → Offer → itemOffered: Product` deixou o `Product` sem `offers` e o Search Console acusou erro
crítico um dia depois da indexação.
**Como conferir:** script que percorre o JSON-LD e falha em `Product` sem `offers`.

### 7.3 Indexar desliga o `noindex` nos dois lugares
**Regra:** o interruptor de indexação do gerador escreve meta robots, canônica, robots.txt, sitemap **e** o
`X-Robots-Tag` do `vercel.json`.
**Por quê:** virar o interruptor e esquecer o cabeçalho manteve a página fora da busca com o HTML "certo".
**Como conferir:** `curl -sI <url> | grep -i x-robots`.

### 7.4 Prévia: `noindex` em dois lugares, robots aberto
**Regra:** prévia = meta `noindex` + `X-Robots-Tag` por host; robots.txt **aberto**. `Disallow` só para um robô de IA
específico, em grupo próprio, se necessário.
**Por quê:** o domínio passou 11 minutos servindo a prévia com `Disallow: /`; o Google guardou o robots.txt (até 24 h),
recusou a indexação e o sitemap. Com `Disallow`, o Google nem vê o `noindex`.
**Regra da virada:** a versão indexável vai ao ar **antes** de o DNS responder; se já aconteceu, esperar o cache e pedir
novo rastreamento no relatório de robots.txt.

### 7.5 Canônica e `og:*` só em URL que responde
**Regra:** canonical, `og:url` e `og:image` trocados para o domínio **no deploy da virada**, nunca antes; depois,
depurador de compartilhamento da Meta.
**Por quê:** páginas que recebiam anúncio compartilhavam no WhatsApp sem imagem porque a `og:image` apontava para host
que dava 403 ou não tinha DNS.

### 7.6 Favicon é arquivo
**Regra:** PNG 48/96 + `apple-touch-icon` + `/favicon.ico` por hostname.
**Por quê:** favicon `data:` SVG não conta para o Google e `/favicon.ico` dava 404.

### 7.7 Canônico ligado no construtor visual
**Regra:** em página de construtor visual, conferir que o link canônico nativo está **ligado** (vem desligado).
**Por quê:** sem canônica, a mesma home aparecia em três endereços (com `www`, com UTM do perfil, com `http`), e a de
UTM tinha mais impressões que a própria home.

### 7.8 Redirecionamento de pasta na Vercel
**Regra:** "tudo debaixo de uma pasta" = `/pasta/(.*)`; capturar e repassar = `/:caminho(.*)`. Conferir com e sem a
barra final.
**Por quê:** com `trailingSlash: true`, `/:resto*` não pegou a própria pasta e o link antigo respondeu 404.

### 7.9 Não consertar aviso de peso zero
**Regra:** antes de consertar um aviso de auditoria, ver se ele pesa e se a casa já decidiu.
**Por quê:** um `llms.txt` foi publicado para zerar uma auditoria e retirado no mesmo dia (mito; e mal formado derruba a
categoria).

---

### 7.10 `Product` para listagem do comerciante
**Regra:** em página com `Product` (só quando há preço publicado), `brand` é `{"@type":"Brand","name":…}` — referência a
`Organization` vira "tipo inválido" — e `offers` leva `hasMerchantReturnPolicy` e `shippingDetails` **da política real**
da loja; sem a política, deixar o aviso aberto e registrado, nunca preencher com valor suposto.
**Por quê:** a página passou em "snippets de produto" e caiu em "listagens do comerciante" no Search Console.
**Como conferir:** o conferidor reprova `Product` sem `offers` e `brand` que não seja `Brand`.

### 7.11 Mudar de host quebra dez coisas em silêncio
**Regra:** junto com o `BASE` do gerador: (1) GTM de servidor na mesma origem do host novo; (2) lista de origens do
serviço de avaliações (sondar antes, reescrever com todas + a nova, provar 200); (3) 308 do host antigo, mesmo caminho e
query; (4) URL final dos anúncios e sitelinks; (5) sitemap no Search Console e IndexNow; (6) vigia de visitas; (7) site
de cada Perfil do Google; (8) Bing (sitemap + envio da URL); (9) cache de DNS de quem testa (consultar um DNS público com `dig @<resolvedor>` e limpar o cache local);
(10) **todo** redirecionamento vai direto à canônica **indexável**, a raiz responde 308 (nunca 302/307) e o sitemap do
host velho sai dos buscadores.
**Por quê:** cada item falhou numa virada real: avaliações em 403 por semanas, aviso falso de "site parou" a cada 7 dias,
perfil apontando para o caminho velho, e um caminho antigo com 1.644 impressões redirecionando para uma variante `noindex`.
**Como conferir:** para cada URL com impressão que não seja a canônica, `curl -sIL`: só 301/308 e o último salto 200 sem
`noindex`; releitura em 14 dias.

## 8. Velocidade

### 8.1 Fontes locais e CSS embutido
**Regra:** woff2 locais recortados e CSS embutido pelo gerador; no CSS embutido, `url()` é relativa à **página**.
**Por quê:** Google Fonts + CSS em `<link>` faziam o celular esperar ~1,9 s antes da primeira letra (FCP 3,5 → 1,0–1,5 s).

### 8.2 GTM depois que a capa pinta
**Regra:** o contêiner carrega depois do aviso de LCP do navegador (`PerformanceObserver`, com detecção da API — no
Safari só a partir da 26.2), ou no primeiro toque/tecla, ou em 3,5 s.
**Por quê:** o snippet padrão derrubou o celular de 98–100 para 67; "no load da imagem + um quadro" deu 63–88; o
observador de LCP deu 85–86. O que falta até 100 é custo do contêiner (GA4, pixel, APIs de terceiros).

### 8.3 Pré-carga da capa antes dos scripts
**Regra:** `<link rel="preload" as="image" imagesrcset>` gerado do mesmo `srcset`, antes do GTM.
**Por quê:** a foto "demorava": 1,07 s de atraso de pintura com o `<head>` cheio de scripts.

### 8.4 Lighthouse no endereço real não pode virar visita
**Regra:** medir página com contêiner do cliente tirando o DNS dos hosts de envio
(`--host-resolver-rules="MAP www.facebook.com ~NOTFOUND, …"`) e com chave própria de "não rastrear"; nesse modo a nota
de boas práticas não vale, a de desempenho vale.
**Por quê:** `--blocked-url-patterns` deixou passar o envio da Meta e as rodadas viraram PageView no pixel; o
Lighthouse 13 não diz "Lighthouse" no user-agent.

---

### 8.5 O peso do GTM vem do contêiner
**Regra:** o `gtag` do GA4 e do Google Ads mora no **contêiner**, não na página; toda versão nova do contêiner web de
cliente com página mede o PageSpeed do celular antes × depois. Queda ≥ 5 pontos por TBT → olhar o contêiner (tag em
"All Pages" que pode esperar o `load` ou o consentimento) antes de mexer na página.
**Por quê:** a nota de duas páginas caiu 10 pontos no mesmo deploy da página: o contêiner tinha ganhado tags.
**Como conferir:** o `gtm.js?id=<GTM>` é público e lista as tags sem chave; `unused-javascript` aponta o `gtag/js`.

## 9. Rastreamento

### 9.1 Com GTM, a página só empurra no `dataLayer`
**Regra:** `medir()` nunca chama `gtag()` ou `fbq()` direto; o que vira evento de plataforma se decide no contêiner;
só **um** evento vira conversão.
**Por quê:** duplicava o que o GTM já mandava.

### 9.2 Protocolo garantido no primeiro toque
**Regra:** quando o GTM é atrasado, um script pequeno no `<head>` garante o protocolo no link do WhatsApp no primeiro
toque (`pointerdown`/`touchstart`/`mousedown`/`click`/`keydown`), com o **mesmo cookie, domínio, alfabeto e frase** da
tag do contêiner — só se faltar. Botões abrem em aba nova.
**Por quê:** o toque que dispara o carregamento do GTM já é o clique no WhatsApp; 5 de 12 mensagens saíam sem protocolo.
**Armadilha de teste:** o Chrome corta cookie em 400 dias — pedir 2 anos e ler 400 não é defeito.

### 9.3 GTM não carrega na prévia
**Regra:** o carregador do GTM tem trava por hostname; em `*.vercel.app` e local o contêiner não carrega (o protocolo
continua funcionando).

### 9.4 Abrir formulário não é contato
**Regra:** o ouvinte de clique em `wa.me` ignora `a[data-form]`; a página empurra o evento de envio do formulário.
**Por quê:** o botão que abre o formulário é um link `wa.me` (para quem não tem JS); com o ouvinte, cada abertura virava
contato — 1 lead = 2 conversões, e quem desiste também conta.
**Como conferir:** gravador de eventos: 1 abertura = 0 contatos.

### 9.5 Contêiner herdado: conferir a lista de domínios e o que ele mexe
**Regra:** antes de pôr um contêiner existente num domínio novo, testar as APIs de terceiros com o `Origin` do domínio
(403 = PageView perdido sem erro); se uma tag colar UTM em todo link, proteger `tel:` e `#` por `MutationObserver` e
conferir os `href` depois que o GTM carrega.

### 9.6 Serviço central com lista de origens
**Regra:** ao virar uma página para o domínio, acrescentar o domínio na lista de origens do serviço central (avaliações
etc.) **no mesmo passo**, sondando antes o que já passa (variável secreta não se lê de volta) e provando 200 em cada
domínio.
**Por quê:** sem a origem, toda página em domínio próprio ficou com nota e contagem congeladas (403).

### 9.7 A prévia local aplica os `rewrites`
**Regra:** o servidor local de prévia aplica redirects, headers **e rewrites** do `vercel.json`, inclusive quando o
pedido não aceita gzip; nunca medir no ar para contornar (manda visita de teste ao cliente).

---

## 10. Publicação e hospedagem

### 10.1 `.vercelignore` em lista de permissão
**Regra:** o gerador escreve o `.vercelignore` permitindo só o que vai ao ar (`/*`, `!index.html`, `!assets`, …),
cobrindo pastas de reserva dentro de `assets/`; depois de cada deploy, sonda `curl` nos caminhos sensíveis (`/LEIA-ME.md`,
`/ferramentas/`, `/.env`, `/gerar.py`) = 404.
**Por quê:** o CLI publica a pasta inteira e não lê `.gitignore`; notas internas da agência (o que o cliente pediu, ids
de fluxo, nomes de cabeçalho) e fotos de IA descartadas ficaram públicas no domínio do cliente.

### 10.2 Arquivo trocado com o mesmo nome muda a URL
**Regra:** `?v=N` no CSS e JS de **toda** página (com `must-revalidate` junto), e contador próprio para imagens
(`?f=N`) ou hash do conteúdo (`?h=`), inclusive nas URLs absolutas de `og:image` e logo.
**Por quê:** com `immutable`, quem já tinha aberto a página ficou com a foto antiga por um ano; mesmo com
`must-revalidate` + ETag, o navegador serviu CSS velho. *Revalidação é promessa; URL nova é fato.*
**Como conferir:** `content-length` no ar × local; `img.currentSrc` na largura do celular.

### 10.3 Linkar o projeto antes do primeiro deploy
**Regra:** `vercel link --project <nome>` e conferir `projectName` **e** `orgId` num script que para se não bater; nunca
copiar a pasta `site/` (com `.vercel/` e `.env.local`) de um projeto para outro.
**Por quê:** o CLI se linkou sozinho a um projeto existente com o nome da pasta ("site") e sobrescreveu a produção de
outro cliente.

### 10.4 Ler a saída do deploy antes de conferir
**Regra:** rodar o deploy, ler a saída e a URL, e só então conferir (`vercel inspect <url>` → `target production`).
Não encadear comandos.
**Por quê:** "Not authorized" transitório deixou a URL vazia e o `inspect` sem argumento ficou pendurado; sem TTY, a
saída lista "Promote to production" e parece prévia sem ser. Deploy parado em "Initializing": olhar a página de status
da Vercel antes de mexer.

### 10.5 DNS: confirmar antes, preencher e salvar na mesma rodada
**Por quê:** a sessão do painel de DNS caiu entre preencher e salvar, e nada foi gravado — a tela não avisa.
**Como conferir:** mensagem de sucesso na tela **e** `dig +short` no servidor autoritativo.

### 10.6 Construtor visual: clicar por referência, conferir antes de publicar
**Regra:** em editor visual hospedado, clicar por texto/referência do botão (nunca por coordenada); conferir o que está
pendente antes de clicar perto de "Atualizar"; página antiga aberta no editor novo pode mudar de visual ao republicar —
olhar a página inteira no editor e, depois de publicar, em 375/768/1000/1440 px; contar **todos** os links de WhatsApp
na página publicada (o botão flutuante costuma morar no código de configurações, não nos blocos).
**Por quê:** um clique por coordenada publicou a edição pendente de outra pessoa; uma republicação herdou a cor e o
tamanho padrão do tema; um botão foi movido por clique errado.

### 10.7 Insumo mora no projeto
**Regra:** original baixado vai para o projeto (ou fica o identificador do arquivo no LEIA-ME); pasta temporária é
apagada entre sessões.

---

### 10.8 Módulo comum pendurado na página
**Regra:** ao ligar um módulo novo numa página (blog, formulário, widget): abrir o `.vercelignore` (em lista de permissão,
a pasta nova precisa entrar), gerar a prévia local com conteúdo de teste e rodar o conferidor nela, ler o rodapé
**gerado** (não o template), e tirar profissão, conselho e norma das constantes do cliente, nunca do módulo.
**Por quê:** o `.vercelignore` deixaria a pasta nova fora do deploy (404 com o conteúdo "publicado"); a página mais antiga
tinha outra marcação de rodapé; a prévia não levava os originais que o porteiro lê; o texto fixo dizia "médico/CRM" numa
página de dentista.

## 11. IA na produção

### 11.1 Pessoa e resultado são reais
**Regra:** IA só para ambiente, textura, equipamento e transição, a partir de foto real; declarar na página. Ver
[medicina](conselhos/medicina-cfm.md) §6.

### 11.2 Imagem do cliente pode ser de IA
**Regra:** olhar os cantos (marca d'água de gerador) antes de usar imagem que o cliente já publicou; se entrar, como
ilustrativa, com aviso — nunca no lugar de foto do lugar ou da equipe.

### 11.3 A IA publica o que está no briefing
**Regra:** o revisor automático recusa `R$`, palavras proibidas do conselho e fatos não confirmados; a regra não pode
depender de a IA "lembrar".

### 11.4 Modelos de mídia saem do ar
**Regra:** não depender de um gerador de vídeo ou imagem específico; ajustar scripts antes da data de desligamento
anunciada.

---

## 12. Formulário

- **Data:** usar o calendário do aparelho (`type="date"`) e converter no envio; texto livre com máscara trava a pessoa.
- **Período:** pedir a duração e calcular o fim, nunca pedir o fim; mostrar antes de salvar as datas reais e o total
  pelo mesmo cálculo de quem cobra.
- **Dinheiro em pt-BR:** `Number("1.200")` = 1,2 — ponto seguido de 3 dígitos é milhar.
- **Valor por extenso** sai do número, nunca digitado à parte.
- **Dado pessoal:** formulário com relato (caso jurídico, sintoma) só liga o envio com política de privacidade e aviso.

---

## 13. Processo e base

### 13.1 Uma base, nunca "o gerador mais novo"
**Regra:** toda página nasce da base única da matriz; correção vai para a base e, até lá, é registrada com "replicar em".
Nomes fixos: `data-origem`, `.flutuante`, `.botao`, `aoRolar()`, `trilho`.
**Por quê:** com três linhagens de cópia, cada correção vivia em 1–2 de 9 geradores; a base declarada estava sem a regra
mais recente.

### 13.2 Ferramentas leem a configuração do projeto
**Regra:** scripts de medição leem `BASE`, `SLUG` e hosts do gerador do projeto; ao copiar, `grep` por nome de outro
projeto antes de rodar.
**Por quê:** scripts copiados mediam a página de outro cliente, bloqueavam os hosts de outro contêiner (e deixavam passar
os envios do próprio) ou nem rodavam.

### 13.3 O fork não corta dobras por falta de insumo
**Regra:** página nova passa no conferidor do padrão (dobras e itens obrigatórios); faltou insumo → placeholder
declarado e pedido ao cliente, não corte silencioso.
**Por quê:** uma página saiu sem avaliações, sem fotos nos cards, sem pausa, sem `/privacidade/` — e foi reprovada.

### 13.4 Página antiga: conferir antes de mexer
**Regra:** em página que não nasceu da base atual, rodar o conferidor **na leitura, antes de mexer**, e levar ao
responsável no mesmo recado: "o pedido é X; a página reprova Y do padrão — corrijo junto?". Card que sai (ou entra) por
pedido → recontar os grupos de 3 no mesmo turno e propor o que completa, ou declarar a exceção.
**Por quê:** um pedido pequeno foi publicado e só depois o conferidor reprovou 4 a 6 itens que já vinham de antes; um
card retirado deixou um grupo com 2, e o buraco só apareceu semanas depois.
**Como conferir:** `python3 ferramentas/conferir.py <url>` antes do primeiro comando de edição.
