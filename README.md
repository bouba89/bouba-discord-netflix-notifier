# 🎬 Bouba Discord Netflix Notifier

[![Release](https://img.shields.io/github/v/release/bouba89/bouba-discord-netflix-notifier)](https://github.com/bouba89/bouba-discord-netflix-notifier/releases)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Security](https://img.shields.io/badge/trivy-0%20CVE-brightgreen)](https://trivy.dev/)
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
- 🔒 **Image sécurisée** avec 0 vulnérabilité CVE

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
├── templates/                 # Templates web
├── .dockerignore              # Fichiers exclus du build Docker
├── .env                       # Variables d'environnement (à créer)
├── .gitignore                 # Fichiers exclus de Git
├── crontab.txt                # Configuration du cron (9h chaque jour)
├── docker-compose.yml         # Configuration Docker Compose
├── Dockerfile                 # Image Docker multi-stage optimisée
├── netflix_bot.py             # Script principal du bot
├── web_interface.py           # Interface web Flask
├── requirements.txt           # Dépendances Python
├── run_netflix.sh             # Script d'exécution Netflix
├── start.sh                   # Script d'initialisation du container
├── README.md                  # Documentation
└── LICENSE                    # Licence open-source
```

## 📦 Dépendances

| Package | Version | Description |
|---------|---------|-------------|
| Python | 3.11 | Runtime |
| Flask | 3.0.0 | Interface web |
| requests | ≥2.32.4 | Appels API |
| werkzeug | ≥3.1.5 | WSGI toolkit |
| python-dotenv | 1.0.0 | Variables d'environnement |
| jaraco.context | ≥6.1.0 | Gestion de contexte |

## 🛡️ Sécurité

Cette image Docker a été durcie et auditée pour la production.

### ✅ Scan de vulnérabilités

L'image est scannée avec [Trivy](https://trivy.dev/) et affiche **0 vulnérabilité CVE** :

```bash
# Scanner l'image
trivy image bouba89/netflix-bot:latest
```

### ✅ Mesures de sécurité implémentées

| Mesure | Description |
|--------|-------------|
| **Multi-stage build** | L'image finale ne contient pas les outils de compilation (gcc, g++) |
| **Image Alpine** | Base minimale (~5MB) réduisant la surface d'attaque |
| **Dépendances patchées** | Toutes les CVE connues corrigées (pip, wheel, werkzeug, requests, jaraco.context) |
| **pip/wheel supprimés** | Les outils d'installation sont supprimés de l'image finale |
| **Secrets externalisés** | Les clés API sont passées via variables d'environnement, jamais dans l'image |
| **Utilisateur non-root** | L'application peut tourner avec un utilisateur dédié (appuser) |
| **Healthcheck** | Monitoring intégré de l'état du container |

### ✅ CVE corrigées

| CVE | Package | Sévérité | Correction |
|-----|---------|----------|------------|
| CVE-2024-34069 | werkzeug | HIGH | ≥3.0.3 |
| CVE-2024-49766 | werkzeug | MEDIUM | ≥3.0.6 |
| CVE-2024-49767 | werkzeug | MEDIUM | ≥3.0.6 |
| CVE-2025-66221 | werkzeug | MEDIUM | ≥3.1.4 |
| CVE-2026-21860 | werkzeug | MEDIUM | ≥3.1.5 |
| CVE-2026-23949 | jaraco.context | HIGH | ≥6.1.0 |
| CVE-2024-35195 | requests | MEDIUM | ≥2.32.0 |
| CVE-2024-47081 | requests | MEDIUM | ≥2.32.4 |
| CVE-2026-24049 | wheel | HIGH | Supprimé |
| CVE-2025-8869 | pip | MEDIUM | Supprimé |

### ✅ Bonnes pratiques Docker

- ✅ `.env` exclu via `.dockerignore`
- ✅ Layers optimisés pour le cache
- ✅ `PYTHONDONTWRITEBYTECODE=1` (pas de fichiers .pyc)
- ✅ `PIP_NO_CACHE_DIR=1` (image plus légère)
- ✅ `apt-get clean` et suppression des listes apt

### 🔍 Auditer l'image vous-même

```bash
# Installer Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin

# Scanner l'image
trivy image bouba89/netflix-bot:latest

# Scanner uniquement les CVE critiques/hautes
trivy image --severity HIGH,CRITICAL bouba89/netflix-bot:latest

# Ignorer les CVE sans correctif disponible
trivy image --ignore-unfixed bouba89/netflix-bot:latest
```

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

## 📊 Monitoring

Le bot inclut un **healthcheck** qui vérifie toutes les 30 secondes :
- Que l'interface web répond sur `/health`
- Que le container fonctionne correctement

```bash
# Vérifier la santé du container
docker ps
```

Le status peut être :
- `healthy` ✅ - Le bot fonctionne correctement
- `unhealthy` ❌ - Problème détecté
- `starting` ⏳ - En cours de démarrage (5s)

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
- [Trivy](https://trivy.dev/) pour le scan de sécurité
- La communauté Docker pour les bonnes pratiques

---

⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !
