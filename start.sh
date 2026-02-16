#!/bin/bash
set -e

echo "=================================================="
echo "🎬 Netflix Bot v3.0 - Démarrage"
echo "=================================================="
echo "📅 $(date)"
echo ""

# Vérifier les variables d'environnement
echo "🔍 Vérification des variables d'environnement..."

# Variables obligatoires
ERRORS=0

if [ -z "$DISCORD_WEBHOOK" ]; then
    echo "❌ ERREUR: DISCORD_WEBHOOK manquant"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ DISCORD_WEBHOOK: configuré"
fi

# Variables recommandées v3
if [ -z "$MDBLIST_API_KEY" ]; then
    echo "⚠️  MDBLIST_API_KEY: non configurée (optionnel)"
    echo "   ℹ️  Le bot fonctionnera mais examinera plus d'items"
else
    echo "✅ MDBLIST_API_KEY: ${MDBLIST_API_KEY:0:10}***"
fi

if [ -z "$TMDB_API_KEY" ]; then
    echo "ℹ️  TMDB_API_KEY: non configurée (optionnel)"
else
    echo "✅ TMDB_API_KEY: ${TMDB_API_KEY:0:10}***"
fi

# DAYS_BACK
DAYS_BACK=${DAYS_BACK:-1}
echo "✅ DAYS_BACK: ${DAYS_BACK} jour(s)"

echo ""

# Arrêter si erreurs critiques
if [ $ERRORS -gt 0 ]; then
    echo "❌ $ERRORS erreur(s) critique(s) détectée(s)"
    echo "❌ Impossible de démarrer le bot"
    exit 1
fi

echo "✅ Configuration validée"
echo ""

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p /app/data /app/logs
echo "✅ Répertoires créés"
echo ""

# Créer le fichier .env pour cron
echo "📝 Génération de la configuration pour cron..."
cat > /app/.env_for_cron << EOF
DISCORD_WEBHOOK=${DISCORD_WEBHOOK}
MDBLIST_API_KEY=${MDBLIST_API_KEY:-}
TMDB_API_KEY=${TMDB_API_KEY:-}
DAYS_BACK=${DAYS_BACK}
FLASK_SECRET_KEY=${FLASK_SECRET_KEY:-netflix-bot-v3-secret}
EOF
echo "✅ Configuration cron créée"
echo ""

# Créer le crontab par défaut s'il n'existe pas
echo "⏰ Configuration du crontab..."
if ! crontab -l 2>/dev/null | grep -q "netflix_bot.py"; then
    echo "0 8 * * * cd /app && export \$(cat /app/.env_for_cron | xargs) && /usr/local/bin/python3 netflix_bot.py >> /app/logs/cron.log 2>&1" | crontab -
    echo "✅ Crontab créé (exécution quotidienne à 8h00)"
else
    echo "✅ Crontab existant conservé"
    crontab -l | grep "netflix_bot.py"
fi
echo ""

# Démarrer le service cron
echo "⏰ Démarrage du service cron..."

# Alpine utilise crond, Debian utilise cron
if command -v crond &> /dev/null; then
    # Alpine
    crond -b -l 2
    echo "✅ Service crond (Alpine) démarré"
elif command -v cron &> /dev/null; then
    # Debian
    service cron start
    echo "✅ Service cron (Debian) démarré"
else
    echo "⚠️  Aucun service cron trouvé"
fi

# Vérifier que cron a démarré
sleep 2
if pgrep -x crond > /dev/null 2>&1 || pgrep -x cron > /dev/null 2>&1; then
    echo "✅ Cron actif et opérationnel"
else
    echo "⚠️  Cron non disponible (tâches planifiées désactivées)"
fi

# Afficher le crontab actif
echo ""
echo "📅 Planification active:"
crontab -l 2>/dev/null || echo "⚠️  Aucune tâche planifiée"
echo ""

# Afficher les informations finales
echo "=================================================="
echo "✨ Configuration complète"
echo "=================================================="
echo "🌐 Interface web: http://localhost:5000"
echo "👤 Login par défaut: admin / admin123"
echo "📡 API Source: mdblist.com"
echo "⏰ Planification: Quotidien à 9h00"
echo "=================================================="
echo ""

# Démarrer Flask
if [ -f /app/web_interface.py ]; then
    echo "🌐 Démarrage de l'interface web Flask..."
    cd /app
    exec python3 web_interface.py
else
    echo "⚠️  Interface web non trouvée"
    echo "🔄 Container en mode monitoring..."
    tail -f /dev/null
fi
