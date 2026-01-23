#!/bin/bash
set -e

echo "🎬 Starting Netflix Bot..."
echo "📅 $(date)"

# Créer dossiers logs/data
mkdir -p /app/data /app/logs

# Créer fichier de log si absent
touch /app/logs/netflix_bot.log

# Lancer cron en foreground pour Docker
echo "⏰ Starting cron in foreground..."
exec cron -f
