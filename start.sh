#!/bin/bash
set -e
echo "=================================================="
echo "🎬 Streaming Bot v4.0 - Netflix + Disney+"        # ← v4
echo "=================================================="
echo "📅 $(date)"
echo ""
# Vérifier les variables d'environnement
echo "🔍 Vérification des variables d'environnement..."
ERRORS=0
if [ -z "$DISCORD_WEBHOOK" ]; then
    echo "❌ ERREUR: DISCORD_WEBHOOK manquant"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ DISCORD_WEBHOOK: configuré"
fi
if [ -z "$MDBLIST_API_KEY" ]; then
    echo "⚠️  MDBLIST_API_KEY: non configurée (optionnel)"
else
    echo "✅ MDBLIST_API_KEY: ${MDBLIST_API_KEY:0:10}***"
fi
if [ -z "$TMDB_API_KEY" ]; then
    echo "ℹ️  TMDB_API_KEY: non configurée (optionnel)"
else
    echo "✅ TMDB_API_KEY: ${TMDB_API_KEY:0:10}***"
fi
DAYS_BACK=${DAYS_BACK:-1}
echo "✅ DAYS_BACK: ${DAYS_BACK} jour(s)"
echo ""
if [ $ERRORS -gt 0 ]; then
    echo "❌ $ERRORS erreur(s) critique(s) détectée(s)"
    echo "❌ Impossible de démarrer le bot"
    exit 1
fi
echo "✅ Configuration validée"
echo ""
echo "📁 Création des répertoires..."
mkdir -p /app/data /app/logs
echo "✅ Répertoires créés"
echo ""
echo "📝 Génération de la configuration pour cron..."
cat > /app/.env_for_cron << EOF
DISCORD_WEBHOOK=${DISCORD_WEBHOOK}
MDBLIST_API_KEY=${MDBLIST_API_KEY:-}
TMDB_API_KEY=${TMDB_API_KEY:-}
DAYS_BACK=${DAYS_BACK}
FLASK_SECRET_KEY=${FLASK_SECRET_KEY:-streaming-bot-v4-secret}
EOF
echo "✅ Configuration cron créée"
echo ""
echo "⏰ Configuration du crontab..."
if ! crontab -l 2>/dev/null | grep -q "netflix_bot_v4.py"; then    # ← v4
    echo "0 8 * * * cd /app && export \$(cat /app/.env_for_cron | xargs) && /usr/local/bin/python3 netflix_bot_v4.py >> /app/logs/cron.log 2>&1" | crontab -    # ← v4
    echo "✅ Crontab créé (exécution quotidienne à 8h00)"
else
    echo "✅ Crontab existant conservé"
    crontab -l | grep "netflix_bot_v4.py"
fi
echo ""
echo "⏰ Démarrage du service cron..."
if command -v crond &> /dev/null; then
    crond -b -l 2
    echo "✅ Service crond (Alpine) démarré"
elif command -v cron &> /dev/null; then
    service cron start
    echo "✅ Service cron (Debian) démarré"
else
    echo "⚠️  Aucun service cron trouvé"
fi
sleep 2
if pgrep -x crond > /dev/null 2>&1 || pgrep -x cron > /dev/null 2>&1; then
    echo "✅ Cron actif et opérationnel"
else
    echo "⚠️  Cron non disponible (tâches planifiées désactivées)"
fi
echo ""
echo "📅 Planification active:"
crontab -l 2>/dev/null || echo "⚠️  Aucune tâche planifiée"
echo ""
echo "=================================================="
echo "✨ Configuration complète"
echo "=================================================="
echo "🌐 Interface web: http://localhost:5000"
echo "👤 Login par défaut: admin / admin123"
echo "📡 API Source: mdblist.com (Netflix + Disney+)"
echo "⏰ Planification: Quotidien à 8h00"
echo "=================================================="
echo ""
if [ -f /app/web_interface.py ]; then
    echo "🌐 Démarrage de l'interface web Flask..."
    cd /app
    exec python3 web_interface.py
else
    echo "⚠️  Interface web non trouvée"
    tail -f /dev/null
fi