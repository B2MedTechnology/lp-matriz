"""Banco da fila (Supabase/PostgREST com a service_role) e, opcional, um cofre de segredos cifrado no próprio banco
(tabela orq_secrets, AES-256-GCM com ORQ_VAULT_KEY). Sem cofre, os segredos vêm do ambiente (ver .env.exemplo).
Os segredos chegam por arquivo (Docker Swarm secrets em /run/secrets) ou pelo ambiente; nunca são impressos."""
import base64, json, os, pathlib, urllib.request, urllib.error

def _segredo(nome):
    p = pathlib.Path("/run/secrets") / nome
    if p.exists():
        return p.read_text().strip()
    return (os.environ.get(nome) or "").strip()

URL = _segredo("SUPABASE_URL").rstrip("/")
SERVICE = _segredo("SUPABASE_SERVICE_ROLE")
VAULT_KEY = _segredo("ORQ_VAULT_KEY")
TENANT = os.environ.get("TENANT", "padrao")

def _req(metodo, caminho, corpo=None, cab=None):
    if not URL or not SERVICE:
        raise RuntimeError("banco não configurado (SUPABASE_URL / SUPABASE_SERVICE_ROLE)")
    h = {"apikey": SERVICE, "Authorization": f"Bearer {SERVICE}", "Content-Type": "application/json"}
    h.update(cab or {})
    dados = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(URL + caminho, data=dados, method=metodo, headers=h)
    with urllib.request.urlopen(r, timeout=60) as x:
        t = x.read()
        return json.loads(t) if t else None

def rpc(nome, args=None):
    return _req("POST", f"/rest/v1/rpc/{nome}", args or {})

def atualizar_pedido(pid, **campos):
    import datetime
    campos["atualizado_em"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return _req("PATCH", f"/rest/v1/lp_pedidos?id=eq.{int(pid)}", campos, {"Prefer": "return=minimal"})

def ler_pedido(pid):
    r = _req("GET", f"/rest/v1/lp_pedidos?id=eq.{int(pid)}&select=*")
    return r[0] if r else None

def ler_config():
    return rpc("lp_config_ver")

def segredo_do_cofre(nome):
    """Lê e decifra um segredo do Cofre do worker (mesma cifra de packages/vault/src/crypto.ts)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if os.environ.get(nome) or pathlib.Path("/run/secrets", nome).exists():
        return _segredo(nome)            # sem cofre: o segredo veio do ambiente ou do Swarm
    if not VAULT_KEY or not URL:
        return None                      # sem cofre: quem chama decide se a falta é erro (servico.py diz qual)
    r = _req("GET", f"/rest/v1/orq_secrets?tenant=eq.{TENANT}&nome=eq.{nome}&select=valor_enc")
    if not r:
        return None
    raw = base64.b64decode(r[0]["valor_enc"])
    iv, tag, ct = raw[:12], raw[12:28], raw[28:]
    return AESGCM(bytes.fromhex(VAULT_KEY)).decrypt(iv, ct + tag, None).decode("utf-8")
