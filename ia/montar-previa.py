#!/usr/bin/env python3
"""Junta o conteúdo da IA à infra do cliente e monta a PRÉVIA (noindex, sem o domínio do cliente) com o motor comum.
    python3 ia/montar-previa.py saidas/<cliente>/<carimbo> [--dir <pasta do cliente>]   (padrão: exemplos/<cliente>)"""
import json, pathlib, shutil, subprocess, sys, os
AQUI = pathlib.Path(__file__).resolve().parent.parent
d = pathlib.Path(sys.argv[1]).resolve(); ref = d.parent.name
CLI = pathlib.Path(sys.argv[sys.argv.index("--dir") + 1]).resolve() if "--dir" in sys.argv else AQUI / "exemplos" / ref
base = json.loads((CLI / "cliente.json").read_text(encoding="utf-8"))
c = json.loads((d / "conteudo.json").read_text(encoding="utf-8"))
t = lambda o: {"__t": [t(x) for x in o]} if isinstance(o, list) and o and not isinstance(o[0], (dict, list)) and False else o
for k in ["MARCA_LINHA", "NUMEROS", "QUEM_HEAD", "MOTIVOS", "CORPO_LEAD", "CORPO_CLINICO", "GRUPOS", "FOTOS_CARDS", "FILTRO",
          "PASSOS", "ESPACO", "SALA_HEAD", "SALA_TEXTO", "FAQ", "BAIRROS", "MENSAGEM", "SERVICOS", "CONDICOES", "SABERES", "JSONLD_DESCRICAO"]:
    if k in c: base[k] = c[k]
# A frase do filtro é UMA constante: o sistema a copia no passo 01 e na 1ª resposta do FAQ (doutrina: "igual nos três lugares").
if base.get("FILTRO") and base.get("PASSOS"):
    base["PASSOS"][0][2] = base["FILTRO"]
    f0 = base["FAQ"][0]
    if not f0[1].startswith(base["FILTRO"]):
        resto = f0[1].split(". ", 1)[1] if f0[1].lower().startswith("não") and ". " in f0[1] else f0[1]
        f0[1] = base["FILTRO"] + (" " + resto if resto and resto != f0[1] else "")
# Ícone de card sem desenho é erro de geração: para aqui com o motivo, não no meio do motor.
ic = set(base.get("ICONES", {}))
ruins = [x[1] for g in base.get("GRUPOS", []) for x in g[1] if x[1] not in ic]
if ruins: sys.exit(f"❌ card com ícone inexistente: {ruins} — disponíveis: {sorted(ic)}")
base["PADRAO_PAGINA"] = {**base["PADRAO_PAGINA"], **{k: v for k, v in c.get("PADRAO_PAGINA", {}).items() if not k.startswith("_")}}
base["PADRAO_PAGINA"]["_MOTIVOS"] = c.get("MOTIVOS", base["PADRAO_PAGINA"].get("_MOTIVOS"))
can = base["CANONICA"]
base["VARIANTES"] = {can: {**base["VARIANTES"][can], **c.get("PAGINA_PRINCIPAL", {})}}   # a prévia: só a página principal
base["TESTES"] = {}; base["CAMINHOS"] = {can: "/"}; base["INDEXAR"] = False; base["GTM_ID"] = ""
import urllib.parse
base["ZAP"] = "https://wa.me/" + base["WHATSAPP"] + "?text=" + urllib.parse.quote(base["MENSAGEM"])
p = d / "cliente"; p.mkdir(exist_ok=True)
(p / "cliente.json").write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
if not (p / "site" / "assets").exists():
    shutil.copytree(CLI / "site" / "assets", p / "site" / "assets")
(p / "insumos").mkdir(exist_ok=True)
r = subprocess.run([sys.executable, str(AQUI / "motor" / "gerar.py"), str(p)], capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-1500:])

# A PRÉVIA não herda o roteamento do site real (domínio, lp1…lp4, redirecionamentos): no *.vercel.app o "/" mostra a página
# principal, tudo sai com noindex, e nenhum endereço aponta para o domínio do cliente (28-09: a 1ª prévia caía num 404).
site = p / "site"
pags = sorted(x.name for x in site.iterdir() if x.is_dir() and (x / "index.html").exists())
principal = next((x for x in pags if x == can), pags[0] if pags else None)
vj = json.loads((site / "vercel.json").read_text(encoding="utf-8"))
previa = {"$schema": vj.get("$schema"), "cleanUrls": True, "trailingSlash": True,
          "rewrites": [{"source": "/", "destination": f"/{principal}/"}] if principal else [],
          "headers": [h for h in vj.get("headers", []) if h.get("source", "").startswith("/assets/")]
                     + [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]}]}
(site / "vercel.json").write_text(json.dumps(previa, ensure_ascii=False, indent=1), encoding="utf-8")
print("vercel.json da prévia: / →", principal, "· noindex · sem o domínio do cliente")
