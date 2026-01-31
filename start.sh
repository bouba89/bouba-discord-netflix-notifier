#!/bin/bash
set -e
echo "=================================================="
echo "🎬 Netflix Bot Container - Démarrage"
echo "=================================================="
echo "📅 $(date)"
echo ""

# Vérifier les variables d'environnement au démarrage
echo "🔍 Vérification des variables d'environnement..."
if [ -z "$RAPIDAPI_KEY" ]; then
    echo "❌ ERREUR: RAPIDAPI_KEY manquante dans .env"
    exit 1
fi
echo "✅ RAPIDAPI_KEY: ${RAPIDAPI_KEY:0:10}***"

if [ -z "$TMDB_API_KEY" ]; then
    echo "❌ ERREUR: TMDB_API_KEY manquante dans .env"
    exit 1
fi
echo "✅ TMDB_API_KEY: ${TMDB_API_KEY:0:10}***"

if [ -z "$DISCORD_WEBHOOK" ]; then
    echo "❌ ERREUR: DISCORD_WEBHOOK manquant dans .env"
    exit 1
fi
echo "✅ DISCORD_WEBHOOK configuré"
echo "✅ COUNTRIES: ${COUNTRIES:-FR}"
echo ""

# Exporter les variables d'environnement pour cron
echo "🔑 Export des variables pour cron..."
printenv | grep -v "no_proxy" >> /etc/environment
echo "✅ Variables exportées"
echo ""

# NOUVEAU : Installer le crontab
echo "📋 Installation du crontab..."
if [ -f /app/crontab.txt ]; then
    crontab /app/crontab.txt
    echo "✅ Crontab installé depuis /app/crontab.txt"
else
    echo "⚠️  Fichier crontab.txt non trouvé"
fi
echo ""

# Afficher la crontab installée
echo "📋 Configuration Crontab active:"
crontab -l
echo ""

# Démarrer cron en arrière-plan
echo "⏰ Démarrage de cron..."
cron
echo "✅ Cron démarré"
echo ""

# Lancer le bot Netflix en arrière-plan
echo "🤖 Démarrage du bot Netflix..."
python3 /app/netflix_bot.py &
BOT_PID=$!
echo "✅ Bot Netflix démarré (PID: $BOT_PID)"
echo ""

echo "=================================================="
echo "✅ Container opérationnel"
echo "🌐 Interface web: http://localhost:5000"
echo "📋 Debug en direct activé"
echo "=================================================="
echo ""

# Démarrer l'interface web Flask (mode développement avec debug)
echo "🌐 Démarrage de l'interface web Flask (debug mode)..."
cd /app
exec python3 web_interface.py
