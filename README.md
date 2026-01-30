# 🎬 Bouba Discord Netflix Notifier

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Open_Source-green.svg)](LICENSE)

Un bot Discord intelligent avec **interface web de monitoring** qui vous informe automatiquement des nouveautés Netflix directement dans votre serveur Discord. Recevez chaque jour à 9h les dernières sorties de films et séries !

## ✨ Fonctionnalités

### 🤖 Bot Discord
- 📅 **Notifications quotidiennes automatiques** - Tous les jours à 9h (heure de sortie FR VOD Netflix)
- 🎭 **Suivi par catégories** - Films et séries classés par genre (Action, Comédie, Documentaire, etc.)
- 🌍 **Multi-pays** - Configurable pour suivre plusieurs pays simultanément
- 🔄 **Anti-doublons intelligent** - Évite les notifications répétitives
- 📊 **Informations détaillées** - Intégration TMDB pour les métadonnées enrichies
- 💾 **Persistance des données** - Stockage local des contenus déjà envoyés

### 🌐 Interface Web (Flask)
- 📊 **Dashboard en temps réel** - Surveillance du statut du bot
- 📈 **Statistiques détaillées** - Nombre de contenus envoyés, par pays, dernière exécution
- 📋 **Visualisation des logs** - Logs en direct (debug & cron)
- ▶️ **Exécution manuelle** - Lancer le bot à la demande depuis l'interface
- 🔧 **Gestion de configuration** - Visualiser les variables d'environnement
- 🔄 **Réinitialisation mémoire** - Reset de la base anti-doublons
- 📥 **Téléchargement des logs** - Export des fichiers de logs
- 🐛 **Debug API** - Visualisation des requêtes API

### 🐳 Déploiement
- **Docker ready** - Déploiement facile avec Docker et Docker Compose
- **Auto-configuration** - Cron automatiquement configuré au build
- **Volumes persistants** - Conservation des données et logs

## 🗂️ Structure du projet

```
bouba-discord-netflix-notifier/
├── data/                        # Dossier de données persistantes
│   ├── sent_ids.json           # Historique des contenus envoyés
│   └── api_responses_debug.json # Debug des réponses API
├── logs/                        # Logs du bot
│   ├── netflix_bot_debug.log   # Logs détaillés du bot
│   └── cron.log                # Logs des tâches planifiées
├── templates/                   # Templates HTML pour Flask
│   └── index.html              # Dashboard principal
├── Dockerfile                  # Configuration Docker
├── docker-compose.yml          # Orchestration Docker
├── netflix_bot.py              # Script principal du bot
├── web_interface.py            # Interface web Flask
├── crontab.txt                 # Configuration des tâches planifiées
├── .env                        # Variables d'environnement (à créer)
└── README.md                   # Documentation
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

### 5️⃣ Accéder à l'interface web

Une fois le conteneur lancé, l'interface web est accessible à :

```
http://localhost:5000
```

🎉 Vous pouvez maintenant monitorer votre bot en temps réel !

### 6️⃣ Tester le bot manuellement

**Via l'interface web :**
- Cliquez sur le bouton "▶️ Exécuter Maintenant" dans le dashboard

**Via la ligne de commande :**
```bash
docker exec -it netflix_bot python /app/netflix_bot.py
```

## 🖥️ Interface Web - Fonctionnalités

### Dashboard Principal

L'interface web Flask offre un dashboard complet avec plusieurs sections :

#### 📊 Section Statut
- **État du bot** : Running / Stopped
- **Cron actif** : Vérification du service cron
- **Variables d'environnement** : Affichage masqué des clés sensibles
- **Dernière exécution** : Timestamp de la dernière notification envoyée

#### 📈 Section Statistiques
- **Total de contenus envoyés** : Nombre cumulé depuis le début
- **Statistiques par pays** : Répartition des notifications par pays configuré
- **Dernière exécution** : 
  - Total de contenus traités
  - Nouveaux contenus envoyés
  - Date et heure d'exécution

#### 📋 Section Logs
- **Logs en temps réel** : Affichage des 100 dernières lignes
- **Basculement Debug/Cron** : Deux types de logs disponibles
- **Auto-refresh** : Mise à jour automatique toutes les 30 secondes
- **Téléchargement** : Export des logs en fichiers

#### 🛠️ Section Actions
- **▶️ Exécuter maintenant** : Lancer le bot manuellement
- **🔄 Réinitialiser la mémoire** : Reset de la liste anti-doublons
- **📥 Télécharger les logs** : Export de tous les fichiers de logs

#### 🐛 Section Debug
- **Requêtes API** : Visualisation des 20 dernières requêtes API
- **Réponses brutes** : Inspection des données retournées par UNOGS et TMDB

### API Endpoints

L'interface web expose plusieurs endpoints API REST :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/status` | GET | Récupérer le statut général du bot |
| `/api/stats` | GET | Obtenir les statistiques détaillées |
| `/api/logs?type=debug&lines=100` | GET | Récupérer les logs (debug ou cron) |
| `/api/run` | POST | Exécuter le bot manuellement |
| `/api/config` | GET | Visualiser la configuration |
| `/api/reset` | POST | Réinitialiser la mémoire anti-doublons |
| `/api/debug` | GET | Récupérer les données de debug API |
| `/download/logs/<type>` | GET | Télécharger les fichiers logs |

## 📋 Commandes utiles

### Docker

```bash
# Voir les logs du conteneur en temps réel
docker-compose logs -f

# Voir uniquement les logs du bot
docker logs -f netflix_bot

# Arrêter le bot
docker-compose down

# Redémarrer le bot
docker-compose restart

# Reconstruire l'image
docker-compose up --build -d

# Accéder au conteneur
docker exec -it netflix_bot /bin/bash

# Vérifier le statut
docker-compose ps
```

### Bot

```bash
# Exécuter le bot manuellement
docker exec -it netflix_bot python /app/netflix_bot.py

# Voir les logs en direct
docker exec -it netflix_bot tail -f /app/logs/netflix_bot_debug.log

# Vérifier le cron
docker exec -it netflix_bot crontab -l

# Réinitialiser la mémoire
docker exec -it netflix_bot bash -c "echo '[]' > /app/data/sent_ids.json"
```

## 🔧 Configuration avancée

### Modifier l'heure d'exécution

Éditez le fichier `crontab.txt` pour changer l'horaire :

```bash
# Format : minute heure jour mois jour_semaine commande
0 9 * * * python /app/netflix_bot.py >> /app/logs/cron.log 2>&1

# Exemples :
# Tous les jours à 6h du matin
0 6 * * * python /app/netflix_bot.py >> /app/logs/cron.log 2>&1

# Deux fois par jour (9h et 18h)
0 9,18 * * * python /app/netflix_bot.py >> /app/logs/cron.log 2>&1
```

Puis reconstruisez l'image Docker :
```bash
docker-compose up --build -d
```

### Changer le port de l'interface web

Modifiez le fichier `docker-compose.yml` :

```yaml
services:
  netflix-notifier:
    ports:
      - "8080:5000"  # Remplacez 8080 par le port souhaité
```

### Système anti-doublons

Le bot stocke les IDs des contenus déjà envoyés dans :
```
/app/data/sent_ids.json
```

Ce fichier est persisté grâce au volume Docker configuré dans `docker-compose.yml`.

Pour réinitialiser :
- Via l'interface web : Cliquez sur "🔄 Réinitialiser"
- Via CLI : `docker exec -it netflix_bot bash -c "echo '[]' > /app/data/sent_ids.json"`

## 🛠️ Technologies utilisées

### Backend
- **Python 3.11** - Langage principal
- **Flask 3.0** - Framework web pour l'interface de monitoring
- **UNOGS API** - Récupération des nouveautés Netflix
- **TMDB API** - Métadonnées enrichies (posters, synopsis, notes)
- **Discord Webhooks** - Envoi des notifications

### Infrastructure
- **Docker & Docker Compose** - Conteneurisation et orchestration
- **Cron** - Planification des tâches automatiques
- **Volume Docker** - Persistance des données et logs

### Frontend
- **HTML5/CSS3** - Interface web responsive
- **JavaScript (Vanilla)** - Interactions dynamiques et API REST
- **Bootstrap** (optionnel) - Framework CSS

## 📝 Exemple de notification

Le bot envoie des messages Discord enrichis avec :
- 🎬 **Titre** du film/série
- 📅 **Date de sortie** sur Netflix
- ⭐ **Note TMDB** (sur 10)
- 📖 **Synopsis** complet
- 🖼️ **Poster** officiel haute qualité
- 🎭 **Genres** (Action, Thriller, etc.)
- 🌍 **Pays** de disponibilité
- 🔗 **Lien** vers la fiche TMDB

## 📸 Captures d'écran

### Interface Web
```
┌─────────────────────────────────────────┐
│  🎬 Netflix Bot Dashboard               │
├─────────────────────────────────────────┤
│  📊 Statut                              │
│  • Bot: ✅ Running                      │
│  • Cron: ✅ Active                      │
│  • Dernière exec: 2026-01-30 09:00     │
│                                         │
│  📈 Statistiques                        │
│  • Total envoyés: 1,234 contenus       │
│  • FR: 456 | US: 398 | CA: 234         │
│  • Dernier run: 15 nouveaux / 50 traités│
│                                         │
│  📋 Logs en direct                      │
│  [Auto-refresh] [Debug] [Cron]         │
│  [...logs...]                           │
│                                         │
│  🛠️ Actions                             │
│  [▶️ Exécuter] [🔄 Reset] [📥 Export]  │
└─────────────────────────────────────────┘
```

### Notification Discord
```
╔══════════════════════════════════════╗
║  🎬 NOUVELLE SORTIE NETFLIX FR      ║
╠══════════════════════════════════════╣
║  [Image du poster]                   ║
║                                      ║
║  📺 Titre: The Awesome Series        ║
║  📅 Sortie: 30 janvier 2026          ║
║  ⭐ Note: 8.5/10                     ║
║  🎭 Genres: Action, Thriller         ║
║                                      ║
║  📖 Synopsis:                        ║
║  Une série captivante qui...         ║
║                                      ║
║  🔗 Plus d'infos: [TMDB]            ║
╚══════════════════════════════════════╝
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. 🍴 **Fork** le projet
2. 🌿 Créer une branche (`git checkout -b feature/amelioration`)
3. 💬 **Commit** vos changements (`git commit -m 'Ajout d'une fonctionnalité'`)
4. 📤 **Push** vers la branche (`git push origin feature/amelioration`)
5. 🔀 Ouvrir une **Pull Request**

### Idées de contributions
- 🎨 Améliorer le design de l'interface web
- 📱 Rendre l'interface responsive (mobile)
- 🔔 Ajouter des alertes par email
- 🌐 Support d'autres plateformes de streaming
- 📊 Graphiques de statistiques
- 🔐 Authentification pour l'interface web
- 🌍 Internationalisation (i18n)

Pour signaler un bug ou proposer une idée, [ouvrez une issue](https://github.com/bouba89/bouba-discord-netflix-notifier/issues).

## 🐛 Troubleshooting

### Le bot ne s'exécute pas automatiquement
```bash
# Vérifier si cron est actif
docker exec -it netflix_bot ps aux | grep cron

# Vérifier la configuration cron
docker exec -it netflix_bot crontab -l

# Voir les logs cron
docker exec -it netflix_bot cat /app/logs/cron.log
```

### L'interface web ne répond pas
```bash
# Vérifier que Flask tourne
docker exec -it netflix_bot ps aux | grep flask

# Voir les logs Flask
docker logs netflix_bot | grep Flask

# Redémarrer le conteneur
docker-compose restart
```

### Pas de notifications reçues
1. ✅ Vérifiez que le webhook Discord est valide
2. ✅ Vérifiez les clés API (RAPIDAPI_KEY, TMDB_API_KEY)
3. ✅ Consultez les logs : `/api/logs` ou `docker logs netflix_bot`
4. ✅ Vérifiez que les pays configurés ont des nouveautés

### Erreurs d'API
```bash
# Voir les réponses API en détail
curl http://localhost:5000/api/debug

# Télécharger le fichier de debug API
curl http://localhost:5000/download/logs/api > api_debug.json
```

## 📄 Licence

Ce projet est sous licence Open Source. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

Si vous rencontrez des problèmes :

1. 📖 Consultez la section [Troubleshooting](#-troubleshooting)
2. 🔍 Vérifiez les [issues existantes](https://github.com/bouba89/bouba-discord-netflix-notifier/issues)
3. 💬 [Ouvrez une nouvelle issue](https://github.com/bouba89/bouba-discord-netflix-notifier/issues/new) avec :
   - Description du problème
   - Logs pertinents
   - Configuration (sans les clés sensibles)
   - Étapes pour reproduire

## 🎯 Roadmap

### Version actuelle (v1.1)
- [x] Interface web Flask de monitoring
- [x] Dashboard avec statistiques en temps réel
- [x] Visualisation et téléchargement des logs
- [x] Exécution manuelle depuis l'interface
- [x] API REST complète

### Prochaines versions
- [ ] 🔐 Authentification pour l'interface web
- [ ] 📊 Graphiques et visualisations avancées
- [ ] 🌍 Support de plus de plateformes (Prime Video, Disney+)
- [ ] 📱 Application mobile (React Native)
- [ ] 🔔 Notifications par email
- [ ] 🤖 Bot Discord interactif (commandes)
- [ ] 🗄️ Base de données (PostgreSQL)
- [ ] 🎨 Thèmes personnalisables (dark/light mode)
- [ ] 📅 Calendrier des sorties à venir
- [ ] 🔍 Recherche et filtres avancés
- [ ] 👥 Gestion multi-utilisateurs
- [ ] 🌐 Internationalisation (EN, ES, DE)

## 🙏 Remerciements

- [UNOGS](https://rapidapi.com/unogs/api/unogs) pour l'API Netflix
- [TMDB](https://www.themoviedb.org/) pour les métadonnées
- [Discord](https://discord.com/) pour les webhooks
- [Flask](https://flask.palletsprojects.com/) pour le framework web
- La communauté open-source pour l'inspiration

## 📞 Contact

- **GitHub** : [@bouba89](https://github.com/bouba89)
- **Issues** : [Signaler un problème](https://github.com/bouba89/bouba-discord-netflix-notifier/issues)
- **Discussions** : [Forum du projet](https://github.com/bouba89/bouba-discord-netflix-notifier/discussions)

---

<div align="center">

**Développé avec ❤️ par [bouba89](https://github.com/bouba89)**

⭐ **N'oubliez pas de donner une étoile au projet si vous l'aimez !**

[![GitHub stars](https://img.shields.io/github/stars/bouba89/bouba-discord-netflix-notifier?style=social)](https://github.com/bouba89/bouba-discord-netflix-notifier/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/bouba89/bouba-discord-netflix-notifier?style=social)](https://github.com/bouba89/bouba-discord-netflix-notifier/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/bouba89/bouba-discord-netflix-notifier?style=social)](https://github.com/bouba89/bouba-discord-netflix-notifier/watchers)

</div>
