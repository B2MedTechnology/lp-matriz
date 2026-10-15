# Doutrina da cena — a página com vídeo na rolagem, passo a passo

A **receita inteira** da página `<slug>-video`, em que o vídeo do cliente anda com a rolagem — do vídeo gerado por IA ao
deploy. Siga **na ordem**: cada passo depende do anterior. Como gerar e aprovar o vídeo está no `README.md`; aqui está
como ele vira página.

> **A página em uma frase.** Um vídeo de 8 s do cliente vira **192 fotos**. A página as desenha num `<canvas>` fixo na
> tela, **uma por posição da rolagem**, enquanto os textos da capa e do "quem é" rolam por cima, à esquerda. Quem rola
> para baixo vê o vídeo andar; quem para, vê o vídeo parar; quem sobe, vê voltar. Da faixa de números em diante, a
> página é a de sempre.

Os números de referência abaixo ("caso de origem") vêm de páginas reais medidas: 60 fps, 98–100 no PageSpeed do celular.

---

## 0. A lógica — por que é assim (leia antes de copiar qualquer linha)

Cada decisão abaixo foi tomada porque a alternativa óbvia **falhou de verdade**. Se você mudar uma delas, está voltando
para um problema que já foi medido.

| # | a decisão | por quê | o que acontece se fizer diferente |
|---|---|---|---|
| 1 | **Sequência de fotos num `<canvas>`**, não o `<video>` arrastado | vídeo de IA vem com **1 quadro-chave em 192**: cada salto no tempo decodifica desde o começo | a rolagem trava — no iPhone, pior |
| 2 | **Todos os quadros** (24 por segundo = 192 em 8 s) | a rolagem mostra cada quadro que existe | com 96, "degrau" visível na troca |
| 3 | **Cores cruas** na extração (Swift, não CIImage) e **sem perfil ICC** | o navegador mostra o vídeo com os valores crus | rosto pálido, meios-tons clareados (+8 níveis) |
| 4 | **AVIF q72** | na mesma aparência, é o formato mais leve | WebP q68 mancha a pele ampliada; WebP q88 pesa quase o dobro |
| 5 | **Dois conjuntos:** quadro inteiro no desktop, **quadrado recortado** no celular | o celular só mostra a fatia do meio | pagar por pixel que não aparece (o celular baixaria 7 MB em vez de 4) |
| 6 | **Esqueleto primeiro** (1 quadro a cada 16), depois o que vem **à frente** | com o esqueleto (~0,5 MB) já dá para rolar a cena inteira | rolagem rápida cai em "buraco" preto |
| 7 | **Baixar ≠ decodificar:** todos baixados (comprimidos), só uma **janela** decodificada | decodificados, os 192 ocupariam ~700 MB | o navegador descarta e redecodifica NA HORA de desenhar: engasgo |
| 8 | **Duas telas empilhadas**, a de cima com opacidade | a mistura entre vizinhos fica com o compositor, sem redesenhar | numa tela só, 30 fps no desktop retina |
| 9 | **Suavização pelo TEMPO** (τ entre 0,04 e 0,11 s) | anda igual em tela de 60 e de 120 Hz | fator fixo por quadro: o dobro da velocidade em telas de 120 Hz |
| 10 | **O poster é o próprio quadro 0**, no mesmo recorte do canvas | a troca foto → canvas não muda um pixel | a imagem "pula" quando o canvas assume |
| 11 | **Os quadros só depois que o poster pintou** (no `load` ou no 1º gesto) | 4–7 MB não podem disputar a banda com a 1ª dobra | LCP do celular a 17,7 s no PageSpeed |
| 12 | **O texto sai por MÁSCARA numa linha fixa** da tela | some linha a linha, exatamente onde a linha está | por opacidade, um parágrafo alto fica inteiro por cima do rosto |
| 13 | **Todas as leituras de posição antes de todas as escritas** | uma medida por quadro de tela | o navegador refaz o layout a cada elemento: micro-travadas |
| 14 | **Palco `sticky` + textos com `margin-top` negativo** | a altura da cena = a soma das dobras de texto = a distância que o vídeo percorre | o vídeo termina antes (ou depois) do texto |

### Parâmetros aceitos (medidos)

- Quadros começam a baixar **no `load`** ou no **1º gesto** — espera entre 0 e 2.500 ms depois do `load`.
- **6 a 10** downloads em paralelo (HTTP/2 aguenta 10, e a cena enche antes).
- **τ entre 0,04 s e 0,11 s.** Com 0,11 s, numa passada rápida o vídeo fica ~20 quadros atrás do dedo ("muito delay",
  na palavra de quem testou); com 0,04 s, 6 a 8 quadros.
- **Teto de ~40 quadros decodificados vivos.**
- No celular, quando a cena é só decorativa: pôster + laço curto ≤ 1 MB, ou só o pôster.
- `navigator.connection.saveData` só existe no Chromium — não conte com ele no iPhone.
- Quadro que falha na rede precisa de **retentativa (teto 3)**.
- Vídeo em laço (a variante simples): `<source>` AV1 antes do H.264.
- Movimento automático com mais de 5 s precisa de **botão de pausa** (WCAG 2.2.2). A cena por rolagem só se mexe quando a
  pessoa rola; o laço automático, não — esse precisa do botão.
- Instrumentação de medida: `?medir-cena&tau=0.04` na URL publica o estado do motor em `window.__cena` (veja §9).

---

## 1. Antes de começar — os quatro portões

Qualquer "não" aqui é conversa com o responsável **antes** de produzir.

1. **Alguém com autoridade decidiu animar a pessoa?** A doutrina da casa manda animar **ambiente, equipamento e produto —
   não gente**: se o paciente ou cliente perceber que é IA, perde a confiança que a página existe para construir.
   Animar gente é **exceção decidida e registrada**, com a frase de aprovação, no registro de decisões do projeto.
2. **A foto de entrada** (a que vai virar vídeo) passa no porteiro:
   - plano geral ou médio, **horizontal**, no lugar de trabalho do cliente;
   - a pessoa no **terço DIREITO**, ocupando no máximo **~40% da largura** (a câmera vai avançar e ela cresce; e o celular
     só mostra a fatia do meio);
   - **parede calma e mais escura à esquerda** — é onde o texto mora;
   - **nenhum terceiro:** porta-retratos de família, outras pessoas, pacientes. Num caso real, porta-retratos de família
     apareciam nos 8 s e derrubaram o vídeo — **apague na foto de entrada, antes de gerar**; borrar no vídeo não funciona
     (a câmera se move);
   - **nenhum dado sensível:** dê zoom em telas, papéis e crachás (num caso real, a capa quase foi ao ar com o nome e o
     prontuário de um paciente na tela de um aparelho);
   - nenhuma marca de terceiro.
   A ferramenta `analisar-fotos.mjs` aplica esses portões, mas o olho humano confere.
3. **A máquina tem as ferramentas:** Python 3 com **Pillow ≥ 11.2** (grava AVIF:
   `python3 -c "from PIL import features; print(features.check('avif'))"` tem de dar `True`), **Swift** (Command Line
   Tools do Xcode; ou ffmpeg, veja o `README.md`), Google Chrome (as medições), `npx` (o Lighthouse) e a CLI do serviço de
   hospedagem logada.
4. **A base da página:** o projeto-matriz da landing page, com gerador, template, CSS e JS, e o contrato de marcadores
   do §6 no template.

---

## 2. Passo 1 — Gerar o vídeo

Pela esteira do `README.md` (passos 1 a 5). O que importa para a cena:

- **Configuração:** 16:9 · 24 fps (ou 30) · **8 s** · **1080p no mínimo** (4K se o orçamento permitir) · qualidade máxima,
  nunca um modo "web" · áudio não importa (a cena não usa).
- **O arco da história.** A rolagem conta o vídeo do começo ao fim, e as duas pontas têm papel:
  - o **1º quadro é a capa** e o poster: tem de ser bonito parado (trabalhando, escrevendo, examinando);
  - o **último é o "quem é"**: a pessoa olha para a câmera, postura de apresentação.
- **Movimento sutil:** a câmera avança devagar (*push-in* de 3–5%), plano contínuo, sem cortes. Nada entra no quadro.
  Mãos longe da lente (a IA erra mãos), sem fala, sem texto em telas.
- **Confira o arquivo antes de seguir:** 8 s em 1080p com menos de ~8 MB (ou 4K com menos de ~30 MB) veio **comprimido
  demais** — peça de novo em qualidade máxima. Se o 4K vier de *upscale* da ferramenta, compare o rosto com a foto: a IA
  mexe na fisionomia.
- **Guarde no projeto**, em `insumos/originais/video-<cliente>-original.mp4`. Pasta temporária some entre sessões.

> **Por que 1080p (ou 4K) se a página usa 1280×720?** O vídeo ocupa a **altura inteira** da tela no desktop. Num notebook
> retina isso é ~1.600–2.200 px físicos: um vídeo de 720p é ampliado 2,2–3× e fica mole. O vídeo grande é a **matriz**:
> dele saem os dois conjuntos já reduzidos, e reduzir de uma fonte maior dá imagem mais nítida que ampliar uma menor. Um
> caso de origem teve exatamente esse teto: veio em 720p a 0,074 bit por pixel.

---

## 3. Passo 2 — O porteiro do vídeo (a folha de 9 quadros)

```bash
node ferramentas/conferir-video.mjs --video insumos/originais/video-<cliente>-original.mp4 --inicio <foto-inicio> [--fim <foto-fim>]
# ou só a folha, sem IA:
swift ferramentas/quadros-video.swift insumos/originais/video-<cliente>-original.mp4 /tmp/porteiro
```
Abra a folha e confira **todos** os quadros, não só o primeiro:
- [ ] nenhum terceiro em **nenhum** quadro (porta-retrato, pessoa, tela com dado);
- [ ] a pessoa fica à direita o tempo todo, e a esquerda continua calma (o texto vai ali);
- [ ] rosto e mãos sem deformação do começo ao fim;
- [ ] o 1º quadro serve de capa parada; o último serve de "quem é".

Qualquer "não" → gerar de novo, com o conserto **na foto de entrada** (ou no prompt).

---

## 4. Passo 3 — Extrair todos os quadros, com as cores cruas

```bash
mkdir -p /tmp/seq
swift ferramentas/sequencia-video.swift insumos/originais/video-<cliente>-original.mp4 /tmp/seq 1
ls /tmp/seq/*.png | wc -l          # 8 s × 24 fps = 192
```
- O último argumento (`1`) é o passo: **1 = todos os quadros**. Não pule quadros.
- Os PNG saem **sem perda**, nomeados pelo tempo de **apresentação** (com quadros B, a ordem em que o decodificador entrega
  não é a de tela) e com os **valores crus** do decodificador.
- ⚠️ Não extraia com `CIImage`, com o Preview nem com um conversor qualquer: todos aplicam a gama de vídeo da Apple e
  clareiam os meios-tons. Medido num caso real: o `<video>` no Chrome dava brilho médio 111,8; o quadro extraído por
  `CIImage`, 120,7 — rosto pálido ao lado do vídeo.
- Sem macOS: ffmpeg com conversão só de matriz (comando no `README.md`), e **confira o brilho** contra o `<video>`.

---

## 5. Passo 4 — Codificar em AVIF, nos dois conjuntos

**Os dois cortes:**
- **Desktop:** o quadro inteiro, reduzido para **1280×720** (com vídeo 4K, dá para subir para 1600×900 se o peso couber —
  alvo: **cada conjunto com até ~7 MB**).
- **Celular:** um **quadrado com a altura do quadro**, centrado na pessoa. Onde cortar:
  **`x0 = (largura − altura) × foco`**, em que `foco` é a posição da pessoa no quadro (0 = esquerda, 1 = direita) — o mesmo
  `--foco` que o CSS do celular vai usar. Exemplo: (1280 − 720) × 0,51 ≈ **287** → o quadrado vai de x 287 a 1007.
  Confira no **primeiro e no último** quadro: a câmera avança, e a pessoa tem de caber no quadrado nos dois.

```bash
python3 ferramentas/cena-avif.py /tmp/seq 0.51 --saida site/assets/video/cena --poster site/assets/img
du -ch site/assets/video/cena/cena-*.avif  | tail -1      # caso de origem: 6,84 MB (35 KB por quadro)
du -ch site/assets/video/cena/movel-*.avif | tail -1      # caso de origem: 4,35 MB (22 KB por quadro)
```
O núcleo do `cena-avif.py`, para quem quiser entender:
```python
im = Image.open(f).convert('RGB')
im = Image.frombytes('RGB', im.size, im.tobytes())        # tira o perfil ICC (o convert() o MANTÉM)
d = im if im.size == DESK else im.resize(DESK, Image.LANCZOS)
d.save(SAIDA / f'cena-{i:03d}.avif', 'AVIF', quality=72, speed=6)
lado = d.height; x0 = round((d.width - lado) * FOCO_MOVEL)
d.crop((x0, 0, x0 + lado, lado)).save(SAIDA / f'movel-{i:03d}.avif', 'AVIF', quality=72, speed=6)
```
- **Nomes com 3 dígitos**, a partir de `000`, e o **mesmo número de quadros nos dois conjuntos** — o gerador para se forem
  diferentes.
- Passou de ~7 MB num conjunto? Baixe a qualidade para 65 ou o tamanho do desktop. **Não** corte quadros (volta o degrau).
- **A pessoa à esquerda do vídeo?** Não espelhe (o texto de telas e roupas sairia ao contrário). Mude o corte: `--foco`
  baixo no desktop (ex.: 0,15, e o poster em `15% 50%`) e o quadrado do celular com foco ~0,10. Medido assim: 60 fps e até
  38 quadros vivos.

**O poster** — a foto que fica na tela até o canvas assumir — é o **próprio quadro 0**, nos dois recortes
(`capa-video.avif` e `capa-video-movel.avif`, que o `cena-avif.py` já copia). Faça também um JPEG de reserva do quadro 0
(navegador sem AVIF), a partir do PNG cru `q000.png`, sem perfil ICC.

---

## 6. Passo 5 — O HTML: o gerador monta a página

**O contrato do template.** A cena substitui a abertura inteira (capa + números + "quem é") e reusa os textos do próprio
template — a versão com vídeo nunca guarda uma segunda cópia do texto. Por isso o template precisa destes marcadores,
exatamente assim (o miolo começa na linha **seguinte** ao marcador de abertura, e o de fechamento fica numa linha **só dele**):
```html
<main id="conteudo">
<!-- troca:abertura -->
<section class="capa capa--fundo" id="capa">
  <figure class="palco">…a foto da capa e o evento dinâmico…</figure>
  <!-- bloco:capa-texto -->
  <div class="capa__env">…assinatura (nome e registro profissional), h1, subtítulo, botão, aviso…</div>
  <!-- /bloco:capa-texto -->
</section>
<!-- bloco:numeros -->
<section class="numeros">…a faixa…</section>
<!-- /bloco:numeros -->
<section class="quem" id="quem">
  <div class="quem__env">
    <figure class="quem__foto">…</figure>
    <!-- bloco:quem-texto -->
    <div class="quem__texto">…etiqueta, h2, parágrafo, <ul class="formacao">, botão…</div>
    <!-- /bloco:quem-texto -->
  </div>
</section>
<!-- /troca:abertura -->
```
⚠️ **As classes são contrato com o JS:** o motor procura `.capa__env > *` (e usa o **primeiro** filho — a assinatura —
para saber onde o texto da capa começa), `.quem__texto > *` e `.formacao li`. Mudou o nome de uma classe, mude no JS.

**O bloco da cena** (`CENA_HTML` no gerador) — `[[CAPA_TEXTO]]` e `[[QUEM_TEXTO]]` são preenchidos com os blocos do
template (são marcadores do gerador, não links):
```html
<section class="capa cena" data-cena>
  <div class="cena__palco" aria-hidden="true">
    <!-- o poster: o quadro 0, escolhido pela MESMA regra de recorte do canvas (ver passo 6) -->
    <picture>
      <source media="(max-width: 900px) and (max-aspect-ratio: 3/5), (min-width: 901px) and (max-aspect-ratio: 159/100)"
              type="image/avif" srcset="../assets/img/capa-video-movel.avif" width="720" height="720">
      <source type="image/avif" srcset="../assets/img/capa-video.avif" width="1280" height="720">
      <img class="cena__poster" src="../assets/img/capa-video.jpg" width="1280" height="720"
           fetchpriority="high" decoding="async" alt="">
    </picture>
    <canvas class="cena__filme" id="cena-filme" data-total="{{QUADROS_N}}"
            data-quadros="../assets/video/cena/cena-{n}.avif?h={{QUADROS_H}}"
            data-quadros-movel="../assets/video/cena/movel-{n}.avif?h={{QUADROS_HM}}"></canvas>
    <span class="capa__veu"></span>
  </div>
  <div class="cena__textos">
    <div class="cena__bloco cena__bloco--capa" id="capa">
[[CAPA_TEXTO]]
    </div>
    <div class="cena__bloco cena__bloco--quem" id="quem">
      <div class="cena__env">
[[QUEM_TEXTO]]
      </div>
    </div>
  </div>
</section>
```
- `fetchpriority="high"` no poster: ele é o maior elemento da 1ª dobra (o LCP). **Nunca** `lazy`.
- O `{n}` do `data-quadros` o JS troca pelo número com 3 dígitos; o `?h=` é o **hash do conjunto** (a pasta é `immutable`
  no cache: trocar os quadros sem mudar a URL não chegaria em ninguém).
- A **faixa de números vem logo depois da cena**, e a **foto do "quem é" sai** (o vídeo já é a pessoa).

**No gerador (Python)** — confira que estes pedaços existem:
```python
# cada página estática ganha a irmã com vídeo: /<slug>/ e /<slug>-video/
VIDEO = {slug: slug + "-video" for slug in PAGINAS_COM_VIDEO}
# a irmã com vídeo: noindex, fora do sitemap, canônica apontando para a estática;
# troca a abertura do template pela cena

def bloco(molde, nome):                               # o miolo entre <!-- bloco:NOME --> e <!-- /bloco:NOME -->
    achados = re.findall(r"<!-- bloco:%s -->\n(.*?)\n\s*<!-- /bloco:%s -->" % (nome, nome), molde, re.S)
    if len(achados) != 1:
        raise SystemExit(f"ERRO: marcador bloco:{nome} aparece {len(achados)} vez(es) no template")
    return achados[0]

def cena_rolagem(molde):                              # capa + quem é dentro do palco, números logo depois
    return (CENA_HTML.replace("[[CAPA_TEXTO]]", bloco(molde, "capa-texto"))
                     .replace("[[QUEM_TEXTO]]", bloco(molde, "quem-texto"))
            + bloco(molde, "numeros"))

# quantos quadros e um hash de cada conjunto (vai na URL); o gerador PARA se os conjuntos diferirem
_CENA = sorted((RAIZ / "site" / "assets" / "video" / "cena").glob("cena-*.avif"))
QUADROS_N = len(_CENA)
QUADROS_H = hashlib.sha1(b"".join(p.read_bytes() for p in _CENA)).hexdigest()[:8] if _CENA else "0"
_CENAM = sorted((RAIZ / "site" / "assets" / "video" / "cena").glob("movel-*.avif"))
QUADROS_HM = hashlib.sha1(b"".join(p.read_bytes() for p in _CENAM)).hexdigest()[:8] if _CENAM else "0"
if _CENAM and len(_CENAM) != QUADROS_N:
    raise SystemExit(f"ERRO: {QUADROS_N} quadros de desktop e {len(_CENAM)} de celular — têm de ser iguais")
```
`QUADROS_N`, `QUADROS_H` e `QUADROS_HM` entram no dicionário de campos da montagem. Resultado: `site/<slug>-video/index.html`,
**noindex, fora do sitemap, canônica apontando para `/<slug>/`** — as duas capas são quase iguais, e indexar as duas é
conteúdo duplicado.

---

## 7. Passo 6 — O CSS da cena

Copiar como está (o gerador embute o CSS no HTML). `--profundo` e `--pag` são tokens do tema da matriz. As máscaras usam a
forma abreviada (`mask:` e `-webkit-mask:` com um só gradiente), que equivale a definir só a imagem da máscara.
```css
.cena{position:relative;isolation:isolate;background:var(--profundo);color:#EDF4F9}
.cena__palco{position:sticky;top:0;height:100vh;height:100svh;overflow:hidden;z-index:1}
.cena__poster,
.cena__filme{position:absolute;top:0;right:0;bottom:0;width:66%;height:100%;display:block;
  -webkit-mask:linear-gradient(to right, transparent 0%, rgba(0,0,0,.45) 14%, #000 32%);
          mask:linear-gradient(to right, transparent 0%, rgba(0,0,0,.45) 14%, #000 32%)}
.cena__poster{z-index:1;object-fit:cover;object-position:40% 50%}
/* --foco é o object-position do canvas: o JS lê daqui para desenhar o quadro com o
   MESMO corte do poster — as duas camadas precisam coincidir, senão a troca pula */
.cena__filme{z-index:2;--foco:.40;will-change:opacity}
.cena__palco .capa__veu{z-index:4}   /* acima das DUAS telas do filme (2 e 3) */
.cena__textos{position:relative;z-index:4;margin-top:-100vh;margin-top:-100svh}
.cena__bloco{min-height:100vh;min-height:100svh;display:flex;align-items:center}
.cena__env{width:var(--pag);margin-inline:auto;padding:clamp(5.5rem,10svh,7.5rem) 0 clamp(3rem,7svh,5rem)}
.cena .quem__texto{width:min(37rem,100%)}
.cena .quem__texto h2{color:#fff}
.cena .quem__texto p{color:rgba(237,244,249,.84)}
.cena .formacao{border-top-color:rgba(186,227,248,.24)}
/* os itens da formação "desdobram": o fio de baixo se desenha e o marcador cresce (--e vem do JS) */
.cena .formacao li{color:rgba(237,244,249,.86);border-bottom-color:transparent}
.cena .formacao li::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:1px;
  background:rgba(186,227,248,.26);transform-origin:left center;transform:scaleX(var(--e,1))}
.cena .formacao li::before{transform:scale(var(--e,1))}
/* palavra por palavra: a capa acende no CARREGAMENTO; o "quem é" com a ROLAGEM (JS).
   ⚠️ fill-mode BACKWARDS, não both: com both o último quadro-chave (opacity:1)
   venceria o estilo do JS e o texto da capa nunca se dissolveria ao sair. */
.cena .pl{display:inline-block}
.cena__bloco--capa h1 .pl{animation:pl-entra .8s cubic-bezier(.2,.7,.2,1) backwards;
  animation-delay:calc(var(--i) * 110ms + 120ms)}
@keyframes pl-entra{from{opacity:.16;transform:translateY(.32em)}to{opacity:1;transform:none}}
.cena__bloco--capa .lead,
.cena__bloco--capa .acoes,
.cena__bloco--capa .aviso-particular{animation:bloco-entra .9s cubic-bezier(.2,.7,.2,1) backwards}
.cena__bloco--capa .lead{animation-delay:.42s}
.cena__bloco--capa .acoes{animation-delay:.56s}
.cena__bloco--capa .aviso-particular{animation-delay:.66s}
@keyframes bloco-entra{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media (max-width:900px){
  /* celular: vídeo nos 57% de cima, dissolvendo para baixo.
     ⚠️ width:100%, NUNCA width:auto com left/right: canvas é elemento SUBSTITUÍDO */
  .cena__poster,
  .cena__filme{left:0;right:auto;width:100%;bottom:auto;height:57%;
    -webkit-mask:linear-gradient(to bottom, #000 0%, #000 56%, transparent 100%);
            mask:linear-gradient(to bottom, #000 0%, #000 56%, transparent 100%)}
  .cena__poster{object-position:51% 50%}
  .cena__filme{--foco:.51}
  .cena__bloco--capa{align-items:flex-end}
  .cena__bloco--quem{align-items:flex-start}   /* o "quem é" começa abaixo do rosto */
  .cena__env{padding:14svh 0 5rem}             /* 44svh deixava um vão escuro de ~300 px entre as dobras */
}
@media (prefers-reduced-motion: reduce){
  .cena .pl,
  .cena__bloco--capa .lead,
  .cena__bloco--capa .acoes,
  .cena__bloco--capa .aviso-particular{animation:none}
}
/* o poster no RECORTE do celular: mesmas condições do <source> e do canvas (caixa do filme com
   largura/altura ≤ 1,05) — centrado, como o canvas desenha o recorte. Sem isto a troca pularia. */
@media (max-width: 900px) and (max-aspect-ratio: 3/5), (min-width: 901px) and (max-aspect-ratio: 159/100){
  .cena__poster{object-position:50% 50%}
}
```

**Os números que você ajusta por cliente:**

| valor | onde | o que decide | como achar |
|---|---|---|---|
| `66%` | largura do filme no desktop | quanto da tela o vídeo ocupa (o resto é o texto) | a coluna de texto tem ~37rem; o vídeo começa logo depois |
| `--foco: .40` | desktop | o corte horizontal: a borda esquerda da pessoa logo depois do texto | print em 1280, 1440 e 1920 — nos três ela tem de ficar fora do texto |
| `--foco: .51` | celular | centra a pessoa no recorte do celular | o mesmo `foco` do passo 4 (o corte do conjunto) |
| rampa `0 → 14% → 32%` | máscara do desktop | a dissolução da borda esquerda na cor de fundo | **uma camada só** de máscara (nada de composição de duas máscaras) |
| `57%` e rampa `56% → 100%` | celular | o vídeo nos 57% de cima, dissolvendo para baixo | a 1ª dobra tem de caber em 390×725 e 360×640 com o texto embaixo |
| `14svh` | respiro do "quem é" no celular | o vão entre o fim da capa e o começo do texto do "quem é" | nada de vão escuro sem texto |

⚠️ **`position: sticky` só funciona se NENHUM ancestral tiver `overflow` hidden ou auto.** O `html` leva
`overflow-x: clip` (não cria contêiner de rolagem) — nunca `overflow-x: hidden` no `body`.

---

## 8. Passo 7 — O JS: o motor inteiro

Vai no JS da página (`defer`), dentro do `(function(){ … })()` principal, que já tem no topo `var d = document`,
`var reduzido = matchMedia('(prefers-reduced-motion: reduce)').matches` e uma função `medir(evento, dados)` que manda o
evento para a medição da página (ou não faz nada). Precisa destes dois ajudantes antes do motor:
```js
  function depoisDoQuadro(fn) {             // ler medidas SÓ depois que o navegador montou a tela
    requestAnimationFrame(function () { setTimeout(fn, 0); });
  }
  function aoPrimeiroGesto(fn, esperaPosLoad) {   // o pesado espera o 1º gesto (ou um tempo depois do load)
    var feito = false, evs = ['scroll', 'wheel', 'touchstart', 'pointerdown', 'keydown'];
    function vai() {
      if (feito) return;
      feito = true;
      evs.forEach(function (ev) { window.removeEventListener(ev, vai); });
      fn();
    }
    evs.forEach(function (ev) { window.addEventListener(ev, vai, { passive: true }); });
    if (d.readyState === 'complete') setTimeout(vai, esperaPosLoad);
    else window.addEventListener('load', function () { setTimeout(vai, esperaPosLoad); });
  }
```

**O motor.** Os valores já vêm com os ajustes medidos depois da 1ª versão: 10 downloads em paralelo, τ = 0,04 s, quadros
no `load`. A retentativa de download (teto 3) é um acréscimo pedido pela revisão e **ainda não medido** nesta forma —
meça (§9) antes de dar como aceito.
```js
  var cena = d.querySelector('[data-cena]');
  var tela = d.getElementById('cena-filme');
  // depoisDoQuadro: a montagem lê medidas (a caixa do canvas, a geometria) — lidas durante a
  // execução do script, custavam 40 ms de layout forçado no celular (PageSpeed)
  if (cena && tela && tela.getContext) depoisDoQuadro(function () {
    var conexao = navigator.connection || {};
    // economia de dados ou 2G: fica o poster parado (os quadros somam 4 a 7 MB). Só o Chromium informa isto.
    var economia = conexao.saveData || /2g$/.test(conexao.effectiveType || '');
    var TOTAL = parseInt(tela.getAttribute('data-total'), 10) || 0;
    var molde = tela.getAttribute('data-quadros') || '';
    var moldeMovel = tela.getAttribute('data-quadros-movel') || '';
    if (reduzido || economia || !TOTAL) return;
    // celular em pé: o conjunto RECORTADO (720×720, centrado na pessoa). O celular só mostra a
    // fatia central do quadro; baixar a largura inteira era pagar por pixel que não aparece.
    var caixa0 = tela.getBoundingClientRect();
    var usaMovel = !!moldeMovel && caixa0.height > 0 && caixa0.width / caixa0.height <= 1.05;
    if (usaMovel) molde = moldeMovel;
    /* DUAS telas empilhadas: a de baixo mostra o quadro da posição e a de cima o SEGUINTE,
       com opacidade = a fração que sobra (em 40,4: o 41 a 40% por cima do 40). Mudar a
       opacidade não redesenha nada — quem mistura é o compositor. Desenhar só acontece
       quando a posição troca de quadro: 1 desenho por quadro, contra 2 a cada nível de
       mistura numa tela só, que no desktop 2× derrubou a rolagem para 30 fps. */
    var tela2 = tela.cloneNode(false);
    [].slice.call(tela2.attributes).forEach(function (a) { if (a.name === 'id' || /^data-/.test(a.name)) tela2.removeAttribute(a.name); });
    tela2.setAttribute('aria-hidden', 'true');
    tela.parentNode.insertBefore(tela2, tela.nextSibling);
    var baixo = { el: tela, ctx: tela.getContext('2d'), mostra: -1 };
    var cima = { el: tela2, ctx: tela2.getContext('2d'), mostra: -1 };
    var opacCima = -1;
    var quadros = [], atual = 0, alvo = 0, anim = 0, dir = 1;
    var ultimoT = 0, sujo = true, dentroAntes = true;
    var W = 0, H = 0, foco = 0.4, topo = 0, curso = 1, vh = window.innerHeight, movel = false, linha = 0;
    var TAU = 0.04;                                       // s; entre 0,04 e 0,11 (ver §0)

    function lim(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }

    /* ── os quadros: BAIXAR e DECODIFICAR são etapas separadas ──
       Comprimidos, os 192 quadros somam 4–7 MB e ficam todos guardados (Blob). Decodificado,
       cada um ocupa 3,7 MB (1280×720×4): os 192 dariam ~700 MB, e o navegador descartava
       decodificados e redecodificava NA HORA de desenhar — o engasgo da rolagem. Só ficam
       decodificados (ImageBitmap: decodifica FORA da thread principal) o ESQUELETO —
       1 a cada 16, que cobre a rolagem rápida — e uma JANELA em volta de onde a pessoa está
       e para onde ela vai. O que sai da janela é fechado na hora (close). */
    var FIXO = 16, blobs = [], baixado = [], baixando = [], emCurso = 0, falhas = [];
    var quer = [], decod = [], emDecod = 0;
    var mapaOk = !!(window.createImageBitmap && window.fetch);
    function fixo(i) { return i % FIXO === 0 || i === TOTAL - 1; }
    function endereco(i) { return molde.replace('{n}', ('00' + i).slice(-3)); }
    // ordem de baixar: o esqueleto do grosso para o fino (0, último, de 64 em 64, 32, 16);
    // depois o que está À FRENTE de onde a pessoa está, no sentido da rolagem — o que
    // ficou para trás custa 3× mais
    var grossa = [0, TOTAL - 1];
    for (var passo = 64; passo >= FIXO; passo = passo >> 1)
      for (var k = 0; k < TOTAL; k += passo) if (grossa.indexOf(k) < 0) grossa.push(k);
    function proximo() {
      for (var q = 0; q < grossa.length; q++) if (!baixado[grossa[q]] && !baixando[grossa[q]]) return grossa[q];
      var c = Math.round(atual), melhor = -1, menor = Infinity;
      for (var i = 0; i < TOTAL; i++) {
        if (baixado[i] || baixando[i]) continue;
        var dd = (i - c) * dir, custo = dd >= 0 ? dd : -dd * 3;
        if (custo < menor) { menor = custo; melhor = i; }
      }
      return melhor;
    }
    function baixar() {
      for (var i; emCurso < 10 && (i = proximo()) >= 0;) buscar(i);
    }
    function buscar(i) {
      baixando[i] = 1; emCurso++;
      var fim = function () { baixando[i] = 0; baixado[i] = 1; emCurso--; baixar(); pedir(); };
      // falhou na rede: tenta de novo até 3 vezes, com espera crescente; depois desiste
      // (o maisPerto() cobre o buraco com o vizinho)
      var falhou = function () {
        falhas[i] = (falhas[i] || 0) + 1;
        if (falhas[i] >= 3) return fim();
        baixando[i] = 0; emCurso--; setTimeout(baixar, 500 * falhas[i]);
      };
      if (!mapaOk) return viaImg(endereco(i), i, fim);
      fetch(endereco(i)).then(function (r) { if (!r.ok) throw r.status; return r.blob(); })
        .then(function (b) { blobs[i] = b; fim(); }, falhou);
    }
    // o caminho antigo, para quem não tem createImageBitmap (ou não decodifica AVIF nele):
    // o <img> decodificado fica guardado inteiro e nunca sai da memória
    function viaImg(src, i, fim) {
      var im = new Image();
      var ok = function () { quadros[i] = im; if (src.indexOf('blob:') === 0) URL.revokeObjectURL(src); fim(); };
      im.src = src;
      if (im.decode) im.decode().then(ok, function () { if (im.complete && im.naturalWidth) ok(); else fim(); });
      else { im.onload = ok; im.onerror = fim; }
    }
    function decodificar(i) {
      decod[i] = 1; emDecod++;
      var fim = function () { decod[i] = 0; emDecod--; pedir(); };
      if (!mapaOk) return viaImg(URL.createObjectURL(blobs[i]), i, fim);
      createImageBitmap(blobs[i]).then(function (bmp) {
        if (quer[i]) quadros[i] = bmp; else bmp.close();     // saiu da janela enquanto decodificava
        fim();
      }, function () { mapaOk = false; decod[i] = 0; emDecod--; decodificar(i); });
    }
    /* A janela, refeita a cada quadro de tela: 2 = decodificar, 1 = pode ficar (folga de
       4 quadros, para não fechar e reabrir o que acabou de sair), 0 = fechar. */
    function manter() {
      var c = Math.round(atual), a = Math.round(alvo), i, j, q;
      var marca = function (lo, hi) { for (var n = Math.max(0, lo); n <= Math.min(TOTAL - 1, hi); n++) quer[n] = 2; };
      for (i = 0; i < TOTAL; i++) quer[i] = 0;
      marca(c - 3, c + 3);                                                        // onde está
      if (a >= c) marca(c, Math.min(a, c + 24)); else marca(Math.max(a, c - 24), c);   // o caminho
      marca(a - 6, a + 6);                                                        // onde vai parar
      if (dir > 0) marca(a, a + 14); else marca(a - 14, a);                      // e o que vem depois
      // a folga vale só para a JANELA. Aplicada também ao esqueleto, prendia ±4 quadros em
      // volta de cada um dos 13 fixos: 115 bitmaps vivos (~425 MB) no fim da descida
      for (i = 0; i < TOTAL; i++) if (quer[i] === 2)
        for (j = Math.max(0, i - 4); j <= Math.min(TOTAL - 1, i + 4); j++) if (!quer[j]) quer[j] = 1;
      for (i = 0; i < TOTAL; i++) if (fixo(i)) quer[i] = 2;                       // o esqueleto, sem folga
      for (i = 0; i < TOTAL; i++)
        if (!quer[i] && quadros[i] && quadros[i].close) { quadros[i].close(); quadros[i] = null; }
      if (emDecod >= 4) return;
      var fila = [], custo = function (x) { var dd = (x - c) * dir; return dd >= 0 ? dd : 0.5 - dd; };
      for (i = 0; i < TOTAL; i++) if (quer[i] === 2 && blobs[i] && !quadros[i] && !decod[i]) fila.push(i);
      fila.sort(function (x, y) { return custo(x) - custo(y); });
      for (q = 0; q < fila.length && emDecod < 4; q++) decodificar(fila[q]);
    }
    function maisPerto(i) {
      if (quadros[i]) return i;
      for (var k = 1; k < TOTAL; k++) {
        if (quadros[i - k]) return i - k;
        if (quadros[i + k]) return i + k;
      }
      return -1;
    }
    function pinta(c, i) {
      var im = quadros[i], iw = im.naturalWidth || im.width, ih = im.naturalHeight || im.height;   // <img> ou ImageBitmap
      var esc = Math.max(W / iw, H / ih), dw = iw * esc, dh = ih * esc;   // object-fit: cover
      c.ctx.drawImage(im, (W - dw) * foco, (H - dh) / 2, dw, dh);
      c.mostra = i;
    }
    function desenhar() {
      if (!W || !H) return;
      var i0 = Math.floor(atual), f = atual - i0, i1 = Math.min(TOTAL - 1, i0 + 1);
      var a = quadros[i0] ? i0 : maisPerto(Math.round(atual));
      if (a < 0) return;
      if (baixo.mostra !== a) {
        // quem já tem o quadro fica com o papel: para a frente, a de cima (que mostrava o
        // seguinte) vira a de baixo; para trás, a de baixo vira a de cima
        if (cima.mostra === a || baixo.mostra === i1) { var t = baixo; baixo = cima; cima = t; }
        if (baixo.mostra !== a) pinta(baixo, a);
        baixo.el.style.zIndex = '2'; baixo.el.style.opacity = '1';
        cima.el.style.zIndex = '3'; opacCima = -1;
      }
      var o = (a === i0 && i1 !== i0 && quadros[i1] && f > 0.005) ? Math.round(f * 1000) / 1000 : 0;
      if (o && cima.mostra !== i1) pinta(cima, i1);
      if (o !== opacCima) { cima.el.style.opacity = String(o); opacCima = o; }
    }

    /* ── os textos: quebra em palavras, preservando <em> e <br> ── */
    function palavras(el) {
      if (el.hasAttribute('data-pl')) return [].slice.call(el.querySelectorAll('.pl'));
      el.setAttribute('data-pl', '');                    // o bloco global das manchetes pula este
      var n = 0;
      (function andar(no) {
        [].slice.call(no.childNodes).forEach(function (f) {
          if (f.nodeType === 3) {
            var frag = d.createDocumentFragment();
            f.textContent.split(/(\s+)/).forEach(function (p) {
              if (!p) return;
              if (/^\s+$/.test(p)) { frag.appendChild(d.createTextNode(p)); return; }
              var s = d.createElement('span');
              s.className = 'pl'; s.textContent = p; s.style.setProperty('--i', n++);
              frag.appendChild(s);
            });
            no.replaceChild(frag, f);
          } else if (f.nodeType === 1 && f.tagName !== 'BR') andar(f);
        });
      })(el);
      return [].slice.call(el.querySelectorAll('.pl'));
    }
    var h1 = cena.querySelector('.cena__bloco--capa h1');
    if (h1) palavras(h1);                                // acende no carregamento (CSS)
    var h2 = cena.querySelector('.cena__bloco--quem h2');
    var h2pl = h2 ? palavras(h2) : [];                   // acende com a rolagem (aqui)
    var capaTxt = [].slice.call(cena.querySelectorAll('.cena__bloco--capa .capa__env > *'));
    var quemTxt = [].slice.call(cena.querySelectorAll('.cena__bloco--quem .quem__texto > *'))
      .filter(function (el) { return el.tagName !== 'UL'; })
      .concat([].slice.call(cena.querySelectorAll('.cena__bloco--quem .formacao li')));
    var ultimoR = -1, mexeu = false;                    // mexeu: a pessoa já rolou (ver textos)

    /* O texto se dissolve numa LINHA FIXA da tela ao subir (ver `linha` na geometria).
       Por MÁSCARA no próprio elemento, não por opacidade: um parágrafo alto, apagado
       pela opacidade, ficava inteiro por cima do rosto enquanto a base dele ainda
       estava abaixo da linha. Com a máscara ele some linha a linha, onde a linha está.
       Só ganha máscara o elemento que está CRUZANDO a linha. */
    function saida(el, r) {
      var rampa = 56;
      if (r.bottom <= linha - rampa / 2) { limpa(el); return 0; }
      if (r.top >= linha + rampa / 2) { limpa(el); return 1; }
      var x = Math.round(linha - r.top);
      var m = 'linear-gradient(to bottom, transparent ' + (x - rampa / 2) + 'px, #000 ' + (x + rampa / 2) + 'px)';
      el.style.webkitMaskImage = m; el.style.maskImage = m; el._mascara = true;
      return 1;
    }
    function limpa(el) {
      if (el._mascara) { el.style.webkitMaskImage = ''; el.style.maskImage = ''; el._mascara = false; }
    }
    function textos() {
      // TODAS as leituras primeiro, depois todas as escritas. Ler a posição, escrever um
      // estilo e ler a do próximo força o navegador a recalcular o layout a cada elemento —
      // era um dos engasgos da rolagem no celular.
      var rc = capaTxt.map(function (el) { return el.getBoundingClientRect(); });
      var rq = quemTxt.map(function (el) { return el.getBoundingClientRect(); });
      var rh = h2 ? h2.getBoundingClientRect() : null;
      capaTxt.forEach(function (el, k) { el.style.opacity = saida(el, rc[k]) ? '' : '0'; });
      quemTxt.forEach(function (el, k) {
        var r = rq[k], fica = saida(el, r);
        if (el === h2) { el.style.opacity = fica ? '' : '0'; return; }   // o h2 entra palavra por palavra
        // entra entre 98% e 84% da tela: no fim da cena o botão do "quem é" fica a ~83%
        // da altura, e com a faixa antiga (95%→75%) chegava só a 62% de opacidade
        var entra = lim((vh * 0.98 - r.top) / (vh * 0.14));
        el.style.opacity = (entra * fica).toFixed(3);
        el.style.transform = 'translate3d(0,' + ((1 - entra) * 22).toFixed(1) + 'px,0)';
        if (el.tagName === 'LI') el.style.setProperty('--e', entra.toFixed(3));
      });
      // o h2 só apaga depois da 1ª rolagem: antes dela, quem não rola (leitor de tela, o
      // PageSpeed) lê com contraste cheio — as palavras a 16% reprovavam o contraste
      if (rh && mexeu) {
        var r = lim((vh * 0.9 - rh.top) / (vh * 0.45));
        if (Math.abs(r - ultimoR) > 0.002) {
          ultimoR = r;
          var n = h2pl.length;
          h2pl.forEach(function (s, i) { s.style.opacity = (0.16 + 0.84 * lim(r * n - i)).toFixed(3); });
        }
      }
    }

    /* ── a conta: rolagem → quadro ── */
    function geometria() {
      vh = window.innerHeight; movel = window.innerWidth <= 900;
      // densidade até 3×: com teto 2 no iPhone (3×) o canvas era ampliado mais 1,5× pelo
      // navegador — duas ampliações bilineares seguidas, uma a mais que o necessário
      var r = tela.getBoundingClientRect(), dpr = Math.min(window.devicePixelRatio || 1, 3);
      var w = Math.round(r.width * dpr), h = Math.round(r.height * dpr);
      if (w && h && (w !== W || h !== H)) {
        W = w; H = h;
        // redimensionar o canvas ZERA o estado do contexto — a suavização volta a ser a
        // padrão do Chrome, "low" (bilinear). Na retina o quadro é ampliado 2,5×: "high"
        // segura o detalhe que o bilinear borra. E apaga a imagem: as duas redesenham.
        [baixo, cima].forEach(function (c) {
          c.el.width = w; c.el.height = h; c.mostra = -1;
          c.ctx.imageSmoothingEnabled = true; c.ctx.imageSmoothingQuality = 'high';
        });
      }
      // o recorte do celular já vem centrado na pessoa: foco no meio; o quadro inteiro usa o --foco do CSS
      foco = usaMovel ? 0.5 : (parseFloat(getComputedStyle(tela).getPropertyValue('--foco')) || 0.4);
      topo = cena.getBoundingClientRect().top + (window.scrollY || d.documentElement.scrollTop);
      curso = Math.max(1, cena.offsetHeight - vh);
      // a linha onde o texto se dissolve: no desktop sob o menu (12%); no celular antes
      // do rosto (40%), mas NUNCA acima do topo do texto da capa em repouso — senão a
      // 1ª dobra nasceria cortada nas telas baixas (em 360×640 o texto começa a 29%)
      var et = cena.querySelector('.cena__bloco--capa .capa__env > *');   // a assinatura
      var repouso = et ? et.getBoundingClientRect().top + (window.scrollY || d.documentElement.scrollTop) - topo : vh;
      linha = movel ? Math.min(vh * 0.40, repouso - 8) : vh * 0.12;
    }
    var marcou = {};
    function rolou() {
      var y = window.scrollY || d.documentElement.scrollTop;
      // abaixo da cena (com folga), rolar o resto da página não pede nada daqui
      var dentro = y < topo + curso + vh * 1.5;
      if (!dentro && !dentroAntes) return;
      dentroAntes = dentro;
      var p = lim((y - topo) / curso), novo = p * (TOTAL - 1);
      if (novo !== alvo) dir = novo > alvo ? 1 : -1;
      alvo = novo;
      [50, 100].forEach(function (m) {
        if (!marcou[m] && p >= m / 100 - 0.02) { marcou[m] = true; medir('cena_video', { marco: m }); }
      });
      sujo = true;
      pedir();
    }
    function pedir() { if (!anim) anim = requestAnimationFrame(quadro); }
    function quadro(t) {
      anim = 0;
      // suavização pelo TEMPO, não por quadro de tela: com um fator fixo por quadro, uma tela
      // de 120 Hz andava o dobro de rápido que uma de 60.
      var dt = ultimoT ? Math.min(0.1, (t - ultimoT) / 1000) : 1 / 60;
      ultimoT = t;
      atual += (alvo - atual) * (1 - Math.exp(-dt / TAU));
      if (Math.abs(alvo - atual) < 0.01) atual = alvo;
      manter();
      desenhar();
      if (sujo) { sujo = false; textos(); }            // texto só depende da rolagem, não do quadro
      if (atual !== alvo) pedir(); else ultimoT = 0;
    }
    function refaz() { geometria(); rolou(); }
    geometria();
    // os quadros (4 a 7 MB) começam no load (o poster, que É o quadro 0 e o LCP, já pintou) ou
    // no 1º gesto, o que vier antes. Baixados JUNTO com a página, disputavam a banda com a 1ª
    // dobra: o LCP do celular foi a 17,7 s no PageSpeed. Esperar mais que o load deixava a
    // pessoa rolar sobre "buracos". Aceito: 0 a 2.500 ms depois do load.
    aoPrimeiroGesto(baixar, 0);
    rolou();
    window.addEventListener('scroll', function () { mexeu = true; rolou(); }, { passive: true });
    window.addEventListener('resize', refaz);
    if (d.fonts && d.fonts.ready) d.fonts.ready.then(refaz);
    if ('ResizeObserver' in window) new ResizeObserver(refaz).observe(cena);
  });
```

**Os botões de ajuste do motor** (mexa só medindo — §9):

| constante | valor | o que faz |
|---|---|---|
| `FIXO` | 16 | o esqueleto: 1 quadro decodificado a cada 16 — cobre a rolagem rápida |
| downloads simultâneos | **10** (1ª versão: 6) | `emCurso < 10` em `baixar()` — HTTP/2 aguenta, e a cena enche antes |
| decodificações simultâneas | 4 | `emDecod >= 4` em `manter()` |
| a janela | ±3 · caminho até 24 · ±6 no alvo · 14 à frente · folga 4 | o que fica decodificado em volta de onde a pessoa está e para onde vai |
| `TAU` | **0,04 s** (1ª versão: 0,11) | a suavização: maior = mais "manteiga" e mais atraso do dedo. Com 0,11 s, numa passada de 1.500 px/s o vídeo fica ~20 quadros atrás do dedo; com 0,04 s, 6 a 8, e alcança em 0,04 s quando o dedo para |
| teto de densidade | 3× | a nitidez no iPhone (com 2×, amplia duas vezes) |
| `linha` | 12% (desktop) · 40% (celular) | onde o texto se dissolve: sob o menu / antes do rosto |
| `rampa` | 56 px | a altura da dissolução do texto |
| entrada do "quem é" | 98% → 84% da tela, sobe 22 px | quando cada bloco aparece |
| manchete do "quem é" | de 90% a 45% da tela | quando as palavras do h2 acendem |
| espera dos quadros | **no load** (1ª versão: 2.500 ms depois) | o poster (LCP) já pintou no load; esperar mais deixava a pessoa rolar sobre "buracos" |
| retentativa | teto 3, espera 0,5 s × n | quadro que falha na rede (acréscimo, medir) |

---

## 9. Passo 8 — Medir (as metas)

```bash
python3 gerar.py                                 # PARA se faltar quadro, se os conjuntos diferirem ou se faltar variante
cd site && python3 -m http.server 8941           # UM servidor por vez (outra aba do terminal)
# abra http://127.0.0.1:8941/<slug>-video/?medir-cena no Chrome e meça (abaixo)
```

| o quê | como medir | a meta | caso de origem |
|---|---|---|---|
| fluidez da rolagem | Chrome por DevTools Protocol: rolar a cena em ~121 passos e registrar o intervalo entre quadros (ou o painel Performance) | intervalo entre quadros **p50 e p95 ≈ 16,7 ms** (60 fps), **0 tarefas longas** | 16,7 / 16,8 ms, 0 |
| memória | contar os `ImageBitmap` vivos (o motor pode publicar em `window.__cena` com `?medir-cena`) | **no máximo ~40** quadros decodificados vivos | 38 |
| conjunto certo | aba Network | desktop baixa só `cena-*`, celular só `movel-*` | ✓ |
| 1ª dobra do celular | medir o fim do texto da capa em 390×725 e 360×640 | folga **≥ 70 px**, sem rolagem lateral | 72 / 74 px |
| a troca não pula | prints a 0,8 s (poster) e a 6 s (canvas), celular e desktop | a pessoa no mesmo lugar nos dois prints | ✓ |
| a história | prints em 0 · 33 · 66 · 100% da cena, desktop 1440 e celular 390 | o texto nunca por cima do rosto; o fim do "quem é" inteiro | ✓ |
| velocidade | Lighthouse/PageSpeed na URL **publicada** (§10) | celular **≥ 95** (mediana de 3), desktop 100, LCP ≤ 2 s | 98 / 100, LCP 1,5 s |
| o vídeo acompanha o dedo? | gesto sintetizado no navegador (`Input.synthesizeScrollGesture`, 1.500 px/s, em 4G bom e fraco), amostrando o estado do motor a cada quadro de tela, **dentro da página** | **≤ 8 quadros** atrás do dedo em média; alcança em < 0,1 s quando para | τ 0,11: 17–21 quadros · τ 0,04: 6–8 |
| a sensação | **um celular de verdade**, rolando devagar e rápido, para cima e para baixo | sem engasgo, sem buraco preto | — |

> **O medidor não pode ser o gargalo.** Uma 1ª versão do medidor de atraso rolava a página em laço por `Runtime.evaluate`
> (um `scrollBy` e uma leitura por chamada): cada ida e volta custava mais que um quadro de tela, e o "atraso" medido era o
> **do medidor**. O gesto tem de ser sintetizado dentro do navegador e a amostra tem de ser feita **dentro da página**,
> num laço de `requestAnimationFrame` que lê o estado que o motor publica (só com `?medir-cena` na URL).

⚠️ **Nunca aprovar efeito de rolagem por print parado**: a mistura numa tela só passou em todos os prints e rodava a 30 fps.
E nunca medir numa aba oculta — lá o `requestAnimationFrame` congela e as leituras mentem.

---

## 10. Passo 9 — Publicar (só com OK humano)

```bash
cd site
npx vercel link --yes --project <projeto> && cat .vercel/project.json      # 1º deploy: CONFERIR o nome do projeto
npx vercel --prod --yes                                                    # "status: error"? repetir uma vez
curl -s -o /dev/null -w "%{http_code}\n" "https://<seu-dominio>/assets/video/cena/cena-000.avif?h=<hash>"   # 200
```
(O exemplo usa Vercel; qualquer hospedagem estática serve, desde que aceite o cabeçalho abaixo.)
- `/assets/video/(.*)` com `Cache-Control: public, max-age=31536000, immutable` — os quadros não mudam de URL sem mudar de hash.
- A página `<slug>-video` continua **noindex**. Depois de publicar, rodar o PageSpeed na URL publicada.

---

## 11. O que NÃO fazer

**No vídeo**
1. **Animar a pessoa sem decisão humana** registrada — a doutrina manda animar ambiente e equipamento.
2. **Gerar a partir de foto com terceiros** (porta-retratos de família, paciente, tela com dados) — e tentar borrar
   depois: a câmera se move e leva a moldura junto.
3. **Aceitar 720p** ou arquivo comprimido demais — o teto da página é a fonte.
4. **Aprovar pelo primeiro quadro** — olhe a folha com os 9.

**Nos quadros**
5. **Arrastar o `currentTime` de um `<video>`** com a rolagem.
6. **Pular quadros** (96 em vez de 192) para economizar peso — volta o degrau.
7. **Extrair com `CIImage`/Preview** ou **salvar com o perfil ICC** — cor lavada.
8. **WebP de qualidade baixa** — pele manchada na ampliação.
9. **Baixar o quadro inteiro no celular** — use o recorte.
10. **Conjuntos com número de quadros diferente** (o gerador para, e está certo).

**No motor**
11. **Decodificar a sequência inteira** ou deixar o navegador decidir — ~700 MB e engasgo.
12. **Aplicar a folga da janela ao esqueleto** — foram 115 bitmaps vivos (~425 MB).
13. **Misturar quadros numa tela só** (`globalAlpha`) — 30 fps no desktop retina.
14. **Suavizar com fator fixo por quadro de tela** — 120 Hz anda o dobro.
15. **Intercalar leitura de posição e escrita de estilo** num laço de rolagem.
16. **Deixar a suavização do canvas no padrão** ("low") ou limitar a densidade a 2× — borra na retina e no iPhone.
17. **Baixar os quadros junto com a página** — LCP de 17,7 s no PageSpeed.
18. **Apagar o título do "quem é" antes da 1ª rolagem** — reprova o contraste de quem não rola.

**No CSS e no HTML**
19. **`width:auto` num `<canvas>` entre `left` e `right`** — ele não estica (mostrou só um pedaço do fundo).
20. **`overflow: hidden` em qualquer ancestral do palco** — o `sticky` para de grudar.
21. **Duas camadas de máscara** compostas (a propriedade de composição de máscara) — a foto some sem erro nenhum.
22. **Tirar o texto por opacidade** quando ele passa pelo rosto — máscara numa linha fixa.
23. **`animation-fill-mode: both`** na entrada da capa — o texto nunca se dissolve.
24. **Poster que não seja o quadro 0**, ou num recorte diferente do canvas — a troca pula.
25. **Pôr a faixa de números no meio da cena** — quebra o palco fixo.
26. **Manter a foto do "quem é"** na versão com vídeo — o vídeo já é a pessoa.
27. **Indexar a versão com vídeo junto com a estática** — as capas são quase iguais (duplicado).

---

## 12. Quando der errado — sintoma → causa → conserto

| o que você vê | a causa provável | o conserto |
|---|---|---|
| a rolagem engasga | decodificação na hora de desenhar; janela sem `close()`; leituras e escritas intercaladas | a janela + `close()` do motor; leituras antes das escritas; medir (§9) |
| o vídeo anda aos "degraus" | poucos quadros, ou sem a mistura | os 192 e as duas telas empilhadas |
| rápido demais em tela de 120 Hz | suavização por quadro de tela | pelo tempo (`TAU`) |
| o vídeo fica atrás do dedo | `TAU` alto (0,11) | `TAU` 0,04 e medir o atraso |
| rosto pálido, cor lavada | extração por `CIImage`, ou perfil ICC gravado | `sequencia-video.swift` + `Image.frombytes` antes de salvar |
| pele manchada | WebP de qualidade baixa | AVIF q72 |
| borrado na retina / no iPhone | `imageSmoothingQuality` "low" ou teto de densidade 2 | `"high"` reposto a cada redimensionamento; teto 3× |
| no celular aparece só um pedaço do fundo | canvas com `width:auto` | `width:100%` |
| o palco não gruda, rola junto | `overflow` hidden/auto num ancestral | `overflow-x: clip` no `html`, nada no `body` |
| a imagem pula quando o canvas assume | o poster não é o quadro 0, ou está noutro recorte | poster = quadro 0 em AVIF, com o `<source>` do recorte na mesma regra do canvas e `object-position: 50%` |
| o texto passa por cima do rosto ao sair | saída por opacidade | máscara na `linha` (40% no celular) |
| o título da capa nunca some ao rolar | `animation-fill-mode: both` | `backwards` |
| tela parada no começo | normal até o `load`/1º gesto (o poster segura); se continuar, os quadros não chegam | aba Network: `data-quadros` errado (404) ou `?h=` desatualizado — rodar o gerador |
| a aba recarrega sozinha no iPhone | quadros decodificados demais | contar os vivos: até ~40 |
| PageSpeed com LCP alto | quadros baixando com a página, ou poster em JPEG pesado | quadros só depois do `load`; poster em AVIF |
| PageSpeed reprovando contraste | título apagado antes de rolar | a trava `mexeu` (só apaga depois da 1ª rolagem) |
| buraco num quadro só, sempre o mesmo | download falhou e não tentou de novo | retentativa com teto 3 |

---

## 13. Checklist final

- [ ] Decisão humana sobre animar a pessoa, registrada (com a frase de aprovação).
- [ ] Foto de entrada sem terceiros e sem dado sensível; pessoa no terço direito.
- [ ] Vídeo em 1080p no mínimo (4K se possível), qualidade máxima, guardado em `insumos/originais/`.
- [ ] Folha de 9 quadros conferida, todos os quadros; veredito humano no caderno.
- [ ] 192 quadros extraídos com as cores cruas; dois conjuntos em AVIF q72, mesmo número de quadros, cada um com até ~7 MB.
- [ ] Poster = quadro 0 (AVIF + JPEG de reserva), `fetchpriority="high"`.
- [ ] Marcadores do template conferidos; `<slug>-video` gerado sem erro; noindex, fora do sitemap, canônica para `<slug>`.
- [ ] `--foco` do desktop e do celular ajustados; a pessoa fora da coluna de texto em 1280, 1440 e 1920.
- [ ] 60 fps, 0 tarefas longas, até ~40 quadros vivos; atraso ≤ 8 quadros.
- [ ] Folga ≥ 70 px na 1ª dobra em 390×725 e 360×640.
- [ ] Prints em 0 · 33 · 66 · 100% da cena, desktop e celular; poster → canvas sem salto.
- [ ] OK humano para publicar; publicado no projeto certo; quadros respondendo 200 no ar.
- [ ] PageSpeed: celular ≥ 95 (mediana de 3), desktop 100.
- [ ] Rolado num celular de verdade.
- [ ] Registro do projeto atualizado (decisão, custo, prints).

---

**A variante mais simples — vídeo em laço na capa, sem rolagem.** O vídeo vai sem `autoplay` no HTML, com o `play()` no
1º gesto, e a volta do laço por dissolução entre duas cópias. ⚠️ O `play()` recusado (iPhone em modo de pouca energia) tem
de **re-armar no próximo toque** — engolir o erro deixa a capa parada para sempre. `<source>` AV1 antes do H.264, e botão
de pausa (movimento automático > 5 s).
