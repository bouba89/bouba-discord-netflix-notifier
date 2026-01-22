🎬 Bouba Discord Netflix Notifier

Un bot Discord en python deployable via un containeur docker  qui t’informe automatiquement des nouveautés Netflix directement dans ton serveur Au jour le jour !

✨ Fonctionnalités

Notifications automatiques des nouveaux films et séries Netflix. Toute les jours à 9h ( sortie FR VOD Netflix )

Suivi par catégorie Netflix (Action, Comédie, Documentaire…).

Compatible avec UNOGS API et TMDB API pour récupérer les contenus.

Déployable facilement avec Docker et Docker Compose.
Crontab Mise automatiquement au build 

Fonction  Anti-doublons

- Ne genere pas la meme serie ou film par jour 
- Stockage dans /app/data/sent_ids.json
- Sauvegarde dans dossier data
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
 
 Python 3.11
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


🔧 Dockerfile & Docker Compose

Dockerfile :
Il gere toute les dependances requises 
Fichier 
- requirements.txt

docker-compose.yml :

version: '3.9'
services:
  netflix-notifier:
    build: .
    container_name: bouba_discord_netflix_notifier
    volumes:
      - ./appsettings.json:/app/appsettings.json
    restart: unless-stopped

@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build l'image Docker
	docker-compose build --no-cache

up: ## Démarre le container en arrière-plan
	docker-compose up -d

down: ## Arrête et supprime le container
	docker-compose down

restart: ## Redémarre le container
	docker-compose restart

logs: ## Affiche les logs du container
	docker-compose logs -f

logs-app: ## Affiche les logs applicatifs
	docker exec -it $(CONTAINER_NAME) tail -f /app/logs/netflix_bot.log

shell: ## Ouvre un shell dans le container
	docker exec -it $(CONTAINER_NAME) /bin/bash

test: ## Exécute le bot manuellement pour tester
	docker exec -it $(CONTAINER_NAME) python /app/netflix_bot.py

status: ## Affiche le status du container
	docker-compose ps

inspect: ## Inspecte le container
	docker inspect $(CONTAINER_NAME)

clean: ## Nettoie les volumes et images inutilisés
	docker-compose down -v
	docker system prune -f

prune: ## Nettoie tout Docker (ATTENTION: supprime toutes les images non utilisées)
	docker system prune -a -f --volumes

backup: ## Backup des données
	@mkdir -p backups
	@tar -czf backups/netflix-bot-data-$(shell date +%Y%m%d-%H%M%S).tar.gz data/
	@echo "Backup créé dans backups/"

restore: ## Restaure le dernier backup (usage: make restore FILE=backup.tar.gz)
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make restore FILE=backups/netflix-bot-data-YYYYMMDD-HHMMSS.tar.gz"; \
		exit 1; \
	fi
	tar -xzf $(FILE) -C .

rebuild: down build up ## Rebuild complet (down + build + up)

health: ## Vérifie le health du container
	docker inspect --format='{{.State.Health.Status}}' $(CONTAINER_NAME)

stats: ## Affiche les stats du container
	docker stats $(CONTAINER_NAME) --no-stream


🤝 Contribution

Les contributions sont bienvenues !

Ouvre une issue pour signaler un bug ou proposer une idée.

Envoie un pull request pour améliorer le projet.


Les contributions sont bienvenues !

Ouvre une issue pour signaler un bug ou proposer une idée.

Envoie un pull request pour améliorer le projet.

📄 Licence

License Open-Source.
