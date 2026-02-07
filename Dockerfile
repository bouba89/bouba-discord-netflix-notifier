FROM python:3.11-slim

# Métadonnées
LABEL maintainer="bouba89"
LABEL description="Bot Discord Netflix Notifier - Version 3.0 (API mdblist complète)"
LABEL version="3.0.0"

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Configuration du timezone
ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

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

# Point d'entrée
CMD ["/app/start.sh"]
