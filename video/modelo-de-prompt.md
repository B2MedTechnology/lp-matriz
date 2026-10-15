# Modelo de prompt — vídeo para a rolagem (quadro inicial e final)

O prompt abaixo é o **modelo aprovado** para vídeo de pessoa (ou dupla) em estúdio ou consultório que vai **andar com a
rolagem** da página. Nasceu de um vídeo real aprovado, gerado a partir de **duas fotos do mesmo ensaio** como quadro inicial
e final. Os detalhes daquele cliente foram trocados por marcadores `{…}`.

O mesmo texto está em `ferramentas/modelo-prompt.txt`, que o `sugerir-movimento.mjs` lê e manda a IA preencher.

---

## As duas ideias que fazem funcionar

1. **Duas fotos reais do ensaio como quadro INICIAL e FINAL** (imagem → vídeo com início e fim travados). A IA só inventa
   o meio. As pontas, que são as que mais aparecem paradas (a capa e o fim do "quem é"), são fotos verdadeiras.
2. **Movimento lento e distribuído por igual nos 8 s.** Na rolagem, o vídeo para em qualquer quadro. Gesto rápido vira
   borrão e "picota" entre quadros vizinhos. Com movimento lento, cada quadro intermediário é uma foto boa, e a mistura
   entre vizinhos que o motor da página faz fica invisível.

Medido no caso de origem: 192 quadros, 60 fps na rolagem (p50 e p95 de 16,7 ms entre quadros), 0 tarefas longas, no
máximo 37 quadros decodificados ao mesmo tempo.

## Como usar

- **Fotos de entrada:** do **mesmo ensaio**, mesmo enquadramento, pessoas no mesmo lugar, mudando **só a pose**.
  Exemplo: foto A com as mãos no bolso → foto B com uma pessoa ajustando o paletó e a outra juntando as mãos.
- **Tamanho:** algumas ferramentas recusam arquivo acima de 20 MB. PNG de estúdio (~30 MB) → JPEG qualidade 95, sem
  subamostragem de cor, na resolução original (~7 MB). As ferramentas desta pasta já reduzem sozinhas.
- **Preencha os marcadores** com o que se vê nas fotos. **Nenhum `{…}` pode sobrar** no prompt enviado.
- **O resto fica igual.** As proibições existem por causa das falhas conhecidas da IA: rosto que muda, mão deformada,
  câmera tremendo, objeto novo.
- **Animar gente é decisão humana**, registrada antes de gerar.
- **Depois:** conferência dos 9 quadros → extração dos 192 com as cores cruas → AVIF nos dois conjuntos
  (`doutrina-da-cena.md`).

### Os marcadores

| marcador | o que pôr | exemplo |
|---|---|---|
| `{PESSOAS}` | quem aparece, com detalhe | `woman` · `two men` · `female dermatologist` |
| `{PESSOAS_CURTO}` | como se referir a elas depois | `She` · `Both men` |
| `{ROUPA}` | roupa, com cor | `white lab coat over a light blue blouse` · `navy blue suits, shirts and ties` |
| `{ACESSORIOS}` | o que não pode mudar | `earrings, wristwatch and wedding ring` |
| `{AMBIENTE}` | o lugar | `bright dermatology office` · `minimalist professional photography studio` |
| `{FUNDO}` | o fundo | `neutral dark gray background` · `light wooden shelves` |
| `{LUZ}` | a luz | `soft studio lighting` · `soft natural window light` |
| `{GESTO_PESSOA_1}` / `{GESTO_PESSOA_2}` | o gesto de **cada** pessoa, descrito à parte, com "slowly" | `The woman slowly lowers the tablet and raises her gaze toward the camera with a gentle smile` |
| `{TIPO_DE_NEGOCIO}` | o tom | `medical clinic` · `law firm` · `architecture studio` |
| `{EXPRESSAO}` | a expressão | `serene, warm and professional` · `serious, professional and composed` |
| `{POSICAO_NO_QUADRO}` | onde a pessoa fica | `in the right third of the frame` · `centered` |
| `{ESTILO_DA_MARCA}` | o estilo | `refined healthcare branding` |
| `{TIPO_DE_FILMAGEM}` | o tipo de filmagem | `studio` · `interior` |

Com **uma pessoa só**: apague a linha do `{GESTO_PESSOA_2}` e ajuste o plural ("She remains…", "her posture").
**Sem foto final** (a IA inventa o fim): troque a 2ª linha e a última por uma descrição precisa do quadro final — o risco
no rosto sobe, então prefira movimentos mínimos (respiração, olhar, ajuste de postura).

---

## O prompt (modelo)

```text
Create a premium, photorealistic, slow and seamless image-to-video transition using the two provided photographs as the exact visual reference.
The first uploaded image is the START FRAME and the second uploaded image is the END FRAME.
Preserve exactly the same {PESSOAS} throughout the entire video: same faces, facial features, hairstyles, facial hair, eyeglasses, body proportions, {ROUPA} and {ACESSORIOS}. Their identity and appearance must remain perfectly consistent with the reference photographs.
The scene takes place in the same {AMBIENTE} with the same {FUNDO} and {LUZ}.
Start exactly from the pose and composition of the first image.
{PESSOAS_CURTO} remain in the same positions. They do NOT walk, change places or move toward the camera.
Gradually and naturally transition their posture toward the pose shown in the second reference image.
{GESTO_PESSOA_1}, until reaching the exact pose shown in the second image.
{GESTO_PESSOA_2}, until reaching the exact pose shown in the second image.
Their movements should feel calm, confident, sophisticated and realistic, like a professional {TIPO_DE_NEGOCIO} institutional film.
Add extremely subtle human micro-movements only: natural breathing, slight posture adjustments, tiny head movement and minimal eye movement. Keep their expressions {EXPRESSAO}.
Camera movement must be extremely smooth and restrained: a very slow cinematic push-in of approximately 3–5%, almost imperceptible, maintaining {PESSOAS_CURTO} completely visible and {POSICAO_NO_QUADRO} throughout the shot.
No camera shake, no handheld movement, no fast zoom, no orbit, no dramatic perspective change.
The animation must feel continuous and progressive rather than like a traditional video scene. Every intermediate frame should look visually polished because the video will be connected to website scroll progression and may pause at any moment.
Motion should be slow, elegant and evenly distributed from beginning to end, with no sudden acceleration or abrupt gestures.
Maintain realistic fabric physics on the {ROUPA} and natural arm and hand anatomy during the transition.
Keep the {FUNDO} completely stable. No background movement or environmental changes.
Do not introduce any additional people, furniture, objects, graphics, logos or text.
No talking, no lip movement, no exaggerated facial expressions.
No morphing of faces, hands or bodies.
No changes to clothing colors or accessories.
No artificial beauty retouching or CGI appearance.
Preserve realistic skin texture and the original photographic look.
Style: premium institutional photography, {ESTILO_DA_MARCA}, understated luxury, realistic {TIPO_DE_FILMAGEM} cinematography.
Motion: extremely slow, fluid, controlled and scroll-friendly.
Duration: approximately 8 seconds.
Audio: none.
Important: the final frame must closely match the second uploaded reference photograph, including body posture, hand position and overall composition.
```

## As partes do prompt e por que existem

| trecho | para quê |
|---|---|
| *START FRAME / END FRAME* | trava as pontas em fotos reais (a capa e o fim do "quem é") |
| *Preserve exactly the same…* (rosto, cabelo, óculos, roupa, acessórios) | a IA não troca a fisionomia nem os acessórios |
| *They do NOT walk, change places or move toward the camera* | as pessoas ficam no mesmo lugar do quadro, e o corte (`--foco`) do CSS vale do começo ao fim |
| o gesto de cada pessoa, descrito à parte | o meio do vídeo fica previsível: nada de gesto inventado |
| *push-in 3–5% … completely visible* | câmera quase parada: o recorte do celular (um quadrado) segura a(s) pessoa(s) do começo ao fim |
| *Every intermediate frame … may pause at any moment* / *evenly distributed* | todo quadro intermediário é usável — é o que a rolagem mostra |
| a lista de *No …* | as falhas conhecidas da IA: fala, morphing, CGI, objeto novo, fundo mexendo, roupa trocando de cor |
| *Audio: none* · *approximately 8 seconds* | 8 s × 24 fps = **192 quadros**, o número da receita |
| *Important: the final frame must closely match…* | sem ela, o último quadro "chega perto" mas não emenda com a foto final |

## Modelo antigo (uma foto só, sem quadro final)

Para quando só existe uma foto boa. Mais risco no rosto no fim do vídeo; prefira o modelo acima.

```text
{PROFISSIONAL} sentada à mesa do {AMBIENTE}, escrevendo com calma numa prancheta. A câmera se aproxima
lentamente (dolly in), em plano contínuo, sem cortes. Nos últimos 2 segundos ela levanta o olhar
para a câmera, com um sorriso leve. Luz natural suave, cores realistas, rosto e mãos estáveis.
Nenhuma pessoa entra no quadro, nenhum texto aparece em telas. 8 segundos, 16:9.
```
O arco é o mesmo: o **1º quadro é a capa** (bonito parado: trabalhando, escrevendo, examinando) e o **último é o "quem é"**
(olha para a câmera).
