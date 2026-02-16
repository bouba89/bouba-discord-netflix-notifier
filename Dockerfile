FROM python:3.11-alpine

# Métadonnées
LABEL maintainer="bouba89"
LABEL description="Bot Discord Netflix Notifier - Version 3.0 (API mdblist complète)"
LABEL version="3.0.0"

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Europe/Paris

# Installation des dépendances système (Alpine)
RUN apk add --no-cache \
    dcron \
    tzdata \
    curl \
    bash \
    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apk del tzdata

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie des fichiers de l'application
COPY netflix_bot_v3.py netflix_bot.py
COPY web_interface.py .
COPY templates/ templates/
COPY crontab.txt .
COPY start.sh .

# Rendre le script start.sh exécutable
RUN chmod +x /app/start.sh

# Création des répertoires nécessaires
RUN mkdir -p /app/data /app/logs

# Configuration de cron
RUN crontab crontab.txt

# Exposition des volumes
VOLUME ["/app/data", "/app/logs"]

# Exposition du port Flask
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Point d'entrée
CMD ["/app/start.sh"]
