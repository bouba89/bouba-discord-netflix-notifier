# ============================================================================
# Stage 1: Builder - Installation des dépendances
# ============================================================================
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc=4:14.2.0-1 \
        g++=4:14.2.0-1 && \
    rm -rf /var/lib/apt/lists/* && \
    python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip==25.3 wheel==0.46.2 && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# ============================================================================
# Stage 2: Runtime - Image finale légère
# ============================================================================
FROM python:3.11-alpine

LABEL maintainer="bouba89" \
      description="Netflix Discord Notifier Bot with Web Interface" \
      version="1.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=Europe/Paris

# hadolint ignore=DL3018
RUN apk add --no-cache \
        bash \
        curl \
        nano \
        tzdata \
        dcron && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    mkdir -p /app/data /app/logs /app/templates && \
    chown -R appuser:appuser /app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

# Supprimer pip/wheel du système Alpine (on utilise le venv)
RUN pip uninstall -y pip wheel setuptools || true && \
    rm -rf /usr/local/lib/python3.11/site-packages/pip* \
           /usr/local/lib/python3.11/site-packages/wheel* \
           /usr/local/lib/python3.11/site-packages/setuptools*

COPY --chown=appuser:appuser netflix_bot.py \
                              web_interface.py \
                              run_netflix.sh \
                              start.sh \
                              crontab.txt \
                              /app/

COPY --chown=appuser:appuser templates/ /app/templates/

RUN chmod +x /app/start.sh /app/run_netflix.sh && \
    touch /app/.env_for_cron && \
    chown appuser:appuser /app/.env_for_cron

EXPOSE 5000

VOLUME ["/app/data", "/app/logs"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

USER root

CMD ["bash", "/app/start.sh"]
