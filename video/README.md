# Vídeo na rolagem — a versão `<slug>-video` da landing page

Toda landing page da matriz sai em **duas versões**:

| versão | endereço | o que é | indexa? |
|---|---|---|---|
| estática | `/<slug>/` | a página de sempre, com a foto da capa | sim |
| com vídeo | `/<slug>-video/` | a mesma página, mas a capa e o bloco "quem é" viram uma **cena**: um vídeo de 8 s, gerado por IA a partir das fotos do cliente, que **anda com a rolagem** | **não** (`noindex`, fora do sitemap, canônica apontando para a estática) |

Quem rola para baixo vê o vídeo andar; quem para, vê o vídeo parar; quem sobe, vê o vídeo voltar.

Esta pasta tem:

| arquivo | para quê |
|---|---|
| `README.md` | este processo, da foto à publicação |
| `doutrina-da-cena.md` | o passo a passo técnico da cena (portões, quadros, AVIF, HTML, CSS, JS, medidas, erros conhecidos) |
| `modelo-de-prompt.md` | o modelo de prompt aprovado (quadro inicial e final) e por que cada trecho existe |
| `licoes.md` | o que as gerações e a construção já ensinaram |
| `ferramentas/` | a esteira em Node (`.mjs`), os extratores de quadros (`.swift`), o conversor AVIF (`.py`), o modelo de prompt (`.txt`) e o `.env.exemplo` |

---

## A esteira em uma tela

```
fotos do cliente
  │
  ├─ 1. analisar-fotos.mjs ......... nota 0–10 por foto, pares início→fim   (centavos)      ■ PARADA: humano escolhe a foto ou o par
  ├─ 2. ajustar-foto.mjs ........... edição por IA + conferência do rosto     (US$ 0,02–0,20)  ■ PARADA: humano aprova o antes/depois
  ├─ 3. sugerir-movimento.mjs ...... 2–4 movimentos com viabilidade e prompt  (centavos)      ■ PARADA: humano escolhe a opção
  ├─ 4. gerar-video.mjs --aprovado . Veo 3.1, 8 s, 16:9, 1080p                (US$ 0,64–3,20)  (sem --aprovado, recusa)
  ├─ 5. conferir-video.mjs ......... 9 quadros × fotos reais → passou/reprovou (centavos)     ■ PARADA: humano dá o veredito
  ├─ 6. montagem da cena ........... 192 quadros, AVIF desktop + celular, HTML/CSS/JS, medir 60 fps e PageSpeed
  └─ 7. publicação ................. só com OK humano                                         ■ PARADA
```

**Regra que não se dobra:** todo passo que **custa dinheiro** ou que **anima gente** para e espera uma decisão humana.
A IA sugere, aponta e confere; quem decide é uma pessoa. Quando a foto não serve, a esteira diz que não serve — sem forçar.

---

## Pré-requisitos

| o quê | versão | para quê | como conferir |
|---|---|---|---|
| Node.js | **20.6+** (usa `fetch`, `FormData`, `Blob` nativos e `--env-file`) | as ferramentas `.mjs` | `node --version` |
| Python 3 + Pillow | Pillow **≥ 11.2** (grava AVIF) | medir, recortar e reduzir imagens; folhas de contato; AVIF | `python3 -c "from PIL import features; print(features.check('avif'))"` → `True` |
| macOS + Swift | Command Line Tools do Xcode | extrair quadros com as **cores cruas** (`sequencia-video.swift`) e a folha de 9 quadros (`quadros-video.swift`) | `swift --version` |
| **ou** ffmpeg | qualquer recente | alternativa fora do macOS (veja "Sem macOS" abaixo) | `ffmpeg -version` |
| Google Chrome | — | medir a rolagem e o PageSpeed | — |
| Chave da **Gemini API** | com faturamento ativo | visão (passos 1, 3, 5) e **Veo 3.1** (passo 4) | — |
| Chave da **OpenAI** | — | só o passo 2 (edição de foto) | — |

### Chaves: só por variável de ambiente

As ferramentas **não leem chave de nenhum outro lugar** (nem arquivo de configuração, nem cofre de senhas).

| variável | obrigatória? | usada por |
|---|---|---|
| `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`) | **sim** | `analisar-fotos`, `ajustar-foto` (conferência), `sugerir-movimento`, `gerar-video` (Veo 3.1), `conferir-video` |
| `OPENAI_API_KEY` | só no passo 2 | `ajustar-foto` |
| `OPENAI_CREDITO_USD` | não | `ajustar-foto` informa quanto resta do crédito |
| `LPV_CADERNO`, `LPV_LIVRO_OPENAI` | não | onde gravar o caderno e o livro de gastos (padrão: pasta de trabalho) |
| `LPV_MODELO_VISAO`, `LPV_MODELO_FOTO` | não | trocar o modelo de visão ou de imagem sem mexer no código |
| `LPV_FUSO` | não | fuso dos horários impressos (padrão `America/Sao_Paulo`) |

```bash
cp ferramentas/.env.exemplo .env      # preencha; NUNCA versione o .env
node --env-file=.env ferramentas/analisar-fotos.mjs …
```
Faltou a chave, a ferramenta para com a mensagem `falta a variável de ambiente …` (saída 3) antes de chamar qualquer API.

### Onde as coisas ficam

Rode tudo de dentro da **pasta de trabalho do projeto** (ex.: `<projeto>/insumos/lp-video/`), nunca de uma pasta temporária
(ela some e leva o histórico junto). Ali ficam:
- `caderno.jsonl` — uma linha por análise, ajuste, vídeo, conferência e veredito humano (ou `--caderno <arq>` / `LPV_CADERNO`);
- `caderno.md` — o mesmo caderno em tabela legível, reescrito a cada conferência;
- `gastos-openai.jsonl` — o custo de cada ajuste de foto (ou `--livro-openai <arq>`);
- as pastas `lp-video-<cliente>/` com análises, sugestões, fotos ajustadas e vídeos (ou `--saida` / `--destino`).

> Quer que o aprendizado valha para **todas** as páginas? Aponte `LPV_CADERNO` para um caderno único da agência.
> O `sugerir-movimento` lê os últimos prompts aprovados e os últimos motivos de reprovação de lá.

---

## Passo 1 — Análise das fotos

```bash
node --env-file=.env ferramentas/analisar-fotos.mjs --cliente fulana --fotos ./fotos \
  --contexto "dermatologista em consultório, capa da LP" --saida ./lp-video-fulana
```

A IA de visão avalia cada foto pelos **portões** (veja `doutrina-da-cena.md` §1): horizontal; pessoa no terço direito,
com até ~40% da largura; área calma (e mais escura) à esquerda, onde o texto vai morar; **nenhum terceiro**
(porta-retratos, pacientes, reflexos); **nenhum dado sensível** (telas, papéis, crachás); nenhuma marca de terceiro;
nitidez para 1080p; risco nas mãos; se serve de capa parada; publicidade sóbria.

Sai:
- `analise.md` — tabela nota / veredito (🟢 usar · 🟡 usar com ajuste · 🔴 não usar) / por quê / ajuste sugerido;
- `analise.json` — tudo, com os problemas de cada foto;
- `prancha.jpg` — todas as fotos com a nota embaixo;
- **pares de início e fim**: fotos do mesmo ensaio, mesmo enquadramento, mudando só a pose. É o que mais acerta.

**Olhe a prancha com os próprios olhos.** A IA erra; o veredito é humano.

> ■ **PARADA.** Leve ao responsável: as 2–3 melhores e por quê, o par início → fim (se houver), o ajuste que cada uma
> precisa e as que **não** servem. **Ele escolhe a foto ou o par.**

## Passo 2 — Ajustes na foto (só os aprovados)

```bash
node --env-file=.env ferramentas/ajustar-foto.mjs --cliente fulana --foto ./fotos/IMG_0001.jpg \
  --pedido "apagar os porta-retratos da estante" --saida ./lp-video-fulana
```
- Ajustes típicos: **ampliar o cenário para 16:9** com espaço à esquerda (`--tamanho 2048x1152`; recortar uma foto
  vertical perde cabeça ou pernas), **apagar terceiros**, apagar tela com dado.
- Também cria o **quadro final** a partir da mesma foto quando não há um 2º clique do ensaio
  (`--pedido "ela levanta o olhar para a câmera, sorriso leve"`) — mais arriscado.
- Conserto **na foto**, sempre: consertar no vídeo depois não funciona (a câmera se move e leva o defeito junto).
- Depois da edição, a IA compara original × editada e diz se **o rosto mudou**. **Rosto mudou = descartar**, nunca "serve".
- Imprime o custo do ajuste e o gasto acumulado (e o saldo, se `OPENAI_CREDITO_USD` existir).

> ■ **PARADA.** Mostre o `… — antes e depois a1.jpg` e a conferência. **O responsável aprova ou recusa.** Recusou
> todos? Volte ao passo 1 com outra foto.

## Passo 3 — Sugestões de movimento

```bash
node --env-file=.env ferramentas/sugerir-movimento.mjs --cliente fulana \
  --inicio ./fotos/IMG_0001.jpg --fim ./fotos/IMG_0002.jpg --contexto "…" --n 3 --saida ./lp-video-fulana
```
- 2 a 4 opções, **da mais viável para a menos**, cada uma com: o que acontece (em português simples), como termina,
  viabilidade 🟢/🟡/🔴, riscos e o **prompt completo em inglês** no molde de `ferramentas/modelo-prompt.txt`.
- A ferramenta lê o caderno: os prompts que já **passaram** e os motivos que já **reprovaram** entram no pedido.
- Se a foto não serve, o campo `nao_recomendo` vem preenchido — **diga isso antes das opções**.
- **Confira cada prompt** contra o modelo (`modelo-de-prompt.md`): cláusulas de identidade, de câmera,
  *"every intermediate frame"*, a lista de *"No …"*, *"Audio: none"*, *"~8 seconds"*, a frase do último quadro, e
  **nenhum marcador `{…}` sobrando**. Corrija o que estiver fraco direto no `sugestoes.json`.

> ■ **PARADA.** Apresente as opções e o **custo de 1 tentativa** (tabela abaixo). **O responsável escolhe a opção**
> (ou pede outra rodada). Animar uma pessoa real é decisão dele — registre a frase de aprovação.

## Passo 4 — Gerar o vídeo (Veo 3.1)

```bash
node --env-file=.env ferramentas/gerar-video.mjs --cliente fulana \
  --sugestoes ./lp-video-fulana/sugestoes.json --opcao 1 \
  --aprovado "pode gerar a opção 1 no Fast" --modelo fast --destino ./lp-video-fulana
```
- **Sem `--aprovado` a ferramenta recusa** (saída 2, nada gasto). O texto do `--aprovado` é a frase literal de quem aprovou,
  e fica no caderno.
- Prepara as entradas em 16:9 com **o mesmo recorte** nas duas pontas (`--ancora`: 0 = topo, 0,5 = centro, 1 = base),
  chama o Veo com 1º e último quadro, `personGeneration: allow_adult`, `seed` (aleatório se não vier), 8 s, sem áudio.
- Imprime o custo **antes** de gerar; leva 1–3 min; grava o `.mp4`, o `.prompt.txt` e a linha no caderno.
- Em seguida roda o passo 5 sozinho.
- Para refazer com prompt corrigido: `--prompt <arquivo.txt> --inicio <foto> [--fim <foto>]` no lugar de `--sugestoes/--opcao`
  (e **novo** `--aprovado`).

### Custo por tentativa (8 s, Gemini API, preços lidos em 05-10-2026)

| modelo | 720p | **1080p** | 4K |
|---|---|---|---|
| **Lite** (`veo-3.1-lite-generate-preview`) | US$ 0,40 | **US$ 0,64** | — (não faz) |
| **Fast** (`veo-3.1-fast-generate-preview`) — padrão | US$ 0,80 | **US$ 0,96** | US$ 2,40 |
| **Standard** (`veo-3.1-generate-preview`) | US$ 3,20 | **US$ 3,20** | US$ 4,80 |

- **O caro é o modelo, não a resolução.** 1080p é o mínimo da receita (o vídeo ocupa a altura inteira da tela no desktop).
- Sem camada grátis. Preços em `PRECO_VEO` no `ferramentas/comum.mjs` — **atualize quando o Google mudar**.
- O mesmo prompt dá um vídeo diferente a cada geração; o `seed` só melhora um pouco a repetição. Conte com
  **1 a 3 tentativas** por página até o caderno amadurecer.

## Passo 5 — Conferência dos 9 quadros

```bash
node --env-file=.env ferramentas/conferir-video.mjs --id fulana-01          # automático depois do passo 4
node --env-file=.env ferramentas/conferir-video.mjs --video x.mp4 --inicio a.jpg --fim b.jpg --cliente fulana   # avulso
```
- Tira 9 quadros (0, 1, 2 … 7, 7,95 s), monta a folha `… — 9 quadros.jpg` e a IA compara com as fotos reais:
  identidade do rosto, mãos, terceiros ou objetos novos, texto inventado, câmera, suavidade, algo entrando à esquerda,
  e se o último quadro bate com a foto final.
- Diz **passou/reprovou**, os motivos com o segundo em que aparecem e o `ajuste_no_prompt` (frase pronta, em inglês).
- **Olhe a folha você mesmo** — todos os 9 quadros, não só o primeiro.

> ■ **PARADA.** Mostre a folha, o veredito da IA e o seu. **O veredito humano vale mais que o da IA** e é ele que ensina:
> ```bash
> node ferramentas/caderno.mjs --id fulana-01 --humano aprovou
> node ferramentas/caderno.mjs --id fulana-01 --humano reprovou --motivo "mão direita deforma aos 5 s"
> ```
> Reprovado? Aplique o `ajuste_no_prompt`, proponha a nova tentativa **com o custo**, e gere de novo **só com novo OK**.

## Passo 6 — Montar a cena

Detalhe completo em `doutrina-da-cena.md` §3 a §9. Em resumo:

1. **Guardar o original** no projeto: `insumos/originais/video-<cliente>-original.mp4`.
2. **Extrair todos os quadros com as cores cruas** (8 s × 24 fps = **192**):
   ```bash
   mkdir -p /tmp/seq && swift ferramentas/sequencia-video.swift insumos/originais/video-<cliente>-original.mp4 /tmp/seq 1
   ls /tmp/seq/*.png | wc -l      # 192
   ```
3. **AVIF nos dois conjuntos** — desktop (quadro inteiro, 1280×720) e celular (quadrado recortado na pessoa):
   ```bash
   python3 ferramentas/cena-avif.py /tmp/seq 0.51 --saida site/assets/video/cena --poster site/assets/img
   ```
   AVIF q72; **mesmo número de quadros nos dois conjuntos**; alvo **até ~7 MB por conjunto**; o poster é o **quadro 0**.
4. **A página `<slug>-video`** no gerador do projeto: a cena substitui a abertura (capa + números + "quem é"), reusando os
   textos do template; `noindex`, fora do sitemap, canônica para `<slug>`.
5. **Medir**:
   - rolagem a **60 fps** (intervalo entre quadros p50 e p95 ≈ 16,7 ms), **0 tarefas longas**, **até ~40 quadros vivos**;
   - 1ª dobra do celular com folga ≥ 70 px em 390×725 e 360×640;
   - poster → canvas sem salto;
   - vídeo no máximo ~8 quadros atrás do dedo;
   - **PageSpeed** na URL publicada: celular **≥ 95** (mediana de 3), desktop 100, LCP ≤ 2 s;
   - e rolar num **celular de verdade**. Nunca aprovar efeito de rolagem por print parado.

### Sem macOS (alternativa ffmpeg)

- **Folha de 9 quadros:** o `conferir-video.mjs` usa ffmpeg sozinho quando não acha Swift.
- **Os 192 quadros:** o Swift existe para pegar os **valores crus** do decodificador (o navegador mostra o vídeo Rec.709
  lido como sRGB, sem correção de gama). Com ffmpeg, converta só a matriz de cor, sem mexer na curva:
  ```bash
  ffmpeg -i video.mp4 -vf "scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24" -start_number 0 /tmp/seq/q%03d.png
  ```
  **Confira**: compare o brilho médio de um quadro extraído com o mesmo instante do `<video>` no Chrome (print). Se o
  extraído vier mais claro, a conversão está errada — rosto pálido ao lado do vídeo é o sintoma clássico.

## Passo 7 — Publicar

- Os quadros vão com cache `public, max-age=31536000, immutable` e a URL leva o **hash do conjunto** (`?h=`): trocar os
  quadros sem mudar a URL não chega em ninguém.
- Conferir no ar que um quadro responde 200 e rodar o PageSpeed na URL publicada.
- `<slug>-video` continua **noindex**.

> ■ **PARADA.** Publicar só com **OK humano**, depois de ver a página medida e rolada num celular.

---

## O que registrar, sempre

- A foto escolhida, o movimento aprovado e **"animar a pessoa: aprovado por <quem> em <data>"** no registro de decisões do projeto.
- O vídeo gerado, o custo e o veredito (o caderno faz sozinho; o veredito humano, pelo `caderno.mjs --humano`).
- O que deu errado e o conserto vira linha em `licoes.md` se valer para todos.
