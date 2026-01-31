#!/bin/bash

# Afficher la date
echo "📅 $(date)"

# Exporter les variables d'environnement pour cron
echo "🔑 Exporting environment variables for cron..."
printenv | grep -v "no_proxy" >> /etc/environment

# Afficher les variables d'environnement importantes
echo "✅ Environment variables loaded"
if [ ! -z "$RAPIDAPI_KEY" ]; then
    echo "   RAPIDAPI_KEY: ${RAPIDAPI_KEY:0:10}***"
fi
if [ ! -z "$TMDB_API_KEY" ]; then
    echo "   TMDB_API_KEY: ${TMDB_API_KEY:0:10}***"
fi
if [ ! -z "$COUNTRIES" ]; then
    echo "   COUNTRIES: $COUNTRIES"
fi

# Démarrer cron en arrière-plan
echo "⏰ Starting cron service..."
cron

# Lancer le bot Netflix en arrière-plan
echo "🤖 Starting Netflix bot..."
python3 netflix_bot.py &

# Lancer l'interface web en premier plan (pour garder le conteneur actif)
echo "🌐 Starting web interface..."
python3 web_interface.py
