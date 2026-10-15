"""Fotos e logo do cliente a partir da pasta do Google Drive compartilhada como "qualquer pessoa com o link".
Sem chave nenhuma: a lista vem da visão embutida pública da pasta e cada arquivo do link de download público.
Para teste local, aceita um caminho de pasta do disco (ou file://)."""
import html, pathlib, re, shutil, urllib.request

EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".svg")
UA = {"User-Agent": "Mozilla/5.0 (lp-matriz)"}

def id_da_pasta(url):
    m = re.search(r"/folders/([A-Za-z0-9_-]{10,})", url) or re.search(r"[?&]id=([A-Za-z0-9_-]{10,})", url)
    return m.group(1) if m else None

def _get(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")

def listar(pasta_id, prof=0):
    """[(file_id, nome)] da pasta pública (e de subpastas, até 2 níveis)."""
    corpo, _ = _get(f"https://drive.google.com/embeddedfolderview?id={pasta_id}#list")
    t = corpo.decode("utf-8", "replace")
    itens = []
    for m in re.finditer(r'<a href="(https://drive\.google\.com/[^"]+)"[^>]*>.*?<div class="flip-entry-title">(.*?)</div>', t, re.S):
        href, nome = html.unescape(m.group(1)), html.unescape(m.group(2)).strip()
        f = re.search(r"/file/d/([A-Za-z0-9_-]+)", href)
        s = re.search(r"/folders/([A-Za-z0-9_-]+)", href)
        if f and nome.lower().endswith(EXT):
            itens.append((f.group(1), nome))
        elif s and prof < 2:
            itens += [(i, f"{nome}/{n}") for i, n in listar(s.group(1), prof + 1)]
    return itens

def baixar(url_ou_pasta, destino: pathlib.Path, limite=60):
    """Baixa as imagens para `destino`. Devolve a lista de arquivos. Levanta erro legível se a pasta não abrir."""
    destino.mkdir(parents=True, exist_ok=True)
    local = url_ou_pasta.replace("file://", "")
    if pathlib.Path(local).is_dir():
        out = []
        for p in sorted(pathlib.Path(local).rglob("*")):
            if p.suffix.lower() in EXT and len(out) < limite:
                alvo = destino / p.name
                shutil.copy(p, alvo)
                out.append(alvo)
        return out
    pid = id_da_pasta(url_ou_pasta)
    if not pid:
        raise ValueError("o link do Drive não é de uma pasta (precisa ter /folders/…)")
    itens = listar(pid)
    if not itens:
        raise ValueError("a pasta do Drive não abriu ou está vazia — compartilhe como “qualquer pessoa com o link pode ver”")
    # Muitas fotos (ensaio inteiro): o logo sempre, e o resto espalhado pelas subpastas até o limite.
    logos = [x for x in itens if "logo" in x[1].lower()]
    resto = [x for x in itens if x not in logos]
    passo = max(1, len(resto) / max(1, limite - len(logos)))
    escolhidos = logos + [resto[int(i * passo)] for i in range(min(len(resto), limite - len(logos)))]
    from concurrent.futures import ThreadPoolExecutor
    def um(par):
        fid, nome = par
        # foto: a miniatura pública de 2400 px (um ensaio tem arquivos de 8 MB; a página não usa mais que 2400)
        url = (f"https://drive.google.com/uc?export=download&id={fid}" if nome.lower().endswith((".svg", ".png"))
               else f"https://drive.google.com/thumbnail?id={fid}&sz=w2400")
        try:
            dados, tipo = _get(url, timeout=120)
        except OSError:
            return None
        if b"<html" in dados[:500].lower():
            return None  # arquivo grande pede confirmação: pulamos (foto de página não passa de alguns MB)
        ext = ".jpg" if "thumbnail" in url else pathlib.Path(nome).suffix.lower()
        seguro = re.sub(r"[^A-Za-z0-9._-]+", "-", pathlib.Path(nome.split("/")[-1]).stem).strip("-") or fid
        return seguro + ext, dados
    out = []
    with ThreadPoolExecutor(6) as ex:
        for r in ex.map(um, escolhidos):
            if not r:
                continue
            nome, dados = r
            alvo = destino / nome
            n = 2
            while alvo.exists():
                alvo = destino / f"{pathlib.Path(nome).stem}-{n}{pathlib.Path(nome).suffix}"; n += 1
            alvo.write_bytes(dados)
            out.append(alvo)
    return out
