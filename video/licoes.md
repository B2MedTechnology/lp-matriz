# Lições — o que as gerações e a construção já ensinaram

O caderno de gerações (`caderno.jsonl` / `caderno.md`, veja `README.md`) é o que faz a esteira acertar na 1ª tentativa com
o tempo. Este arquivo guarda as lições que valem para **todas** as páginas, sem nome de ninguém.

> **Estado honesto (06-10-2026).** A esteira automática ainda **não gerou nenhum vídeo pela API**: o caderno tem 0 gerações,
> 0 aprovadas, US$ 0,00 gastos. O que está abaixo vem (a) dos vídeos feitos à mão, numa ferramenta de imagem → vídeo, que
> originaram a receita da cena, e (b) da construção e dos testes da esteira. Quando o caderno tiver gerações, as lições
> novas entram aqui, com o número de tentativas.
>
> **Ainda não provado:** a geração real no Veo pela API (falta o teste lado a lado Lite × Fast) e a conferência de ponta a
> ponta num vídeo gerado pela esteira.

---

## 1. O que mais derruba um vídeo é a foto de entrada, não o prompt

| o que aconteceu | lição |
|---|---|
| Porta-retratos de família numa estante apareceram nos 8 s do vídeo; borrar depois não funcionou (a câmera se move e leva a moldura junto). O vídeo foi descartado. | **Apagar terceiros na foto, antes de gerar.** Conserto no vídeo não existe. |
| A capa quase foi ao ar com o nome e o prontuário de um paciente na tela de um aparelho. | **Dar zoom em telas, papéis e crachás** antes de aprovar a foto. Dado sensível é bloqueio, não detalhe. |
| A pessoa chegou no terço esquerdo do vídeo, com outra pessoa de costas à direita. Espelhar estragaria o close (texto ao contrário). | **Mudar o corte, não espelhar:** `--foco` baixo no desktop e no celular. Mediu 60 fps do mesmo jeito. |
| Todas as fotos de um ensaio eram verticais. | Para 16:9, **ampliar o cenário por IA** (passo 2). Recortar perde cabeça ou pernas. |

## 2. Duas fotos do mesmo ensaio valem mais que um prompt bom

- O vídeo que virou modelo foi gerado com **duas fotos reais do mesmo ensaio** como 1º e último quadro, mudando só a pose.
  A IA inventa só o meio; as pontas, que são as que ficam paradas na tela, são fotos verdadeiras.
- A análise automática encontrou sozinha, em 30 fotos, o **mesmo par** que a pessoa tinha escolhido à mão (marcado como
  "ótimo"). E a sugestão de movimento mais viável para esse par foi **o mesmo movimento** que tinha sido aprovado.
  → A esteira acerta o par e o movimento; a dúvida que sobra é a geração em si.
- **Sem foto final**, a IA inventa o fim e o risco no rosto sobe: prefira movimentos mínimos (respiração, olhar, postura).

## 3. Movimento lento e uniforme, porque a rolagem para em qualquer quadro

- Gesto rápido vira borrão e "picota" entre quadros vizinhos. Movimento lento, distribuído nos 8 s: cada quadro
  intermediário é uma foto boa e a mistura entre vizinhos fica invisível.
- Pessoas **não andam, não trocam de lugar, não vão para a câmera** — assim o corte do CSS vale do começo ao fim.
- Câmera: *push-in* de 3–5%, quase parada. Nada de órbita, tremor ou zoom rápido.
- Mãos são onde a IA mais erra: gesto simples, perto do corpo, longe da lente.

## 4. Gerar custa pouco; repetir é que custa

- O mesmo prompt dá um vídeo diferente a cada geração. O `seed` só melhora um pouco a repetição. **O prompt reduz
  tentativas; não zera.**
- **O caro é o modelo, não a resolução:** Fast 1080p US$ 0,96 × Standard 1080p US$ 3,20 por tentativa.
- Estimativa (não medição) por página em 1080p, 3 tentativas: Lite ≈ US$ 1,90 · Fast ≈ US$ 2,90 · Standard ≈ US$ 9,60.
- Meta do caderno: **1 a 1,5 tentativa por página**. O indicador que tem de cair é "tentativas até o 1º aprovado".
- Toda chamada que custa **imprime o custo antes** e grava no caderno; sem `--aprovado`, não gera.

## 5. Qualidade do arquivo de vídeo

- Um vídeo que veio de uma ferramenta web saiu em **1280×720, 24 fps, 8 s, 1,1 MB** — abaixo da receita. No desktop ele é
  ampliado ~2× e fica mole. **1080p é o mínimo; 4K se couber no orçamento**; sempre a qualidade máxima de download.
- Algumas ferramentas recusam imagem de entrada acima de **20 MB**: PNG de estúdio → JPEG 95, sem subamostragem, na
  resolução original. As ferramentas desta pasta já reduzem sozinhas.
- Faixa escura de ~14 px na borda esquerda do 1º e do último quadro apareceu num vídeo; caiu na rampa transparente da
  máscara do desktop e não apareceu. Confira mesmo assim.

## 6. A IA aponta; a pessoa decide

- A conferência por IA dos 9 quadros é o **porteiro**, não o juiz: o veredito humano vale mais e é gravado à parte
  (`caderno.mjs --humano`).
- A edição de foto por IA **mexe na fisionomia**. Por isso o passo 2 compara original × editada; "rosto mudou" = descartar.
- Toda etapa que custa ou anima gente **para** e espera escolha humana. A esteira diz "não use esta foto" quando for o caso.

## 7. Construção da esteira — erros e consertos

| o que aconteceu | causa | conserto |
|---|---|---|
| A análise repetia "vertical" e "> 20 MB" nas 30 linhas | rubrica técnica por foto | aviso único quando todas são verticais; o tamanho saiu (a esteira reduz sozinha) |
| `swift script.swift` levava minutos por conferência | o Swift compila o script a cada execução, e a máquina era lenta | `swiftc -O quadros-video.swift -o quadros-video`; o script fica como reserva |
| `fetch failed ECONNRESET` no meio da conferência | rede oscilando | 3 tentativas na chamada à IA, com espera crescente |
| Pedido com 11 imagens de 1.600 px caindo | pedido grande em rede ruim | quadros a 1.024 px na conferência |
| Teste de horário falhando | erro **do teste**, não da lógica | teste corrigido — antes de mexer no código, confira o teste |

## 8. Na cena (resumo; detalhe em `doutrina-da-cena.md`)

- Extração com **cores cruas**: brilho médio 111,8 no `<video>` × 120,7 extraído por `CIImage` — rosto pálido.
- **192 quadros, não 96** (degrau). **AVIF q72**, não WebP (pele manchada). **Dois conjuntos** (celular recortado).
- **Quadros depois do `load`**: baixados junto com a página, o LCP do celular foi a 17,7 s.
- **τ 0,04 s**, não 0,11: com 0,11 o vídeo ficava ~20 quadros atrás do dedo ("muito delay").
- **Medidor dentro da página**: um medidor que rolava por chamadas externas mediu o próprio atraso, não o do motor.
- **Nunca aprovar rolagem por print parado**: a mistura numa tela só passou em todos os prints e rodava a 30 fps.
