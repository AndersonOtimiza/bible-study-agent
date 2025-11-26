# syntax=docker/dockerfile:1

# Imagem base (Python 3.12 slim). Ajuste se precisar de 3.13.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Dependências do sistema (faiss pode exigir libgomp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar código
COPY src ./src
COPY scripts ./scripts
COPY data ./data
COPY indexes ./indexes
COPY Documentação ./Documentação

# Porta padrão FastAPI
EXPOSE 8000

# Comando: se índice não existir, o container só sobe API (setup pode ser executado manualmente)
CMD ["python", "src/app.py"]

# Para gerar índice dentro do container (opcional):
# docker run --rm -it --entrypoint bash imagem && python scripts/setup_corpus.py