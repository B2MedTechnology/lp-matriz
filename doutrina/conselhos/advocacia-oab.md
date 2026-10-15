# Advocacia — o que a OAB permite numa landing page

Normas: **Provimento nº 205/2021 do Conselho Federal da OAB** (revogou o 94/2000; arts. 3º e 6º e Anexo Único) e
**Código de Ética e Disciplina da OAB** (art. 44). Vale para página, anúncio e proposta de escritório de advocacia.
Não é parecer jurídico.

> **O que muda no modelo, em uma linha:** em página de advogado **saem duas dobras padrão** — a de **avaliações do
> Google** e a do **espaço físico** — e nenhum texto pode dizer "consulta grátis". (Regra da casa: preço nunca vai na
> página; aqui a própria norma já proíbe.)

Ver também: [anatomia](../02-anatomia-da-pagina.md) · [copy](../04-copy.md) · [componentes](../06-componentes.md).

---

## 1. O que libera trabalho

**Google Ads por palavra-chave é permitido de forma expressa.** Anexo Único do Provimento 205/2021: é permitida a
utilização de ferramentas de aquisição de palavra-chave quando responsiva a uma busca iniciada pelo potencial cliente.

Por que importa: é o argumento de venda da Pesquisa do Google para advogado — o anúncio só aparece para quem buscou.
Rede social (anúncio que interrompe quem não buscou) é terreno mais estreito: impulsionar **conteúdo informativo**,
nunca oferta de serviço.

## 2. O que é proibido

| Proibição | Onde | O que muda no trabalho |
|---|---|---|
| Referência, direta ou indireta, a **honorários, forma de pagamento, gratuidade ou descontos** | Prov. 205, art. 3º, I | Nada de preço na página nem no anúncio. **"Consulta grátis" é vedada** — é o chavão mais comum em anúncio de advogado |
| Dimensões, qualidades ou **estrutura física do escritório** na publicidade ativa | art. 6º | A dobra "o espaço" sai; "escritório moderno e confortável" também |
| **Promessa de resultado** e **casos concretos** para oferecer serviço | art. 6º | Nada de "causas ganhas", "valores recuperados" ou história de cliente — nem na faixa de números |
| Pagar para aparecer em ranking, prêmio ou honraria | citado por fontes secundárias | Conferir o artigo antes de usar como argumento; na dúvida, não usar selo de ranking |

## 3. Depoimentos e avaliações — a norma não cita, os Tribunais de Ética condenam

O texto do Provimento 205/2021 não menciona depoimento nem avaliação de cliente. Mas o entendimento majoritário dos
Tribunais de Ética e Disciplina é que depoimento elogioso na publicidade do advogado configura **captação de clientela e
mercantilização**. Há guias de mercado de 2026 dizendo que depoimento é permitido "com autorização" — **a leitura dos
Tribunais pesa mais**. Regra da casa:

- **Sem depoimento e sem carrossel de avaliações** na página.
- **Sem selo "5,0 no Google" na capa** (é a mesma avaliação, em outro formato).
- O perfil do Google pode ser **linkado** junto do endereço — quem quiser ler as avaliações vai até lá.
- O sinal de confiança da capa é a **inscrição na OAB** junto do nome, anos de atuação e áreas.

## 4. Identificação obrigatória (Código de Ética, art. 44)

**Nome (ou nome social) do advogado ou da sociedade + número de inscrição na OAB** em toda peça. O §1º lista o que pode
acompanhar: títulos acadêmicos, especialidades, endereço, e-mail, site, horário de atendimento, idiomas, logotipo.

Conferir cada inscrição no Cadastro Nacional dos Advogados antes de publicar. Número de OAB não se inventa nem se
"completa depois": no rodapé, "Dra. Fulana de Tal · OAB/UF 000000" para cada advogado e a sociedade com o registro dela.

## 5. Como isso vira desenho de página

| # | Dobra do modelo | Em advocacia |
|---|---|---|
| 1 | Capa | Igual; CTA "Falar com o escritório" — **nunca** "consulta grátis" |
| 2 | Números | Só **anos de atuação, áreas, formas de atendimento** (online, estados); nunca causas ganhas ou valores |
| 3 | Quem é | Um card por advogado: foto, nome e **OAB** |
| 4 | Catálogo | Vira **Áreas de atuação** — um card por área, com a foto do **objeto** do problema, não de gente |
| 5 | Como funciona | Do contato à análise do caso; **sem prazo nem resultado prometido** |
| 6 | O espaço | **Sai** (art. 6º) |
| 7 | Avaliações | **Sai** (Tribunais de Ética) |
| 8 | Perguntas frequentes | Vira o **coração da página**: a OAB quer publicidade informativa. Citar a lei em cada resposta |
| 9 | Onde e quando | Igual; sem escritório físico, vira dobra de **canais** (WhatsApp · vídeo · presencial agendado) |
| 10 | Rodapé | Sociedade + inscrição de cada advogado |

**Escritório sem sede própria:** `LegalService` **sem `address`** (sala de atendimento cedida, como a de uma sede da
OAB, não é endereço do escritório), com `areaServed` (cidade e estado), `openingHoursSpecification` e a dobra de canais
no lugar do mapa.

**O briefing do advogado costuma pedir o que a OAB veda** — consulta sem custo numa área, valor da consulta, honorários
por área, "melhores resultados", escritório "moderno e confortável". Nada disso entra; diga isso ao cliente **uma vez**,
na entrega, com o artigo.

## 6. Formulário e dados

O relato do caso num formulário é **dado pessoal** (LGPD). O envio do formulário (webhook, planilha) só se liga com
**política de privacidade publicada** e **aviso junto do formulário**. Ver [componentes](../06-componentes.md).

## 7. Dados estruturados

- `LegalService` (o tipo `Attorney` está **descontinuado** no schema.org), cada advogado como `Person` com a inscrição
  em `hasCredential`.
- `aggregateRating`/`review`: proibido pela política do Google e, aqui, também pela leitura dos Tribunais — pesa em dobro.
- Item do catálogo é `Service` (não há preço publicado, logo não existe `Product`).

## 8. Trava no gerador

O gerador de página de advocacia **para** se encontrar `aggregateRating`, "grátis"/"gratuit", `R$` com número, ou a
semente de avaliações (arquivo de avaliações copiado de uma página de saúde). Assim, copiar uma dobra de página médica
não reintroduz o vedado sem aviso.

## 9. Anúncios (Google Ads)

- Texto **informativo e sóbrio**. Fora: "grátis", "garantido", "o melhor", preço, desconto, "ganhe sua causa", número
  de causas.
- Negativas de partida: `modelo de petição`, `concurso`, `exame da ordem`, `jurisprudência`, `grátis`, `gratuito`,
  `vagas`, `estágio`, `curso`. Negativar "grátis" também tira quem procura a Defensoria Pública.

## 10. Checklist — página de advocacia

- [ ] Nome e OAB/UF de cada advogado junto do nome e no rodapé; sociedade com registro; conferidos no Cadastro Nacional.
- [ ] Nenhuma referência a honorários, pagamento, gratuidade, desconto — "consulta grátis" em nenhum lugar.
- [ ] Sem dobra do espaço; nenhuma qualidade da estrutura física no texto.
- [ ] Sem promessa de resultado, casos concretos, causas ganhas, valores recuperados.
- [ ] Sem depoimento, sem carrossel de avaliações, sem selo de nota do Google; perfil só linkado.
- [ ] FAQ informativo, com a lei citada; `FAQPage` igual ao visível.
- [ ] Formulário só com política de privacidade e aviso.
- [ ] JSON-LD `LegalService` + `Person` com OAB; sem `aggregateRating`; catálogo como `Service`.
- [ ] Gerador com a trava de palavras da OAB ligada.
