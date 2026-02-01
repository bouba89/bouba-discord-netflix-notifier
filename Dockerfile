# ============================================================================
# Stage 1: Builder - Installation des dépendances
# ============================================================================
FROM python:3.11-slim AS builder

# Variables d'environnement pour optimiser pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système nécessaires pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier et installer les dépendances Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# ============================================================================
# Stage 2: Runtime - Image finale légère
# ============================================================================
FROM python:3.11-alpine

# Métadonnées
LABEL maintainer="bouba89"
LABEL description="Netflix Discord Notifier Bot with Web Interface"
LABEL version="1.0.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Installer les dépendances runtime nécessaires
RUN apk add --no-cache \
    bash \
    curl \
    nano \
    tzdata \
    dcron \
    && rm -rf /var/cache/apk/*

ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone



# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Créer l'utilisateur non-root pour la sécurité
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Créer les dossiers nécessaires
RUN mkdir -p /app/data /app/logs /app/templates && \
    chown -R appuser:appuser /app

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY --chown=appuser:appuser netflix_bot.py /app/
COPY --chown=appuser:appuser web_interface.py /app/
COPY --chown=appuser:appuser run_netflix.sh /app/
COPY --chown=appuser:appuser start.sh /app/
COPY --chown=appuser:appuser crontab.txt /app/
COPY --chown=appuser:appuser templates/ /app/templates/

# Rendre les scripts exécutables
RUN chmod +x /app/start.sh /app/run_netflix.sh

# Créer le fichier .env_for_cron vide (sera rempli au runtime)
RUN touch /app/.env_for_cron && chown appuser:appuser /app/.env_for_cron

# Exposer le port Flask
EXPOSE 5000

# Volumes pour la persistance des données
VOLUME ["/app/data", "/app/logs"]

# Nouveau healthcheck (utilise /health qui est public)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

USER root


# Commande de démarrage
CMD ["bash", "/app/start.sh"]
