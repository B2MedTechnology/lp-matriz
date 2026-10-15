# Odontologia — o que o CFO permite numa landing page

Normas: **Código de Ética Odontológica** (aprovado pela Resolução CFO-118/2012; arts. 43, 44 e 45) e **Resolução
CFO-196/2019** (selfie e imagens de diagnóstico e resultado). Não é parecer jurídico. O texto integral dos artigos deve
ser conferido no site do CFO antes de usar um ponto como argumento com o cliente.

> **A diferença que mais pesa:** o CFM liberou preço de consulta em 2023; **o CFO não**. O art. 44 trata como infração a
> publicidade com **preços, serviços gratuitos, modalidades de pagamento** ou qualquer forma que signifique
> comercialização da Odontologia. Em página de dentista não existe filtro por preço: nem "avaliação gratuita", nem
> "12× no cartão", nem "a partir de R$". (Regra da casa, de qualquer forma: preço nunca vai na página — o FAQ do valor
> responde *"informado pelo WhatsApp antes do agendamento"*.)

Ver também: [medicina](medicina-cfm.md) (clínica mista) · [copy](../04-copy.md) · [anatomia](../02-anatomia-da-pagina.md).

---

## 1. Identificação obrigatória (art. 43)

- **Nome e número de inscrição** da pessoa física **ou jurídica** no CRO.
- Clínica (pessoa jurídica): **nome e inscrição do responsável técnico (RT)**.
- Imagem de diagnóstico ou resultado (Res. 196/2019): **nome do profissional que fez o procedimento e o CRO dele**, na
  própria peça.

Pode acompanhar (art. 43, §§): áreas de atuação, procedimentos e técnicas, **especialidades registradas**, títulos de
formação, logotipo, endereço, telefone, e-mail, horário, convênios e credenciamentos, atendimento domiciliar e hospitalar.

**Na página:** "Responsável técnico: Dr. Anselmo Rubim · CRO-UF 0000" no rodapé **e** perto do bloco da equipe; a inscrição
da clínica (CRO-UF EPAO 0000) no rodapé; no JSON-LD, `Dentist` (+ `MedicalClinic` se houver médico) com `hasCredential`
do RT. **Sem esses dados a página só vai ao ar como prévia `noindex`.**

## 2. O que é infração (art. 44) e como fica na página

| Vedado | Exemplo típico | Como fica |
|---|---|---|
| Preço, gratuidade, forma de pagamento | "consulta R$ 100", "avaliação gratuita", "parcelamos" | O filtro é **particular, sem convênio**, pelo que o paciente ganha (tempo, explicação, acompanhamento) |
| Superlativo, comparação, ranking | "somos a número 1 em aparelho estético", "clínica de referência" | Fala do próprio serviço, sem ranking |
| Título não possuído ou não registrado | "especialista" sem especialidade registrada no CRO | "Especialista em Ortodontia" **só com a especialidade registrada** — conferir na busca do CFO |
| Imagem do "durante" | instalação de aparelho com afastador | **Nunca**, nem nos cards — "evitar pânico, receio ou medo" |
| "Antes e depois" com finalidade comercial | sorrisos do feed | Só como imagem de diagnóstico/resultado, **com TCLE**, publicada por quem fez, com nome e CRO. Em LP de campanha: **não usar** |
| Depoimento como peça de venda | depoimentos sem fonte ("Iolanda S.") | Não se publica depoimento sem fonte; inventado, nunca |

## 3. O que a Res. CFO-196/2019 liberou

- **Selfie** do dentista, com ou sem paciente (com autorização escrita do paciente).
- **Imagem de diagnóstico e de resultado** — regulamentada, não liberada: só quem fez divulga, com TCLE e com nome + CRO
  na peça. O "durante" continua vedado.

## 4. Avaliações do Google em página de dentista

Guias de mercado dizem que republicar avaliação de paciente é vedado; o texto do Código não foi conferido por inteiro.
**Até conferir, a dobra de avaliações entra só com decisão escrita do cliente e do RT**, com **nota e contagem** (fato)
e **sem o texto** das avaliações — a mesma lógica da curadoria médica, um degrau mais conservadora. Registrar a decisão
com data no LEIA-ME do projeto.

## 5. Clínica com dentista e médico

Cada frente responde ao seu conselho na mesma página:

- odontologia → CFO (sem preço; RT com CRO);
- medicina → CFM 2.336/2023 (nome, CRM, RQE). O CFM permitiria preço, mas numa página que não pode ter preço para o
  dentista **não se publica preço nenhum** — preço numa frente só confunde e parece brecha.

## 6. Como conferir o registro

- Dentista e especialidade: busca pública de inscritos do CFO/CRO (por nome ou número).
- Médico da mesma clínica: busca de médicos do CFM (CRM + RQE).
- Fonte do próprio cliente (Instagram, placa, receituário) + conselho; divergindo, a do conselho decide.

## 7. Direção do vento

Em 2025 o CADE questionou a proibição de promoções do CFO. Se a regra de preço mudar, muda por resolução nova:
reconferir o art. 44 antes de afirmar qualquer coisa ao cliente. A regra da casa (sem preço) não muda.

## 8. Trava no gerador

O gerador de página odontológica **para** (erro, não aviso) se encontrar `R$` seguido de número fora de script,
"grátis"/"gratuit", "a partir de" ou `aggregateRating`.

## 9. Checklist — página odontológica

- [ ] Nome e CRO de cada dentista; RT com CRO no rodapé e perto da equipe; inscrição da clínica no rodapé.
- [ ] "Especialista em X" só com especialidade registrada (conferida no CFO).
- [ ] Nenhum preço, gratuidade, forma de pagamento, "avaliação gratuita", parcelamento — nem no FAQ, nem nos números.
- [ ] Nenhum superlativo, ranking, "referência", "número 1".
- [ ] Nenhuma imagem do "durante"; nenhum antes/depois em página de campanha.
- [ ] Nenhum depoimento sem fonte; avaliações só com decisão escrita do cliente e do RT (nota e contagem, sem texto).
- [ ] Clínica mista: frente médica com CRM/RQE e, mesmo assim, sem preço.
- [ ] Sem os dados do RT: página em `noindex`.
- [ ] JSON-LD `Dentist` com `hasCredential` do RT; sem `aggregateRating`.
