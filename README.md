# 🎬 Bouba Discord Netflix Notifier

[![Release](https://img.shields.io/github/v/release/bouba89/bouba-discord-netflix-notifier)](https://github.com/bouba89/bouba-discord-netflix-notifier/releases)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Open--Source-green)](LICENSE)

Un bot Discord automatisé qui vous notifie quotidiennement des nouvelles sorties Netflix directement dans votre serveur Discord ! 🍿

## ✨ Fonctionnalités

- 🔔 **Notifications automatiques** des nouveaux films et séries Netflix chaque jour à 9h
- 🎯 **Suivi par catégorie** (Action, Comédie, Documentaire, etc.)
- 🌍 **Multi-pays** : Configurez les pays que vous souhaitez suivre (FR, US, CA, etc.)
- 🚫 **Anti-doublons** : Ne notifie jamais le même contenu deux fois
- 🐳 **Déployable facilement** avec Docker et Docker Compose
- 📊 **Healthcheck intégré** pour monitorer l'état du container
- 💾 **Persistence des données** avec volumes Docker

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

Créez un fichier `.env` à la racine du projet :

```bash
touch .env
```

Remplissez-le avec vos clés API :

```env
# API Keys
RAPIDAPI_KEY=votre_cle_rapidapi
TMDB_API_KEY=votre_cle_tmdb

# Discord
DISCORD_WEBHOOK=https://discord.com/api/webhooks/VOTRE_WEBHOOK_URL

# Configuration
COUNTRIES=FR,US,CA
```

### 3. Lancer le bot

```bash
# Build et démarrage en arrière-plan
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### 4. Tester manuellement (optionnel)

```bash
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py
```

## 🗂️ Architecture du projet

```
bouba-discord-netflix-notifier/
├── data/                      # Données persistantes (anti-doublons)
├── logs/                      # Fichiers de logs
├── .dockerignore              # Fichiers exclus du build Docker
├── .env                       # Variables d'environnement (à créer)
├── .gitignore                 # Fichiers exclus de Git
├── crontab.txt                # Configuration du cron (9h chaque jour)
├── docker-compose.yml         # Configuration Docker Compose
├── Dockerfile                 # Image Docker multi-stage optimisée
├── netflix_bot.py             # Script principal du bot
├── requirements.txt           # Dépendances Python
├── start.sh                   # Script d'initialisation du container
├── README.md                  # Documentation
└── LICENSE                    # Licence open-source
```

## 📦 Dépendances

- **Python 3.11**
- **requests 2.31.0** - Pour les appels API
- **python-dotenv 1.0.0** - Pour la gestion des variables d'environnement

## 🔧 Commandes utiles

```bash
# Démarrer le bot
docker-compose up -d

# Arrêter le bot
docker-compose down

# Voir les logs en temps réel
docker-compose logs -f

# Redémarrer le bot
docker-compose restart

# Rebuild complet
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Vérifier le statut du healthcheck
docker inspect bouba_discord_netflix_notifier | grep -A 10 Health

# Voir les statistiques du container
docker stats bouba_discord_netflix_notifier --no-stream

# Accéder au shell du container
docker exec -it bouba_discord_netflix_notifier /bin/bash
```

## ⚙️ Configuration avancée

### Modifier l'heure d'exécution

Éditez le fichier `crontab.txt` :

```bash
# Format: minute heure jour mois jour_semaine commande
0 9 * * * /usr/local/bin/python /app/netflix_bot.py >> /app/logs/netflix_bot.log 2>&1
```

Exemples :
- `0 9 * * *` → Tous les jours à 9h00
- `0 12 * * *` → Tous les jours à 12h00
- `0 9 * * 1` → Tous les lundis à 9h00

### Ajouter des pays

Dans votre `.env`, modifiez la variable `COUNTRIES` :

```env
COUNTRIES=FR,US,CA,GB,ES,DE
```

## 🛡️ Sécurité

- ✅ Le fichier `.env` n'est **jamais** copié dans l'image Docker
- ✅ Les secrets sont passés via variables d'environnement au runtime
- ✅ Image Docker optimisée avec multi-stage build
- ✅ Mise à jour automatique des packages système avec `apt-get`

## 📊 Monitoring

Le bot inclut un **healthcheck** qui vérifie toutes les heures :
- Que le fichier de données existe (`sent_ids.json`)
- Que le container fonctionne correctement

```bash
# Vérifier la santé du container
docker ps
```

Le status peut être :
- `healthy` ✅ - Le bot fonctionne correctement
- `unhealthy` ❌ - Problème détecté
- `starting` ⏳ - En cours de démarrage (30s)

## 🐛 Dépannage

### Le bot ne démarre pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier que les variables d'environnement sont correctes
docker exec -it bouba_discord_netflix_notifier printenv | grep -E "RAPIDAPI|TMDB|DISCORD"
```

### Les notifications ne s'affichent pas

1. Vérifiez que votre webhook Discord est valide
2. Testez manuellement le bot :
   ```bash
   docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py
   ```
3. Vérifiez les logs : `docker-compose logs -f`

### Le container est "unhealthy"

```bash
# Vérifier si le fichier de données existe
docker exec -it bouba_discord_netflix_notifier ls -la /app/data/

# Redémarrer le container
docker-compose restart
```

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-feature`)
3. Committez vos changements (`git commit -m 'Ajout de ma feature'`)
4. Pushez vers la branche (`git push origin feature/ma-feature`)
5. Ouvrez une Pull Request

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

---

⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !
