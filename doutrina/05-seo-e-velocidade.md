# 05 · SEO e velocidade

**Em uma frase:** SEO é fundamento decidido no insumo, não acabamento — NAP do Perfil, canônica, interruptor de indexação, JSON-LD útil, sitemap e robots corretos, prévia em `noindex` sem bloquear o robô — e velocidade é regra da pilha, provada pelo Lighthouse com metas fixas (≥ 95 celular, 100 no resto, SEO 69 na prévia e 100 publicada).

---

## 1. A lição que gerou esta doutrina

Numa página de especialista, o SEO só foi auditado **na sexta rodada**. Até ali a página estava no ar **sem sitemap, com o telefone do schema divergindo do Perfil do Google, com schema raso e sem nenhum robô de IA considerado**. Nada era difícil; era **ordem**. O argumento que fez adiar era verdadeiro e mesmo assim errado: "metadados não entram no Índice de Qualidade do Google Ads". É fato — mas virou desculpa para não fazer o orgânico. **O correto é fazer as duas coisas desde o primeiro deploy.**

Os oito erros daquela página, para não repetir:

| # | erro | causa | custo |
|---|---|---|---|
| 1 | NAP divergente (telefone do briefing no schema; o Perfil publicava outro) | schema montado sem conferir o Perfil | alto — enfraquece a entidade na busca local, o canal principal de clínica |
| 2 | sem `sitemap.xml` | nunca entrou na lista | alto ao indexar |
| 3 | versão de produção do `robots.txt` nunca preparada | prévia tratada como estado final | alto |
| 4 | `sameAs` com 2 perfis e sem o Perfil do Google | `sameAs` tratado como enfeite | médio |
| 5 | sem `hasCredential`, `knowsAbout`, `alumniOf` | schema "que valida" ≠ schema útil | médio |
| 6 | `areaServed` só com a cidade | os bairros do briefing não foram usados | médio |
| 7 | *doorway* não levantado | duas variantes quase idênticas sem decidir canônica | alto se indexar |
| 8 | auditoria só no fim | não estava no processo | causa de 1 a 7 |

Seis dos oito são erros de **sequência**, não de conhecimento.

---

## 2. As cinco decisões antes do primeiro pixel

| decisão | por quê |
|---|---|
| **NAP canônico** (nome, endereço, telefone) | idêntico ao Perfil da Empresa em todo lugar. Decidir depois = reescrever schema, rodapé, FAQ e mapa. Vive numa constante só. |
| **Quantas URLs, e qual é a canônica** | variantes por palavra-chave servem ao anúncio, mas são o exemplo literal de *doorway* na política do Google. |
| **A página vai ser indexada?** | muda `robots`, `canonical`, sitemap e cabeçalhos. Um **interruptor** (`INDEXAR`, `CANONICA`) no gerador comanda tudo de uma vez — nunca editar à mão. |
| **Quais entidades a página declara** | credenciais, especialidade, área servida, temas. Sai do briefing; se não coletar, inventa depois. |
| **Quem lê além do Google** | ChatGPT, Gemini, Perplexity, Copilot. O caminho real do paciente: **a IA descobre · o Google confirma · o WhatsApp fecha**. |

### Variantes por palavra-chave: decidir cedo
Em `noindex` **não há risco** — o Índice de Qualidade do Ads não depende de indexação. O risco nasce no dia em que se indexa. Três saídas:
1. **Canônica única** — todas apontam o `canonical` para uma. Simples, concentra autoridade, mantém todas servindo ao anúncio.
2. **Só uma indexada** — as outras em `noindex, follow`, só para campanha. (Regra vigente: **uma URL indexável por termo**; variante de anúncio em `noindex, follow`.)
3. **Páginas de verdade** — conteúdo substancialmente diferente em cada uma.

### O que pesa mais que a página
1. **O Perfil da Empresa no Google é o ativo nº 1.** É a fonte que IAs e o 3-pack mais leem. Consertar categoria, horário, serviços e fotos rende mais que qualquer ajuste de página. (Um Perfil dizia "Aberto 24 horas", falso — isso vale mais que todo o resto desta doutrina.)
2. **Avaliações recentes** — boa parte das pessoas exige avaliação recente; a maioria descarta abaixo de 4 estrelas e pesa a resposta do dono.
3. **Search Console** (o relatório de IA generativa é a forma de medir presença nas IAs) + **Bing Webmaster/IndexNow** (sustenta o Copilot).
4. **Diretórios da área completos** (em saúde, o Doctoralia é fonte que as IAs leem).
5. **NAP idêntico em toda ficha** — site, Perfil, diretórios, Facebook, Bing, Apple.

---

## 3. Metadados e `<head>`

Ordem do `<head>`: charset · viewport · title · description · robots · canonical · GTM · Open Graph · ícones · `<style>` · JSON-LD.

- `<html lang="pt-BR">`; **um único `<h1>`** com o termo; hierarquia h2/h3 coerente.
- `title` ≤ 60 (termo exato + diferencial); `description` ≤ 155 (termo, bairro, razão para clicar); os dois falando da mesma coisa. (Os limites são heurística de redação, não exigência do Google — mas o gerador trava neles.)
- `canonical`, `og:url`, `og:image` **sempre numa URL que já responde 200**. Apontar para domínio sem DNS ou para outro servidor deixa a prévia do link sem imagem.
- Open Graph completo: `og:image` JPEG **1200×630 < 600 KB** com `?h=`, `og:image:alt`, `og:site_name`, `twitter:card`.
- Ao indexar: `<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">`.
- Favicon: PNG 48 e 96 + `apple-touch-icon` + `/favicon.ico` em cada hostname (o Google não usa favicon `data:`).
- **Não usar:** `meta keywords`, `geo.*`, `href="#"`.

---

## 4. Dados estruturados (JSON-LD) — raso não serve

Um `@graph` só, gerado. Esqueleto de referência (saúde):

```json
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "WebSite", "@id": "https://lp.exemplo.com.br/#site", "url": "https://lp.exemplo.com.br/", "name": "Clínica de Olhos Aurora" },
    { "@type": "MedicalWebPage", "@id": "https://lp.exemplo.com.br/#pagina",
      "url": "https://lp.exemplo.com.br/", "isPartOf": { "@id": "https://lp.exemplo.com.br/#site" },
      "dateModified": "AAAA-MM-DD",
      "about": { "@id": "https://lp.exemplo.com.br/#medica" } },
    { "@type": "IndividualPhysician", "@id": "https://lp.exemplo.com.br/#medica",
      "name": "Fulana de Tal", "medicalSpecialty": "Dermatology",
      "telephone": "+55-00-00000-0000",
      "address": { "@type": "PostalAddress", "streetAddress": "Av. Exemplo, 000, Sala 0",
                   "addressLocality": "Cidade", "addressRegion": "UF", "postalCode": "00000-000", "addressCountry": "BR" },
      "geo": { "@type": "GeoCoordinates", "latitude": -0.00000, "longitude": -0.00000 },
      "hasMap": "https://www.google.com/maps?cid=0",
      "sameAs": ["https://www.google.com/maps?cid=0", "https://www.instagram.com/exemplo"],
      "hasCredential": [{ "@type": "EducationalOccupationalCredential", "name": "CRM-UF 000000",
                          "recognizedBy": { "@type": "Organization", "name": "Conselho Regional de Medicina" } }],
      "alumniOf": "Universidade Exemplo",
      "knowsAbout": ["Tratamento A", "Tratamento B"],
      "areaServed": ["Cidade", "Bairro 1", "Bairro 2"],
      "practicesAt": { "@id": "https://lp.exemplo.com.br/#clinica" },
      "image": "https://lp.exemplo.com.br/assets/img/og.jpg?h=…" },
    { "@type": "FAQPage", "mainEntity": [ "(gerado da MESMA lista do FAQ visível)" ] }
  ]
}
```

**Regras**
- **Subtipo mais específico:** `IndividualPhysician` + `practicesAt` → `MedicalClinic`/`PhysiciansOffice`; `Dentist` + `MedicalClinic`; `LegalService` (nunca `Attorney`); `Bakery`; `HardwareStore`…
- `telephone` **idêntico** à página e ao Perfil; `address` completo, igual ao Perfil (inclusive torre/sala).
- `sameAs` com o **Perfil do Google primeiro** (`maps?cid=`), depois redes e diretórios.
- `geo` com ≥ 5 casas decimais; `hasMap`; `image` em 16×9, 4×3 e 1×1; `logo` ≥ 112×112 quadrado.
- `Person`/profissional com `hasCredential` (cada uma com `name`) e `name` **sem título**.
- `knowsAbout` com as condições/serviços em texto simples — é o mapa que IA e Google leem. `availableService` um por serviço, quando couber.
- `areaServed` = cidade **+ os bairros do briefing**.
- `openingHoursSpecification` **só se o horário for exato** (declarar parcialmente faz o Google entender que fecha nos outros dias).
- `MedicalWebPage` com `dateModified` verdadeiro; `lastReviewed` **só com** `reviewedBy` (depois que o profissional leu de fato).
- `FAQPage` = FAQ visível, da mesma lista. (Não gera mais resultado enriquecido no Google, mas fica pelas IAs e pela coerência.)
- **Proibido:** `aggregateRating`/`review` próprios (avaliação de terceiro como se fosse do site viola a política do Google); marcar o que não está visível; `VideoObject` em cena decorativa; valor fora da enumeração de `medicalSpecialty`; `priceRange` com valor em R$ (regra da casa: preço não vai na página).
- Profissional sem registro confirmado fica **fora** do JSON-LD.
- **Validação:** `json.loads` **não** detecta chave repetida (fica com a última). Validar com `object_pairs_hook`:

```python
import json, re
def sem_duplicada(pares):
    chaves = [k for k, _ in pares]
    dup = {k for k in chaves if chaves.count(k) > 1}
    if dup: raise SystemExit(f"JSON-LD com chave duplicada: {dup}")
    return dict(pares)
for bloco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
    json.loads(bloco, object_pairs_hook=sem_duplicada)
```

**Auditoria rápida da página gerada:**
```python
import json, re, os
h = open('site/index.html', encoding='utf-8').read()
ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S).group(1))
ent = [g for g in ld['@graph'] if g['@type'] not in ('WebSite', 'WebPage', 'MedicalWebPage', 'FAQPage')][0]
for k in ('telephone', 'sameAs', 'hasCredential', 'knowsAbout', 'areaServed', 'address'):
    print(k, '→', 'AUSENTE' if k not in ent else (len(ent[k]) if isinstance(ent[k], list) else ent[k]))
print('aggregateRating:', 'PROIBIDO — remover' if 'aggregateRating' in ent else 'ok')
print('h1:', len(re.findall(r'<h1', h)), '(deve ser 1)')
print('img sem alt:', len(re.findall(r'<img(?![^>]*alt=)', h)))
print('sitemap:', os.path.exists('site/sitemap.xml'))
```
E o teste manual que mais falta: **abrir o Perfil do Google do cliente e comparar telefone, endereço e horário, campo a campo, com a página.**

---

## 5. Prévia, robots, sitemap e indexação

### Prévia = `noindex` em dois lugares, com `robots.txt` aberto
- `<meta name="robots" content="noindex, nofollow">` **e** cabeçalho `X-Robots-Tag: noindex` — ambos gerados pelo `INDEXAR`.
- **`robots.txt` aberto** (`Allow: /`). Nunca `Disallow: /` na prévia: ele impede o Google de ler o `noindex` (a página pode aparecer na busca mesmo assim) e é a única peça com cache de até 24 h. Uma página ficou travada para indexar porque o domínio passou a responder com o `robots.txt` bloqueado da prévia.
- Para barrar algum robô específico na prévia, `Disallow` só a ele, em grupo próprio.

```json
{
  "trailingSlash": true,
  "headers": [
    { "source": "/(.*)", "has": [{ "type": "host", "value": "projeto-exemplo.vercel.app" }],
      "headers": [{ "key": "X-Robots-Tag", "value": "noindex" }] },
    { "source": "/teste-(.*)", "headers": [{ "key": "X-Robots-Tag", "value": "noindex" }] },
    { "source": "/assets/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] },
    { "source": "/(.*)", "headers": [
      { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" },
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
      { "key": "Content-Security-Policy", "value": "frame-ancestors 'self'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests" } ] }
  ]
}
```

### `robots.txt` de produção
```
# O grupo * já libera todos os robôs. Os grupos nomeados abaixo são DOCUMENTAÇÃO
# de quem deve entrar; atenção: grupos nomeados NÃO herdam regras do *.
User-agent: *
Allow: /

User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Googlebot
User-agent: Google-Extended
User-agent: Bingbot
User-agent: Applebot
User-agent: Meta-WebIndexer
User-agent: DuckAssistBot
User-agent: Amzn-SearchBot
User-agent: MistralAI-Index
Allow: /

Sitemap: https://lp.exemplo.com.br/sitemap.xml
```
A ideia de que os robôs "precisam estar explícitos" é mito: o `*` já libera. Não confundir robô de **busca** (citação) com robô de **treino**.

### Sitemap
- **Gerado**, nunca escrito à mão; só URLs **canônicas** indexáveis.
- Só `loc`, `lastmod` **verdadeiro** (data em que o conteúdo mudou, = `dateModified` = "página atualizada em") e `image:loc`.
- **Sem `priority` nem `changefreq`** — o Google ignora.

### Não publicar
`llms.txt` (o Google não usa; a auditoria tem peso desprezível e ausente = "não se aplica"; um *catch-all* que responda 200 em `/llms.txt` ou um 5xx **derruba** a categoria Agentic), `Content-Signal`, WebMCP como entrega, texto oculto, menções inautênticas. Não bloquear "AI Bots" no firewall da hospedagem. Não reenviar "Rastreada, mas não indexada" em série.

---

## 6. O fluxo da casa: prévia → prova → domínio → indexação

1. **Prévia** em `<projeto>.vercel.app`, `noindex` — é o que se mostra ao cliente.
2. **Prova com o cliente:** aprova texto, fotos e números (número sem fonte não entra; o profissional lê e aí entra o `reviewedBy`). O rastreamento é provado na prévia, menos a visita (a trava de host descarta o domínio de prévia de propósito).
3. **Domínio** — subdomínio do site do cliente quando ele já tem site (mesmo cookie do protocolo, mesmo servidor de medição, mesma trava):
   - `npx vercel domains add <sub.dominio> <projeto>` → `vercel domains verify` dá o **CNAME do projeto**;
   - quem tem acesso cria o CNAME no registrador (**subdomínio por CNAME, não troca de servidores DNS**, quando o domínio já tem outras coisas). Confirmar antes de preencher a zona e salvar na mesma rodada (a sessão do painel do registrador pode cair entre preencher e salvar);
   - certificado: com DNS certo e HTTPS ainda recusando, `npx vercel certs issue <host>` (já demorou 7 minutos depois do DNS);
   - o serviço de avaliações ganha o sufixo do domínio nas **origens aceitas** e se reimplanta;
   - a prévia redireciona para o domínio pelo **redirecionamento nativo da hospedagem** (308);
   - prova do rastreamento no domínio (visita registrada; apagar a de prova).
4. **Indexar** — nesta ordem:
   1. versão indexável **no ar antes de o DNS responder** (`INDEXAR=True`, canônica/`og:url`/`og:image` na URL que responde);
   2. `curl -I` no domínio: 200, **sem** `X-Robots-Tag`;
   3. 308 do `*.vercel.app` e do `http://` para o domínio;
   4. **Search Console com propriedade de DOMÍNIO** (TXT `google-site-verification=…` na raiz, na conta da agência) — cobre `www` e subdomínios;
   5. sitemap → Inspeção de URL → Testar URL publicado → **Solicitar indexação**; "Request a recrawl" no relatório de `robots.txt` se algo ficou em cache;
   6. Bing Webmaster (importar do Search Console) + **IndexNow** (chave aleatória, URLs do sitemap);
   7. Sharing Debugger da Meta;
   8. conferir no ar, com e sem barra final: principal 200 com `index, follow` e canônica no domínio; raiz, link antigo, prévia e `http://` em 308; páginas de teste com `noindex`; `robots.txt` liberado com `Sitemap:`; chave do IndexNow 200; JSON-LD sem chave repetida;
   9. conferir o Perfil do Google campo a campo contra a página.
5. **Anúncios:** teste 50/50 contra a página antiga (experimento do Google Ads).

Conferir também "Search generative AI = Include" na propriedade e medir no relatório de IA do Search Console e no AI Performance do Bing.

---

## 7. Como ler a nota do PageSpeed

O PageSpeed é o Lighthouse rodado nos servidores do Google. **Só auditorias com peso entram na nota**; "Insights" e "Diagnósticos" (payload, DOM, minificar) têm peso 0 — servem para achar a causa.

| categoria | o que pesa | na prática |
|---|---|---|
| **Performance** | TBT 30% · LCP 25% · CLS 25% · FCP 10% · Speed Index 10% | o que chega primeiro e o que trava a thread. No celular: 4G lento simulado (150 ms de ida e volta, ~1,6 Mbps) e CPU 4× mais lenta |
| **Acessibilidade** | cada regra do axe com seu peso; contraste e ARIA pesam muito | **um** tipo de erro em 20 elementos custa o mesmo que em 1. O axe conta a **opacidade**: texto a 16% "existe" e reprova |
| **Boas práticas** | HTTPS, console sem erro, proporção de imagem, bibliotecas sem falha conhecida | nasce 100 com o gerador (cai com cookie de terceiro de pixel) |
| **SEO** | "bloqueada para indexação" pesa ~4 de ~13 pontos; o resto pesa 1 cada | **com `noindex`, o teto é 69**. Não existe SEO 100 em prévia bloqueada |
| **Agentic Browsing** | auditorias de peso 1, nota = fração das aprovadas (árvore de acessibilidade, CLS, `llms.txt` só se existir e quebrar…) | é a acessibilidade vista por um agente de IA. Um `aria-label` proibido derruba Acessibilidade e Agentic ao mesmo tempo |

**SEO 69 na prévia é o número certo** — a auditoria reprovada tem de ser **só** "a página está bloqueada para indexação". Qualquer outra reprovada é conserto. **Tirar o `noindex` para "passar" não é conserto**: indexar é decisão de publicação. Para provar o 100 sem publicar, gerar uma cópia com `INDEXAR=True` e `BASE` local (§10).

**O celular oscila na mesma página** (ex.: 97–100) porque o Speed Index varia com o instante em que a fonte chega e com as entradas animadas da capa. Arrancar animação pedida pelo cliente para estabilizar 1–3 pontos é trocar pedido por número. **Leia a mediana.** Um 97 isolado não é regressão; três seguidos abaixo de 95, sim.

**O resumo mostra só os primeiros 5 elementos** — e já escondeu 18. **Contraste e ARIA se leem no JSON inteiro.**

---

## 8. A rota de velocidade — as regras que dão a nota

Caso de referência: uma página foi de **66 · 88 · 100 · 69 · 50** (Performance · Acessibilidade · Boas práticas · SEO · Agentic, celular) para **100 · 100 · 100 · 69 · 100**, com FCP 3,4–3,6 s → 1,0–1,5 s, LCP 5,3–17,7 s → 1,2–1,9 s, TBT 60–210 ms → 0–20 ms e CLS 0.

1. **Nada externo trava a pintura.** CSS **embutido** pelo gerador (lê `estilo.css`, tira comentário e espaço, injeta num `<style>`); fontes **locais** woff2 com recorte latino (inclui U+00C0–U+00FF, ª/º, U+2013–U+201D), `font-display: swap`; fonte variável só com 3+ pesos; `preload` só da fonte do título e só se o LCP for texto. **Nunca Google Fonts nem CSS em `<link>`** (eram ~1,9 s de espera antes da 1ª letra). Nas `url()` do CSS embutido, o caminho é relativo à **página**.
2. **Imagem na largura em que aparece.** AVIF por largura com JPEG de reserva; `width`/`height` sempre; `sizes` com a largura **real** (foto que cobre pela altura é mais larga que a tela: `sizes="(max-aspect-ratio: 2/1) 200vh, 100vw"`, nunca `100vw` às cegas); recorte em retrato para o celular e teto na maior largura. Cards em 3 larguras (400/660/800); logos em WebP por largura. Capa com `fetchpriority="high"` e **nunca** lazy; todo o resto lazy. Efeito medido: capa de 225 → 55 KB no desktop e 130 → 41 KB no celular; logo de 40 → 4–7 KB. **Não usar:** só AVIF sem reserva, JPEG XL, otimizador de imagem da hospedagem em `<img>` comum.
3. **O pesado espera o gesto; o terceiro espera a proximidade.** Vídeo sem `autoplay` e com `preload="none"` (play no 1º gesto ou 1–1,5 s depois do `load`; pôster = quadro 0); sequência de quadros no 1º gesto; API de avaliações e iframe do mapa **só perto da dobra** (observador com margem + rede de segurança pela rolagem). **Nunca por cronômetro pós-load** — puxa o terceiro para dentro da medição de quem nem rolou.
4. **Ler medidas só depois do quadro.** `getBoundingClientRect`/`offsetHeight` no meio do script força o layout inteiro (layout forçado de 69 ms e tarefas longas de 196 + 112 ms viraram TBT 0 com isso). Toda leitura de inicialização por `requestAnimationFrame(() => setTimeout(fn, 0))`; dentro de uma função, **todas as leituras antes de todas as escritas**.
5. **Acessibilidade é nota — e é o que o agente de IA lê.**
   - contraste ≥ **4,5:1** decidido no **token** (uma cor terciária de 4,0:1 derrubava vinte elementos; trocada por uma de 5,3:1);
   - `aria-label` só em elemento com papel (`role="img"`, botão, link, região) — `aria-label` num `<span>` de estrelas derrubou Agentic de 100 para 50;
   - link com nome **também no celular** (quando o texto some, o `aria-label` fica);
   - revelação (texto que acende, passo que esmaece) **só depois da 1ª rolagem**;
   - cor sólida no lugar de `opacity` em texto pequeno ("atualizada em" a 55% reprovava);
   - especificidade: `.secao a{color}` pinta os botões da seção → `:not(.botao)`;
   - alvo ≥ 24×24 px, skip link, `scroll-padding-bottom` = barra fixa, zoom 200%, botão de pausa (WCAG 2.2.2).
6. **SEO técnico pelo interruptor.** Title, description, canonical, robots, `X-Robots-Tag`, `robots.txt` e sitemap saem do gerador (`INDEXAR`); JSON-LD em `@graph`.
7. **Cache.** Imagem, vídeo, fonte, CSS e JS com `?h=<hash do conteúdo>` + `immutable` (o gerador põe o hash e **para** se o HTML apontar para arquivo inexistente); HTML com `max-age=0, must-revalidate`. Sem hash, CSS/JS nunca `immutable` (senão uma versão congela por um ano). **Não usar:** `no-store`, HSTS manual, COEP/COOP/Permissions-Policy, CSP estrita com hash sob GTM, Early Hints, Speculation Rules.
8. **Não minificar com etapa de build só para zerar um diagnóstico** de peso 0: o projeto é sem build e os comentários são a documentação.
9. **Deploy:** `.vercelignore` em lista de permissão (só `site/`) + sonda `curl` pós-deploy nos caminhos sensíveis; vídeo curto no deploy, longo em serviço de streaming; plano pago para cliente.

---

## 9. Medir — sempre todas as páginas, celular **e** desktop

1. **Lighthouse local na mesma versão do PageSpeed** (conferir no rodapé do relatório do PSI), sem cota, contra a URL **publicada** (a hospedagem comprime e manda os cabeçalhos; o servidor local não). Prévia que ainda não pode ser publicada: medir por um servidor local que aplique gzip e os cabeçalhos do `vercel.json` (com `http.server` puro, HTML de 100 KB e nota 94; com gzip e cabeçalhos, 25 KB e mediana 96).
2. **Mediana de 3 rodadas** na rotina e de **5** nas decisões de 1–3 pontos; máquina calma; uma medição por vez.
3. Contraste e ARIA no **JSON inteiro**.
4. Print final do PageSpeed web para o cliente (a API anônima esgota a cota em poucas chamadas; usar chave de API própria).
5. Mudou efeito de rolagem? Medir fluidez: 60 fps, 0 tarefas longas.
6. **Página com o GTM do cliente:** medir no endereço real bloqueando os hosts de envio (ex.: `--host-resolver-rules`), senão a medição vira **visita de teste** na conta dele (já gerou 8 PageViews falsos num pixel). Esperar a queda: um contêiner pesado levou ~100 → 67 no celular; com o GTM carregando depois da pintura, 86; boas práticas caem para ~77 pelo cookie de terceiro do pixel. Enquanto o contêiner não enxugar, a meta do celular é ~85–90 — o resto é contêiner, não página.
7. Validação em cadeia: `vnu` (HTML) → axe/pa11y em JSON → verificador de links → sonda de cabeçalhos (`curl -I`) nos dois hosts.
8. Campo: RUM com `web-vitals` v6 pelo `dataLayer`; CrUX quando houver volume.

### Metas
| | prévia | publicada |
|---|---|---|
| Performance celular | ≥ 95 (mediana) | ≥ 95 (mediana) |
| Performance desktop | 100 | 100 |
| Acessibilidade | 100 | 100 |
| Boas práticas | 100 | 100 |
| Agentic Browsing | 100 | 100 |
| SEO | **69** (só o `noindex` reprovado) | **100** |
| LCP celular (campo/lab) | < 2,5 s, ~300 KB antes do LCP | idem |

---

## 10. Comandos — colar e rodar

```bash
# Lighthouse local, celular e desktop (mesma versão do PageSpeed)
npx lighthouse https://lp.exemplo.com.br/ --form-factor=mobile --output=json --output-path=/tmp/lh/pagina-mobile.json
npx lighthouse https://lp.exemplo.com.br/ --preset=desktop --output=json --output-path=/tmp/lh/pagina-desktop.json
```
```python
# TODOS os elementos reprovados no contraste (o resumo mostra só os primeiros)
import json
lh = json.load(open('/tmp/lh/pagina-mobile.json'))
for it in lh['audits']['color-contrast']['details']['items']:
    n = it['node']; print(n['snippet'][:70], '|', n['explanation'].split('(')[1][:90])
```
```bash
# PROVAR o SEO de publicação sem publicar: cópia do gerador com INDEXAR=True e BASE local
P=/tmp/prova-seo; rm -rf $P; mkdir -p $P; cp -R gerar.py template site $P/
sed -i '' 's#^BASE = ".*"#BASE = "http://127.0.0.1:8950"#; s#^INDEXAR = False#INDEXAR = True#' $P/gerar.py
(cd $P && python3 gerar.py) && (cd $P/site && python3 -m http.server 8950 &)
npx lighthouse http://127.0.0.1:8950/ --form-factor=mobile --only-categories=seo   # tem de dar 100
pkill -f "http.server 8950"            # um servidor por vez
```
```bash
# Conferir cabeçalhos no ar (prévia e domínio)
curl -sI https://lp.exemplo.com.br/ | grep -iE 'HTTP/|x-robots|cache-control|content-security'
curl -sI https://projeto-exemplo.vercel.app/ | grep -iE 'HTTP/|location|x-robots'
curl -s -A "OAI-SearchBot/1.4" -o /dev/null -w "%{http_code}\n" https://lp.exemplo.com.br/
```

---

## 11. O que NÃO fazer

1. Deixar SEO para o fim.
2. Montar o schema com o telefone do briefing sem conferir o Perfil.
3. Publicar sem `sitemap.xml`; pôr `priority`/`changefreq` nele.
4. `Disallow: /` na prévia.
5. Schema mínimo "que valida" — validar não é o objetivo, ser lido é.
6. Coletar bairros e não usar no `areaServed`.
7. `aggregateRating` com nota de terceiro.
8. Indexar variantes idênticas sem decidir canônica; duas páginas indexáveis para sinônimos.
9. Editar robots, canonical, sitemap e meta à mão.
10. Achar que a página é o trabalho — o Perfil pesa mais.
11. Ler SEO 69 da prévia como SEO ruim; tirar o `noindex` para passar.
12. Publicar `llms.txt` para zerar aviso.
13. Puxar terceiro por cronômetro pós-load.
14. Apagar texto antes da 1ª rolagem.
15. `aria-label` em `<span>`/`<div>` sem `role`.
16. `sizes="100vw"` em foto que cobre pela altura.
17. Ler medidas no meio do script.
18. Confiar no resumo de 5 elementos.
19. Google Fonts ou CSS em `<link>`.
20. Data de geração como `dateModified`; data que muda sem mudança de conteúdo.

---

## Checklist de aceite

**Antes de desenhar**
- [ ] As cinco decisões tomadas e registradas (NAP, URLs/canônica, indexar, entidades, robôs).

**Na página**
- [ ] `<head>` na ordem; title ≤ 60 e description ≤ 155 sobre a mesma coisa; um `<h1>`.
- [ ] Canonical, `og:url` e `og:image` numa URL que responde; OG 1200×630 < 600 KB.
- [ ] Favicon PNG 48/96 + `apple-touch-icon` + `/favicon.ico`.
- [ ] JSON-LD em `@graph`, subtipo mais específico, NAP idêntico ao Perfil, `sameAs` com o Perfil primeiro, sem chave duplicada (`object_pairs_hook`), sem `aggregateRating`, sem R$, `FAQPage` = FAQ visível.
- [ ] CSS embutido, fontes locais, AVIF por largura com reserva, capa `fetchpriority="high"` sem lazy, `?h=` em todo asset.
- [ ] Nenhum terceiro no carregamento; nenhum cronômetro pós-load.

**Prévia**
- [ ] `noindex` na meta e no `X-Robots-Tag`; `robots.txt` aberto.
- [ ] Lighthouse: ≥ 95 celular (mediana de 3), 100 desktop, 100 acessibilidade, 100 boas práticas, 100 Agentic, SEO 69 com o `noindex` como única reprovada.
- [ ] Prova do SEO 100 com cópia `INDEXAR=True` local.

**Publicação**
- [ ] Sequência da virada cumprida na ordem (§6), `curl -I` conferido, 308 ativos.
- [ ] Search Console de domínio, sitemap enviado, indexação solicitada, Bing + IndexNow, Sharing Debugger.
- [ ] Sitemap só com canônicas, `lastmod` verdadeiro; `robots.txt` de produção com o `Sitemap:`.
- [ ] Perfil do Google conferido campo a campo contra a página.
