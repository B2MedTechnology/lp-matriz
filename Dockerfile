# Fábrica de landing pages: pega pedidos da fila (lp_pedidos), gera a página e publica a prévia (noindex) na Vercel.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=0 FABRICA_TRABALHO=/tmp/fabrica
RUN pip install --no-cache-dir pillow==11.3.0 cryptography==44.0.2
WORKDIR /app
COPY fabrica ./fabrica
COPY motor ./motor
COPY ia ./ia
COPY doutrina ./doutrina
COPY exemplos/clinica-exemplo/cliente.json ./exemplos/clinica-exemplo/cliente.json
COPY exemplos/_assets ./exemplos/clinica-exemplo/site/assets
USER nobody
CMD ["python3", "-m", "fabrica.servico"]
