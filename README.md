<div align="center">

# 🎬 Bouba Discord Netflix Notifier

### Votre assistant automatique pour les nouveautés Netflix sur Discord

[![Version](https://img.shields.io/badge/version-3.0-blue.svg?style=for-the-badge)](https://github.com/bouba89/bouba-discord-netflix-notifier/releases)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Open_Source-green?style=for-the-badge)](LICENSE)

[Fonctionnalités](#-fonctionnalités) • [Installation](#-installation-rapide) • [Configuration](#️-configuration) • [Documentation](#-documentation-complète) • [Contribution](#-contribution)

</div>

---

## 📖 À propos

**Bouba Discord Netflix Notifier** est un bot Discord intelligent qui surveille automatiquement les nouvelles sorties Netflix et vous notifie directement sur votre serveur Discord. Plus besoin de vérifier manuellement : recevez chaque jour les dernières nouveautés avec des informations détaillées et des visuels attractifs ! 🍿

### ✨ Nouveautés Version 3.0

- 🎯 **Système de logging avancé** - Suivi détaillé de toutes les opérations
- 🔒 **Sécurité renforcée** - Meilleure gestion des variables d'environnement
- 🚀 **Performance optimisée** - Dockerfile multi-stage amélioré
- 🛡️ **Healthcheck robuste** - Surveillance automatique de l'état du bot
- 📊 **Rapports enrichis** - Statistiques détaillées dans les logs
- 🖼️ **Support d'images** - Intégration de Pillow pour le traitement d'images
- 🔄 **Migration vers MDBList API** - API gratuite et plus fiable que UNOGS

### 🆕 Pourquoi MDBList ?

La version 3.0 utilise désormais **MDBList API** à la place de UNOGS/RapidAPI :

- ✅ **Gratuit** - 1000 requêtes par jour sans coût (clé API optionnelle)
- ✅ **Fiable** - Données agrégées de multiples sources (IMDb, Trakt, TMDb)
- ✅ **Complet** - Support de toutes les plateformes de streaming
- ✅ **Maintenu** - API activement développée et mise à jour
- ✅ **Listes publiques** - Utilise des listes communautaires pré-filtrées pour Netflix

### 🔍 Comment ça marche ?

Le bot v3.0 utilise une approche innovante basée sur des **listes publiques MDBList** :

1. **Source de données** : Listes publiques maintenues par la communauté
   - Films : `thebirdod/new-on-netflix-movies`
   - Séries : `thebirdod/new-on-netflix-shows`

2. **Détection des nouveautés** : Le bot récupère les items les plus récents de ces listes et vérifie s'ils ont déjà été envoyés (système anti-doublons)

3. **Enrichissement** :
   - **Sans clé MDBList** : Informations de base (titre, année, poster, synopsis en anglais)
   - **Avec clé MDBList** : Détails enrichis (notes IMDb/Trakt, genres détaillés, etc.)
   - **Avec clé TMDB** : Synopsis en **français** au lieu de l'anglais

4. **Couverture globale** : Les listes agrègent les sorties Netflix de tous les pays, vous garantissant une couverture maximale ! 🌍

---

## 🌟 Fonctionnalités

<table>
<tr>
<td width="50%">

### 🔔 Notifications Intelligentes
- Notifications quotidiennes automatiques à 9h
- Format Discord riche avec embeds colorés
- Informations détaillées (synopsis, note, durée)
- Liens directs vers Netflix

</td>
<td width="50%">

### 🎯 Filtrage Avancé
- Suivi par catégorie (Action, Comédie, etc.)
- Support multi-pays (FR, US, CA, GB, etc.)
- Système anti-doublons intelligent
- Personnalisation complète

</td>
</tr>
<tr>
<td width="50%">

### 🐳 Déploiement Facile
- Configuration Docker en 3 minutes
- Docker Compose prêt à l'emploi
- Volumes persistants pour les données
- Mises à jour automatiques

</td>
<td width="50%">

### 📊 Monitoring & Logs
- Système de logging complet
- Healthcheck intégré
- Statistiques détaillées
- Debugging facilité

</td>
</tr>
</table>

---

## 🚀 Installation Rapide

### Prérequis

Assurez-vous d'avoir installé :

- 🐳 [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- 🔧 [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0+)

Vous aurez également besoin de :

- 🔑 Clé API [MDBList](https://mdblist.com/preferences/) (optionnelle mais recommandée, gratuite, 1000 requêtes/jour)
- 🎬 Clé API [TMDB](https://www.themoviedb.org/settings/api) (optionnelle, pour les synopsis en français)
- 🪝 [Webhook Discord](https://support.discord.com/hc/en-us/articles/228383668) **(requis)**

### Installation en 3 étapes

#### 1️⃣ Cloner le projet

```bash
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier
```

#### 2️⃣ Configurer les variables d'environnement

Créez votre fichier `.env` :

```bash
cp .env.example .env
nano .env  # ou utilisez votre éditeur préféré
```

Remplissez avec vos clés API :

```env
# Discord Configuration (REQUIS)
DISCORD_WEBHOOK=https://discord.com/api/webhooks/VOTRE_WEBHOOK_URL

# API Keys (OPTIONNELLES mais recommandées)
MDBLIST_API_KEY=votre_cle_mdblist_ici
TMDB_API_KEY=votre_cle_tmdb_ici

# Configuration avancée (OPTIONNEL)
DAYS_BACK=7          # Nombre de jours à vérifier en arrière (défaut: 7)
LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR
```

**Note importante :** Le bot utilise des listes publiques MDBList qui agrègent les nouveautés Netflix de tous les pays. La variable `COUNTRIES` n'est plus utilisée dans la v3.0.

#### 3️⃣ Lancer le bot

```bash
docker-compose up -d
```

🎉 **C'est tout !** Votre bot est maintenant opérationnel et vous enverra des notifications chaque jour à 9h.

### Vérification de l'installation

```bash
# Vérifier que le container tourne
docker ps | grep bouba_discord_netflix_notifier

# Consulter les logs en temps réel
docker-compose logs -f

# Tester manuellement le bot
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py
```

---

## ⚙️ Configuration

### Configuration de base (.env)

| Variable | Description | Exemple | Requis |
|----------|-------------|---------|--------|
| `DISCORD_WEBHOOK` | URL du webhook Discord | `https://discord.com/api/webhooks/...` | ✅ |
| `MDBLIST_API_KEY` | Clé API MDBList (détails enrichis) | `abc123def456` | ⚠️ Recommandé |
| `TMDB_API_KEY` | Clé API TMDB (synopsis en français) | `xyz789uvw012` | ⚠️ Recommandé |
| `DAYS_BACK` | Nombre de jours à vérifier en arrière | `7` | ❌ |
| `LOG_LEVEL` | Niveau de logs | `INFO` | ❌ |

### Personnaliser l'heure d'exécution

Le bot s'exécute par défaut à 9h chaque jour. Pour modifier cela, éditez `crontab.txt` :

```bash
# Format: minute heure jour mois jour_semaine commande
0 9 * * * /usr/local/bin/python /app/netflix_bot.py >> /app/logs/netflix_bot.log 2>&1
```

**Exemples de configuration :**

| Configuration | Description | Crontab |
|---------------|-------------|---------|
| Tous les jours à 12h | Midi | `0 12 * * *` |
| Deux fois par jour | 9h et 21h | `0 9,21 * * *` |
| Tous les lundis à 9h | Hebdomadaire | `0 9 * * 1` |
| Toutes les 6 heures | Fréquent | `0 */6 * * *` |

### Ajuster la période de vérification

Le bot vérifie par défaut les nouveautés des **7 derniers jours**. Pour modifier cette période, ajoutez dans votre `.env` :

```env
# Vérifier les 14 derniers jours
DAYS_BACK=14

# Vérifier seulement les 3 derniers jours (moins de résultats)
DAYS_BACK=3
```

**Note :** Plus la période est longue, plus le bot vérifiera d'items dans les listes MDBList. La valeur recommandée est entre 7 et 14 jours pour un bon équilibre entre couverture et performance.

### À propos du filtrage par pays

**Important :** La version 3.0 utilise des listes publiques MDBList qui agrègent automatiquement les nouveautés Netflix de **tous les pays**. Le bot vous notifiera donc des sorties globales Netflix, sans possibilité de filtrage par pays spécifique.

Cette approche garantit que vous ne manquerez aucune nouveauté, quelle que soit votre région ! 🌍

---

## 📂 Architecture du Projet

```
bouba-discord-netflix-notifier/
├── 📁 data/                      # Données persistantes
│   └── sent_ids.json             # Anti-doublons
├── 📁 logs/                      # Fichiers de logs
│   └── netflix_bot.log           # Logs du bot
├── 📄 .dockerignore              # Exclusions Docker
├── 📄 .env                       # Variables d'environnement (à créer)
├── 📄 .env.example               # Exemple de configuration
├── 📄 .gitignore                 # Exclusions Git
├── ⏰ crontab.txt                # Configuration cron
├── 🐳 docker-compose.yml         # Orchestration Docker
├── 🐳 Dockerfile                 # Image Docker optimisée
├── 🐍 netflix_bot.py             # Script principal
├── 📦 requirements.txt           # Dépendances Python
├── 🚀 start.sh                   # Script d'initialisation
├── 📖 README.md                  # Documentation
└── 📜 LICENSE                    # Licence open-source
```

---

## 🛠️ Commandes Utiles

### Gestion du bot

```bash
# Démarrer le bot
docker-compose up -d

# Arrêter le bot
docker-compose down

# Redémarrer le bot
docker-compose restart

# Voir les logs en temps réel
docker-compose logs -f

# Voir les dernières 100 lignes de logs
docker-compose logs --tail=100
```

### Maintenance

```bash
# Rebuild complet (après modifications du code)
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Nettoyer les anciennes images Docker
docker system prune -a

# Sauvegarder les données
cp -r data/ data_backup_$(date +%Y%m%d)/

# Restaurer les données
cp -r data_backup_YYYYMMDD/ data/
```

### Monitoring

```bash
# Vérifier le statut du healthcheck
docker inspect bouba_discord_netflix_notifier | grep -A 10 Health

# Voir les statistiques du container
docker stats bouba_discord_netflix_notifier --no-stream

# Vérifier l'utilisation du disque
docker system df

# Accéder au shell du container
docker exec -it bouba_discord_netflix_notifier /bin/bash
```

### Debugging

```bash
# Exécuter le bot manuellement
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py

# Vérifier les variables d'environnement
docker exec -it bouba_discord_netflix_notifier printenv | grep -E "MDBLIST|TMDB|DISCORD"

# Lire les logs complets
docker exec -it bouba_discord_netflix_notifier cat /app/logs/netflix_bot.log

# Vérifier que les dépendances sont installées
docker exec -it bouba_discord_netflix_notifier pip list
```

---

## 📊 Système de Logging

### Nouveauté Version 3.0 : Logs Avancés

Le bot dispose maintenant d'un système de logging complet qui enregistre :

- ✅ Démarrage et initialisation
- 🔍 Recherche de nouveaux contenus
- 📤 Envoi des notifications
- ❌ Erreurs et exceptions
- 📈 Statistiques d'exécution

### Structure des logs

```
[2026-02-07 09:00:00] INFO - Bot démarré
[2026-02-07 09:00:01] INFO - Recherche des nouveautés pour: FR, US, CA
[2026-02-07 09:00:05] INFO - 12 nouveaux contenus trouvés
[2026-02-07 09:00:06] INFO - Envoi notification: Stranger Things S5
[2026-02-07 09:00:10] INFO - Toutes les notifications envoyées avec succès
[2026-02-07 09:00:10] INFO - Exécution terminée - Durée: 10s
```

### Niveaux de logs

| Niveau | Description | Utilisation |
|--------|-------------|-------------|
| `DEBUG` | Informations détaillées | Développement et debugging |
| `INFO` | Informations générales | Utilisation normale (défaut) |
| `WARNING` | Avertissements | Problèmes non-bloquants |
| `ERROR` | Erreurs | Problèmes nécessitant attention |

Modifiez le niveau dans `.env` :

```env
LOG_LEVEL=DEBUG  # Pour plus de détails
```

---

## 🛡️ Sécurité

### Bonnes pratiques implémentées

- ✅ Le fichier `.env` n'est **jamais** copié dans l'image Docker
- ✅ Les secrets sont passés via variables d'environnement au runtime
- ✅ Image Docker optimisée avec multi-stage build
- ✅ Mise à jour automatique des packages système
- ✅ Permissions minimales dans le container
- ✅ Pas de secrets hardcodés dans le code

### Recommandations

1. **Ne jamais commiter votre `.env`** : Le fichier est déjà dans `.gitignore`
2. **Régénérer vos clés API** si elles sont exposées
3. **Limiter les permissions** du webhook Discord
4. **Sauvegarder régulièrement** le fichier `data/sent_ids.json`
5. **Surveiller les logs** pour détecter les comportements anormaux

---

## 📈 Monitoring & Healthcheck

### Healthcheck intégré

Le bot inclut un healthcheck qui vérifie toutes les heures :

- ✅ Existence du fichier de données (`sent_ids.json`)
- ✅ Bon fonctionnement du container
- ✅ Accessibilité des répertoires

**Status du healthcheck :**

```bash
docker ps
```

| Status | Signification | Action |
|--------|---------------|--------|
| `healthy` ✅ | Tout fonctionne | Aucune |
| `unhealthy` ❌ | Problème détecté | Vérifier les logs |
| `starting` ⏳ | Démarrage | Attendre 30s |

### Surveillance des logs

```bash
# Suivre les logs en temps réel
tail -f logs/netflix_bot.log

# Rechercher des erreurs
grep "ERROR" logs/netflix_bot.log

# Compter les notifications envoyées aujourd'hui
grep "$(date +%Y-%m-%d)" logs/netflix_bot.log | grep "notification" | wc -l
```

---

## 🐛 Dépannage

### Problèmes courants

<details>
<summary><b>❌ Le bot ne démarre pas</b></summary>

**Solution :**

```bash
# 1. Vérifier les logs
docker-compose logs

# 2. Vérifier les variables d'environnement
docker exec -it bouba_discord_netflix_notifier printenv | grep -E "RAPIDAPI|TMDB|DISCORD"

# 3. Vérifier les permissions
ls -la data/ logs/

# 4. Rebuild complet
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
</details>

<details>
<summary><b>🔕 Les notifications ne s'affichent pas</b></summary>

**Solution :**

1. Vérifiez que votre webhook Discord est valide :
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"Test"}' \
  VOTRE_WEBHOOK_URL
```

2. Testez le bot manuellement :
```bash
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py
```

3. Vérifiez les logs :
```bash
docker-compose logs -f
```
</details>

<details>
<summary><b>🏥 Le container est "unhealthy"</b></summary>

**Solution :**

```bash
# Vérifier si le fichier de données existe
docker exec -it bouba_discord_netflix_notifier ls -la /app/data/

# Recréer le fichier si nécessaire
docker exec -it bouba_discord_netflix_notifier touch /app/data/sent_ids.json
docker exec -it bouba_discord_netflix_notifier echo "[]" > /app/data/sent_ids.json

# Redémarrer
docker-compose restart
```
</details>

<details>
<summary><b>🔑 Erreur "Invalid API Key"</b></summary>

**Solution :**

1. Vérifiez que vos clés API sont correctes dans `.env`
2. Assurez-vous qu'il n'y a pas d'espaces avant/après les clés
3. Vérifiez que les clés n'ont pas expiré
4. Redémarrez après modification du `.env` :
```bash
docker-compose restart
```
</details>

<details>
<summary><b>💾 Erreur "No space left on device"</b></summary>

**Solution :**

```bash
# Nettoyer Docker
docker system prune -a

# Nettoyer les logs anciens
find logs/ -name "*.log" -mtime +30 -delete

# Vérifier l'espace disque
df -h
```
</details>

### Obtenir de l'aide

Si vous rencontrez un problème non résolu :

1. 📖 Consultez les [Issues GitHub](https://github.com/bouba89/bouba-discord-netflix-notifier/issues)
2. 🔍 Recherchez si le problème a déjà été signalé
3. 🆕 Ouvrez une nouvelle issue avec :
   - Description détaillée du problème
   - Logs complets (`docker-compose logs`)
   - Version de Docker et de votre OS
   - Fichier `.env` (sans les clés API !)

---

## 🗺️ Roadmap

### Version 3.1 (Prochainement)

- [ ] Interface web pour configuration
- [ ] Support de multiples webhooks Discord
- [ ] Filtrage par genre plus fin
- [ ] Notifications personnalisées par utilisateur
- [ ] Statistiques mensuelles

### Version 4.0 (Futur)

- [ ] Support d'autres plateformes (Amazon Prime, Disney+)
- [ ] Recommandations basées sur l'historique
- [ ] Intégration avec Plex/Jellyfin
- [ ] Application mobile companion
- [ ] API REST pour intégrations externes

### Proposer une fonctionnalité

Vous avez une idée ? [Ouvrez une issue](https://github.com/bouba89/bouba-discord-netflix-notifier/issues/new) avec le tag `enhancement` !

---

## ❓ FAQ

<details>
<summary><b>Ai-je vraiment besoin des clés API MDBList et TMDB ?</b></summary>

**Non, elles sont optionnelles !** Le bot fonctionne sans elles, mais avec des fonctionnalités réduites :

**Sans clés API :**
- ✅ Notifications des nouveautés Netflix
- ✅ Titre, année, poster
- ⚠️ Synopsis en anglais uniquement
- ❌ Pas de notes détaillées (IMDb, Trakt)
- ❌ Pas de genres détaillés

**Avec clé MDBList :**
- ✅ Toutes les fonctionnalités ci-dessus
- ✅ Notes de multiples sources (IMDb, Trakt, etc.)
- ✅ Genres détaillés
- ✅ Informations enrichies

**Avec clé TMDB :**
- ✅ **Synopsis en français** au lieu de l'anglais
- ✅ Informations plus complètes

**Recommandation :** Utilisez au minimum la clé TMDB pour avoir les synopsis en français !
</details>

<details>
<summary><b>Comment obtenir ma clé API MDBList ?</b></summary>

1. Créez un compte gratuit sur [mdblist.com](https://mdblist.com/)
2. Allez dans vos [préférences](https://mdblist.com/preferences/)
3. Scrollez jusqu'à la section "API"
4. Copiez votre clé API (elle sera générée automatiquement)
5. Collez-la dans votre fichier `.env`

La clé gratuite offre **1000 requêtes par jour**, largement suffisant pour un bot quotidien !
</details>

<details>
<summary><b>Le bot peut-il notifier plusieurs fois par jour ?</b></summary>

Oui ! Modifiez simplement le fichier `crontab.txt` pour exécuter le bot plusieurs fois :

```bash
# Deux fois par jour (9h et 21h)
0 9,21 * * * /usr/local/bin/python /app/netflix_bot.py >> /app/logs/netflix_bot.log 2>&1
```
</details>

<details>
<summary><b>Que se passe-t-il si je dépasse les 1000 requêtes/jour ?</b></summary>

MDBList offre 1000 requêtes gratuites par jour. Pour un bot qui s'exécute une fois par jour :
- Chaque film/série = 1-2 requêtes
- Avec 3 pays surveillés, vous consommez ~50-100 requêtes maximum par jour
- Largement sous la limite !

Si vous dépassez la limite (peu probable), le bot attendra simplement le lendemain pour reprendre.
</details>

<details>
<summary><b>Puis-je filtrer par pays spécifique (uniquement France, US, etc.) ?</b></summary>

Non, la version 3.0 utilise des listes globales qui agrègent toutes les sorties Netflix internationales. Cette approche présente des avantages :

**Avantages :**
- ✅ Vous ne manquez aucune nouveauté
- ✅ Découvrez des contenus de toutes les régions
- ✅ Plus simple et plus fiable que les filtres par pays

**Note :** Netflix rend souvent disponibles les mêmes contenus dans plusieurs pays simultanément, donc vous verrez principalement des sorties pertinentes pour votre région.

Si le filtrage par pays est essentiel pour vous, ouvrez une [issue GitHub](https://github.com/bouba89/bouba-discord-netflix-notifier/issues) pour discuter d'une implémentation future !
</details>

<details>
<summary><b>Puis-je utiliser plusieurs webhooks Discord ?</b></summary>

Actuellement, seul un webhook est supporté. Le support multi-webhook est prévu pour la version 3.1.
</details>

<details>
<summary><b>Comment filtrer par genre spécifique ?</b></summary>

Cette fonctionnalité n'est pas encore disponible mais est prévue dans la roadmap. Actuellement, tous les genres sont inclus.
</details>

<details>
<summary><b>Le bot consomme-t-il beaucoup de ressources ?</b></summary>

Non ! Le bot est très léger :
- RAM : ~50-100 MB
- CPU : Pic de quelques secondes lors de l'exécution
- Stockage : ~100 MB (image + logs)
</details>

<details>
<summary><b>Puis-je héberger le bot sur un Raspberry Pi ?</b></summary>

Oui ! Le bot fonctionne parfaitement sur Raspberry Pi 3/4 avec Docker installé. Assurez-vous d'avoir au moins 1 GB de RAM disponible.
</details>

<details>
<summary><b>Comment contribuer au projet ?</b></summary>

Consultez la section [Contribution](#-contribution) ci-dessous !
</details>

---

## 🤝 Contribution

Les contributions sont les bienvenues et grandement appréciées ! 🎉

### Comment contribuer

1. 🍴 **Fork** le projet
2. 🌿 Créez une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/ma-super-feature
   ```
3. ✨ Committez vos changements :
   ```bash
   git commit -m "✨ Ajout de ma super feature"
   ```
4. 📤 Pushez vers la branche :
   ```bash
   git push origin feature/ma-super-feature
   ```
5. 🔃 Ouvrez une **Pull Request**

### Convention de commits

Utilisez des emojis pour rendre les commits plus clairs :

- ✨ `:sparkles:` - Nouvelle fonctionnalité
- 🐛 `:bug:` - Correction de bug
- 📝 `:memo:` - Documentation
- 🎨 `:art:` - Amélioration du style/format
- ⚡ `:zap:` - Amélioration des performances
- 🔒 `:lock:` - Sécurité
- ♻️ `:recycle:` - Refactoring

### Guidelines

- Suivez le style de code existant
- Ajoutez des tests si possible
- Mettez à jour la documentation
- Vérifiez que le bot fonctionne avant de soumettre

---

## 📄 Licence

Ce projet est sous licence **Open Source**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

Vous êtes libre de :

- ✅ Utiliser le code pour des projets personnels ou commerciaux
- ✅ Modifier le code selon vos besoins
- ✅ Distribuer votre version modifiée
- ✅ Contribuer au projet

---

## 👤 Auteur

**bouba89**

- 🐙 GitHub: [@bouba89](https://github.com/bouba89)
- 📦 Projet: [bouba-discord-netflix-notifier](https://github.com/bouba89/bouba-discord-netflix-notifier)

---

## 🙏 Remerciements

Un grand merci à :

- 🎬 [MDBList API](https://mdblist.com/) - Agrégation de données multi-sources pour Netflix
- 🎥 [TMDB API](https://www.themoviedb.org/) - Informations détaillées sur les films et séries
- 🐳 [Docker Community](https://www.docker.com/community/) - Pour les bonnes pratiques et le support
- 💬 [Discord](https://discord.com/) - Pour l'API webhook
- 🐍 [Python Community](https://www.python.org/community/) - Pour les excellentes bibliothèques

---

## 📞 Support

Besoin d'aide ? Plusieurs options s'offrent à vous :

- 📖 Consultez la [documentation complète](#-documentation-complète)
- 🐛 Signalez un bug via les [Issues](https://github.com/bouba89/bouba-discord-netflix-notifier/issues)
- 💬 Posez vos questions dans les [Discussions](https://github.com/bouba89/bouba-discord-netflix-notifier/discussions)
- ⭐ Donnez une étoile si le projet vous plaît !

---

<div align="center">

### ⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !

**Fait avec ❤️ par [bouba89](https://github.com/bouba89)**

[![GitHub stars](https://img.shields.io/github/stars/bouba89/bouba-discord-netflix-notifier?style=social)](https://github.com/bouba89/bouba-discord-netflix-notifier/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/bouba89/bouba-discord-netflix-notifier?style=social)](https://github.com/bouba89/bouba-discord-netflix-notifier/network/members)

</div>
