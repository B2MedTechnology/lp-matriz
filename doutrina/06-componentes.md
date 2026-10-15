# 06 · Componentes

**Em uma frase:** as três peças que toda página reaproveita com receita própria — o botão de pausa (WCAG 2.2.2), o evento dinâmico da capa (um por cliente, nascido do instrumento ou do produto dele) e a dobra de avaliações do Google (serviço central, semente no HTML, prompt pronto) — com código, medidas e critérios de aceite.

---

## 1. O botão de pausa

### Por que existe
A WCAG 2.2.2 (nível A) exige que tudo o que **se move sozinho por mais de 5 segundos** ao lado de outro conteúdo tenha um jeito **visível** de pausar, parar ou ocultar. Pausar no hover ou no foco **não** conta, e `prefers-reduced-motion` **não** é técnica suficiente para esse critério. A Lei Brasileira de Inclusão (art. 63) faz disso risco jurídico, não só estético. Numa página da casa, cinco peças se movem sozinhas: o evento da capa, o letreiro de números, o carrossel de avaliações, as fotos que respiram e o vídeo em laço.

**Decisão de desenho:** botão em **todas** as páginas com interação, **bem discreto, bem pequeno, sem evidência** — "só para ter".

### O desenho
- **24 px** (22 no celular), círculo, canto **inferior esquerdo** (o WhatsApp mora à direita), opacidade 55% e 100% no hover/foco, ícone de pausa de 9 px que vira ▶ quando pausado. Fundo escuro translúcido na cor da página.
- **`aria-pressed`** + `aria-label` que alterna entre "Pausar" e "Retomar animações da página" — é assim que o leitor de tela e o Lighthouse (`button-name`, `aria-*`) leem o botão.
- **No celular, sobe só quando a barra fixa aparece** (`.barra.visivel ~ .pausa`). Nascer 78 px acima do pé o tempo todo encostou no aviso da 1ª dobra em 725 px de altura.
- A escolha fica no `localStorage` (`lp-pausa`): quem pausou uma vez abre a página pausada.
- Mede `pausa_animacoes` com `estado: pausa|toca`.

### O que pausa e o que não pausa
| Peça | Entra? | Como |
|---|---|---|
| Evento da capa em ciclo (luz, névoa, rótulos que acendem, trecho marcado, kit que se monta, traçado) | **sim** | o **estado parado do `prefers-reduced-motion` daquela página** — nunca congelar no meio: uma luz parada atravessada no rosto parece defeito |
| Letreiro de números (`desliza`) | sim | `animation-play-state: paused` — pausar no lugar é seguro |
| Carrossel de avaliações (`setInterval`) | sim | a função que anda lê `window.__pausado` |
| Fotos que respiram (`respira`) | sim | `animation: none` (volta ao tamanho base) |
| Vídeo em laço | sim | eventos `lp:pausar`/`lp:retomar` + guardas no laço |
| Animações da Web Animations API ou laço em `requestAnimationFrame` | sim | `document.getAnimations()` para WAAPI; guarda `if (window.__pausado) return` no passo do rAF |
| Cena arrastada pela rolagem, manchetes que acendem ao rolar, cards que entram, linha do tempo, contadores (1,4 s) | **não** | só se movem com o dedo ou duram < 5 s — fora do 2.2.2 |

### O código
**HTML** — antes do `<script src="…pagina.js">` e **depois** da `.barra` (senão o seletor `~` não funciona):
```html
<!-- Botão de pausa (WCAG 2.2.2, nível A): pequeno e discreto. -->
<button class="pausa" id="pausa" type="button" aria-pressed="false" aria-label="Pausar animações da página" title="Pausar animações">
  <svg viewBox="0 0 10 10" width="9" height="9" aria-hidden="true"><g class="pausa__ii"><rect x="1.6" y="1" width="2.4" height="8" rx=".5"/><rect x="6" y="1" width="2.4" height="8" rx=".5"/></g><path class="pausa__play" d="M2.4 1.1v7.8L8.6 5z"/></svg>
</button>
```

**CSS** — o `.pausa` é igual em toda página; o bloco `html.pausado …` é o **reduced-motion daquela página**, peça a peça:
```css
.pausa{position:fixed;left:.75rem;bottom:.8rem;z-index:44;width:24px;height:24px;padding:0;border-radius:50%;
       border:1px solid rgba(255,255,255,.42);background:rgba(10,24,38,.64);color:#fff;display:grid;place-items:center;
       cursor:pointer;opacity:.55;transition:opacity .25s ease}
.pausa:hover,.pausa:focus-visible{opacity:1}
.pausa:focus-visible{outline:2px solid #fff;outline-offset:2px}
.pausa svg{fill:currentColor;display:block}
.pausa .pausa__play{display:none}
html.pausado .pausa .pausa__ii{display:none}
html.pausado .pausa .pausa__play{display:block}
/* ── o estado parado de CADA efeito da página (copiar do bloco prefers-reduced-motion dela) ── */
html.pausado .capa h1 .pl{animation:none}                        /* entrada do título: fica no estado final */
html.pausado .numeros__lista{animation-play-state:paused}        /* letreiro: pausar no lugar é seguro */
html.pausado .carrossel img{animation:none}                      /* fotos que respiram: tamanho base */
html.pausado .evento-capa *{animation:none}                      /* o evento da capa: o estado parado DELE */
@media (max-width:900px){
  .pausa{width:22px;height:22px;bottom:calc(env(safe-area-inset-bottom) + .8rem)}
  .barra.visivel ~ .pausa{bottom:calc(env(safe-area-inset-bottom) + 4.9rem)}   /* sobe SÓ quando a barra aparece */
}
```

**JS** — o módulo, dentro do IIFE da página (onde `d = document` e `medir()` existem):
```js
/* PAUSA — html.pausado leva o CSS ao mesmo estado parado do prefers-reduced-motion; aqui ficam os laços
   de JS (vídeo em laço, carrossel) e as animações da Web Animations API, que a classe não alcança. */
(function () {
  var b = d.getElementById('pausa'), raiz = d.documentElement, CHAVE = 'lp-pausa';
  if (!b) return;
  function aplica(p, medindo) {
    raiz.classList.toggle('pausado', p);
    window.__pausado = p;
    b.setAttribute('aria-pressed', p ? 'true' : 'false');
    b.setAttribute('aria-label', (p ? 'Retomar' : 'Pausar') + ' animações da página');
    b.title = (p ? 'Retomar' : 'Pausar') + ' animações';
    try {
      d.getAnimations().forEach(function (a) {              // WAAPI
        var css = (typeof CSSAnimation !== 'undefined' && a instanceof CSSAnimation) ||
                  (typeof CSSTransition !== 'undefined' && a instanceof CSSTransition);
        if (!css) { if (p) a.pause(); else a.play(); }
      });
    } catch (e) { /* sem getAnimations: a classe já pausa o CSS */ }
    try { d.dispatchEvent(new CustomEvent(p ? 'lp:pausar' : 'lp:retomar')); } catch (e) {}
    if (medindo) medir('pausa_animacoes', { estado: p ? 'pausa' : 'toca' });
  }
  b.addEventListener('click', function () {
    var p = !raiz.classList.contains('pausado');
    try { localStorage.setItem(CHAVE, p ? '1' : '0'); } catch (e) {}
    aplica(p, true);
  });
  var ini = false;
  try { ini = localStorage.getItem(CHAVE) === '1'; } catch (e) {}
  if (ini) aplica(true, false);
})();
```

**Ganchos nos laços que a classe não alcança:**
```js
// carrossel automático: a função que anda checa a pausa
function andarProva() {
  if (!trilho || window.__pausado || Date.now() < pausaAte) return;
  /* … */
}
// vídeo em laço: o laço e a volta à tela checam a pausa; os eventos param/retomam
function laco() { raf = 0; if (!naTela || window.__pausado) return; /* … */ }
d.addEventListener('lp:pausar', function () { ativo.pause(); if (raf) { cancelAnimationFrame(raf); raf = 0; } });
d.addEventListener('lp:retomar', function () {
  if (!naTela) return;
  var pr = ativo.play(); if (pr && pr.catch) pr.catch(function () {});
  if (!raf) raf = requestAnimationFrame(laco);
});
// … e no IntersectionObserver da capa: if (naTela && !window.__pausado) { …play… }
```

### Como provar (antes de publicar)
1. Prints em **1440×900**, **390×725** e **360×640** (o botão não encosta no aviso da 1ª dobra) e um rolado (`innerHeight × 1,6`) em 390×844 (o botão subiu com a barra).
2. Clicar: `html` ganha `pausado`, `aria-pressed="true"`, o ícone vira ▶, o letreiro para, o evento da capa assume o estado parado, o carrossel não anda, o vídeo pausa. Clicar de novo: tudo volta. Recarregar: continua pausado.
3. Lighthouse: Acessibilidade e Agentic continuam 100.
4. Com `prefers-reduced-motion` ligado nada muda (o estado já é o mesmo).

### O que não fazer
- `html.pausado *{animation-play-state:paused !important}` para tudo: congela a entrada do título a 16% (ilegível) e deixa a luz da capa atravessada no rosto. O estado parado é o do reduced-motion, **peça a peça**.
- Pausa no hover como "mecanismo" · botão grande ou colorido · esconder o botão no celular (é onde a WCAG mais pesa) · pôr o botão antes da `.barra` no HTML.

### Aceite
- [ ] Botão presente em toda página com algo que se move > 5 s.
- [ ] Todas as peças da tabela "sim" param; nenhuma congela no meio.
- [ ] Celular: botão sobe só com a barra; não encosta na 1ª dobra em 725/640.
- [ ] `aria-pressed`/`aria-label` alternam; `localStorage` lembra; evento `pausa_animacoes` dispara.

---

## 2. O evento dinâmico da capa

### A regra
**Cada cliente ganha UM evento dinâmico na primeira dobra, e ele sai do instrumento, do sintoma, do gesto, do rito ou do produto daquele cliente — nunca de um catálogo de efeitos.** É o que faz a pessoa parar. **Se o efeito serviria para qualquer negócio, está errado.**

### 2.1 Casos que funcionaram (como padrão de raciocínio)

**Dermatologia — a lente do dermatoscópio.** Uma lente circular passeia em laço sobre o retrato e amplia o que está embaixo, com o retículo do aparelho. Três credenciais espalhadas pela foto acendem quando a lente passa. Cursor ou dedo **tomam o volante**; ao sair, o passeio recomeça de onde parou. *Por que funciona:* o dermatoscópio é o instrumento e a metáfora do método — "olhar de perto". Comunica sem uma palavra.

**Coloproctologia — a luz que revela.** Uma lâmina de luz de negatoscópio atravessa o retrato em diagonal e acende, **uma por vez**, três marcas de confiança; a mesma luz varre as pílulas de sintoma na dobra seguinte. *Por que funciona:* nasce do **gesto real** da médica nas fotos (segurando um filme de exame contra a luz) e da **dor real do paciente**, que nessa especialidade é vergonha e adiamento — a pessoa se reconhece na pílula sem dizer nada. *Como:* **100% CSS** — `@keyframes` de `transform`/`opacity` com `animation-delay` escalonado; o JS só pausa fora da tela e cede o volante ao ponteiro.

> **Os delays se calculam, não se chutam.** Para a luz varrer de −25% a 125% (percurso de 150%) e acender uma marca na altura `y` (%): `delay = duração × (y + 25) / 150`. Janela acesa de **1,7 s em 9 s**, para que duas marcas nunca fiquem abertas juntas — "um rótulo por vez" resolvido na aritmética.

**Oftalmologia — a névoa da catarata que o feixe da lâmpada de fenda desfaz.** No carregamento, uma névoa leitosa cobre a foto e sai pela direita com a luz grudada na borda; depois o feixe volta a passar, discreto, a cada 9 s. *Por que funciona:* nasce do **sintoma** (visão embaçada) e do **instrumento** (o feixe). Quando a foto da capa foi trocada pela recepção da clínica, o evento ficou — ele é do sintoma e do instrumento, não da foto. *Como:* 100% CSS, só `transform` e `opacity`; a névoa não é imagem, então o LCP continua sendo a foto (celular 99, desktop 100). A luz fica na borda esquerda de um elemento do tamanho da caixa (em %, o `translateX` mede o próprio elemento). A primeira versão era uma linha de 2 px que, num print parado atravessando o rosto, parecia defeito de tela: a luz é uma **faixa com as bordas dissolvidas**.

**Buffet/evento — a mesa se apresenta.** Na capa, a foto da mesa montada (tirada do vídeo do próprio evento). As palavras da arte da campanha ("Bolos", "Salgados", "Doces") acendem **um por vez**, cada uma com um ponto sobre a comida real, em ciclo de 9 s. *Por que funciona:* é o anúncio dito com a comida do dia — quem chegou pela arte vê as mesmas palavras sobre o que vai encontrar. *Como:* 100% CSS (`animation-delay: calc(var(--i) * 3s)`, janela acesa de 5% a 27% do ciclo — nunca dois juntos). A cena tem a proporção da foto e cobre o palco por `max(100cqw, 100cqh)` (container query), então os rótulos ficam em **% da foto** sem JS de medida. Âncoras do desktop (`--x/--y`) e do celular (`--xm/--ym`); no celular os três cabem acima do texto. O JS só pausa fora da tela e mede o 1º ciclo (`capa_ciclo`).

**Advocacia do consumidor — a lei, marcada.** Sete trechos **reais** da lei (conferidos no texto oficial) passam um por vez no **pé da capa, como a nota de rodapé de um documento**; um marca-texto corre sobre o trecho que interessa a quem lê, e "Aconteceu comigo" abre o formulário com aquele assunto marcado. *Por que funciona:* a lei é o instrumento do advogado; o trecho marcado diz ao visitante que aquilo é um direito dele — sem promessa e informativo, como a OAB pede. *Como:* 100% CSS, um ciclo com uma janela de 1/n por trecho; os `@keyframes` **saem do gerador** (dependem de quantos trechos há). Fora do rosto e fora do título (descartados "sobre a foto", que cobria o terno, e "acima do título"). No celular, só o trecho entre aspas; **some abaixo de 700 px de altura**.

**Telecom — o chip que atravessa a página.** Um chip em 3D percorre a página conforme a rolagem, girando e mudando de escala em sete poses; as trilhas acendem conforme o formulário é preenchido. *Por que funciona:* o produto é um chip; a marca é velocidade.

**Confeitaria — o produto que atravessa a página.** A torta da própria casa, recortada, pousa na capa, desce até um anel no meio da página e termina num arco ao lado da foto da confeiteira. *Por que funciona:* no negócio de produto, o produto **é** a promessa e vira o fio da página. *Como:*
1. **Recorte** do assunto pelo recurso nativo de remover fundo do sistema; a borda vem com a cor do fundo original e deixa halo — recuar a máscara e trocar a cor da franja pela do interior vizinho.
2. **AVIF com alfa** de 520 a 1460 px (18–84 KB) e WebP com alfa de reserva.
3. **Vagas, não coordenadas:** cada dobra tem uma caixa vazia onde o produto pousa; o CSS posiciona a caixa em cada tela; o JS lê as caixas depois do quadro e interpola posição, escala e giro pela rolagem num `transform` só. Com o produto numa vaga, nada se escreve (ele rola junto). O produto mora na vaga da capa, então é o LCP e fica ali sem JS.
4. **O caminho se desenha para não cobrir nada:** cada eixo anda no seu tempo (desce e encolhe primeiro, depois desliza); um "salto" no meio encolhe mais 28%; em linha reta passaria por cima do título e do rosto.
5. **No celular não há lado para desviar:** no meio do caminho o produto quase some (opacidade 0,08) e reaparece na vaga.
6. **Itens girando em volta do produto, com a dobra presa:** **prender, não travar** — a seção ganha altura extra (`--pino`: 140% da tela no desktop, 120% no celular) e o palco interno fica `sticky`; rolar é o que gira; ao fim, solta sozinha (travar a rolagem por JS prende quem rola rápido e briga com dedo e teclado). O giro segue a rolagem com atraso medido no tempo: `atual += (alvo − atual) × (1 − e^(−dt/0,14))`. A âncora é o **ícone**, não o centro da caixa. Girando, só ícone e título; a descrição aparece ao pousar. Item atrás do produto: como `sticky` cria pilha própria, enquanto o produto está no anel aparece uma **cópia parada** dele dentro da pilha e o que viaja fica `visibility: hidden`. **Só prende se couber numa tela** (o JS confere `scrollHeight` e desliga se transbordar).
7. **Medido:** 60 fps e nenhuma tarefa longa (desktop 2× e celular 3×); o anel coube de 360×640 a 1920×1080; Lighthouse 97 celular / 100 desktop.

### 2.2 Ideias por tipo de cliente (ponto de partida, não receita)
| Cliente | Evento possível | Vem de |
|---|---|---|
| Dentista | espelho clínico que revela o sorriso | o instrumento |
| Oftalmologista | foco que sai do embaçado e resolve sobre o título | o sintoma |
| Fisioterapeuta / ortopedista | traço de movimento acompanhando a articulação | o gesto |
| Advogado | selo/carimbo que assenta no lugar; trecho de lei marcado | o rito |
| Arquiteto | planta que vira render conforme a rolagem | a entrega |
| Restaurante | vapor/ingredientes que se montam no prato | o produto |
| Academia | contador de repetição que responde à rolagem | o hábito |
| Ótica | armação que troca de lente sobre o rosto | o produto |
| Veterinário | pegada que segue o cursor | o afeto |

### 2.3 Como construir sem travar o celular
1. **Só `transform` e `opacity`.** Nada de `filter`, `clip-path`, `box-shadow`, `background-size` ou `backdrop-filter` animados em elemento que se move.
2. **Preferir `animation-timeline: scroll()`/`view()`** quando o efeito segue a rolagem — roda no compositor. JS só como plano B, escrevendo **um** `transform` por quadro.
3. **Lupa/janela = dois elementos com transforms opostos:** o círculo anda para um lado, a imagem de dentro para o outro. Sem máscara animada.
4. **No celular o efeito acontece sozinho** (ninguém descobre que pode arrastar): passeio em laço, com pausa para leitura; toque assume; ao soltar, o passeio volta.
5. **Fora da tela, parar de gastar quadro** (`IntersectionObserver`).
6. **`prefers-reduced-motion`:** estado final estático, tudo visível — e é esse mesmo estado que o botão de pausa usa (§1). Ouvir o `change`.
7. **Botão de pausa** ou assentar em ≤ 5 s (WCAG 2.2.2). O evento **não** pausa no hover (o cliente quer o laço mesmo com o cursor na dobra) — por isso o botão é obrigatório.
8. **Um rótulo por vez.** Três cartões abertos ao mesmo tempo se sobrepõem — sempre.
9. **O rótulo é etiqueta, não parágrafo:** uma linha, `white-space: nowrap`. Texto que quebra dobra a altura do cartão (107 px → 52 px depois de encurtar). Se precisa dizer mais, encurte; a frase completa vai no `aria-label` do marcador.
10. **Território:** o efeito não pousa sobre o texto (`data-lupa-min`, âncoras em % da foto, no celular acima de ~38% da foto — ver [anatomia §4c](02-anatomia-da-pagina.md)). No celular, o efeito **não pode empurrar o conteúdo para fora da dobra**.
11. **Medir o efeito:** um evento (`lente_usada`, `credencial_vista`, `capa_ciclo`) diz se prendeu alguém.
12. **Ritmo se mede — print parado não mostra engasgo.** Intervalo entre quadros e tarefas longas, rolando a página inteira. Uma mistura de quadros numa tela só passou em todos os prints e rodava a 30 fps.
13. **O efeito é o diferencial; o botão é sóbrio.** "Nada estático", mas nada que atrapalhe a leitura: cartões encolhem e saem de cima do rosto.

### 2.4 Vídeo curto por IA
**O caminho mais barato:** uma "animação de equipamento" que parece código sofisticado numa página de referência era só **um vídeo curto gerado por IA a partir de uma foto** (848×1056, 12 s, 1,7 MB), em laço — sem biblioteca de animação.

**Receita (fora da 1ª dobra, como segunda camada — p. ex. na dobra do espaço):**
1. Uma foto boa e parada do equipamento, ambiente ou produto (**não da pessoa**).
2. Gerar 5–12 s por imagem→vídeo. Movimento **sutil**: travelling lento, luz que respira, brilho que percorre. Movimento largo denuncia a origem.
3. MP4 ≤ 2 MB, **sem trilha de áudio** e com o índice (`moov`) no início (*fast-start*) — os geradores costumam entregar com áudio inútil e `moov` no fim. Laço que salta: cortar num quadro parecido com o inicial ou fechar com dissolução **gravada no arquivo**.
4. `muted loop playsinline` (sem `muted` o iOS não toca sozinho; sem `playsinline` abre em tela cheia), `poster` sempre, pausa fora da tela.
5. Declarar na página que há mídia gerada por IA.

**Não animar a pessoa.** Vídeo de IA a partir do retrato do cliente: quando o paciente percebe, o dano cai sobre a confiança que a página existe para construir. Animar **ambiente, equipamento e produto**. Se o cliente pedir o próprio retrato animado, o risco é nomeado uma vez e a decisão é dele.

**Vídeo na 1ª dobra (capa):**
- `muted loop playsinline preload="none" aria-hidden="true"`, **sem `autoplay`**, `<source>` AV1 antes do H.264, ≤ 1–2 MB, 5–12 s. O JS dá o `play()` 1–1,5 s depois do `load` ou no 1º gesto. (Com `autoplay`, um vídeo de 1,5 MB disputava a banda com o LCP.)
- **O pôster é o quadro 0 do próprio vídeo, em AVIF, como `<img fetchpriority="high">` POR BAIXO.** O vídeo entra com opacidade 0 e acende no `playing`: sem costura, e com play bloqueado aparece a mesma cena parada, nunca um retângulo preto. Sem JS, fica o pôster.
- **A recusa do play é tratada:** no iPhone em Pouca Energia o Safari recusa todo play sem toque. Engolir a recusa com `.catch(function(){})` deixa o vídeo no pôster para sempre. A recusa **arma nova tentativa** no próximo `touchend`/`pointerup`/`click`/`keydown` (não `touchstart` nem `scroll`), e o mesmo toque destrava as outras cópias.
- Fora da capa, com `autoplay`: o script `defer` roda depois do início, e o `playing` já passou — checar `!paused` antes de esperar o evento.
- **Laço que salta → dissolução entre duas cópias:** a de cima entra por cima da de baixo (1,1 s) e a de baixo só some depois de coberta (duas camadas a 50% deixariam o fundo vazar). Mesma URL: a segunda cópia sai do cache. O `ended` é a rede de segurança do `requestAnimationFrame`, que não roda em aba oculta.
- **Pessoa no meio do quadro, em vídeo: recuar a CAIXA** (66% à direita, `object-fit: cover`, máscara de uma camada dissolvendo a borda esquerda; no celular, os 57% de cima dissolvendo para baixo), não recodificar alargando.

**O porteiro do vídeo — olhar os 9 quadros, não o primeiro** (folha de contato de 0 a 8 s):
1. **Tem terceiro no quadro em algum momento?** (Porta-retratos de família numa estante entraram no quadro com o avanço da câmera; recorte não resolve — regerar a partir de foto sem eles.)
2. **Onde está a pessoa?** No meio do quadro é onde mora o texto.
3. **O último quadro emenda com o primeiro?** Senão, corte seco a cada ciclo.
4. **Resolução:** 720p vira 1,25× em 1440 e 1,5× em 1920 (≈ 2,5× em retina). Capa pede 1080p (ou 4K).
5. **O arquivo:** trilha de áudio e `moov` no fim.

### 2.5 Quando a rolagem arrasta o vídeo (cena)
- **Não arraste o `<video>` — desenhe uma sequência de quadros num `<canvas>`.** Vídeo de IA sai com um quadro-chave em centenas: cada `currentTime` novo decodifica desde o começo e a rolagem trava. Extrair todos os quadros na ordem de **apresentação**, gravar AVIF (q≈72, sem perfil de cor); dois cortes — o quadro inteiro no desktop e, no celular, só a fatia que ele mostra.
- **Qualidade:** três perdas empilham — cor clareada pela extração, compressão manchando a pele ampliada e o canvas ampliando com suavização "low". O teto é a fonte: gerar o vídeo em 1080p.
- **Suave de verdade:** (1) esqueleto primeiro (1 quadro a cada 16), depois o que está à frente; o que falta é coberto pelo quadro pronto mais próximo; (2) decodificar fora da thread (`createImageBitmap`) e só numa janela, com `close()` no que sai (todos decodificados dariam ~700 MB); (3) misturar vizinhos pelo compositor com **duas telas empilhadas**, a de cima só mudando `opacity` (dois `drawImage` numa tela só derrubaram o desktop para 30 fps); (4) suavizar pelo tempo: `atual += (alvo − atual) × (1 − e^(−dt/τ))`, τ entre 0,04 e 0,11 s (fator fixo por quadro faz 120 Hz andar o dobro de 60); (5) ler todo o layout antes de escrever.
- **Os quadros esperam o 1º gesto** (ou o `load`): baixados com a página, 4–7 MB levaram o LCP do celular a 17,7 s. Pôster = quadro 0 em AVIF, no **mesmo recorte** do canvas (senão a troca pula). Resultado: LCP 1,5 s e 60 fps.
- **No celular, rebaixar:** pôster + laço ≤ 1 MB, ou 96–120 quadros se a medição aprovar; ≤ 40 quadros vivos; teto por memória.
- **Estrutura:** palco `position: sticky; top: 0; height: 100svh` e os textos por cima com `margin-top: -100svh`; a altura da cena é a soma das dobras de texto. Canvas com **largura explícita**.
- **Texto que sai: por máscara, não por opacidade** — um parágrafo alto apagado por opacidade fica inteiro sobre o rosto; a máscara numa linha fixa da tela faz sumir linha a linha. A linha nunca acima do topo do texto da capa em repouso. `animation-fill-mode: backwards`, não `both`.

### Aceite do evento
- [ ] Nasce do instrumento/sintoma/gesto/rito/produto **deste** cliente; não serviria para outro negócio.
- [ ] Só `transform`/`opacity`; CSS quando possível; pausa fora da tela; estado parado definido (reduced-motion = pausa).
- [ ] Um rótulo por vez, em uma linha; nunca sobre o texto nem no olho/boca.
- [ ] Cabe na dobra do celular (725/640) sem empurrar conteúdo.
- [ ] 60 fps, 0 tarefas longas, LCP inalterado.
- [ ] Evento de medição do efeito disparando.

---

## 3. A dobra de avaliações do Google

### A regra
Padrão em toda página (exceto advocacia). Da mais recente para a mais antiga, em carrossel, com a **foto de cada pessoa**, nota e contagem sempre da API, atualização em minutos. Não é opcional e não muda de cliente para cliente. Anatomia visual em [anatomia §6b](02-anatomia-da-pagina.md).

### A arquitetura: a chave é da agência, o lugar é do cliente — num serviço só
- A chave do Google **nunca vai ao navegador**. Fica em variável de ambiente secreta de **um serviço central** de avaliações (uma função `api/` funciona em projeto estático, sem framework); as páginas só apontam para ele. Cliente novo **não configura nada**, e bug corrigido na função conserta todos os clientes de uma vez.
- Na página, **a única linha que muda**:
```html
<section id="avaliacoes"
  data-avaliacoes="https://avaliacoes.exemplo.com.br/api/avaliacoes?lugar=PLACE_ID_DO_CLIENTE">
```
- Busca **por `?lugar=<place_id>`**, não por nome (numa franquia, a busca por nome puxou outra unidade). Sem Perfil próprio: o Perfil do grupo/matriz, com a atribuição dizendo de qual unidade é.
- A chave é **sem restrição de aplicativo** (a chamada é servidor a servidor; restrição por referenciador quebraria). O serviço se protege com **origens aceitas** (sufixos permitidos — ao publicar em domínio próprio, acrescentar e reimplantar) e um **teto diário** de lugares novos (ex.: 80).
- **Faturamento separado = chave separada.** Empresas diferentes não compartilham a mesma chave/serviço.
- Variável nova não entra em deploy que já existe: reimplantar depois de colar.

### Duas fontes, em cascata (dentro do serviço)
| fonte | o que dá | o que exige |
|---|---|---|
| **API do Perfil da Empresa (Business Profile)** | **todas**, paginadas; atualização em minutos (cache de 5 min) | liberação do Google + OAuth do dono do perfil (perfis que a agência gerencia) |
| **Places API (New)** | **no máximo 5**, sem paginação, escolhidas pelo Google | só a chave |

Sem chave ou com erro → `{ok:false}` e vale a lista escrita no HTML.

### A API SOMA, não substitui
A Places devolve 5 e **quem escolhe quais é o Google** — numa página, as 5 eram mais antigas que nove das 28 já publicadas; substituir teria custado 23 cartões. O front compara por **nome + início do texto**: o que já existe é ignorado, o que é novo entra **na frente**. Nota e contagem, essas sim, sempre da API.

### A semente: a dobra nasce cheia
As avaliações lidas na montagem ficam num `<script type="application/json" id="prova-semente">` dentro do HTML, **da mais recente para a mais antiga**, com a data de cada uma (para o "há x dias" ser **calculado** no navegador, nunca congelado). A dobra não espera rede e funciona sem chave. **Texto e nome verbatim** — nunca editar avaliação de ninguém; só escolher quem entra.

### Carregamento e acessibilidade
- **A API é chamada perto da dobra, nunca no load:** observador com margem de ~1500 px + rede de segurança pela rolagem.
- Estrelas de cada cartão com `role="img"` + `aria-label` (num `<span>` sem papel, o `aria-label` é proibido e derruba Acessibilidade e Agentic).
- Texto inserido com `textContent`, **nunca `innerHTML`**.
- Fotos: `authorAttribution.photoUri`. Quem não tem foto recebe do próprio Google um círculo colorido com a inicial — é o avatar real. O fallback próprio (inicial em cor da marca) só entra se a URL morrer. `loading="lazy"` e `referrerpolicy` **antes** do `src` (depois, não valem e o navegador baixa todas de uma vez).
- Carrossel: anda a cada 5 s, para 9 s ao toque, para fora da tela, com movimento reduzido e no botão de pausa (§1); barra fina de posição, não bolinhas.
- Atribuição "Fornecido pelo Google" e link "Ler todas as avaliações no Google" sempre presentes.

### Três coisas que não são curadoria, são correção
1. Avaliação cujo texto capturado é a **resposta do dono** não entra — publicar aquilo como depoimento é falso.
2. Nome que é **endereço de e-mail** vira só o primeiro nome (não se publica e-mail de terceiro).
3. Avaliação de pessoas com **o mesmo sobrenome do cliente** — avisar uma vez (numa página eram 7 de 30; quem repara desconta a dobra inteira). Não esconder sem pedido.

Avaliação que cita **preço**: avisar (regra da casa: preço não vai na página).

### Curadoria ≠ supressão
Nota e contagem **totais** e o link "ler todas" sempre. Em saúde, republicar depoimento no site faz dele publicação **do profissional** (CFM 2.336/2023: "sites" estão na lista), e o depoimento tem de ser **sóbrio, sem adjetivo de superioridade nem promessa de resultado**. O filtro existe no código (`AVALIACOES_CURADORIA`) e vem **desligado**. Levantar o ponto **uma vez**, com o texto na mão, e seguir a decisão de quem assina. Se a curadoria do serviço central vale para todos os clientes, e um profissional pedir o filtro e outro não, filtrar **no front** daquele cliente.

### Nunca `aggregateRating` no JSON-LD
A política do Google proíbe usar avaliação de terceiro como avaliação própria do site.

### O Perfil é o dono da prova social
Cliente **sem** Perfil (nem do grupo) não tem a dobra — conferir antes de prometer. Melhorar a nota é trabalho **no Perfil**, não na página.

### Advocacia
Avaliação de cliente é o depoimento que os tribunais de ética da OAB tratam como captação: **a dobra não entra**. O Perfil pode ser linkado junto do endereço. Declarar na página: `<meta name="lp-excecao" content="avaliacoes:advocacia">`.

### O prompt pronto (colar numa sessão nova, dentro da pasta do projeto do cliente)

```
Quero adicionar a dobra de avaliações do Google nesta página, no padrão da matriz.

Antes de escrever qualquer código, leia:
- doutrina/06-componentes.md, seção 3 (esta dobra) e seção 1 (botão de pausa);
- doutrina/02-anatomia-da-pagina.md, §6b (o que a dobra mostra) e §6e (o carrossel);
- se o cliente for da área da saúde, as regras do conselho sobre republicar depoimento.

O que é da agência e não muda:
- As páginas NÃO guardam chave. Elas apontam para o serviço central de avaliações
  (URL em configuração da agência). A chave do Google vive só nesse serviço,
  como variável secreta. Se o serviço ainda não aceitar a origem desta página,
  me avise para incluir o sufixo nas origens aceitas e reimplantar.

O que muda neste cliente:
- O PLACE_ID do Perfil da Empresa (atributo data-avaliacoes da seção, com ?lugar=).
- O link "Ler as avaliações no Google" (cid do Perfil).
- Os textos da dobra (etiqueta, headline).

Como fazer:
1. Abra o Perfil do cliente no Google Maps, leia a nota, a contagem e as avaliações
   com texto, e escreva as publicáveis na <script type="application/json" id="prova-semente">
   do HTML — da mais recente para a mais antiga, com a data, texto e nome VERBATIM.
2. Confira antes de publicar: avaliação cujo texto é na verdade a RESPOSTA do dono
   não entra; nome que é e-mail vira só o primeiro nome; me avise se houver avaliação
   de gente com o mesmo sobrenome do cliente ou que cite preço.
3. Se for da área da saúde: me diga UMA vez o que o conselho diz sobre republicar
   depoimento e me deixe decidir se liga a curadoria (AVALIACOES_CURADORIA). Não decida por mim.
4. A API SOMA, não substitui. Nota e contagem sempre da API; avaliação nova entra
   na frente; o que já existe fica.
5. Carrossel: anda a cada 5 s, para 9 s ao toque, para fora da tela, com movimento
   reduzido e no botão de pausa; barra fina de posição (não bolinhas); "há x dias"
   calculado da data; textContent, nunca innerHTML; estrelas com role="img".
6. Chame a API só perto da dobra (observador com margem ~1500 px + rede pela rolagem).
7. Não marque aggregateRating no JSON-LD.
8. Atualize o hash/versão dos assets, publique a prévia e me mostre: o serviço
   respondendo "ok": true para este lugar, o número de cartões no ar e a medição
   da dobra em 390×725 e 360×640.
9. Registre no LEIA-ME.md do projeto o que foi feito e o que ficou pendente.
```

### Aceite da dobra
- [ ] `data-avaliacoes` com `?lugar=` do Perfil certo (ou do grupo, com atribuição da unidade).
- [ ] Semente no HTML, ordenada, verbatim, com datas; "há x dias" calculado.
- [ ] Nota e contagem da API; link "ler todas"; "Fornecido pelo Google".
- [ ] API chamada só perto da dobra; nenhuma conexão de terceiro no carregamento.
- [ ] Carrossel automático com parada ao toque, fora da tela, reduced-motion e botão de pausa.
- [ ] Nenhuma resposta do dono, nenhum e-mail publicado; sobrenome e preço avisados.
- [ ] Sem `aggregateRating`; Acessibilidade e Agentic 100.
- [ ] Advocacia: dobra ausente e exceção declarada na página.
