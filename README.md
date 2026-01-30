# 📦 Guide d'installation - Version améliorée

## 🎯 Objectif

Cette version améliorée corrige le problème des statistiques par pays qui restaient à 0, et ajoute de nombreuses fonctionnalités au dashboard.

## ✨ Nouveautés

### 🔧 Corrections
- ✅ **Statistiques par pays fonctionnelles** - Les compteurs FR, US, CA, etc. s'affichent correctement
- ✅ **Système de mémoire enrichi** - Stockage des métadonnées complètes (titre, pays, type, note, date)
- ✅ **Meilleur parsing des logs** - Extraction fiable des informations

### 🎨 Améliorations interface
- ✅ **Graphiques Chart.js** - Visualisations par pays, type et évolution temporelle
- ✅ **Notifications récentes** - Affichage des 15 derniers contenus envoyés
- ✅ **Design modernisé** - Interface sombre Netflix-style
- ✅ **Export CSV** - Téléchargement des statistiques
- ✅ **Endpoint de debug** - `/api/debug/memory` pour diagnostiquer
- ✅ **Health check** - `/api/health` pour vérifier le système

## 📋 Fichiers fournis

```
improved_bot/
├── netflix_bot.py          # Bot principal amélioré
├── web_interface.py        # Interface Flask améliorée
├── templates/
│   └── index.html         # Dashboard avec graphiques
└── migrate.py             # Script de migration
```

## 🚀 Installation

### Méthode 1 : Remplacement direct (RECOMMANDÉ)

```bash
# 1. Se connecter au serveur où tourne le bot
ssh user@votre-serveur

# 2. Arrêter le conteneur
docker-compose down

# 3. Créer une sauvegarde
cp netflix_bot.py netflix_bot.py.backup
cp web_interface.py web_interface.py.backup
cp templates/index.html templates/index.html.backup
cp data/sent_ids.json data/sent_ids.json.backup

# 4. Remplacer les fichiers
# Copier les nouveaux fichiers depuis votre machine locale
# Utiliser scp, sftp, ou votre méthode préférée

# 5. Créer le dossier templates s'il n'existe pas
mkdir -p templates

# 6. Rendre les scripts exécutables
chmod +x netflix_bot.py
chmod +x web_interface.py
chmod +x migrate.py

# 7. Migrer les données
docker-compose run --rm netflix-notifier python /app/migrate.py

# 8. Redémarrer
docker-compose up --build -d
```

### Méthode 2 : Mise à jour via Git

```bash
# 1. Sauvegarder l'ancien format
cp data/sent_ids.json data/sent_ids.json.backup

# 2. Pull les nouveaux fichiers
git pull origin main

# 3. Rebuild et restart
docker-compose up --build -d

# 4. Migrer les données
docker exec -it netflix_bot python /app/migrate.py
```

## 🔄 Migration des données

Le script `migrate.py` convertit automatiquement l'ancien format vers le nouveau :

**Avant (liste simple) :**
```json
[
  "netflix_id_12345",
  "netflix_id_67890"
]
```

**Après (structure enrichie) :**
```json
{
  "sent_items": [
    {
      "id": "netflix_id_12345",
      "title": "Stranger Things",
      "country": "FR",
      "type": "series",
      "sent_date": "2026-01-30T09:00:00",
      "tmdb_rating": 8.5
    }
  ],
  "stats": {
    "total": 1,
    "by_country": {"FR": 1},
    "by_type": {"series": 1}
  }
}
```

### Exécuter la migration manuellement

```bash
# Dans le conteneur
docker exec -it netflix_bot python /app/migrate.py

# Ou directement
docker-compose run --rm netflix-notifier python /app/migrate.py
```

## 🧪 Vérification

### 1. Vérifier que le bot fonctionne

```bash
# Tester l'exécution
docker exec -it netflix_bot python /app/netflix_bot.py

# Vérifier les logs
docker logs -f netflix_bot
```

### 2. Vérifier l'interface web

```bash
# Accéder au dashboard
open http://localhost:5000

# Vérifier les endpoints
curl http://localhost:5000/api/status | jq .
curl http://localhost:5000/api/stats | jq .by_country
curl http://localhost:5000/api/debug/memory | jq .
```

### 3. Vérifier les statistiques

Dans l'interface web, les statistiques par pays devraient maintenant s'afficher :

```
🌍 Statistiques par Pays
🇫🇷 FR: 45  🇺🇸 US: 32  🇨🇦 CA: 18
```

## 📊 Nouveaux endpoints API

| Endpoint | Description |
|----------|-------------|
| `/api/health` | Santé du système |
| `/api/debug/memory` | Debug du fichier mémoire |
| `/api/export/csv` | Export CSV des données |
| `/download/logs/memory` | Télécharger sent_ids.json |

### Exemples d'utilisation

```bash
# Vérifier la santé
curl http://localhost:5000/api/health

# Debug mémoire
curl http://localhost:5000/api/debug/memory | jq .

# Exporter en CSV
curl http://localhost:5000/api/export/csv > stats.csv
```

## 🐛 Troubleshooting

### Les stats par pays sont toujours à 0

**Cause :** Migration non effectuée ou bot pas encore exécuté avec la nouvelle version

**Solution :**
```bash
# 1. Vérifier le format du fichier
docker exec -it netflix_bot cat /app/data/sent_ids.json | jq .

# 2. Vérifier la structure
curl http://localhost:5000/api/debug/memory | jq .structure

# 3. Re-migrer si nécessaire
docker exec -it netflix_bot python /app/migrate.py

# 4. Exécuter le bot une fois
docker exec -it netflix_bot python /app/netflix_bot.py
```

### L'interface ne charge pas les graphiques

**Cause :** Chart.js ou Bootstrap non chargés

**Solution :**
```bash
# Vérifier les erreurs dans la console du navigateur (F12)
# Recharger la page avec Ctrl+F5

# Vérifier que le template est bien à jour
docker exec -it netflix_bot cat /app/templates/index.html | grep chart.js
```

### Erreur "Structure invalide"

**Cause :** Fichier sent_ids.json corrompu

**Solution :**
```bash
# Restaurer depuis la sauvegarde
docker exec -it netflix_bot cp /app/data/sent_ids.json.backup /app/data/sent_ids.json

# Ou réinitialiser
docker exec -it netflix_bot bash -c 'echo "{\"sent_items\":[],\"stats\":{\"total\":0,\"by_country\":{},\"by_type\":{}}}" > /app/data/sent_ids.json'
```

## 📝 Compatibilité

- ✅ Compatible avec Docker et Docker Compose
- ✅ Rétrocompatible avec l'ancien format (migration automatique)
- ✅ Fonctionne avec Python 3.11+
- ✅ Compatible avec tous les navigateurs modernes

## 🔐 Sécurité

Les clés API restent masquées dans l'interface :
```
RAPIDAPI_KEY: sk_abc1234***
TMDB_API_KEY: abc123def4***
```

## 📞 Support

Si vous rencontrez des problèmes :

1. Consultez les logs : `docker logs netflix_bot`
2. Vérifiez la structure : `curl http://localhost:5000/api/debug/memory`
3. Testez manuellement : `docker exec -it netflix_bot python /app/netflix_bot.py`
4. Ouvrez une issue sur GitHub avec les logs

## 🎉 Résultat attendu

Après l'installation, vous devriez voir :

- ✅ Statistiques par pays avec les bons chiffres
- ✅ Graphiques interactifs (barres, donut, ligne)
- ✅ Liste des dernières notifications
- ✅ Export CSV fonctionnel
- ✅ Design modernisé Netflix-style

Profitez de votre nouveau dashboard ! 🚀
