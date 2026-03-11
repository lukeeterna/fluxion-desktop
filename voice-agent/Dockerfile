# FLUXION Voice Agent — Dockerfile
# Platform: linux/amd64 | Python 3.9-slim
# Porta: 3002 | DB via volume mount /data/fluxion.db
#
# Build:  docker build -t fluxion-voice-agent .
# Run:    docker-compose up -d

FROM python:3.9-slim

# Metadati
LABEL maintainer="FLUXION" \
      version="2.1.0" \
      description="FLUXION Voice Agent — 5-layer RAG pipeline italiana"

# ─── System deps ───────────────────────────────────────────────────
# libgomp: richiesto da onnxruntime
# ca-certificates: HTTPS calls verso Groq API
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ─── Utente non-root (security best practice) ──────────────────────
RUN useradd --create-home --shell /bin/bash fluxion
WORKDIR /app

# ─── Dipendenze Python ─────────────────────────────────────────────
# Copiamo prima solo requirements per cache layer efficiente
COPY requirements-docker.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-docker.txt

# ─── Codice sorgente ───────────────────────────────────────────────
COPY main.py .
COPY src/ ./src/
COPY verticals/ ./verticals/
COPY data/ ./data/

# Directory DB (volume mount esterno in produzione)
RUN mkdir -p /data && chown fluxion:fluxion /data /app

USER fluxion

# ─── Configurazione ────────────────────────────────────────────────
# GROQ_API_KEY: obbligatorio — passare via env o .env file
# FLUXION_DB_PATH: path al SQLite (default /data/fluxion.db)
# HTTP_BRIDGE_URL: URL Tauri HTTP Bridge (default http://host.docker.internal:3001)
ENV FLUXION_DB_PATH=/data/fluxion.db \
    HTTP_BRIDGE_URL=http://host.docker.internal:3001 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 3002

# Healthcheck ogni 30s — fallisce se pipeline non risponde
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3002/health')" || exit 1

# Bind 127.0.0.1 inside Docker è sbagliato — dentro container usa 0.0.0.0
# Il traffico è già isolato dalla rete Docker (vedi docker-compose.yml)
CMD ["python", "main.py", "--port", "3002", "--host", "0.0.0.0"]
