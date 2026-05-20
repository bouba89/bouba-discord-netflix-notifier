# Bouba Discord Netflix Notifier

![Stars](https://img.shields.io/github/stars/bouba89/bouba-discord-netflix-notifier?style=social)
![Forks](https://img.shields.io/github/forks/bouba89/bouba-discord-netflix-notifier?style=social)
![Version](https://img.shields.io/badge/version-4.0-blue.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GHCR](https://img.shields.io/badge/GHCR-Available-181717?style=for-the-badge&logo=github&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 À propos

**Bouba Discord Netflix Notifier** est un bot Discord automatisé qui surveille et notifie les **nouvelles sorties Netflix** directement dans ton serveur Discord.

---

## ✨ Fonctionnalités

- Notifications quotidiennes automatiques
- Embeds Discord personnalisés
- Filtrage par catégories
- Interface web Flask intégrée
- Docker & Docker Compose prêts à l'emploi
- Image disponible sur GitHub Container Registry (GHCR)
- Healthcheck intégré
- Logs et statistiques détaillés

---

## 🐳 Installation via GHCR (recommandé)

### Prérequis

- 🐳 Docker (≥ 20.10)
- 🐙 Docker Compose (≥ 2.0)
- (Optionnel) Clés API :
  - MDBList (recommandé, gratuit)
  - TMDB (pour synopsis en français)

### Étapes rapides

\`\`\`bash
# 1. Télécharge l'image depuis GHCR
docker pull ghcr.io/bouba89/bouba-discord-netflix-notifier:latest

# 2. Clone le repo pour récupérer le docker-compose
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier

# 3. Configure ton .env
cp .env.example .env
nano .env  # configure tes clés

# 4. Lance le container
docker compose up -d
\`\`\`

### Variables d'environnement

| Variable            | Description             | Requis        |
| ------------------- | ----------------------- | ------------- |
| \`DISCORD_WEBHOOK\`   | Webhook Discord         | ✅             |
| \`MDBLIST_API_KEY\`   | Clé MDBList API         | ⚠️ recommandé |
| \`TMDB_API_KEY\`      | Clé TMDB API            | ⚠️ recommandé |
| \`DAYS_BACK\`         | Jours à vérifier        | ❌             |
| \`FLASK_SECRET_KEY\`  | Clé secrète Flask       | ❌             |

---

## 🔧 Installation via build local (avancé)

\`\`\`bash
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier
docker compose build --no-cache
docker compose up -d
\`\`\`

---

## 📦 Utilisation

### Vérifier que le bot tourne

\`\`\`bash
docker ps | grep bouba_netflix_notifier_v3
\`\`\`

### Voir les logs

\`\`\`bash
docker compose logs -f
\`\`\`

### Mettre à jour l'image

\`\`\`bash
docker pull ghcr.io/bouba89/bouba-discord-netflix-notifier:latest
docker compose down
docker compose up -d
\`\`\`

---

## 🤖 CI/CD — GitHub Actions

L'image Docker est automatiquement buildée et pushée sur **GHCR** à chaque push sur \`main\` via GitHub Actions.

\`\`\`
ghcr.io/bouba89/bouba-discord-netflix-notifier:latest
\`\`\`

---

## 🛡️ Sécurité

Ce projet est conçu pour être sécurisé et maintenu :

- Le fichier \`.env\` n'est jamais committé 📁
- Secrets gérés via variables d'environnement
- Dockerfile optimisé avec dernières mises à jour
- Dépendances Python et OS à jour
- Pas de secrets dans le code

Dernier scan Trivy :

\`\`\`bash
trivy image ghcr.io/bouba89/bouba-discord-netflix-notifier:latest
\`\`\`

---

## 📁 Arborescence

\`\`\`
bouba-discord-netflix-notifier/
├── .github/
│   └── workflows/
│       └── docker.yml
├── data/
├── logs/
├── templates/
├── .dockerignore
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── start.sh
├── netflix_bot_v4.py
├── web_flask_v4.py
├── crontab.txt
├── README.md
└── LICENSE
\`\`\`

---

## 📌 License

Ce projet est open-source et libre d'utilisation.

---

## 🤝 Contribution

Contributions bienvenues !

1. Fork le projet
2. Ouvre une branche
3. Envoie une Pull Request

---

## 💬 Support

Besoin d'aide ? Ouvre une [Issue](https://github.com/bouba89/bouba-discord-netflix-notifier/issues) ou pose la question dans les [Discussions](https://github.com/bouba89/bouba-discord-netflix-notifier/discussions) !

✨ N'hésite pas à laisser une ⭐ si le projet te plaît !

---

**bouba89** – Mainteneur du projet
