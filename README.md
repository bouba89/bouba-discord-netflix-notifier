🎬 Bouba Discord Netflix Notifier

Un bot Discord qui t’informe automatiquement des nouveautés Netflix directement dans ton serveur !

✨ Fonctionnalités

Notifications automatiques des nouveaux films et séries Netflix.

Configuration simple via appsettings.json.

Suivi par catégorie Netflix (Action, Comédie, Documentaire…).

Compatible avec UNOGS API et TMDB API pour récupérer les contenus.

Déployable facilement avec Docker et Docker Compose.

🗂️ Architecture du projet
bouba-discord-netflix-notifier/
├─ src/                  # Code source principal
│  ├─ Bot/               # Gestion du bot Discord
│  ├─ Services/          # Services Netflix, UNOGS, TMDB
│  ├─ Models/            # Modèles de données
│  └─ main.py            # Point d'entrée du bot (exemple)
├─ appsettings.example.json # Fichier de configuration exemple
├─ Dockerfile
├─ docker-compose.yml
├─ README.md
└─ LICENSE

⚙️ Prérequis

Docker
 installé

Docker Compose
 installé

Token Discord pour ton bot

Abonnement à l’API UNOGS via RapidAPI

Clé API TMDB pour récupérer les informations détaillées des films/séries

Connexion Internet

Installation & Lancement

Clone le projet :

git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier

2 - Copie le fichier de configuration :

cp appsettings.example.json appsettings.json


3 - Remplis appsettings.json avec tes clés et informations :

{
  "DiscordToken": "TON_TOKEN_DISCORD",
  "ChannelId": "ID_DU_CHANNEL",
  "NetflixCategories": ["Action", "Comédie", "Documentaire"],
  "UNOGS": {
    "X-RapidAPI-Key": "TA_CLE_RAPIDAPI",
    "X-RapidAPI-Host": "unogsng.p.rapidapi.com"
  },
  "TMDB": {
    "ApiKey": "TA_CLE_TMDB"
  }
}

4 - Construis et lance le bot avec Docker Compose :

docker-compose up --build -d

5 - Vérifie que le bot est bien connecté à ton serveur Discord.

FROM python:3.11-slim

WORKDIR /app
COPY src/ ./src
COPY appsettings.json ./

RUN pip install --no-cache-dir -r src/requirements.txt

CMD ["python", "src/main.py"]

🔧 Dockerfile & Docker Compose

Dockerfile :

FROM python:3.11-slim

WORKDIR /app
COPY src/ ./src
COPY appsettings.json ./

RUN pip install --no-cache-dir -r src/requirements.txt

CMD ["python", "src/main.py"]


docker-compose.yml :

version: '3.9'
services:
  netflix-notifier:
    build: .
    container_name: bouba_discord_netflix_notifier
    volumes:
      - ./appsettings.json:/app/appsettings.json
    restart: unless-stopped

🤝 Contribution

Les contributions sont bienvenues !

Ouvre une issue pour signaler un bug ou proposer une idée.

Envoie un pull request pour améliorer le projet.


Les contributions sont bienvenues !

Ouvre une issue pour signaler un bug ou proposer une idée.

Envoie un pull request pour améliorer le projet.

📄 Licence

MIT License – voir LICENSE
 pour plus de détails.
