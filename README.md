# Bouba Discord Netflix Notifier

![Stars](https://img.shields.io/github/stars/bouba89/bouba-discord-netflix-notifier?style=social)
![Forks](https://img.shields.io/github/forks/bouba89/bouba-discord-netflix-notifier?style=social)
![Version](https://img.shields.io/badge/version-3.0-blue.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Open_Source-green?style=for-the-badge)

---

## 🚀 À propos

**Bouba Discord Netflix Notifier** est un bot Discord automatisé qui surveille et notifie les **nouvelles sorties Netflix** directement dans ton serveur Discord.

---

## ✨ Fonctionnalités

- Notifications quotidiennes automatiques
- Embeds Discord personnalisés
- Filtrage par catégories
- Docker & Docker Compose prêts à l’emploi
- Healthcheck intégré
- Logs et statistiques détaillés

---

## 🛠️ Installation

### Prérequis

- 🐳 Docker (≥ 20.10)
- 🐙 Docker Compose (≥ 2.0)
- (Optionnel) Clés API :
  - MDBList (recommandé, gratuit)
  - TMDB (pour synopsis en français)

### Étapes rapides

```bash
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier
cp .env.example .env
nano .env  # configure tes clés
docker-compose up -d


| Variable          | Description      | Requis        |
| ----------------- | ---------------- | ------------- |
| `DISCORD_WEBHOOK` | Webhook Discord  | ✅             |
| `MDBLIST_API_KEY` | Clé MDBList API  | ⚠️ recommandé |
| `TMDB_API_KEY`    | Clé TMDB API     | ⚠️ recommandé |
| `DAYS_BACK`       | Jours à vérifier | ❌             |

📦 Utilisation
Vérifier que le bot tourne

docker ps | grep bouba_discord_netflix_notifier

Voir les logs
docker-compose logs -f

Rebuilder l’image
docker-compose down
docker-compose build --no-cache
docker-compose up -d

🛡️ Sécurité

Ce projet est conçu pour être sécurisé et maintenu :

Le fichier .env n’est jamais committé 📁
Secrets gérés via variables d’environnement
Dockerfile optimisé avec dernières mises à jour
Dépendances Python et OS à jour
Pas de secrets dans le code

Dernier scan Trivy (local build) : 0 vulnérabilités détectées
Command utilisée :

trivy image bouba89/netflix-bot-v3

📁 Arborescence

bouba-discord-netflix-notifier/
├── data/
├── logs/
├── .dockerignore
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── start.sh
├── netflix_bot.py
├── web_interface.py
├── crontab.txt
├── README.md
└── LICENSE

📌 License

Ce projet est open-source et libre d’utilisation.

🤝 Contribution

Contributions bienvenues !

Fork le projet
Ouvre une branche
Envoie une Pull Request
💬 Support

Besoin d’aide ? Ouvre une Issue ou pose la question dans les Discussions !
✨ N’hésite pas à laisser une ⭐ si le projet te plaît !

bouba89 – Mainteneur du projet




