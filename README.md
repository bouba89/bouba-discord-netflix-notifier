# 🎬 Bouba Discord Netflix Notifier

[![Release](https://img.shields.io/github/v/release/bouba89/bouba-discord-netflix-notifier)](https://github.com/bouba89/bouba-discord-netflix-notifier/releases)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Open--Source-green)](LICENSE)

Un bot Discord automatisé qui vous notifie quotidiennement des nouvelles sorties Netflix directement dans votre serveur Discord ! 🍿

## ✨ Fonctionnalités

- 🔔 **Notifications automatiques** des nouveaux films et séries Netflix chaque jour à 9h
- 🎯 **Suivi par catégorie** (Action, Comédie, Documentaire, etc.)
- 🌍 **Multi-pays** : Configurez les pays que vous souhaitez suivre (FR, US, CA, KR, THA, etc.)
- 🚫 **Anti-doublons** : Ne notifie jamais le même contenu deux fois
- 🐳 **Déployable facilement** avec Docker et Docker Compose
- 🔍 **Système de debug complet** avec logs détaillés et sauvegarde des réponses API
- 📊 **Monitoring avancé** avec logs multi-niveaux
- 💾 **Persistence des données** avec volumes Docker
- ⏰ **Gestion du timezone** pour une exécution précise
- 🧪 **Test automatique** au démarrage du container

## 📋 Prérequis

- [Docker](https://docs.docker.com/get-docker/) installé
- [Docker Compose](https://docs.docker.com/compose/install/) installé
- Un webhook Discord (voir [Comment créer un webhook Discord](https://support.discord.com/hc/en-us/articles/228383668))
- Clé API [UNOGS via RapidAPI](https://rapidapi.com/unogs/api/unogs)
- Clé API [TMDB](https://www.themoviedb.org/settings/api)

## 🚀 Installation rapide

### 1. Cloner le projet

```bash
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier
```

### 2. Configurer les variables d'environnement

Créez un fichier `.env` à partir de l'exemple :

```bash
cp .env.example .env
```

Éditez le fichier `.env` avec vos clés API :

```env
# API Keys
RAPIDAPI_KEY=votre_cle_rapidapi
TMDB_API_KEY=votre_cle_tmdb

# Discord
DISCORD_WEBHOOK=https://discord.com/api/webhooks/VOTRE_WEBHOOK_URL

# Configuration (pays séparés par des virgules)
COUNTRIES=FR,US,CA,KR,THA
```

### 3. Créer les dossiers nécessaires

```bash
mkdir -p data logs
```

### 4. Lancer le bot

```bash
# Build et démarrage en arrière-plan
docker-compose up --build -d

# Vérifier les logs de démarrage
docker logs -f bouba_discord_netflix_notifier
```

Le bot effectuera un **test automatique** au démarrage et vous verrez :
- ✅ Vérification des variables d'environnement
- ✅ Création du fichier `.env_for_cron`
- ✅ Configuration de la crontab
- ✅ Démarrage de cron
- ✅ Test immédiat du bot

### 5. Tester manuellement (optionnel)

```bash
# Exécution manuelle du script wrapper
docker exec -it bouba_discord_netflix_notifier /app/run_netflix.sh

# Ou directement le script Python
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py
```

## 🗂️ Architecture du projet

```
bouba-discord-netflix-notifier/
├── data/                          # Données persistantes
│   ├── sent_ids.json             # IDs des contenus déjà notifiés (anti-doublons)
│   └── api_responses_debug.json  # Réponses API pour debug (100 dernières)
├── logs/                          # Fichiers de logs
│   ├── netflix_bot_debug.log     # Logs détaillés avec niveau DEBUG
│   ├── cron.log                  # Logs des exécutions cron
│   └── netflix_bot.log           # Logs standards (legacy)
├── .dockerignore                  # Fichiers exclus du build Docker
├── .env                          # Variables d'environnement (à créer)
├── .env.example                  # Template pour .env
├── .gitignore                    # Fichiers exclus de Git
├── crontab.txt                   # Configuration cron (8h UTC = 9h FR)
├── docker-compose.yml            # Configuration Docker Compose avec timezone
├── Dockerfile                    # Image Docker multi-stage optimisée
├── netflix_bot.py                # Script principal avec debug complet
├── requirements.txt              # Dépendances Python
├── README.md                     # Documentation
└── LICENSE                       # Licence open-source

# Fichiers générés automatiquement dans le container :
├── run_netflix.sh                # Script wrapper avec vérification des ENV
├── start.sh                      # Script de démarrage du container
└── .env_for_cron                 # Variables ENV pour cron (créé au runtime)
```

## 📦 Dépendances

- **Python 3.11**
- **requests 2.31.0** - Pour les appels API

## 🔧 Commandes utiles

### Gestion du container

```bash
# Démarrer le bot
docker-compose up -d

# Arrêter le bot
docker-compose down

# Voir les logs en temps réel
docker logs -f bouba_discord_netflix_notifier

# Redémarrer le bot
docker-compose restart

# Rebuild complet
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Accéder au shell du container
docker exec -it bouba_discord_netflix_notifier /bin/bash
```

### Consultation des logs

```bash
# Logs de démarrage et status
docker logs bouba_discord_netflix_notifier

# Logs détaillés du bot (avec debug)
docker exec -it bouba_discord_netflix_notifier tail -f /app/logs/netflix_bot_debug.log

# Logs des exécutions cron
docker exec -it bouba_discord_netflix_notifier tail -f /app/logs/cron.log

# Voir les 50 dernières lignes
docker exec -it bouba_discord_netflix_notifier tail -50 /app/logs/netflix_bot_debug.log

# Chercher des erreurs
docker exec -it bouba_discord_netflix_notifier grep -i "erreur\|error" /app/logs/netflix_bot_debug.log
```

### Debug et diagnostic

```bash
# Voir les réponses API brutes (JSON formaté)
docker exec -it bouba_discord_netflix_notifier cat /app/data/api_responses_debug.json

# Voir les contenus déjà notifiés
docker exec -it bouba_discord_netflix_notifier cat /app/data/sent_ids.json

# Vérifier les variables d'environnement
docker exec -it bouba_discord_netflix_notifier cat /app/.env_for_cron

# Vérifier que cron tourne
docker exec -it bouba_discord_netflix_notifier cat /var/run/crond.pid

# Voir la crontab installée
docker exec -it bouba_discord_netflix_notifier crontab -l

# Test manuel du bot
docker exec -it bouba_discord_netflix_notifier /app/run_netflix.sh
```

### Réinitialisation

```bash
# Réinitialiser la mémoire anti-doublons (va renvoyer tout ce qui a < 24h)
echo "[]" > data/sent_ids.json

# Vider les logs
rm -f logs/*.log

# Rebuild complet avec nettoyage
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## ⚙️ Configuration avancée

### Modifier l'heure d'exécution

Le bot est configuré pour s'exécuter à **8h00 UTC** (= **9h00 heure française** en hiver).

Éditez le fichier `crontab.txt` :

```bash
# Format: minute heure jour mois jour_semaine commande
0 8 * * * . /app/.env_for_cron && /app/run_netflix.sh >> /app/logs/cron.log 2>&1
```

Exemples :
- `0 8 * * *` → Tous les jours à 8h00 (avec TZ=Europe/Paris = 8h00 FR)
- `0 9 * * *` → Tous les jours à 9h00
- `0 12 * * *` → Tous les jours à 12h00
- `0 9 * * 1` → Tous les lundis à 9h00
- `0 */6 * * *` → Toutes les 6 heures

**Important** : Après modification, vous devez reconstruire le container :

```bash
docker-compose down
docker-compose up --build -d
```

### Configurer le timezone

Le bot utilise par défaut le timezone **Europe/Paris**. Pour changer :

Éditez `docker-compose.yml` :

```yaml
environment:
  - TZ=Europe/Paris  # Changez selon votre zone
```

Exemples de timezones :
- `Europe/Paris` - France
- `America/New_York` - USA Est
- `America/Los_Angeles` - USA Ouest
- `Asia/Tokyo` - Japon
- `Australia/Sydney` - Australie

Liste complète : https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Ajouter/Modifier des pays

Dans votre `.env`, modifiez la variable `COUNTRIES` :

```env
# Pays supportés (codes ISO à 2 lettres)
COUNTRIES=FR,US,CA,GB,ES,DE,IT,JP,KR,THA,AU,BR
```

Pays disponibles via l'API uNoGS :
- 🇫🇷 FR - France
- 🇺🇸 US - États-Unis
- 🇨🇦 CA - Canada
- 🇬🇧 GB - Royaume-Uni
- 🇪🇸 ES - Espagne
- 🇩🇪 DE - Allemagne
- 🇮🇹 IT - Italie
- 🇯🇵 JP - Japon
- 🇰🇷 KR - Corée du Sud
- 🇹🇭 THA - Thaïlande
- 🇦🇺 AU - Australie
- 🇧🇷 BR - Brésil
- Et bien d'autres...

### Niveau de logging

Le bot utilise par défaut le niveau **DEBUG** pour un maximum de détails. Pour changer :

Éditez `netflix_bot.py` ligne 14 :

```python
logging.basicConfig(
    level=logging.INFO,  # Changez DEBUG en INFO, WARNING, ou ERROR
    ...
)
```

Niveaux disponibles :
- `DEBUG` - Tous les détails (recommandé pour le debug)
- `INFO` - Informations importantes
- `WARNING` - Avertissements uniquement
- `ERROR` - Erreurs uniquement

## 🔍 Système de Debug

### Fichiers de debug

Le bot génère automatiquement des fichiers de debug :

1. **`/app/logs/netflix_bot_debug.log`** - Logs détaillés avec :
   - Toutes les requêtes API (URL, paramètres, headers)
   - Toutes les réponses API (status, contenu)
   - Filtrage pays par pays
   - Vérification des dates
   - Anti-doublons en détail
   - Payloads Discord

2. **`/app/data/api_responses_debug.json`** - Historique des 100 dernières requêtes API avec :
   - Timestamp
   - Endpoint appelé
   - Paramètres envoyés
   - Réponse complète
   - Code status HTTP
   - Erreurs éventuelles

### Exemple de sortie

```
2026-01-25 19:37:35 - INFO - 🎬 NETFLIX BOT - DÉMARRAGE
2026-01-25 19:37:35 - INFO - 🌍 Pays configurés: ['FR', 'US', 'CA', 'KR', 'THA']
2026-01-25 19:37:35 - INFO - 🔑 RapidAPI Key: ✅ Configurée
2026-01-25 19:37:35 - INFO - 🔑 TMDB API Key: ✅ Configurée
2026-01-25 19:37:36 - INFO - 📥 Réponse uNoGS: Status 200
2026-01-25 19:37:36 - INFO - ✅ Total titres récupérés: 100
2026-01-25 19:37:36 - INFO - 🌍 TRAITEMENT DU PAYS: FR
2026-01-25 19:37:36 - INFO - 📺 45 titres disponibles dans FR
2026-01-25 19:37:36 - INFO - 🆕 12 titres récents (dernières 24h)
2026-01-25 19:37:36 - INFO - ✨ 5 nouveaux titres (non envoyés)
2026-01-25 19:37:36 - INFO - 🎥 Films: 3 | 📺 Séries: 2
2026-01-25 19:37:37 - INFO - 📨 ENVOI DISCORD POUR FR
2026-01-25 19:37:38 - INFO - ✅ Chunk 1 envoyé avec succès
2026-01-25 19:37:38 - INFO - 🏁 TERMINÉ
2026-01-25 19:37:38 - INFO - 📊 Résumé:
2026-01-25 19:37:38 - INFO -    - Contenus traités: 100
2026-01-25 19:37:38 - INFO -    - Nouveaux envoyés: 5
2026-01-25 19:37:38 - INFO -    - Total en mémoire: 9
```

## 🛡️ Sécurité

- ✅ Le fichier `.env` n'est **jamais** copié dans l'image Docker
- ✅ Les secrets sont passés via variables d'environnement au runtime
- ✅ Fichier `.env_for_cron` créé avec permissions restrictives (600)
- ✅ Image Docker optimisée avec multi-stage build
- ✅ Mise à jour automatique des packages système
- ✅ Pas de credentials en clair dans les logs (masqués avec ***)

## 🐛 Dépannage

### Le bot ne démarre pas

```bash
# Vérifier les logs de démarrage
docker logs bouba_discord_netflix_notifier

# Vérifier les variables d'environnement
docker exec -it bouba_discord_netflix_notifier cat /app/.env_for_cron

# Vérifier que toutes les clés sont présentes
docker exec -it bouba_discord_netflix_notifier env | grep -E "RAPIDAPI|TMDB|DISCORD|COUNTRIES"
```

### Les notifications ne s'affichent pas sur Discord

1. **Vérifiez le webhook Discord** :
   ```bash
   # Tester le webhook manuellement
   curl -X POST -H "Content-Type: application/json" \
     -d '{"content":"Test du bot Netflix"}' \
     "VOTRE_WEBHOOK_URL"
   ```

2. **Vérifiez les logs** :
   ```bash
   docker exec -it bouba_discord_netflix_notifier tail -100 /app/logs/netflix_bot_debug.log | grep -i discord
   ```

3. **Testez manuellement** :
   ```bash
   docker exec -it bouba_discord_netflix_notifier /app/run_netflix.sh
   ```

### Pas de nouveaux contenus détectés

C'est normal si :
- Aucun nouveau contenu n'est sorti dans les dernières 24h
- Les contenus ont déjà été notifiés (vérifiez `data/sent_ids.json`)
- Les contenus ne sont pas disponibles dans vos pays configurés

Pour forcer une nouvelle détection (⚠️ va tout renvoyer) :
```bash
echo "[]" > data/sent_ids.json
docker exec -it bouba_discord_netflix_notifier /app/run_netflix.sh
```

### Cron ne s'exécute pas

```bash
# Vérifier que cron tourne
docker exec -it bouba_discord_netflix_notifier cat /var/run/crond.pid

# Voir la crontab installée
docker exec -it bouba_discord_netflix_notifier crontab -l

# Vérifier les logs cron
docker exec -it bouba_discord_netflix_notifier cat /app/logs/cron.log

# Tester le script wrapper manuellement
docker exec -it bouba_discord_netflix_notifier /app/run_netflix.sh
```

### Erreurs API

Les erreurs API sont sauvegardées dans `api_responses_debug.json` :

```bash
# Voir les erreurs API
docker exec -it bouba_discord_netflix_notifier cat /app/data/api_responses_debug.json | grep -i error

# Voir la dernière réponse uNoGS
docker exec -it bouba_discord_netflix_notifier cat /app/data/api_responses_debug.json | grep -A 20 "uNoGS"
```

Causes fréquentes :
- **Quota API dépassé** : Vérifiez votre compte RapidAPI
- **Clé API invalide** : Vérifiez vos clés dans le `.env`
- **Problème réseau** : Vérifiez la connexion du serveur

### Timezone incorrect

```bash
# Vérifier l'heure du container
docker exec -it bouba_discord_netflix_notifier date

# Vérifier le timezone configuré
docker exec -it bouba_discord_netflix_notifier cat /etc/timezone

# Si incorrect, modifiez TZ dans docker-compose.yml et relancez
docker-compose down
docker-compose up -d
```

## 📊 Monitoring

### Vérifications quotidiennes

```bash
# Status du container
docker ps | grep bouba

# Dernière exécution
docker exec -it bouba_discord_netflix_notifier tail -1 /app/logs/cron.log

# Nombre de contenus en mémoire
docker exec -it bouba_discord_netflix_notifier cat /app/data/sent_ids.json | wc -l

# Taille des logs
docker exec -it bouba_discord_netflix_notifier ls -lh /app/logs/
```

### Nettoyage périodique

Les logs peuvent devenir volumineux avec le temps :

```bash
# Archiver les anciens logs (optionnel)
docker exec -it bouba_discord_netflix_notifier bash -c "cd /app/logs && tar -czf logs_$(date +%Y%m%d).tar.gz *.log && rm *.log"

# Ou simplement vider
rm -f logs/*.log
docker-compose restart
```

Le fichier `api_responses_debug.json` garde automatiquement les 100 dernières requêtes.

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-feature`)
3. Committez vos changements (`git commit -m 'Ajout de ma feature'`)
4. Pushez vers la branche (`git push origin feature/ma-feature`)
5. Ouvrez une Pull Request

### Guidelines

- Testez vos modifications avec `docker-compose up --build`
- Assurez-vous que les logs de debug sont clairs
- Mettez à jour le README si nécessaire
- Respectez le style de code Python (PEP 8)

## 🔮 Fonctionnalités futures

- [ ] Support de Disney+ et Amazon Prime Video
- [ ] Filtres par genre (Action, Comédie, etc.)
- [ ] Notifications personnalisées par utilisateur
- [ ] Interface web pour la configuration
- [ ] Support de Telegram et Slack
- [ ] Statistiques et graphiques
- [ ] Mode "digest" hebdomadaire

## 📄 Licence

Ce projet est sous licence Open-Source. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**bouba89**

- GitHub: [@bouba89](https://github.com/bouba89)
- Projet: [bouba-discord-netflix-notifier](https://github.com/bouba89/bouba-discord-netflix-notifier)

## 🙏 Remerciements

- [UNOGS API](https://rapidapi.com/unogs/api/unogs) pour les données Netflix
- [TMDB API](https://www.themoviedb.org/) pour les informations détaillées des films/séries
- La communauté Docker pour les bonnes pratiques
- La communauté Python pour l'écosystème riche

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/bouba89/bouba-discord-netflix-notifier/issues)
- **Discussions** : [GitHub Discussions](https://github.com/bouba89/bouba-discord-netflix-notifier/discussions)

---

⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !

💬 Des questions ? Ouvrez une issue ou une discussion !
