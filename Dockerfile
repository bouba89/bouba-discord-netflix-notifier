# =========================================
# Builder stage - installer les dépendances Python
# =========================================
FROM python:3.11-slim AS builder
WORKDIR /app

# Installer gcc pour pip (build de certains paquets)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python localement
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# =========================================
# Runtime stage - image finale légère
# =========================================
FROM python:3.11-slim
WORKDIR /app

# Installer cron, curl et bash
RUN apt-get update && apt-get install -y --no-install-recommends cron curl bash && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python depuis le builder
COPY --from=builder /root/.local /root/.local

# Ajouter le PATH pour pip --user
ENV PATH=/root/.local/bin:/usr/local/bin:$PATH

# Copier l'application
COPY netflix_bot.py /app/
COPY crontab.txt /app/

# Créer les dossiers nécessaires
RUN mkdir -p /app/data /app/logs



# Créer le script wrapper avec echo multi-lignes
RUN echo '#!/bin/bash' > /app/run_netflix.sh && \
    echo 'cd /app || exit 1' >> /app/run_netflix.sh && \
    echo '/usr/local/bin/python3 /app/netflix_bot.py' >> /app/run_netflix.sh && \
    echo 'exit $?' >> /app/run_netflix.sh && \
    chmod +x /app/run_netflix.sh

# Créer le script de démarrage avec echo multi-lignes
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'echo "🎬 Starting Netflix Bot..."' >> /app/start.sh && \
    echo 'echo "📅 $(date)"' >> /app/start.sh && \
    echo 'echo "📋 Crontab configurée:"' >> /app/start.sh && \
    echo 'crontab -l' >> /app/start.sh && \
    echo 'echo "⏰ Starting cron in foreground..."' >> /app/start.sh && \
    echo 'cron' >> /app/start.sh && \
    echo 'tail -f /app/logs/netflix_bot.log 2>/dev/null || tail -f /dev/null' >> /app/start.sh && \
    chmod +x /app/start.sh

# Charger la crontab
RUN crontab /app/crontab.txt

# Afficher la crontab pour debug
RUN echo "📋 Crontab chargée:" && crontab -l

# Lancer avec bash explicitement
CMD ["/bin/bash", "/app/start.sh"]