FROM python:3.11-slim

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
    

# --- Installer dépendances Python ---
RUN pip install --no-cache-dir requests python-dotenv

# --- Fichier log cron ---
RUN touch /var/log/cron.log

# --- Commande par défaut ---
CMD ["cron", "-f"]
