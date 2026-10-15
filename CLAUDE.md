# lp-matriz — leia antes de agir

Este repositório é a **matriz de landing pages** da casa: doutrina + motor + IA + fábrica + esteira de vídeo. Ele é
autossuficiente: **não existe outra fonte**. Tudo o que você precisa saber para fazer uma página está em `doutrina/`.

## A ordem é: doutrina → código → suposição
1. Antes de escrever ou mudar qualquer página, leia **inteiros** `doutrina/01-padrao.md` e `doutrina/02-anatomia-da-pagina.md`,
   e o conselho da área em `doutrina/conselhos/`. Em caso de conflito, o `01-padrao.md` manda.
2. O código diz como; a doutrina diz o que e por quê. Não redescubra no código o que a doutrina já diz.
3. Suposição só declarada: "a doutrina não diz (procurei X); o código faz Y; suponho Z".

## Para criar a página de um cliente
Use a skill **`criar-landing-page`** (`.claude/skills/criar-landing-page/SKILL.md`). Ela tem as paradas obrigatórias.

## Leis deste repositório (inegociáveis)
- **Nenhum dado de cliente entra aqui.** Briefing, fotos, `cliente.json` real, prévias e saídas ficam numa pasta FORA do
  repositório (ex.: `../clientes/<slug>/`). Antes de todo commit: `python3 ferramentas/anonimato.py` precisa dar ✓.
  A lista de bloqueio e o sal são segredos (nunca versionados); nunca enfraqueça a trava para um commit passar.
  Sem o segredo na sua máquina: `python3 ferramentas/anonimato.py --sem-nomes` — a checagem de nomes roda no CI.
- **Preço nunca vai na página** — "informado pelo WhatsApp antes do agendamento". O revisor recusa qualquer R$.
- **A IA não inventa fato.** Faltou nos insumos → vira PENDÊNCIA (pergunta ao cliente), nunca frase na página.
- **Toda página sai em duas versões**: estática e com vídeo na rolagem (`video/README.md`). A com vídeo é `noindex`.
- **Prévia é `noindex`.** Publicar no domínio do cliente, indexar e mexer em DNS só com o OK humano, na sessão.
- **Gerar vídeo e ajustar foto custam dinheiro e animam gente:** PARE e peça a escolha humana em cada passo (a ferramenta
  recusa gerar sem `--aprovado "<frase da pessoa>"`).
- **Segredo nunca em arquivo, chat ou commit.** Chaves só por variável de ambiente (`.env.exemplo` lista os nomes).
- Mudou o motor ou a IA → `python3 testes/test_matriz.py` verde antes do commit.

## Mapa rápido
`doutrina/` regras · `motor/gerar.py` monta · `ia/gerar-conteudo.py` escreve · `ia/validar.py` revisor · `ia/verificar_fatos.py`
verificador · `ia/montar-previa.py` prévia · `fabrica/` serviço da fila · `video/` vídeo na rolagem · `sql/` fila ·
`exemplos/clinica-exemplo/` o cliente fictício (modelo de forma e tom; nunca copiar fatos dele).
