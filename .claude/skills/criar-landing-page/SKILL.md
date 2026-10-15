---
name: criar-landing-page
description: Cria a landing page de um cliente no padrão da matriz, nas DUAS versões (estática e com vídeo na rolagem), do briefing à prévia noindex. Use quando pedirem "cria a landing page de…", "página para o cliente…", "LP nova", "refaz a página", "versão com vídeo", ou mandarem briefing, fotos do Drive, Instagram ou Perfil do Google de um cliente.
---

# Criar landing page (matriz)

Leia antes, **inteiros**: `doutrina/01-padrao.md`, `doutrina/02-anatomia-da-pagina.md`, `doutrina/03-insumos-e-briefing.md`,
`doutrina/04-copy.md` e o conselho da área em `doutrina/conselhos/`. Lições: `doutrina/10-licoes-aprendidas.md`.

## 0. Pasta do cliente — FORA do repositório
`../clientes/<slug>/` com `insumos.md` (briefing + pedido), `cliente.json` (comece do `exemplos/clinica-exemplo/cliente.json`
e troque TODOS os fatos) e `site/assets/` (css, js e fonts de `exemplos/_assets/`; fotos tratadas em `img/`).
Nunca crie nada do cliente dentro do repositório.

## 1. Insumos (checklist em `03-insumos-e-briefing.md`)
Briefing, fotos (Drive), logo, Instagram, Perfil do Google (NAP, horário, avaliações), registro no conselho e nome do
responsável técnico, termo principal da campanha, WhatsApp. **Faltou → pergunte; não invente.**

## 2. Capa e fotos — PARE
Escolha 3 candidatas à capa pelo porteiro (`02-anatomia-da-pagina.md` §0) e mostre à pessoa. **A pessoa escolhe.**

## 3. Conteúdo
`OPENROUTER_API_KEY=… python3 ia/gerar-conteudo.py --dir ../clientes/<slug> --insumos ../clientes/<slug>/insumos.md --area <medico|dentista|advogado|fisioterapeuta>`
Até 3 voltas de revisor + verificador. Leia `conteudo.json` e as PENDÊNCIAS. Pendência de fato vira pergunta à pessoa/cliente.

## 4. Prévia estática
`python3 ia/montar-previa.py saidas/<slug>/<carimbo> --dir ../clientes/<slug>` → publique a pasta `site/` como prévia
**noindex**. Meça: dobra 725/640, PageSpeed, JSON-LD, nenhum R$, botões do WhatsApp com a mensagem, e o aviso de
cookies em 390×844 e 360×640 **depois do `load`** (não pode cobrir o botão da capa).
**`python3 ferramentas/conferir.py <link da prévia>` tem de sair 0 antes de mostrar o link** (nas páginas geradas, antes do
deploy, rode nos arquivos `site/<página>/index.html`). Dobra que falta por decisão humana vai em `EXCECOES` do
`cliente.json`, com o motivo — nunca corte silencioso. Mostre o link e a lista "falta decidir".

## 5. Versão com vídeo — siga `video/README.md`
Análise das fotos → **PARE** (escolha) → ajuste → **PARE** (antes/depois) → movimento → **PARE** (opção + custo) → gerar com
`--aprovado "<frase da pessoa>"` → conferência dos 9 quadros → **PARE** (aprovação) → cena (`<slug>-cena`/`-video`, noindex).

## 6. Ir ao ar — só com OK humano
Domínio, DNS, indexação, Search Console, GTM (web + servidor no domínio do cliente). Nada disso sem o "pode" da pessoa.

## Antes de qualquer commit neste repositório
`python3 ferramentas/anonimato.py` = ✓ (sem o segredo da lista na máquina: `--sem-nomes`; o CI confere os nomes) e
`python3 testes/test_matriz.py` verde. Dados do cliente nunca entram.
