# CLAUDE.md - Guide pour Assistants IA

Ce document fournit le contexte essentiel pour les assistants IA travaillant sur le code du Bouba Discord Netflix Notifier.

## Aperçu du Projet

**Bouba Discord Netflix Notifier** est un bot Discord basé sur Python qui notifie automatiquement les serveurs Discord des nouvelles sorties Netflix dans plusieurs pays. Il propose :

- **Intégration Webhook Discord** : Envoie des notifications enrichies sur les nouveaux contenus Netflix
- **Tableau de Bord Web Flask** : Interface stylisée Netflix pour la surveillance, la configuration et l'exécution manuelle du bot
- **Support Multi-pays** : Surveille les sorties Netflix dans plus de 25 pays simultanément
- **Prévention des Doublons** : Système de mémoire pour éviter d'envoyer le même contenu deux fois
- **Enrichissement TMDB** : Récupère les affiches, synopsis et notes depuis The Movie Database API

**Langage Principal** : Python 3.11
**Langue de Documentation** : Français
**Auteur** : Bouba89

## Structure du Dépôt

```
bouba-discord-netflix-notifier/
├── netflix_bot.py           # Logique principale du bot (appels API, filtrage, envoi Discord)
├── web_interface.py         # Serveur web Flask (auth, tableau de bord, endpoints API)
├── templates/
│   ├── login.html           # Page de connexion style Netflix
│   ├── index.html           # Tableau de bord principal
│   └── settings.html        # Interface de configuration
├── Dockerfile               # Image Docker multi-étapes basée sur Alpine
├── docker-compose.yml       # Orchestration des conteneurs
├── start.sh                 # Script d'initialisation du conteneur
├── crontab.txt              # Exécution planifiée du bot (par défaut : 8h00 quotidien)
├── requirements.txt         # Dépendances Python
├── .env.example             # Modèle de variables d'environnement
├── data/                    # Données persistantes (volume Docker)
│   ├── sent_ids.json        # Mémoire anti-doublons (IDs Netflix déjà envoyés)
│   └── users.json           # Stockage des identifiants utilisateurs
├── logs/                    # Fichiers de logs (volume Docker)
│   ├── netflix_bot_debug.log
│   └── cron.log
└── README.md                # Documentation utilisateur (Français)
```

## Fichiers Clés

| Fichier | Objectif | Lignes |
|---------|----------|--------|
| `netflix_bot.py` | Bot principal : appels API UNOGS, enrichissement TMDB, webhooks Discord | ~415 |
| `web_interface.py` | Application Flask : authentification, tableau de bord, API paramètres | ~570 |
| `templates/index.html` | Tableau de bord avec stats, logs, contrôles | ~1088 |
| `templates/settings.html` | Interface de configuration pays et cron | ~638 |
| `templates/login.html` | Page de connexion style Netflix | ~438 |

## Stack Technologique

### Backend
- **Python 3.11** avec Flask 3.0.0
- **Werkzeug 3.0.1** pour le hachage des mots de passe (bcrypt)
- **requests 2.31.0** pour les appels HTTP API
- **python-dotenv 1.0.0** pour les variables d'environnement

### APIs Externes
- **API UNOGS** (via RapidAPI) : Données du catalogue Netflix
- **API TMDB** : Enrichissement des métadonnées films/séries
- **Webhooks Discord** : Livraison des notifications

### Infrastructure
- **Docker** avec build multi-étapes Alpine
- **dcron** pour l'exécution planifiée
- **Docker Compose** pour l'orchestration

### Frontend
- HTML5/CSS3/JavaScript vanilla (pas de frameworks)
- Thème sombre inspiré de Netflix avec animations
- Design responsive (mobile/tablette/desktop)

## Commandes de Développement

### Opérations Docker
```bash
# Construire et démarrer
docker-compose up --build -d

# Voir les logs
docker logs -f bouba_discord_netflix_notifier

# Redémarrer le conteneur
docker-compose restart

# Arrêter le conteneur
docker-compose stop

# Entrer dans le shell du conteneur
docker exec -it bouba_discord_netflix_notifier bash

# Exécuter le bot manuellement
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py

# Vérifier le statut cron
docker exec -it bouba_discord_netflix_notifier crontab -l
```

### Développement Local
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'interface web
python web_interface.py

# Lancer le bot directement
python netflix_bot.py
```

## Variables d'Environnement

Requises dans le fichier `.env` :

| Variable | Description |
|----------|-------------|
| `RAPIDAPI_KEY` | Clé API UNOGS depuis RapidAPI |
| `TMDB_API_KEY` | Clé API The Movie Database |
| `DISCORD_WEBHOOK` | URL du webhook Discord pour les notifications |
| `COUNTRIES` | Codes pays ISO séparés par virgules (ex : `FR,US,CA,GB`) |
| `FLASK_SECRET_KEY` | Clé secrète pour les sessions Flask (générer avec `secrets.token_hex(32)`) |

## Conventions de Code

### Logging
- Utilise le module `logging` de Python avec niveau DEBUG
- Double sortie : fichier (`logs/netflix_bot_debug.log`) et console
- Préfixes emoji pour la clarté visuelle dans les logs
- Réponses de debug API sauvegardées dans `logs/api_debug_last_*.json`

### Conventions de Nommage
- **Variables/Fonctions** : snake_case (ex : `sent_ids`, `fetch_titles`)
- **Constantes** : MAJUSCULES (ex : `API_KEY`, `WEBHOOK_URL`)
- **Commentaires** : Langue française

### Gestion des Erreurs
- Blocs try-catch autour de tous les appels API
- Fallbacks gracieux pour les données manquantes
- Messages d'erreur détaillés avec contexte
- Timeouts configurés pour toutes les requêtes HTTP

### Pratiques de Sécurité
- Hachage des mots de passe avec bcrypt via Werkzeug
- Gestion des sessions avec timeout de 24 heures
- Variables d'environnement pour tous les secrets
- Utilisateur Docker non-root (UID 1000)
- Clés API masquées dans les logs (10 premiers caractères + `***`)

## Patterns d'Architecture

### Flux d'Exécution du Bot (netflix_bot.py)
1. Charger les variables d'environnement et configurer le logging
2. Charger sent_ids.json (mémoire anti-doublons)
3. Pour chaque pays configuré :
   - Récupérer le catalogue Netflix depuis l'API UNOGS
   - Filtrer par date (7 derniers jours)
   - Retirer les éléments déjà envoyés
   - Enrichir avec les données TMDB (affiche, synopsis, note)
   - Envoyer au webhook Discord (max 10 embeds par message)
4. Sauvegarder sent_ids.json mis à jour

### Routes de l'Interface Web (web_interface.py)
- `/` - Tableau de bord (requiert authentification)
- `/login`, `/logout` - Authentification
- `/settings` - Page de configuration
- `/api/status` - Statut du bot et du cron
- `/api/stats` - Statistiques détaillées
- `/api/logs` - Récupération des logs
- `/api/run` - Exécution manuelle du bot
- `/api/config/*` - Gestion de la configuration
- `/api/reset` - Réinitialisation de la mémoire
- `/download/logs/<type>` - Téléchargement des fichiers de logs
- `/health` - Endpoint de health check Docker

### Persistance des Données
- `data/sent_ids.json` : Tableau des IDs Netflix déjà envoyés
- `data/users.json` : Identifiants utilisateurs avec mots de passe hachés
- Les volumes Docker montent ces répertoires pour la persistance

## Tâches Courantes

### Ajouter un Nouveau Pays
1. Via l'interface web : Paramètres > "Pays à Surveiller" > Ajouter le code pays
2. Via .env : Ajouter le code ISO à la variable `COUNTRIES`

### Modifier la Planification Cron
1. Via l'interface web : Paramètres > Modifier heure/minute
2. Manuel : Éditer `crontab.txt`, réinstaller avec `crontab /app/crontab.txt`

### Réinitialiser la Mémoire des Doublons
1. Via l'interface web : Tableau de bord > Bouton "Réinitialiser Mémoire"
2. Manuel : `echo '[]' > data/sent_ids.json`

### Tester le Webhook Discord
Exécuter le bot manuellement et vérifier les logs pour les réponses du webhook.

## Problèmes Connus

1. **Mode Debug Flask** : `app.run(debug=True)` en production - devrait être désactivé
2. **Chemins Codés en Dur** : Beaucoup de chemins supposent le répertoire `/app/` (Docker uniquement)
3. **Pas de Type Hints** : Le code Python manque d'annotations de types

## Identifiants par Défaut

- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `admin123`

**Important** : Changer le mot de passe immédiatement après la première connexion via l'interface web.

## Limites de Taux API

- **API UNOGS** : Vérifier les limites du plan RapidAPI
- **API TMDB** : 40 requêtes par 10 secondes
- **Webhooks Discord** : 30 requêtes par 60 secondes par webhook

## Référence des Chemins de Fichiers

Dans le conteneur Docker, tous les chemins sont relatifs à `/app/` :
- Script du bot : `/app/netflix_bot.py`
- Interface web : `/app/web_interface.py`
- Templates : `/app/templates/`
- Répertoire données : `/app/data/`
- Répertoire logs : `/app/logs/`
- Crontab : `/app/crontab.txt`

## Tests

Aucune suite de tests automatisés n'existe. Les tests sont effectués manuellement :
1. Exécuter le bot avec `python netflix_bot.py`
2. Vérifier les logs pour les erreurs
3. Vérifier que les messages Discord sont reçus
4. Utiliser l'interface web pour surveiller le statut

## Contribuer

1. Forker le dépôt
2. Créer une branche feature : `git checkout -b feature/nouvelle-feature`
3. Commiter les changements : `git commit -m 'Ajouter nouvelle feature'`
4. Pousser la branche : `git push origin feature/nouvelle-feature`
5. Ouvrir une Pull Request

## Dépendances

Depuis `requirements.txt` :
```
requests==2.31.0
python-dotenv==1.0.0
Flask==3.0.0
Werkzeug==3.0.1
```
