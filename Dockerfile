# =========================================
# Builder stage - installer les dépendances Python
# =========================================
FROM python:3.11-slim AS builder
WORKDIR /app

# Installer gcc pour pip (build de certains paquets)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*


ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m pip install --upgrade pip



# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt



# =========================================
# Runtime stage - image finale légère
# =========================================
FROM python:3.11-slim
WORKDIR /app

# Installer cron, curl, bash et procps (pour ps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    curl \
    bash \
    procps \
    && rm -rf /var/lib/apt/lists/*


# Copier l'application
COPY netflix_bot.py /app/
COPY web_interface.py /app/
COPY crontab.txt /app/
COPY templates /app/templates/

# Créer les dossiers nécessaires
RUN mkdir -p /app/data /app/logs

# =========================================
# CORRECTION: Script wrapper qui charge les ENV
# =========================================
RUN echo '#!/bin/bash' > /app/run_netflix.sh && \
    echo 'set -e' >> /app/run_netflix.sh && \
    echo '' >> /app/run_netflix.sh && \
    echo '# Afficher les infos de debug' >> /app/run_netflix.sh && \
    echo 'echo "=================================================="' >> /app/run_netflix.sh && \
    echo 'echo "🎬 Netflix Bot - Exécution Cron"' >> /app/run_netflix.sh && \
    echo 'echo "📅 $(date)"' >> /app/run_netflix.sh && \
    echo 'echo "=================================================="' >> /app/run_netflix.sh && \
    echo '' >> /app/run_netflix.sh && \
    echo '# Vérifier les variables d'\''environnement' >> /app/run_netflix.sh && \
    echo 'if [ -z "$RAPIDAPI_KEY" ]; then' >> /app/run_netflix.sh && \
    echo '    echo "❌ ERREUR: RAPIDAPI_KEY non définie!"' >> /app/run_netflix.sh && \
    echo '    exit 1' >> /app/run_netflix.sh && \
    echo 'fi' >> /app/run_netflix.sh && \
    echo '' >> /app/run_netflix.sh && \
    echo 'if [ -z "$TMDB_API_KEY" ]; then' >> /app/run_netflix.sh && \
    echo '    echo "❌ ERREUR: TMDB_API_KEY non définie!"' >> /app/run_netflix.sh && \
    echo '    exit 1' >> /app/run_netflix.sh && \
    echo 'fi' >> /app/run_netflix.sh && \
    echo '' >> /app/run_netflix.sh && \
    echo 'if [ -z "$DISCORD_WEBHOOK" ]; then' >> /app/run_netflix.sh && \
    echo '    echo "❌ ERREUR: DISCORD_WEBHOOK non défini!"' >> /app/run_netflix.sh && \
    echo '    exit 1' >> /app/run_netflix.sh && \
    echo 'fi' >> /app/run_netflix.sh && \
    echo '' >> /app/run_netflix.sh && \
    echo 'echo "✅ Variables d'\''environnement chargées"' >> /app/run_netflix.sh && \
    echo 'echo "   RAPIDAPI_KEY: ${RAPIDAPI_KEY:0:10}***"' >> /app/run_netflix.sh && \
    echo 'echo "   TMDB_API_KEY: ${TMDB_API_KEY:0:10}***"' >> /app/run_netflix.sh && \
    echo 'echo "   COUNTRIES: $COUNTRIES"' >> /app/run_netflix.sh && \
    echo '' >> /app/run_netflix.sh && \
    echo '# Exécuter le bot' >> /app/run_netflix.sh && \
    echo 'cd /app' >> /app/run_netflix.sh && \
    echo '/usr/local/bin/python3 /app/netflix_bot.py' >> /app/run_netflix.sh && \
    echo '' >> /app/run_netflix.sh && \
    echo 'echo "=================================================="' >> /app/run_netflix.sh && \
    echo 'echo "🏁 Exécution terminée"' >> /app/run_netflix.sh && \
    echo 'echo "=================================================="' >> /app/run_netflix.sh && \
    chmod +x /app/run_netflix.sh

# =========================================
# Script de démarrage principal avec Flask
# =========================================
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'echo "=================================================="' >> /app/start.sh && \
    echo 'echo "🎬 Netflix Bot Container - Démarrage"' >> /app/start.sh && \
    echo 'echo "=================================================="' >> /app/start.sh && \
    echo 'echo "📅 $(date)"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Vérifier les variables d'\''environnement au démarrage' >> /app/start.sh && \
    echo 'echo "🔍 Vérification des variables d'\''environnement..."' >> /app/start.sh && \
    echo 'if [ -z "$RAPIDAPI_KEY" ]; then' >> /app/start.sh && \
    echo '    echo "❌ ERREUR: RAPIDAPI_KEY manquante dans .env"' >> /app/start.sh && \
    echo '    exit 1' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo 'echo "✅ RAPIDAPI_KEY: ${RAPIDAPI_KEY:0:10}***"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'if [ -z "$TMDB_API_KEY" ]; then' >> /app/start.sh && \
    echo '    echo "❌ ERREUR: TMDB_API_KEY manquante dans .env"' >> /app/start.sh && \
    echo '    exit 1' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo 'echo "✅ TMDB_API_KEY: ${TMDB_API_KEY:0:10}***"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'if [ -z "$DISCORD_WEBHOOK" ]; then' >> /app/start.sh && \
    echo '    echo "❌ ERREUR: DISCORD_WEBHOOK manquant dans .env"' >> /app/start.sh && \
    echo '    exit 1' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo 'echo "✅ DISCORD_WEBHOOK configuré"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'echo "✅ COUNTRIES: ${COUNTRIES:-FR}"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Créer un fichier pour passer les ENV à cron' >> /app/start.sh && \
    echo 'echo "📝 Création du fichier d'\''environnement pour cron..."' >> /app/start.sh && \
    echo 'printenv | grep -E "RAPIDAPI_KEY|TMDB_API_KEY|DISCORD_WEBHOOK|COUNTRIES" > /app/.env_for_cron' >> /app/start.sh && \
    echo 'chmod 600 /app/.env_for_cron' >> /app/start.sh && \
    echo 'echo "✅ Fichier .env_for_cron créé"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Afficher la crontab' >> /app/start.sh && \
    echo 'echo "📋 Configuration Crontab:"' >> /app/start.sh && \
    echo 'crontab -l' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Démarrer cron en arrière-plan' >> /app/start.sh && \
    echo 'echo "⏰ Démarrage de cron..."' >> /app/start.sh && \
    echo 'cron' >> /app/start.sh && \
    echo 'echo "✅ Cron démarré"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Démarrer Flask en arrière-plan' >> /app/start.sh && \
    echo 'echo "🌐 Démarrage de l'\''interface web sur le port 5000..."' >> /app/start.sh && \
    echo 'cd /app && python3 /app/web_interface.py &' >> /app/start.sh && \
    echo 'FLASK_PID=$!' >> /app/start.sh && \
    echo 'echo "✅ Interface web démarrée (PID: $FLASK_PID)"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Tester immédiatement' >> /app/start.sh && \
    echo 'echo "🧪 Test immédiat du bot..."' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo '/app/run_netflix.sh' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo 'echo "=================================================="' >> /app/start.sh && \
    echo 'echo "✅ Container opérationnel"' >> /app/start.sh && \
    echo 'echo "⏰ Prochaine exécution: 8h00 UTC chaque jour"' >> /app/start.sh && \
    echo 'echo "🌐 Interface web: http://localhost:5000"' >> /app/start.sh && \
    echo 'echo "📋 Logs disponibles dans /app/logs/"' >> /app/start.sh && \
    echo 'echo "=================================================="' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Suivre les logs Flask' >> /app/start.sh && \
    echo 'tail -f /app/logs/netflix_bot.log /app/logs/netflix_bot_debug.log 2>/dev/null || tail -f /dev/null' >> /app/start.sh && \
    chmod +x /app/start.sh

# Charger la crontab
RUN crontab /app/crontab.txt

# Afficher la crontab pour debug
RUN echo "📋 Crontab chargée:" && crontab -l

# Exposer le port Flask
EXPOSE 5000

# Lancer avec bash explicitement
CMD ["/bin/bash", "/app/start.sh"]
