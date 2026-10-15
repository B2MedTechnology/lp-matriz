# 03 · Insumos e briefing

**Em uma frase:** o que coletar e conferir antes de abrir o editor — NAP, decisões de SEO, fotos, marca, credenciais, números com fonte — e o que fica pendente para um humano decidir, porque insumo errado não se conserta com CSS.

---

## Por que insumo vem antes

- **O erro caro não é falta de técnica, é insumo.** Quatro rodadas reprovadas numa capa tinham uma causa só: a foto do cliente novo não tinha a composição exigida (ver o porteiro em [anatomia §0](02-anatomia-da-pagina.md)).
- **SEO é insumo, não etapa posterior.** Coletado junto com o resto, na mesma sessão; senão vira retrabalho na hora de indexar (ver [SEO e velocidade](05-seo-e-velocidade.md)).
- **Faltou insumo durante a construção?** Use a alternativa que a doutrina dá ou pergunte. Nunca remova dobra ou troque formato de card por conta própria ([padrão](01-padrao.md)).

---

## 1. O que levantar, sempre, antes do primeiro pixel

| Item | Onde costuma estar | Por que trava se faltar |
|---|---|---|
| **O cliente já tem site?** | busca pelo nome + `site:` | Muda domínio, SEO e o que a página precisa provar. Página nova indexada compete com o site antigo pelo mesmo nome. |
| **Objetivo da campanha** | o responsável pela conta | Mensagem ou cadastro? Qual serviço? Muda o texto inteiro. |
| **O que os anúncios prometem** | as campanhas ativas | A página continua a frase do anúncio. Ler antes de escrever a capa. |
| **Termos de busca reais** | relatório de termos de pesquisa | O eixo (H1, title) sai da busca real, não do briefing. |
| **NAP do Perfil da Empresa no Google** (nome, endereço, telefone **exatos**) | o Perfil do cliente | É o NAP canônico. O do briefing costuma divergir — numa página, eram dois telefones diferentes e o schema saiu com o errado. |
| **`PLACE_ID` e `cid` do Perfil** | URL do Perfil / Places | `?lugar=` das avaliações, `sameAs`, link "ler todas". |
| **Número de contato**, conferido | bio, site, Perfil | É o único ponto de conversão. **Testar clicando** (já apareceu número com dígito a menos). |
| **Bairros atendidos** | briefing | `areaServed`. Coletar e não usar é desperdício comum. |
| **Perfis oficiais** (Instagram, Doctoralia, Facebook, Bing, Apple) | busca pelo nome | `sameAs` — amarram a entidade. |
| **Credenciais** (registro profissional, especialista, formação, ano) | site do conselho, site do cliente | `hasCredential`, `alumniOf`, rodapé, "quem é". |
| **Identificação legal** | conselho / registro | Saúde: nome, CRM, RQE. Advocacia: OAB. Comércio: razão social e CNPJ (00.000.000/0000-00). |
| **Horário e endereço** conferidos | Perfil do Google | Bairro errado quebra a ficha. Horário só exato entra no JSON-LD. |
| **Fotos em alta** | pasta do cliente, ensaio | Acervo de Instagram é quase todo arte com texto queimado. Passar pelo porteiro da capa. |
| **Arquivo do logo + manual de marca** | o cliente | Sem logo, o cabeçalho vira nome tipografado. O manual traz logo em vetor, fontes e cores — e o que ele define substitui o que a página escolheu (houve cinco rodadas com uma montagem do logo antes de o manual chegar). |
| **Prova social** | Perfil do Google, o cliente | O campo do checklist sempre volta vazio. A dobra de avaliações lê o Perfil. |
| **Números da faixa** (tempo de atuação, atendimentos, cirurgias…) | o cliente, com fonte | Cada um com fonte registrada e `confirmado=True`. |
| **Revisor do conteúdo** | o cliente | Quem lê (médico, responsável técnico) e quando. Sem revisão, sem `reviewedBy`. |
| **Conselho profissional** | a área do cliente | Define travas do gerador (avaliações, espaço, "grátis", depoimento). |

### As cinco decisões de SEO que vêm antes do desenho
1. **Qual é o NAP canônico** — idêntico ao Perfil em todo lugar.
2. **Quantas URLs, e qual é a canônica** — variantes por palavra-chave são úteis ao anúncio, mas trazem risco de *doorway*.
3. **A página vai ser indexada?** — muda robots, canonical, sitemap. Um interruptor (`INDEXAR`), nunca edição à mão.
4. **Quais entidades a página declara** — credenciais, especialidade, área servida, temas.
5. **Quem lê além do Google** — ChatGPT, Gemini, Perplexity, Copilot.

### Médico? O Doctoralia costuma ter o que o checklist não tem
Numa página, o campo de prova social voltou vazio, mas o perfil público da médica entregou de uma vez: avaliações, nota, depoimentos com nome, formação (residência e ano) e tempo de atuação. São dados **públicos e autodeclarados** — usar com atribuição à fonte. **O endereço de lá pode estar desatualizado** (apontava outro bairro). Preço que aparecer lá **não vai para a página** (regra da casa).

### Duas fontes do cliente que se contradizem exigem uma terceira
Registro profissional com dois dígitos trocados entre o Instagram e uma arte publicada → o site oficial decidiu. E ainda gerou um aviso útil ao cliente: **existe arte circulando com o número errado**.

---

## 2. Colher fotos e mídia

### Pasta compartilhada do Drive
Quando a listagem por pasta volta vazia pela API, a visão incorporada da pasta (`drive.google.com/embeddedfolderview?id=<ID>#list`) devolve HTML puro com o nome e o identificador de cada arquivo; a miniatura em alta (`thumbnail?id=<ID>&sz=w2400`) baixa cada um. Para triagem de muitas fotos (uma vez, 142), montar **uma folha de contato** em HTML e olhar tudo de uma vez.

### Instagram do próprio cliente (com autorização dele)
- Foto em tamanho cheio de um post: `/p/<shortcode>/media/?size=l`, com user-agent de navegador.
- **Nunca usar a `og:image` de post em vídeo**: vem com o ▶ queimado.
- A legenda inteira (curtidas, comentários, data e texto) sai na `og:description` do post lido com o user-agent de pré-visualização de links — dá para montar o acervo de **texto** (horários, unidades, produtos) sem sessão logada.
- Leitura em sessão logada tem limite baixo (resposta 429 depois de ~10 leituras seguidas): **parar na primeira 429**.
- Cardápio, tabela e preço de destaques **se pedem ao cliente** — o de lá pode estar velho (e preço não vai à página de qualquer forma).
- Preferir sempre a Graph API do Instagram com o token autorizado pelo cliente quando houver.

### Quadros tirados de um Reel/vídeo do cliente
Para uma página de evento, o melhor acervo pode ser o vídeo do próprio evento (comida real daquele dia, salão).
1. **Folha de contato de 1 em 1 s** para achar as cenas; depois **0,1 s em volta de cada corte** — a legenda do vídeo entra uns décimos depois do corte, e é aí que mora o quadro limpo (ou recortar abaixo da legenda).
2. **Cor:** gravar o quadro **sem perfil de cor** embutido, senão clareia.
3. **Resolução:** 1080 de largura dá capa e cards; não dá foto de 1920 nítida — a capa fica em ~60% da tela.
4. A arte do anúncio (feed/story) serve para o OG (o letreiro que as pessoas reconhecem) e para faixas entre textos.

### Foto e IA
- **Nunca** banco de imagem para pessoa ou lugar do cliente; **nunca** IA gerando pessoa ou resultado.
- Banco livre (ex.: Pexels) só para ilustrar **tratamento** nos cards de serviço (regras em [anatomia §6c](02-anatomia-da-pagina.md)). Negócio de produto: só foto do próprio cliente.
- Vídeo por IA só a partir de foto real, de ambiente, equipamento ou produto — não animar gente sem decisão explícita do cliente (ver [componentes](06-componentes.md)).

---

## 3. Recortar e preparar imagem

**Recorte com âncora**, para o assunto não ficar no lugar errado:

```python
from PIL import Image
def corta(origem, destino, ratio, anc_y=.5, larg=1200, q=84):
    im = Image.open(origem).convert("RGB"); W, H = im.size
    if W/H > ratio: nw, nh = int(H*ratio), H
    else:           nw, nh = W, int(W/ratio)
    im = im.crop((int((W-nw)*.5), int((H-nh)*anc_y),
                  int((W-nw)*.5)+nw, int((H-nh)*anc_y)+nh))
    im = im.resize((larg, round(im.height*larg/im.width)), Image.LANCZOS)
    im.save(destino, "JPEG", quality=q, optimize=True, progressive=True)
```

**Alargar o quadro estendendo o fundo** (quando o cliente pede "afastar", não ampliar) — funciona com foto de fundo liso:

```python
# amostra uma coluna que seja fundo em TODAS as linhas (a outra pode ter roupa)
fundo = [tuple(sum(px[cw-1-x, y][c] for x in range(8))//8 for c in range(3))
         for y in range(ch)]
# pinta as laterais linha a linha, cola a foto no meio,
# e passa GaussianBlur(11) só nas faixas laterais para não listrar
```
Referência: quadro de 1024 → 1311 px de largura (143 px de cada lado); a pessoa aparece da cabeça à cintura sem perder um pixel. Toda a faixa inventada tem de caber na parte transparente da máscara da capa.

**Arte de Instagram com texto queimado:** recortar a região limpa e normalizar para 4:3. Costuma sobrar imagem boa em 5 de 10.

**Saída para a web:** AVIF por largura + JPEG de reserva, cores sem perfil, `width`/`height` declarados (ver [SEO e velocidade](05-seo-e-velocidade.md)).

---

## 4. Imagem de compartilhamento e favicon

- `og.jpg` de **1200×630**, JPEG < 600 KB, recortado do retrato principal ou da arte da campanha, com `og:url`, `og:site_name`, `og:image:alt` e `twitter:card`. Sem isso o link no WhatsApp abre sem prévia.
- Favicon: **PNG 48 e 96 + `apple-touch-icon` + `/favicon.ico`** em cada hostname. O monograma do manual de marca, na cor do desenho do logo. Um SVG `data:` embutido serve **só** como provisório na prévia — o Google não usa favicon `data:`, e a página não vai ao domínio com ele.

---

## 5. Checklist do briefing (entregar preenchido antes de desenhar)

**Negócio e campanha**
- [ ] Objetivo da campanha e serviço-foco.
- [ ] Frase principal dos anúncios ativos.
- [ ] Termos de busca reais que trazem clique (para o eixo/H1).
- [ ] O cliente já tem site? Qual domínio? Vai ser substituído, convive, ou a página vira subdomínio?

**Identidade e contato**
- [ ] NAP copiado do Perfil do Google (não do briefing), com `PLACE_ID` e `cid`.
- [ ] WhatsApp testado clicando.
- [ ] Perfis oficiais para `sameAs`.
- [ ] Identificação legal completa e registro profissional conferido em duas fontes.
- [ ] Horário exato (ou registrado como inexato → fora do JSON-LD).
- [ ] Bairros/área atendida.

**Material**
- [ ] Foto da capa passou no porteiro (plano geral, ar acima da cabeça ≈ 17% da dobra, nenhuma borda corta a pessoa, lado do texto calmo).
- [ ] Foto vertical própria para o celular.
- [ ] Fotos do espaço (ou marcadores tracejados até chegarem).
- [ ] Logo em vetor e manual de marca (ou registro de que não existe).
- [ ] Foto de cada profissional do corpo clínico (ou vaga marcada).

**Conteúdo**
- [ ] Números com fonte, cada um `confirmado=True` ou fora da faixa.
- [ ] Lista de serviços/tratamentos reais, agrupáveis em grupos de 3.
- [ ] O filtro (convênio, antecedência, público) e o ganho que ele permite.
- [ ] 6 a 8 perguntas reais do atendimento.
- [ ] Revisor e data prevista de revisão.

**Decisões de SEO**
- [ ] Indexar? Quantas URLs? Qual canônica?
- [ ] Entidades a declarar (subtipo schema.org mais específico).

---

## 6. O que fica pendente para um humano (nunca decidir sozinho)

Registrar cada item no `LEIA-ME.md` do projeto, numerado, com o que falta e quem resolve:

1. **Publicar e indexar** — tirar o `noindex`, apontar domínio, indexar: decisão do responsável pela conta, depois da aprovação do cliente.
2. **Foto que não passou no porteiro** — fotografar de novo ou autorizar alargar o quadro.
3. **Números sem fonte** — confirmar com o cliente; até lá, fora da faixa.
4. **Tratamento citado sem fonte** — confirmar onde é feito.
5. **Curadoria de avaliações** — em saúde, apontar uma vez o que o conselho diz sobre republicar depoimento e deixar o profissional decidir; avaliações de pessoas com o mesmo sobrenome do cliente ou que citem preço: avisar.
6. **Revisão técnica do texto** pelo profissional (habilita `reviewedBy`).
7. **Animar pessoa em vídeo de IA** — o risco é nomeado uma vez; quem decide é o cliente.
8. **Fonte paga do manual** — só com licença web do cliente.
9. **DNS do domínio** — quem tem acesso cria o CNAME; confirmar antes de salvar a zona.
10. **Mudanças de layout em páginas já no ar** — migrar formato antigo só com pedido.
11. **Qualquer exceção ao esqueleto** — dobra que sai precisa de motivo legítimo declarado na página.
