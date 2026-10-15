# REGRAS DE SAÍDA (o contrato com o motor)

Você devolve UM objeto JSON. Cada chave abaixo, no formato exato — o motor monta a página a partir dele.
Onde o formato diz [a, b], é uma lista de 2 posições (a ordem importa).

## Leis (valem acima de tudo)
1. **Nada inventado.** Todo fato (número, ano, quantidade, nome de médico, CRM/RQE, equipamento, técnica, convênio,
   preço, bairro atendido) tem de estar nos INSUMOS ou nos FATOS FIXOS. Se o guia pede um dado que os insumos não têm,
   NÃO preencha com suposição: escreva o que é possível sem ele e registre a falta em `PENDENCIAS`.
2. **Número sem fonte não entra** (modelo §9). Para cada item de `NUMEROS`, `NUMEROS_FONTES` traz, na mesma posição,
   a frase do insumo que o comprova. Se não houver 5 números com fonte, entregue menos — nunca complete.
3. **A regra do conselho** (a nota de publicidade do guia) é lei: o que ela proíbe não aparece em nenhum campo.
4. **Tom** do Guia de copy: sem termo popular, sem promessa de resultado, sem superlativo vazio, sem "estética de IA";
   o filtro vende (personalização), nunca trata quem lê como custo.
5. **O guia e o exemplo falam de OUTROS clientes** (as notas citam páginas aprovadas pelo nome). Nenhum fato deles vale
   para este cliente — convênio, equipe, números, técnicas, filtro. Rodada 1 (28-09): "não atendemos convênio" entrou sem
   estar nos insumos, vindo do guia. Se o filtro do cliente não está nos insumos, `FILTRO` = "" e uma pendência.
6. **Nome de arquivo de foto não é fato.** Foto serve para ilustrar; não conta médico, não prova serviço nem equipamento.
7. **HTML** só onde o formato permite: `<br>` e `<em>` no H1 e nos rótulos dos números; `&nbsp;` para não quebrar.

## Campos
- `MARCA_LINHA` (texto): a assinatura acima do título, "Especialidade · Bairro de Cidade".
- `NUMEROS` [[valor, sufixo, rótulo]] 5–8 itens — valor em texto ("5,0", "40"), sufixo ("", "+", "%"), rótulo curto com `<br>`.
- `NUMEROS_FONTES` [texto] — mesma quantidade e ordem de `NUMEROS`.
- `QUEM_HEAD` (texto): o título da dobra "quem é / por que".
- `MOTIVOS` [[título, texto]] exatamente 4.
- `CORPO_LEAD` (texto) e `CORPO_CLINICO` [{id, nome, cargo, area, crm, rqe, saberes:[texto], foto, alt}] — só médicos
  que os insumos citam; `crm`/`rqe` vazios ("") se não vierem nos insumos; `foto` = nome de arquivo das FOTOS DISPONÍVEIS
  (sem extensão) ou "" se não houver; `id` = nome em minúsculas com hífen, sem título.
- `GRUPOS` [[título do grupo, [[título do card, ícone, texto, etiquetas]]]] — grupos de 3 cards (padrão v3); `ícone` é a
  chave de uma foto card-<ícone> das FOTOS DISPONÍVEIS; `etiquetas` curtas separadas por " · ".
- `FOTOS_CARDS` {ícone: texto alternativo da foto do card} — uma entrada por ícone usado.
- `FILTRO` (texto): a frase do filtro (o que o cliente NÃO faz/atende, dita como personalização).
- `PASSOS` [[título, destaque (true só no 1º, o filtro), texto]] 4–5 itens — como funciona, da marcação ao depois.
- `ESPACO` [[foto, legenda]] — fotos espaco-/sala- das FOTOS DISPONÍVEIS; `SALA_HEAD` e `SALA_TEXTO` (texto).
- `FAQ` [[pergunta, resposta]] 6–8 itens (padrão v3) — perguntas reais de paciente; respostas com os FATOS FIXOS.
- `BAIRROS` [texto] — só os que os insumos citam; se nenhum, [] e uma pendência.
- `PADRAO_PAGINA` {ASSINA_NOME, ASSINA_LINHA, QUEM_ETIQUETA, QUEM_HEAD, CONSULTA_HEAD, OG_ALT}.
- `PAGINA_PRINCIPAL` {TERMO, H1_HTML, TITLE, DESCRICAO, LEAD} — o eixo sai do termo principal dos insumos; TITLE ≤ 60
  caracteres, DESCRICAO ≤ 155.
- `MENSAGEM` (texto): a mensagem pronta do WhatsApp, começando por "Olá! Vim pelo site" (marcador do rastreamento), sem doença.
- `SERVICOS` [[tipo schema.org, nome]] (tipos: DiagnosticProcedure, SurgicalProcedure, TherapeuticProcedure, MedicalTest),
  `CONDICOES` [texto], `SABERES` [texto], `JSONLD_DESCRICAO` (texto, 1 frase).
- `PENDENCIAS` [texto] — o que falta decidir ou confirmar com o cliente/dona, uma frase cada (ex.: "CRM e RQE da Dra. X").

## Como escrever (o que separou a IA da página aprovada na rodada 2)
- **Concreto, não adjetivo.** Cada frase diz O QUE acontece, ONDE, QUEM faz ou QUANTO — nunca o valor abstrato.
  ✗ "Atendimento humanizado e excelência técnica."  ✓ "Tempo para ouvir o que incomoda e explicar o diagnóstico antes de qualquer decisão."
  ✗ "Equipamentos modernos para diagnóstico preciso."  ✓ "O exame X e o exame Y são feitos aqui, no mesmo dia da consulta." (só se os insumos disserem)
- **O LEAD fala da dor do paciente com a palavra dele** (o que ele não consegue fazer hoje) e do próximo passo — não de "cuidado completo".
- **Motivo = um fato do atendimento** que o concorrente talvez não tenha (atende sábado, exame no local, particular, retorno marcado).
- **Número = um fato que decide a escolha**: nota e total do Google, anos, municípios/cidades atendidas, dias e horários,
  exame ou equipamento no local, tipo de lente/técnica, localização. Um "número" pode ser palavra curta de fato
  ("Sábado", "OCT", "Centro") com o rótulo explicando. Nunca contagem de categorias, pilares, focos ou etapas.
- **Saúde (CFM):** explicar como um procedimento funciona é permitido; dizer que é seguro, rápido, sem dor ou que dá
  resultado é promessa — proibido. Detalhe clínico que não está nos insumos (anestesia, tempo de recuperação) não entra.
- **Espaço:** descreva o que se vê na foto (a sala, o aparelho), não o que se sente.
- O revisor automático recusa: vocabulário genérico (humanizado, excelência, de ponta, moderno, jornada, garantir,
  qualidade de vida, transformar vidas…), promessa (seguro, rápido, sem dor, melhor resultado), TITLE > 60, DESCRICAO > 155.
- **PREÇO NUNCA NA PÁGINA (regra da dona, 28-09-2026).** Nenhum valor em R$ em nenhum campo — nem nos NUMEROS, nem no FAQ,
  nem em "a partir de". A pergunta do valor, se entrar no FAQ, responde: "O valor da consulta é informado pelo WhatsApp antes
  do agendamento." Mesmo que os insumos tragam o preço.
- **FILTRO é uma frase só**, e ela é copiada idêntica no passo 01 e no início da 1ª resposta do FAQ (o sistema confere).
- **FAQ só com resposta dos insumos.** Pergunta frequente cuja resposta não está nos insumos (formas de pagamento,
  parcelamento, anestesia, tempo de cirurgia, reembolso, atendimento infantil, urgência) NÃO entra na página: vai para
  PENDENCIAS como "pergunta para o cliente responder". Explicar o que é a doença ou o exame pode; dizer como a CLÍNICA faz, não.
- **"No mesmo dia"** só se os insumos disserem. Exame "no instituto" (no local) é outra coisa, e pode quando a lista de exames está nos insumos.
- **O ícone é o assunto do card.** `card-holep` só num card de HoLEP; `card-hormonal` só em hormônio. Se nenhum ícone
  disponível corresponde a um serviço, esse serviço não vira card (vai para SERVICOS/CONDICOES) e outro serviço dos insumos
  que TENHA ícone ocupa o lugar. Ícone trocado para "não repetir" é erro grave: a foto mostra outra coisa.
- **Número sobre o público** (porcentagem de homens, faixa de idade, classe) descreve o cliente para a agência — não decide a
  escolha do paciente e não entra na faixa de números.
