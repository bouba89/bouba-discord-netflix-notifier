# Dans start.sh
printenv | grep -v "no_proxy" >> /etc/environment

# --- Installer cron et utilitaires ---
RUN apt-get update && apt-get install -y cron curl && rm -rf /var/lib/apt/lists/*

# --- Créer dossier app ---
WORKDIR /app

# --- Copier le script et crontab ---
COPY netflix_bot.py /app/
COPY crontab.txt /etc/cron.d/netflix-cron
COPY .env /app/

# --- Permissions crontab ---
RUN chmod 0644 /etc/cron.d/netflix-cron
RUN crontab /etc/cron.d/netflix-cron

# Configurer cron
RUN crontab crontab.txt && \
    chmod 0644 crontab.txt
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Fichier log cron ---
RUN touch /var/log/cron.log

# Copier le script de démarrage
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Utiliser start.sh comme point d'entrée
CMD ["/app/start.sh"]


# Healthcheck pour vérifier que le container fonctionne
HEALTHCHECK --interval=1h --timeout=10s --start-period=30s --retries=3 \
    CMD test -f /app/data/sent_ids.json || exit 1


