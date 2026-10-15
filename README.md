# lp-matriz — a matriz de landing pages (estática + vídeo na rolagem)

Tudo o que é preciso para criar a landing page de um cliente no padrão da casa, **sem depender de nenhum outro sistema e
sem nome de cliente nenhum dentro**: a doutrina (o que a página tem e por quê), o motor que monta a página, a IA que escreve
o conteúdo com revisor e verificador de fatos, a fábrica que roda num servidor, a esteira do vídeo na rolagem e um cliente
fictício que gera de ponta a ponta.

> **Duas versões, sempre.** Toda página nasce em duas: a **estática** (`<slug>`) e a **com vídeo** (`<slug>-video` ou
> `<slug>-cena`, `noindex`), em que um vídeo gerado por IA anda com a rolagem. O motor é o mesmo; a versão com vídeo só
> acrescenta a cena.

## O que tem aqui

| Pasta | O quê |
|---|---|
| [`doutrina/`](doutrina/) | As regras, em ordem de autoridade: [padrão](doutrina/01-padrao.md) · [anatomia da página](doutrina/02-anatomia-da-pagina.md) · [insumos e briefing](doutrina/03-insumos-e-briefing.md) · [copy](doutrina/04-copy.md) · [SEO e velocidade](doutrina/05-seo-e-velocidade.md) · [componentes](doutrina/06-componentes.md) · [lições aprendidas](doutrina/10-licoes-aprendidas.md) · [estado da arte 2026](doutrina/11-estado-da-arte-2026.md) · [conselhos profissionais](doutrina/conselhos/) (CFM, CFO, OAB, COFFITO) |
| [`motor/`](motor/) | `gerar.py` + o molde `template/pagina.html` + 74 ícones. Lê `cliente.json` e escreve o site pronto (HTML, CSS e JS embutidos, JSON-LD, sitemap, robots, `vercel.json`). |
| [`ia/`](ia/) | `gerar-conteudo.py` (a IA escreve o conteúdo seguindo o guia), `validar.py` (revisor mecânico), `verificar_fatos.py` (fato que o cliente nunca disse), `montar-previa.py`, `guia.py` (compila a doutrina por área), `regras-de-saida.md` (o contrato da IA). |
| [`fabrica/`](fabrica/) | O serviço que roda num contêiner: pega o pedido da fila, baixa as fotos do Drive, faz a ficha (IA com visão), escreve, monta e publica a prévia na Vercel. |
| [`video/`](video/) | A esteira do vídeo na rolagem: análise das fotos → ajuste → movimento → **escolha humana** → Veo 3.1 → conferência dos 9 quadros → cena. |
| [`sql/`](sql/) | A fila da fábrica (`lp_config`, `lp_pedidos` e as funções) para Postgres/Supabase. |
| [`exemplos/clinica-exemplo/`](exemplos/clinica-exemplo/) | Um cliente **fictício** (clínica de olhos) com o conteúdo no nível de uma página aprovada e imagens-marcador. É o exemplo que a IA recebe. |
| [`ferramentas/`](ferramentas/) | A trava de anonimato, o gerador de imagens-marcador. |
| [`testes/`](testes/) | O que segura as regras que já custaram caro. |

## Começar em 2 minutos (sem chave nenhuma)

```bash
python3 -m pip install pillow cryptography
python3 ferramentas/gerar-marcadores.py exemplos/clinica-exemplo
echo 0 > exemplos/clinica-exemplo/.versao
PYTHONHASHSEED=0 python3 motor/gerar.py exemplos/clinica-exemplo
python3 -m http.server 8000 --directory exemplos/clinica-exemplo/site   # abra /clinica-de-olhos-campinas/ e /clinica-de-olhos-campinas-cena/
python3 testes/test_matriz.py
```

## Criar a página de um cliente de verdade

**Com o Claude (recomendado):** abra uma sessão do Claude Code nesta pasta e peça *"cria a landing page do cliente X"*,
mandando o briefing, o link do Drive das fotos, o Instagram, o Perfil do Google e o termo principal da campanha. O
[`CLAUDE.md`](CLAUDE.md) e a skill [`criar-landing-page`](.claude/skills/criar-landing-page/SKILL.md) guiam a sessão pelo processo
inteiro, com as paradas para decisão humana. Os dados do cliente ficam numa pasta **fora** deste repositório.

**Pela linha de comando:**
1. Pasta do cliente fora do repositório (ex.: `../clientes/<slug>/`), com `cliente.json` (copie o do exemplo e troque os
   fatos) e `site/assets/` com as fotos tratadas — ver [insumos](doutrina/03-insumos-e-briefing.md).
2. Conteúdo pela IA: `OPENROUTER_API_KEY=… python3 ia/gerar-conteudo.py --dir ../clientes/<slug> --insumos ../clientes/<slug>/insumos.md --area medico`
   (`medico` · `dentista` · `advogado` · `fisioterapeuta`). Até 3 voltas de revisor + verificador; o que sobra vira PENDÊNCIA.
3. Prévia: `python3 ia/montar-previa.py saidas/<slug>/<carimbo> --dir ../clientes/<slug>` → `vercel deploy` da pasta `site/`
   (sempre `noindex` até alguém aprovar). **Conferidor do padrão:** `python3 ferramentas/conferir.py <link ou site/<página>/index.html>`
   tem de sair 0 antes de o link ir a alguém.
4. Versão com vídeo: [`video/README.md`](video/README.md).
5. Antes de ir ao ar: a lista "falta decidir" (capa, H1, números contraditórios, revisão do responsável técnico, domínio,
   indexação, GTM servidor) — [padrão](doutrina/01-padrao.md).

**Pelo painel (a fábrica num servidor):** [`fabrica/`](fabrica/) + [`sql/`](sql/) + [`Dockerfile`](Dockerfile). O painel grava o
pedido em `lp_pedidos`; o contêiner pega, gera e grava o link da prévia e as pendências. Custo medido: **~US$ 0,50 e ~7 min
por página** (Gemini 2.5 Pro pelo OpenRouter).

## Variáveis de ambiente
Veja [`.env.exemplo`](.env.exemplo). Nenhuma chave entra no repositório.

## Regras que não se negociam
- **Preço nunca vai na página.** A pergunta do valor responde *"informado pelo WhatsApp antes do agendamento"*. O revisor recusa qualquer R$.
- **Número só com fonte.** Sem fonte, não entra.
- **A IA não inventa.** O que não está nos insumos vira pergunta ao cliente (PENDÊNCIAS), não frase na página.
- **Prévia é `noindex`.** Indexar, domínio e DNS são decisão humana.
- **Animar gente (vídeo) só com o OK humano em cada passo pago.**
- **Nenhum nome de cliente neste repositório.** A trava (`ferramentas/anonimato.py`) roda no commit e no CI.

## A trava de anonimato
`python3 ferramentas/anonimato.py` varre todo arquivo de texto atrás de: (1) **nomes** — sequências de 1 a 6 palavras
comparadas, em hash com sal secreto, com a lista de bloqueio (lista e sal são segredos do repositório, nunca versionados;
sem eles na sua máquina, rode com `--sem-nomes` e o CI faz a checagem de nomes);
(2) **identificadores** — GTM/GA4/Ads/Meta, conta Google, telefone, CNPJ, registro profissional com número, e-mail, domínio,
IP. Placeholders aceitos: `exemplo.com.br`, `(00) 00000-0000`, `00.000.000/0000-00`, `GTM-XXXXXXX`, `CRM-UF 000000`.
Ligar no seu clone: `git config core.hooksPath .githooks`.
