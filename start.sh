#!/bin/bash

# Afficher un message de démarrage
echo "🎬 Starting Netflix Bot..."
echo "📅 $(date)"

# Exporter les variables d'environnement pour cron
echo "🔑 Exporting environment variables for cron..."
printenv | grep -v "no_proxy" >> /etc/environment

# Vérifier que les variables critiques sont présentes
if [ -z "$RAPIDAPI_KEY" ]; then
    echo "❌ ERROR: RAPIDAPI_KEY not set!"
    exit 1
fi

if [ -z "$DISCORD_WEBHOOK" ]; then
    echo "❌ ERROR: DISCORD_WEBHOOK not set!"
    exit 1
fi

echo "✅ Environment variables loaded"

# Créer les dossiers si nécessaire
mkdir -p /app/data /app/logs

# Démarrer cron
echo "⏰ Starting cron service..."
cron

echo "✅ Cron started successfully"
echo "📊 Watching logs at /app/logs/netflix_bot.log"
echo "----------------------------------------"

# Suivre les logs (créé automatiquement le fichier si nécessaire)
tail -f /app/logs/netflix_bot.log 2>/dev/null || (touch /app/logs/netflix_bot.log && tail -f /app/logs/netflix_bot.log)
