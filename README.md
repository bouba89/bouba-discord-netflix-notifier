# 🎬 Bouba Discord Netflix Notifier

Un bot Discord en Python déployable via Docker qui vous informe automatiquement des nouveautés Netflix directement sur votre serveur Discord, au jour le jour !

## ✨ Fonctionnalités

### 🤖 Bot Discord
- ✅ **Notifications automatiques** des nouveaux films et séries Netflix (sorties du jour)
- ✅ **Exécution planifiée** via cron (configurable depuis l'interface web)
- ✅ **Multi-pays** : surveillez Netflix dans plusieurs régions simultanément (🇫🇷 🇺🇸 🇨🇦 🇬🇧 🇩🇪 🇪🇸 🇮🇹 🇯🇵 etc.)
- ✅ **Anti-doublons** : ne notifie jamais deux fois le même contenu
- ✅ **Informations enrichies** via TMDB API (synopsis, note, poster, lien)
- ✅ **Logs détaillés** pour le debug et le monitoring

### 🌐 Interface Web Moderne
- ✅ **Dashboard Netflix-style** avec design professionnel rouge/noir
- ✅ **Authentification sécurisée** (mots de passe hashés avec bcrypt)
- ✅ **Monitoring en temps réel** : statistiques, logs, état du cron
- ✅ **Configuration interactive** :
  - 🌍 Modifier les pays surveillés avec drapeaux
  - ⏰ Changer l'horaire du cron sans toucher au code
  - 🔑 Gestion sécurisée des mots de passe
- ✅ **Interface responsive** compatible mobile/tablette/desktop
- ✅ **Logs en direct** avec auto-refresh (30s)
- ✅ **Exécution manuelle** du bot en un clic

### 📊 Statistiques Détaillées
- 📦 Total de contenus notifiés depuis le début
- 🆕 Nouveaux contenus du dernier run
- 🌍 Statistiques par pays avec drapeaux
- 📅 Dernière exécution (format français JJ/MM/AAAA HH:MM:SS)
- 📥 Téléchargement des logs (debug et cron)

### 🐳 Docker Optimisé
- ✅ **Image multi-stage Alpine** (~200MB au lieu de 800MB - **75% plus légère** !)
  - **Stage 1 (Builder)** : Compile les dépendances Python avec gcc/g++
  - **Stage 2 (Runtime)** : Image finale minimaliste sans outils de build
  - **Alpine Linux** : Distribution ultra-légère et sécurisée
- ✅ **Healthcheck intégré** : Vérification automatique toutes les 30s
- ✅ **Fuseau horaire Europe/Paris** configuré (CET/CEST)
- ✅ **Redémarrage automatique** en cas de crash
- ✅ **.dockerignore** : Exclut les fichiers inutiles du build

## 🗂️ Architecture du Projet

```
bouba-discord-netflix-notifier/
├── 📁 data/                    # Données persistantes
│   ├── sent_ids.json          # Mémoire anti-doublons
│   ├── users.json             # Base de données utilisateurs
│   └── api_responses_debug.json # Réponses API pour debug
├── 📁 logs/                    # Logs du bot
│   ├── cron.log               # Logs des exécutions cron
│   └── netflix_bot_debug.log  # Logs de debug détaillés
├── 📁 templates/               # Templates HTML Flask
│   ├── index.html             # Dashboard principal
│   ├── login.html             # Page de connexion
│   └── settings.html          # Page de configuration
├── 🐳 Dockerfile               # Image Docker multi-stage Alpine
├── 🐳 docker-compose.yml       # Configuration Docker Compose
├── 🐍 netflix_bot.py           # Script principal du bot
├── 🌐 web_interface.py         # Interface web Flask
├── 🚀 start.sh                 # Script de démarrage
├── 🔧 run_netflix.sh           # Script d'exécution pour cron
├── ⏰ crontab.txt              # Configuration du cron
├── 📦 requirements.txt         # Dépendances Python
├── 🚫 .dockerignore            # Fichiers exclus du build
├── 🔐 .env                     # Variables d'environnement (à créer)
└── 📖 README.md               # Documentation
```

## ⚙️ Prérequis

- 🐳 **Docker** installé ([Guide d'installation](https://docs.docker.com/get-docker/))
- 🐳 **Docker Compose** installé
- 🔑 **Token Discord** (Webhook pour les notifications)
- 🔑 **Clé API UNOGS** via [RapidAPI](https://rapidapi.com/unogs/api/unogs)
- 🔑 **Clé API TMDB** via [The Movie Database](https://www.themoviedb.org/settings/api)
- 🌐 **Connexion Internet**

## 🚀 Installation & Lancement

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier
```

### 2️⃣ Créer le fichier `.env`

```bash
touch .env
```

Remplissez le fichier `.env` avec vos clés API :

```env
# APIs Netflix & TMDB
RAPIDAPI_KEY=votre_cle_rapidapi_ici
TMDB_API_KEY=votre_cle_tmdb_ici

# Discord Webhook
DISCORD_WEBHOOK=https://discord.com/api/webhooks/votre_webhook_ici

# Pays à surveiller (codes ISO 2 lettres, séparés par des virgules)
COUNTRIES=FR,US,CA,GB

# Clé secrète Flask pour les sessions (générez-en une aléatoire)
FLASK_SECRET_KEY=votre_cle_secrete_super_aleatoire_ici

# Fuseau horaire (optionnel, par défaut Europe/Paris)
TZ=Europe/Paris
```

💡 **Générer une clé secrète Flask sécurisée :**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3️⃣ Construire et lancer le conteneur

```bash
# Build et démarrage
docker-compose up --build -d

# Vérifier que tout fonctionne
docker logs -f bouba_discord_netflix_notifier
```

### 4️⃣ Accéder à l'interface web

Ouvrez votre navigateur : **http://localhost:5000**

**Compte par défaut :**
- 👤 **Username :** `admin`
- 🔒 **Password :** `admin123`

⚠️ **IMPORTANT :** Changez le mot de passe immédiatement après la première connexion via le bouton "🔑 Mot de passe" !

## 🎮 Utilisation

### Interface Web

#### 1. **Dashboard** (`http://localhost:5000`)
   - 📊 Voir les statistiques en temps réel
   - 📜 Consulter les logs en direct (auto-refresh 30s)
   - ▶️ Exécuter le bot manuellement
   - 📥 Télécharger les logs (debug et cron)
   - 🗑️ Reset la mémoire anti-doublons

#### 2. **Paramètres** (`http://localhost:5000/settings`)
   - ⏰ Modifier l'horaire du cron (heure et minutes)
   - 🌍 Ajouter/retirer des pays surveillés
   - 💾 Sauvegarder la configuration en temps réel

#### 3. **Gestion du compte**
   - 🔑 Changer votre mot de passe
   - 🚪 Se déconnecter

### Commandes Docker

```bash
# Voir les logs en temps réel
docker logs -f bouba_discord_netflix_notifier

# Redémarrer le conteneur
docker-compose restart

# Arrêter le conteneur
docker-compose stop

# Démarrer le conteneur
docker-compose start

# Supprimer le conteneur
docker-compose down

# Entrer dans le conteneur
docker exec -it bouba_discord_netflix_notifier bash

# Exécuter le bot manuellement
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py

# Vérifier le cron
docker exec -it bouba_discord_netflix_notifier crontab -l

# Vérifier le fuseau horaire
docker exec -it bouba_discord_netflix_notifier date
```

## 🐳 Optimisation Docker

### Pourquoi Alpine Linux ?

Le projet utilise **Alpine Linux** comme base au lieu de Debian/Ubuntu pour plusieurs raisons :

| Critère | Alpine | Debian |
|---------|--------|--------|
| **Taille de base** | ~5 MB | ~124 MB |
| **Taille finale** | ~200 MB | ~800 MB |
| **Gain** | ✅ **75% plus léger** | ❌ 4x plus lourd |
| **Sécurité** | ✅ Surface d'attaque minimale | ⚠️ Plus de packages = plus de CVE |
| **Performance** | ✅ Démarrage rapide | ⚠️ Plus lent |

### Multi-Stage Build

Le Dockerfile utilise une **approche multi-stage** pour optimiser l'image :

#### **Stage 1 : Builder** (python:3.11-slim)
```dockerfile
FROM python:3.11-slim AS builder
# Installation des outils de compilation (gcc, g++)
# Création d'un environnement virtuel Python
# Installation de toutes les dépendances
```

**Avantages :**
- ✅ Accès à tous les outils nécessaires pour compiler
- ✅ Dépendances Python correctement buildées

**Inconvénient :**
- ❌ Image très lourde (~600 MB) → Non conservée !

#### **Stage 2 : Runtime** (python:3.11-alpine)
```dockerfile
FROM python:3.11-alpine
# Copie UNIQUEMENT l'environnement virtuel depuis le builder
# Installation des outils runtime (bash, curl, cron)
# Aucun outil de compilation
```

**Avantages :**
- ✅ Image finale ultra-légère (~200 MB)
- ✅ Pas d'outils de compilation = plus sécurisé
- ✅ Tous les packages Python fonctionnels

### Comparaison Avant/Après

**Avant optimisation :**
```bash
REPOSITORY              TAG       SIZE
bouba89/netflix-bot    latest    680 MB
```

**Après optimisation :**
```bash
REPOSITORY              TAG       SIZE
bouba89/netflix-bot    latest    180 MB  ✅ -73%
```

### Bénéfices concrets

1. **Déploiement plus rapide** : Moins de bande passante utilisée
2. **Moins d'espace disque** : Économie de 500 MB par instance
3. **Startup plus rapide** : Moins de couches à charger
4. **Plus sécurisé** : Moins de packages = moins de vulnérabilités
5. **Coûts réduits** : Moins de stockage cloud nécessaire

### Vérifier la taille de votre image

```bash
# Voir la taille de l'image
docker images | grep netflix-bot

# Voir l'historique des couches
docker history bouba89/netflix-bot:latest

# Comparer avec une image non-optimisée
docker images python:3.11-slim  # ~600 MB
docker images python:3.11-alpine  # ~50 MB
```

## 🔧 Configuration Avancée

### Modifier l'horaire du cron

**Via l'interface web (recommandé) :**
1. Allez sur `http://localhost:5000/settings`
2. Modifiez l'heure et les minutes
3. Cliquez sur "💾 Sauvegarder l'Horaire"

**Manuellement :**
```bash
# Éditer le crontab
docker exec -it bouba_discord_netflix_notifier nano /app/crontab.txt

# Réinstaller le crontab
docker exec -it bouba_discord_netflix_notifier crontab /app/crontab.txt

# Redémarrer cron
docker exec -it bouba_discord_netflix_notifier sh -c "pkill crond && crond -f -l 2 &"
```

### Ajouter/Retirer des pays

**Via l'interface web (recommandé) :**
1. Allez sur `http://localhost:5000/settings`
2. Section "Pays à Surveiller"
3. Ajoutez ou retirez des pays
4. Cliquez sur "💾 Sauvegarder les Pays"

**Codes pays disponibles :**
- 🇫🇷 FR (France)
- 🇺🇸 US (USA)
- 🇨🇦 CA (Canada)
- 🇬🇧 GB (Royaume-Uni)
- 🇩🇪 DE (Allemagne)
- 🇪🇸 ES (Espagne)
- 🇮🇹 IT (Italie)
- 🇯🇵 JP (Japon)
- 🇧🇷 BR (Brésil)
- 🇲🇽 MX (Mexique)
- 🇦🇺 AU (Australie)
- 🇮🇳 IN (Inde)
- Et bien d'autres... (codes ISO 3166-1 alpha-2)

### Réinitialiser la mémoire anti-doublons

Si vous souhaitez que le bot renvoie tous les contenus :

**Via l'interface web :**
- Dashboard → "🗑️ Reset Mémoire"

**Manuellement :**
```bash
docker exec -it bouba_discord_netflix_notifier bash -c "echo '[]' > /app/data/sent_ids.json"
```

### Modifier le filtre temporel

Par défaut, le bot cherche les sorties **du jour** (24h). Pour changer :

**Éditer `netflix_bot.py` ligne 41 :**
```python
# Pour chercher les 3 derniers jours
yesterday = today - timedelta(days=3)

# Pour chercher la dernière semaine
last_week = today - timedelta(days=7)
```

Puis redéployer :
```bash
docker cp netflix_bot.py bouba_discord_netflix_notifier:/app/
docker-compose restart
```

## 🔒 Sécurité

### Authentification
- ✅ Mots de passe hashés avec **bcrypt**
- ✅ Sessions sécurisées avec clé secrète Flask
- ✅ Protection de toutes les routes API avec `@login_required`
- ✅ Timeout de session configurable (24h par défaut avec "Se souvenir de moi")

### Bonnes pratiques
1. **Changez le mot de passe admin** après la première connexion
2. **Définissez une clé secrète Flask forte** dans `.env`
3. **Ne commitez jamais** le fichier `.env` sur GitHub
4. **Limitez l'accès** au port 5000 (pare-feu si exposé publiquement)
5. **Sauvegardez régulièrement** le dossier `/data`

## 🐛 Dépannage

### Le cron ne s'exécute pas

```bash
# Vérifier que crond tourne
docker exec -it bouba_discord_netflix_notifier ps aux | grep crond

# Vérifier le crontab
docker exec -it bouba_discord_netflix_notifier crontab -l

# Réinstaller le crontab
docker exec -it bouba_discord_netflix_notifier crontab /app/crontab.txt

# Redémarrer crond
docker exec -it bouba_discord_netflix_notifier sh -c "pkill crond && crond -f -l 2 &"
```

### Erreur "crontab file is missing newline"

Le fichier `crontab.txt` doit se terminer par une ligne vide :

```bash
echo "" >> crontab.txt
docker cp crontab.txt bouba_discord_netflix_notifier:/app/
docker exec -it bouba_discord_netflix_notifier crontab /app/crontab.txt
```

### L'interface web ne fonctionne pas

```bash
# Vérifier que Flask est installé
docker exec -it bouba_discord_netflix_notifier pip list | grep Flask

# Vérifier que les templates existent
docker exec -it bouba_discord_netflix_notifier ls -la /app/templates/

# Redémarrer le conteneur
docker-compose restart
```

### Les notifications Discord ne partent pas

1. Vérifiez que le webhook Discord est correct dans `.env`
2. Testez le webhook manuellement avec curl
3. Consultez les logs : `docker logs bouba_discord_netflix_notifier`
4. Vérifiez les logs détaillés : `docker exec -it bouba_discord_netflix_notifier cat /app/logs/netflix_bot_debug.log`

### Le bot ne trouve aucun contenu (0 nouveaux)

C'est **normal** ! Netflix n'ajoute pas de contenu tous les jours.
- Les **vendredis** sont les jours principaux de sortie (5-15 nouveautés)
- Les autres jours : 0-2 nouveautés maximum
- Pour tester : augmentez le filtre à 7 jours dans `netflix_bot.py`

### Le dashboard affiche "Inactif" mais le cron tourne

Vérifiez que `crond` est bien actif :
```bash
docker exec -it bouba_discord_netflix_notifier ps aux | grep crond
```

Si oui, c'est juste un problème d'affichage (corrigé dans la dernière version).

## 🔄 Mises à jour

```bash
# Récupérer les dernières modifications
git pull origin main

# Reconstruire l'image
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 Statistiques & Monitoring

### Fichiers de logs disponibles

- **`/logs/cron.log`** : Logs des exécutions automatiques
- **`/logs/netflix_bot_debug.log`** : Logs détaillés du bot avec debug
- **`/data/api_responses_debug.json`** : Réponses API brutes pour analyse

### Healthcheck Docker

Le conteneur vérifie automatiquement toutes les 30s que Flask répond :
```bash
# Voir le statut de santé
docker ps

# STATUS devrait afficher "healthy"
```

### Portainer (optionnel)

Si vous utilisez Portainer, vous verrez :
- ✅ Status: "healthy" (avec icône verte)
- ✅ Taille d'image réduite (~200MB)
- ✅ Métriques en temps réel

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. 🍴 Fork le projet
2. 🌿 Créez une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. 💾 Commit vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. 📤 Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. 🔀 Ouvrez une Pull Request

### Idées de contributions

- [ ] Support de Telegram/Slack en plus de Discord
- [ ] Filtres par genre/note/année
- [ ] Système de recommandations personnalisées
- [ ] Export des statistiques en CSV/JSON
- [ ] Notifications par email
- [ ] Support multi-utilisateurs avec rôles
- [ ] API REST complète
- [ ] Application mobile native
- [ ] Graphiques Chart.js pour les statistiques
- [ ] Watchlist partagée

## 📄 Licence

Ce projet est sous licence **Open Source**.

## 👨‍💻 Auteur

**Bouba89**
- GitHub: [@bouba89](https://github.com/bouba89)
- Projet: [bouba-discord-netflix-notifier](https://github.com/bouba89/bouba-discord-netflix-notifier)

## 🙏 Remerciements

- [UNOGS API](https://rapidapi.com/unogs/api/unogs) pour les données Netflix
- [TMDB API](https://www.themoviedb.org/) pour les informations détaillées
- [Discord](https://discord.com/) pour l'API de webhooks
- [Flask](https://flask.palletsprojects.com/) pour le framework web
- [Docker](https://www.docker.com/) pour la conteneurisation
- [Alpine Linux](https://alpinelinux.org/) pour l'image Docker légère

## 📞 Support

En cas de problème :
1. 📖 Consultez la section [Dépannage](#-dépannage)
2. 🐛 Ouvrez une [Issue](https://github.com/bouba89/bouba-discord-netflix-notifier/issues)
3. 💬 Consultez les discussions existantes

## 🎯 Roadmap

- [x] Bot Discord fonctionnel
- [x] Interface web moderne
- [x] Authentification sécurisée
- [x] Configuration interactive
- [x] Docker optimisé (Alpine multi-stage)
- [x] Support multi-pays avec drapeaux
- [ ] Graphiques de statistiques (Chart.js)
- [ ] Historique des notifications
- [ ] Filtres avancés (note, genre, année)
- [ ] Support Telegram/Slack
- [ ] Application mobile

---

🎬 **Bon monitoring Netflix !** 🍿

*Dernière mise à jour : 01/02/2026*
