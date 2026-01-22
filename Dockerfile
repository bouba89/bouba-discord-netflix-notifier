# ============================================
# STAGE 1: Builder - Installation des dépendances
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Installer les outils de build nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer dans un dossier utilisateur
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# STAGE 2: Runtime - Image finale légère
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Installer seulement cron (pas gcc ni build-tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python depuis le builder
# Au lieu de réinstaller avec pip
COPY --from=builder /root/.local /root/.local

# Mettre à jour le PATH pour utiliser les packages Python
ENV PATH=/root/.local/bin:$PATH

# Copier les fichiers de l'application
COPY netflix_bot.py /app/
COPY crontab.txt /app/
COPY start.sh /app/

# Configuration du cron
RUN crontab /app/crontab.txt && \
    chmod 0644 /app/crontab.txt

# Créer les dossiers nécessaires
RUN mkdir -p /app/data /app/logs && \
    chmod -R 755 /app/data /app/logs

# Rendre start.sh exécutable
RUN chmod +x /app/start.sh

# Healthcheck
HEALTHCHECK --interval=1h --timeout=10s --start-period=30s --retries=3 \
    CMD test -f /app/data/sent_ids.json || exit 1

# Commande par défaut
CMD ["/app/start.sh"]
