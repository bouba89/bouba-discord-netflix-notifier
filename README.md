# 🎬 Bouba Discord Netflix Notifier

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Open_Source-green.svg)](LICENSE)

Un bot Discord intelligent qui vous informe automatiquement des nouveautés Netflix directement dans votre serveur Discord. Recevez chaque jour à 9h les dernières sorties de films et séries !

## ✨ Fonctionnalités

- 📅 **Notifications quotidiennes automatiques** - Tous les jours à 9h (heure de sortie FR VOD Netflix)
- 🎭 **Suivi par catégories** - Films et séries classés par genre (Action, Comédie, Documentaire, etc.)
- 🌍 **Multi-pays** - Configurable pour suivre plusieurs pays simultanément
- 🔄 **Anti-doublons intelligent** - Évite les notifications répétitives
- 🐳 **Docker ready** - Déploiement facile avec Docker et Docker Compose
- 📊 **Informations détaillées** - Intégration TMDB pour les métadonnées enrichies
- 💾 **Persistance des données** - Stockage local des contenus déjà envoyés

## 🗂️ Structure du projet

```
bouba-discord-netflix-notifier/
├── data/                    # Dossier de données persistantes
│   └── sent_ids.json       # Historique des contenus envoyés
├── logs/                    # Logs du bot
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration Docker
├── netflix_bot.py          # Script principal du bot
├── crontab.txt             # Configuration des tâches planifiées
├── .env                    # Variables d'environnement (à créer)
└── README.md               # Documentation
```

## ⚙️ Prérequis

Avant de commencer, assurez-vous d'avoir :

- 🐳 [Docker](https://www.docker.com/) et Docker Compose installés
- 🐍 Python 3.11 (si exécution locale)
- 🤖 [Token Discord](https://discord.com/developers/applications) pour votre bot
- 🔑 Abonnement à l'[API UNOGS](https://rapidapi.com/unogs/api/unogs) via RapidAPI
- 🎬 Clé [API TMDB](https://www.themoviedb.org/settings/api) pour les métadonnées
- 🌐 Connexion Internet

## 🚀 Installation & Lancement

### 1️⃣ Cloner le repository

```bash
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier
```

### 2️⃣ Créer le fichier de configuration

```bash
touch .env
```

### 3️⃣ Configurer les variables d'environnement

Éditez le fichier `.env` et ajoutez vos clés API :

```env
# API RapidAPI pour UNOGS
RAPIDAPI_KEY=votre_cle_rapidapi_ici

# API TMDB pour les informations détaillées
TMDB_API_KEY=votre_cle_tmdb_ici

# Webhook Discord pour recevoir les notifications
DISCORD_WEBHOOK=https://discord.com/api/webhooks/votre_webhook_ici

# Pays à surveiller (codes ISO, séparés par des virgules)
COUNTRIES=FR,US,CA,GB
```

### 4️⃣ Lancer avec Docker Compose

**Construction et démarrage initial :**
```bash
docker-compose up --build -d
```

**Démarrage après la première installation :**
```bash
docker-compose up -d
```

### 5️⃣ Tester le bot manuellement

Pour vérifier que tout fonctionne correctement :

```bash
docker exec -it netflix_bot python /app/netflix_bot.py
```

Vous devriez voir apparaître une notification dans votre canal Discord !

## 📋 Commandes utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Arrêter le bot
docker-compose down

# Redémarrer le bot
docker-compose restart

# Reconstruire l'image
docker-compose up --build -d

# Accéder au conteneur
docker exec -it netflix_bot /bin/bash
```

## 🔧 Configuration avancée

### Modifier l'heure d'exécution

Éditez le fichier `crontab.txt` pour changer l'horaire :

```bash
# Format : minute heure jour mois jour_semaine commande
0 9 * * * python /app/netflix_bot.py >> /app/logs/cron.log 2>&1
```

### Système anti-doublons

Le bot stocke les IDs des contenus déjà envoyés dans :
```
/app/data/sent_ids.json
```

Ce fichier est persisté grâce au volume Docker configuré dans `docker-compose.yml`.

## 🛠️ Technologies utilisées

- **Python 3.11** - Langage principal
- **Docker & Docker Compose** - Conteneurisation et orchestration
- **UNOGS API** - Récupération des nouveautés Netflix
- **TMDB API** - Métadonnées enrichies (posters, synopsis, etc.)
- **Discord Webhooks** - Envoi des notifications
- **Cron** - Planification des tâches

## 📝 Exemple de notification

Le bot envoie des messages Discord enrichis avec :
- 🎬 Titre du film/série
- 📅 Date de sortie
- ⭐ Note TMDB
- 📖 Synopsis
- 🖼️ Poster officiel
- 🎭 Genres
- 🌍 Pays de disponibilité

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. 🍴 Fork le projet
2. 🌿 Créer une branche (`git checkout -b feature/amelioration`)
3. 💬 Commit vos changements (`git commit -m 'Ajout d'une fonctionnalité'`)
4. 📤 Push vers la branche (`git push origin feature/amelioration`)
5. 🔀 Ouvrir une Pull Request

Pour signaler un bug ou proposer une idée, [ouvrez une issue](https://github.com/bouba89/bouba-discord-netflix-notifier/issues).

## 📄 Licence

Ce projet est sous licence Open Source. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

Si vous rencontrez des problèmes :

1. Vérifiez que toutes les clés API sont valides
2. Consultez les logs : `docker-compose logs netflix-notifier`
3. Assurez-vous que le webhook Discord est actif
4. [Ouvrez une issue](https://github.com/bouba89/bouba-discord-netflix-notifier/issues) si le problème persiste

## 🎯 Roadmap

- [ ] Support de plus de plateformes de streaming
- [ ] Interface web pour la configuration
- [ ] Filtres personnalisables par utilisateur
- [ ] Notifications push mobiles
- [ ] Base de données pour l'historique

---

Développé avec ❤️ par [bouba89](https://github.com/bouba89)

⭐ N'oubliez pas de donner une étoile au projet si vous l'aimez !
