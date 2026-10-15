"""Publica a pasta da prévia na Vercel da dona pela API (um projeto por cliente, "lp-<nome>-previa"), sem CLI:
sobe cada arquivo pelo sha1, cria o deploy de produção do projeto e espera ficar pronto. Devolve o endereço público."""
import hashlib, json, pathlib, time, urllib.error, urllib.parse, urllib.request

API = "https://api.vercel.com"


def _req(token, metodo, caminho, corpo=None, cab=None, time_id=None, bruto=None):
    url = API + caminho
    if time_id:
        url += ("&" if "?" in url else "?") + "teamId=" + urllib.parse.quote(time_id)
    h = {"Authorization": f"Bearer {token}"}
    h.update(cab or {})
    dados = bruto if bruto is not None else (json.dumps(corpo).encode() if corpo is not None else None)
    if corpo is not None:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=dados, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=120) as x:
            t = x.read()
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        corpo_erro = e.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"Vercel recusou {metodo} {caminho.split('?')[0]}: {e.code} {corpo_erro}") from None


def publicar(pasta: pathlib.Path, nome_projeto: str, token: str, time_id=None, espera=240):
    arquivos = []
    for p in sorted(pasta.rglob("*")):
        if p.is_file() and not p.name.startswith("."):
            dados = p.read_bytes()
            sha = hashlib.sha1(dados).hexdigest()
            _req(token, "POST", "/v2/files", cab={"x-vercel-digest": sha, "Content-Type": "application/octet-stream",
                                                   "Content-Length": str(len(dados))}, time_id=time_id, bruto=dados)
            arquivos.append({"file": str(p.relative_to(pasta)), "sha": sha, "size": len(dados)})
    dep = _req(token, "POST", "/v13/deployments?skipAutoDetectionConfirmation=1", {
        "name": nome_projeto, "files": arquivos, "target": "production",
        "projectSettings": {"framework": None, "buildCommand": None, "installCommand": None, "outputDirectory": None},
    }, time_id=time_id)
    did = dep["id"]
    fim = time.time() + espera
    while time.time() < fim:
        d = _req(token, "GET", f"/v13/deployments/{did}", time_id=time_id)
        estado = d.get("readyState") or d.get("status")
        if estado == "READY":
            aliases = d.get("alias") or []
            curto = next((a for a in aliases if a == f"{nome_projeto}.vercel.app"), None) or (aliases[0] if aliases else d.get("url"))
            return "https://" + curto
        if estado in ("ERROR", "CANCELED"):
            raise RuntimeError(f"o deploy na Vercel terminou em {estado}")
        time.sleep(4)
    raise RuntimeError("a Vercel não terminou o deploy a tempo")
