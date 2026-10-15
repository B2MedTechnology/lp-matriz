# Medicina — o que o CFM permite numa landing page

Norma: **Resolução CFM nº 2.336/2023**, em vigor desde **11-03-2024** (revogou a 1.974/2011). Vale para médico,
clínica médica e para a frente médica de uma clínica mista. Não é parecer jurídico: em dúvida, quem decide é o médico
que assina — o registro em risco é dele.

> **Regra da casa acima da norma:** o CFM permite divulgar o valor da consulta. **A casa não publica preço em página
> nenhuma** — nem na faixa de números, nem no FAQ, nem "a partir de". A pergunta do valor no FAQ responde:
> *"informado pelo WhatsApp antes do agendamento"*, mesmo quando o briefing traz o número.

Ver também: [copy](../04-copy.md) · [anatomia da página](../02-anatomia-da-pagina.md) · [SEO e velocidade](../05-seo-e-velocidade.md).

---

## 1. O que a norma permite

| Tema | O que a 2.336/2023 diz | Como a casa aplica |
|---|---|---|
| Preço | Pode divulgar valor da consulta e formas de pagamento, de forma clara, sem caráter promocional excessivo, sem pacote ou consórcio | **Não publica** (regra da casa). O filtro de público é feito por clareza, não por preço (§4) |
| Desconto e campanha | Campanha promocional com desconto é permitida; venda casada é vedada | Não se usa em página: preço não aparece, logo desconto também não |
| Antes e depois | Permitido com **finalidade educativa**, consentimento documentado, contexto clínico e sem sensacionalismo | Só com o termo de consentimento arquivado e decisão do médico registrada; nunca imagem manipulada ou "melhorada" |
| Depoimento | Não é mais proibido; deve ser **sóbrio**, "sem adjetivos que denotem superioridade ou induzam a promessa de resultado" (Cap. IX, alínea "g") | Curadoria de texto é opção do médico (§3) |
| Equipamento | Pode divulgar os equipamentos disponíveis no local de trabalho | Só o equipamento que existe; mídia a partir de foto real do aparelho |
| Imagem de banco | Permitida citando a origem | Evitar: foto real da pessoa e do lugar converte mais e é mais segura |

## 2. O que continua proibido

- Garantia de resultado e qualquer frase que a insinue ("resultado garantido", "100%", "sem dor").
- Sensacionalismo, comparação enganosa, autopromoção exagerada; "o melhor", "referência número 1", "melhor dermatologista de…".
- Afirmação sem comprovação científica.
- Publicidade que induza consumo desnecessário de serviço médico.
- Imagem de paciente manipulada ou melhorada.
- Equipamento que o consultório não tem (inclusive "aparecendo" em vídeo gerado por IA).

## 3. Identificação obrigatória

Em toda peça: **nome completo · CRM-UF 000000 · RQE 000000 · especialidade**.

- "Especialista" e o nome da especialidade só com RQE. Sem RQE, a página diz a área de atuação, não "especialista".
- Registro **junto do nome** (no bloco "quem é" e no cartão de cada médico), não só no rodapé. É o padrão das boas páginas
  médicas e é o sinal de confiança que dá para pôr na capa.
- Conferir CRM e RQE na busca pública de médicos do CFM. Duas fontes divergindo (Instagram × receituário × site antigo):
  vale a do conselho.
- Médico sem CRM/RQE confirmado: o cartão **sai** ou vira vaga ("em breve"), e a página fica em prévia `noindex`.
  Nunca publicar "CRM a confirmar".
- Clínica: identificar também o **diretor técnico** médico no rodapé.

## 4. Como isso vira desenho de página

**Filtro "somente particular" sem preço.** Ninguém lê a página inteira, então o aviso aparece em mais de um lugar:

1. logo abaixo do botão da capa, separado por um fio;
2. como primeira regra de "Como funciona a consulta", com peso de bloco;
3. na primeira pergunta do FAQ;
4. **na mensagem que abre no WhatsApp** — a secretária recebe o assunto resolvido.

Uma vez, discreto, de baixo contraste: não filtra. E o filtro vem **depois** do catálogo — nunca tratar quem lê como custo.

**A pergunta que vale dinheiro:** o médico emite nota e relatório para o paciente pedir reembolso ao plano? Se sim,
vira uma linha ("emitimos documentos para reembolso") e transforma recusa em paciente. Perguntar sempre no briefing.

**FAQ é conversão antes de ser SEO.** As três primeiras perguntas são as que a secretária responde o dia inteiro:
convênio, endereço, horário. O `FAQPage` em JSON-LD deixou de gerar resultado enriquecido no Google em **07-05-2026**;
a marcação fica como semântica barata (Bing, IAs), sempre igual ao FAQ visível — trocar a resposta nos dois lugares.

**Mensagem do WhatsApp sem doença.** Se a URL do clique vai para GA4/Ads, a mensagem pré-preenchida não leva doença nem
procedimento: é dado de saúde (LGPD, art. 5º, II) e a Meta proíbe parâmetro que reflita condição. Use "Vim pelo site e
gostaria de agendar uma consulta" ou retire a query no disparo da tag.

**Nome comercial de remédio trava o anúncio.** Um nome de marca de medicamento em qualquer lugar do HTML (texto, `alt`,
nome de arquivo, JSON embutido, comentário) limita o anúncio de saúde a 0 impressões. Use o nome genérico
("toxina botulínica") e filtre as avaliações ao vivo por uma lista fixa de nomes comerciais.

## 5. Avaliações do Google na página de um médico

> **Art. 8º, §1º** inclui "sites" na definição de rede própria do médico. **§3º:** publicação de terceiro ou paciente
> compartilhada ou repostada pelo médico passa a ser considerada publicação **dele**. Um carrossel de avaliações é peça
> publicitária do médico, não conteúdo de terceiro. **§4º:** elogio reiterado a técnica e resultado deve ser investigado
> pela comissão de divulgação do CRM.

O desenho que resolve:

1. **Nota e contagem são fato, não depoimento** — "5,0 em 36 avaliações no Google" entra sempre, automático, sem filtro.
   É onde mora a maior parte da credibilidade, e pode subir para a capa como selo (ver [anatomia](../02-anatomia-da-pagina.md)).
2. **O texto pode passar por curadoria** — uma lista de expressões de risco (`melhor`, `perfeito`, `incrível`,
   `fantástico`, `garante`, `100%`, `superou`, `milagre`…) segura a avaliação. **Ligar ou não é decisão do médico.**
   Apresente o risco **uma vez**, com o artigo na mão, registre a decisão com data e autoria no LEIA-ME do projeto e siga.
   Reabrir a cada página vira ruído. A decisão mais comum dos médicos é publicar todas ("é opinião do paciente, não
   copy do médico").
3. **Curadoria ≠ supressão.** Nunca esconder avaliação sem pedido do cliente; nota e contagem são as totais e há link
   "ler todas no Google".
4. **Conferir sobrenome.** Avaliação de parente publicada como paciente derruba a dobra inteira — com perfil pequeno,
   pesa muito mais (2 em 3 é diferente de 1 em 28). Levantar uma vez; o cliente decide.
5. **Conferir fato errado.** Relato longo pode afirmar algo que a clínica não tem (um equipamento que não existe). Como a
   republicação vira afirmação do médico, essa avaliação não entra. Avaliação **não se edita**: publica como está ou não
   publica. Elogio genérico não tem esse risco.
6. **Técnico:** "Fornecido pelo Google" visível; "há x dias" **calculado** da data, nunca congelado; **nunca**
   `aggregateRating`/`review` no JSON-LD com nota do Google (política de avaliações autosservidas); a chave da API vive
   no servidor. Detalhe em [componentes](../06-componentes.md).

## 6. Mídia gerada por IA

- **Pessoa e resultado sempre reais.** Retrato de médico gerado por IA é cada vez mais reconhecível e, revelado, a
  confiança cai mais em saúde do que em outros setores (CHI 2026, amostra pequena).
- IA só para **ambiente, textura, equipamento e transição**, partindo de foto real do local (imagem → vídeo).
- **Declarar na página** em uma linha: *"vídeo ilustrativo gerado a partir de fotos reais do consultório"*.
- A Res. CFM 2.454/2026 regula IA na prática médica, não na publicidade — não há exigência legal de rótulo hoje, mas a
  verificação de proveniência (C2PA/SynthID) está chegando à busca e ao navegador.
- Imagem que o cliente já publicou pode ser de IA: olhar os cantos (marca d'água) antes de usar.
- Arquivos de IA descartados não podem ficar servidos no domínio (pasta de reserva dentro de `assets/`).

## 7. Dados estruturados

- Médico solo: `IndividualPhysician` com `practicesAt` → `MedicalClinic`/`PhysiciansOffice` (`Physician` é ambíguo).
- `Person.name` sem "Dr./Dra." (o título vai em `honorificPrefix`); `hasCredential` com `name` (CRM, RQE).
- `medicalSpecialty` só com valor da enumeração do schema.org.
- `lastReviewed` **só junto** de `reviewedBy`, e só se a revisão aconteceu — com o revisor visível na página
  ("Conteúdo revisado por Dra. Fulana de Tal, CRM-UF 000000, em DD-MM-AAAA").

## 8. Checklist — página médica

- [ ] Nome completo, CRM-UF e RQE de **cada** médico junto do nome e no rodapé; conferidos no CFM.
- [ ] "Especialista" só com RQE; nenhum superlativo, "melhor", "referência", "garantido", "100%".
- [ ] Nenhum `R$` na página (texto, FAQ, números, JSON-LD); FAQ do valor = "informado pelo WhatsApp antes do agendamento".
- [ ] Filtro particular/convênio em ≥ 3 lugares + na mensagem do WhatsApp; pergunta de reembolso feita.
- [ ] Mensagem pré-preenchida sem doença/procedimento.
- [ ] Nenhum nome comercial de medicamento no HTML, `alt`, nomes de arquivo ou comentários.
- [ ] Avaliações: nota e contagem totais, "Fornecido pelo Google", data relativa calculada, link "ler todas";
      decisão de curadoria registrada; sobrenome e fato errado conferidos; sem `aggregateRating`.
- [ ] Antes/depois só com consentimento arquivado e finalidade educativa; nenhuma imagem de paciente retocada.
- [ ] Pessoa e resultado reais; mídia de IA declarada; nenhum equipamento inexistente.
- [ ] Diretor técnico no rodapé (clínica); "esta página não substitui uma consulta".
- [ ] JSON-LD: `IndividualPhysician`/`MedicalClinic`, credenciais com `name`, `reviewedBy` só com revisão real.
