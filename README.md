🎬 Bouba Discord Netflix Notifier

Un bot Discord en python deployable via un containeur docker  qui t’informe automatiquement des nouveautés Netflix directement dans ton serveur Au jour le jour !

✨ Fonctionnalités

Notifications automatiques des nouveaux films et séries Netflix. Toute les jours à 9h ( sortie FR VOD Netflix )

Suivi par catégorie Netflix (Action, Comédie, Documentaire…).

Compatible avec UNOGS API et TMDB API pour récupérer les contenus.

Déployable facilement avec Docker et Docker Compose.
Crontab Mise automatiquement au build 

Fonction  Anti-doublons

Ne genere pas la meme serie ou film par jour 
Stockage dans /app/data/sent_ids.json

# --- Sauvegarde dans un dossier data
MEMORY_FILE = "/app/data/sent_ids.json"

🗂️ Architecture du projet
bouba-discord-netflix-notifier 
├─ Data
├─ Dockerfile
├─ docker-compose.yml
|_ netflix-bot.py
|_ crontab.txt
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

2 - Creez un fichier .env a la base du projet :
touch .env

3 - Dans ton fichier .env 

Remplis tes id token et API

RAPIDAPI_KEY= 
TMDB_API_KEY=
DISCORD_WEBHOOK=URL_WEBHOOK-DISCORD 
COUNTRIES=FR,US,CA etc..  ( Pays souhaiter )


4 - Construis et lance le bot avec Docker Compose :

docker-compose up --build -d
docker-compose up -d 

5 - Execute une demo

docker exec -it netflix_bot python /app/netflix_bot.py

6 - Vérifie que le bot est bien connecté à ton serveur Discord.

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
