FROM python:3.11-slim

# --- Installer cron et utilitaires ---
RUN apt-get update && \
    apt-get install -y cron curl && \
    rm -rf /var/lib/apt/lists/*

# --- Créer dossier app ---
WORKDIR /app

# --- Copier requirements et installer les dépendances Python ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copier les fichiers de l'application ---
COPY netflix_bot.py /app/
COPY crontab.txt /app/
COPY start.sh /app/

# --- Configuration du cron ---
RUN crontab /app/crontab.txt && \
    chmod 0644 /app/crontab.txt

# --- Créer les dossiers nécessaires ---
RUN mkdir -p /app/data /app/logs && \
    chmod -R 755 /app/data /app/logs

# --- Rendre start.sh exécutable ---
RUN chmod +x /app/start.sh

# --- Healthcheck pour vérifier que le container fonctionne ---
HEALTHCHECK --interval=1h --timeout=10s --start-period=30s --retries=3 \
    CMD test -f /app/data/sent_ids.json || exit 1

# --- Commande par défaut : utiliser start.sh ---
CMD ["/app/start.sh"]
