#!/usr/bin/env python3
"""
TRAVA DE ANONIMATO da lp-matriz — nenhum nome de cliente, nenhum identificador real entra neste repositório.

Por que existe: a matriz nasceu do processo real de uma agência, e a regra da dona dela é que o material possa ser enviado a
qualquer lugar sem expor clientes. Regra escrita não basta (já falhou antes); por isso a trava roda no pre-commit e no CI.

Duas checagens:
  1. NOMES — cada sequência de 1 a 6 palavras do texto (sem acento, minúscula) vira sha256 com sal e é comparada com
     a lista de bloqueio. A lista e o sal são SEGREDOS (15-10-2026, repositório público): moram nos segredos do GitHub
     (LP_MATRIZ_SAL, LP_MATRIZ_BLOQUEIO) e em ~/.config/lp-matriz/ de quem tem a carteira, nunca aqui.
  2. IDENTIFICADORES — padrões que denunciam conta real: GTM-/AW-/G- com ID, act_ do Meta, conta Google 000-000-0000,
     telefone, CNPJ, CRM/CRO/OAB com número, e-mail, domínio .com.br/.com, IP, ref de projeto Supabase.
     Placeholders aceitos: exemplo.com.br, (00) 00000-0000, 00.000.000/0000-00, GTM-XXXXXXX etc. (veja PERMITIDOS).

Uso:  python3 ferramentas/anonimato.py            # varre os arquivos do git (ou a pasta, se não for git)
      python3 ferramentas/anonimato.py arquivo…   # só esses
Saída 1 = achou algo (o commit/CI para). Mostra arquivo:linha e o TIPO do achado — nunca repete o nome bloqueado.
"""
import hashlib, pathlib, re, subprocess, sys, unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
import os
# 15-10-2026 — repositório PÚBLICO: o sal e a lista de bloqueio são SEGREDOS e nunca entram aqui. Com sal conhecido, qualquer
# um testaria um nome de médico contra a lista e descobriria quem é cliente. Ordem de leitura: variáveis de ambiente
# (CI: segredos LP_MATRIZ_SAL e LP_MATRIZ_BLOQUEIO) → ~/.config/lp-matriz/{sal,bloqueio.sha} (máquina de quem tem a carteira).
# Sem o segredo, a checagem de NOMES não roda e a trava RECUSA (fail-closed), salvo `--sem-nomes` (colaborador externo:
# só a checagem de identificadores; a de nomes roda no CI do repositório antes de qualquer merge).
_CFG = pathlib.Path.home() / ".config/lp-matriz"
def _segredo(env, arquivo):
    v = os.environ.get(env)
    if v: return v
    f = _CFG / arquivo
    return f.read_text() if f.exists() else None
_sal, _lista = _segredo("LP_MATRIZ_SAL", "sal"), _segredo("LP_MATRIZ_BLOQUEIO", "bloqueio.sha")
SEM_NOMES = "--sem-nomes" in sys.argv
if not (_sal and _lista) and not SEM_NOMES:
    print("⛔ trava: segredo da lista de bloqueio ausente (LP_MATRIZ_SAL / LP_MATRIZ_BLOQUEIO ou ~/.config/lp-matriz/). "
          "Recusado. Colaborador externo: rode com --sem-nomes (o CI confere os nomes).", file=sys.stderr)
    sys.exit(1)
SAL = (_sal or "").strip()
BLOQUEIO = {l.strip() for l in (_lista or "").splitlines() if l.strip() and not l.startswith("#")}
EXT_TEXTO = {".md", ".py", ".mjs", ".js", ".ts", ".json", ".html", ".css", ".txt", ".yml", ".yaml", ".sh", ".swift", ".toml", ".svg", ".sql", ".exemplo", ".env", ""}
IGNORAR = set()

PADROES = [
    ("id de GTM", r"\bGTM-[A-Z0-9]{6,9}\b"),
    ("id do Google Ads (AW-)", r"\bAW-\d{6,}\b"),
    ("id do GA4", r"\bG-[A-Z0-9]{8,12}\b"),
    ("conta do Meta (act_)", r"\bact_\d{6,}\b"),
    ("conta do Google Ads", r"\b\d{3}-\d{3}-\d{4}\b"),
    ("telefone", r"(?:\+?55\s?)?\(?\b\d{2}\)?\s?9\d{4}[-\s]?\d{4}\b"),
    ("telefone corrido (55 + DDD)", r"(?<!\d)55(?!00)\d{2}9?\d{8}(?!\d)"),
    ("CNPJ", r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"),
    ("registro profissional com número", r"\b(?:CRM|CRO|CREFITO|OAB|RQE)\s*[-/:]?\s*[A-Z]{0,2}\s*[-/:]?\s*\d{3,}"),
    ("e-mail", r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
    ("domínio", r"\b[\w-]+(?:\.[\w-]+)*\.(?:com\.br|com|net\.br|adv\.br|med\.br|odo\.br|app|co)\b"),
    ("IP", r"(?<![\d.\-])\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b(?![\d.])"),
    ("ref de projeto Supabase", r"\b[a-z]{20}\.supabase\.co\b"),
]
# Placeholders e domínios de ferramentas públicas que a documentação precisa citar.
PERMITIDOS = re.compile(r"""(?ix)
    \bGTM-X+\b | \bAW-0+\b | \bG-X+\b | act_0+ | 000-000-0000 | \(?00\)?\s?9?0000-?0000 | 00\.000\.000/0000-00 | 0\.0\.0\.0 | 127\.0\.0\.1
  | (?:CRM|CRO|CREFITO|OAB|RQE)[^\n]{0,8}0{3,}
  | [\w.+-]*@exemplo\.com\.br | (?:[\w-]+\.)*exemplo\.com\.br | (?:[\w-]+\.)*example\.com
  | (?:[\w-]+\.)*(?:google|googleapis|googletagmanager|google-analytics|googleadservices|gstatic|youtube|facebook|instagram|meta|wa\.me|whatsapp|vercel|vercel\.app|github|githubusercontent|openrouter|openai|anthropic|claude|schema|w3|mozilla|web\.dev|pagespeed|cloudflare|jsdelivr|unpkg|fonts|lucide|stape|docker|traefik|letsencrypt|obsidian|supabase|cfm|cfo|oab|coffito|planalto|gov|org|wikipedia|npmjs|python|pypi|apple|microsoft|bing|duckduckgo|maxmind|ipinfo|nodejs|deno)\.(?:com\.br|com|org|app|co|net\.br|org\.br|gov\.br)
  | \bwa\.me\b | \bmeu-dominio\.com\.br\b | \bdominio-do-cliente\.com\.br\b
""")

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s)

def h(s: str) -> str:
    return hashlib.sha256((SAL + "|" + s).encode()).hexdigest()[:20]

def arquivos(args):
    if args:
        return [pathlib.Path(a) for a in args]
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=RAIZ, capture_output=True, text=True, check=True).stdout
        return [RAIZ / l for l in out.splitlines() if l]
    except Exception:
        return [p for p in RAIZ.rglob("*") if p.is_file() and ".git" not in p.parts]

def checar(p: pathlib.Path):
    rel = str(p.resolve().relative_to(RAIZ)) if p.resolve().is_relative_to(RAIZ) else str(p)
    if rel in IGNORAR or p.suffix.lower() not in EXT_TEXTO or not p.exists():
        return []
    try:
        texto = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    achados = []
    for n, linha in enumerate(texto.splitlines(), 1):
        pal = norm(linha).split()
        for i in range(len(pal)):
            for k in range(1, 7):
                if i + k <= len(pal) and h(" ".join(pal[i:i + k])) in BLOQUEIO:
                    achados.append((rel, n, f"nome da lista de bloqueio ({k} palavra{'s' if k > 1 else ''}, posição {i + 1})"))
        limpa = PERMITIDOS.sub(" ", re.sub(r'\bd="[^"]*"', " ", linha))  # traço de SVG (d="…") não é IP
        for tipo, rx in PADROES:
            if re.search(rx, limpa):
                achados.append((rel, n, tipo))
    return achados

def main():
    todos = [a for p in arquivos([x for x in sys.argv[1:] if not x.startswith("--")]) for a in checar(p)]
    for rel, n, tipo in todos:
        print(f"✗ {rel}:{n} — {tipo}")
    if todos:
        print(f"\n{len(todos)} achado(s). Troque por placeholder (Dra. Fulana, exemplo.com.br, (00) 00000-0000, GTM-XXXXXXX).")
        sys.exit(1)
    print("✓ anonimato: nenhum nome de cliente nem identificador real.")

if __name__ == "__main__":
    main()
