#!/usr/bin/env python3
"""
🎬 Bouba Discord Netflix Notifier - Version 3.0 (API Complète)
Bot Discord pour notifier des nouvelles sorties Netflix
Utilise l'API officielle mdblist.com avec tous les endpoints
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration du logging
LOG_DIR = Path("/app/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'netflix_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MEMORY_FILE = Path("/app/data/sent_ids.json")
DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Variables d'environnement
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
MDBLIST_API_KEY = os.getenv("MDBLIST_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
COUNTRIES = os.getenv("COUNTRIES", "FR").split(",")
DAYS_BACK = int(os.getenv("DAYS_BACK", "7"))  # Jours à vérifier en arrière

# URLs de base
MDBLIST_API_BASE = "https://api.mdblist.com"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# Configuration des listes mdblist
NETFLIX_LISTS = {
    "movies": {
        "username": "thebirdod",
        "listname": "new-on-netflix-movies"
    },
    "shows": {
        "username": "thebirdod", 
        "listname": "new-on-netflix-shows"
    }
}


class NetflixNotifier:
    """Classe principale pour gérer les notifications Netflix"""
    
    def __init__(self):
        self.sent_ids = self.load_sent_ids()
        self.api_headers = {}
        if MDBLIST_API_KEY:
            self.api_headers = {"apikey": MDBLIST_API_KEY}
        
    def load_sent_ids(self):
        """Charge les IDs déjà envoyés"""
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                    logger.info(f"✅ Chargé {len(data)} IDs depuis le fichier de mémoire")
                    return data
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement de {MEMORY_FILE}: {e}")
                return {}
        return {}
    
    def save_sent_ids(self):
        """Sauvegarde les IDs envoyés"""
        try:
            with open(MEMORY_FILE, 'w') as f:
                json.dump(self.sent_ids, f, indent=2)
            logger.info(f"✅ Sauvegardé {len(self.sent_ids)} IDs")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde: {e}")
    
    def is_already_sent(self, item_id):
        """Vérifie si un item a déjà été envoyé"""
        return str(item_id) in self.sent_ids
    
    def mark_as_sent(self, item_id, title):
        """Marque un item comme envoyé"""
        self.sent_ids[str(item_id)] = {
            "title": title,
            "sent_at": datetime.now().isoformat()
        }
    
    def get_french_overview(self, tmdb_id, media_type):
        """
        Récupère le synopsis en français depuis TMDB
        """
        if not TMDB_API_KEY or not tmdb_id:
            return None
        
        try:
            # Déterminer le type (movie ou tv)
            tmdb_type = "tv" if media_type == "show" else "movie"
            url = f"{TMDB_BASE_URL}/{tmdb_type}/{tmdb_id}"
            params = {
                "api_key": TMDB_API_KEY,
                "language": "fr-FR"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Récupérer le synopsis français
            overview = data.get("overview", "")
            if overview:
                logger.debug(f"✅ Synopsis français récupéré pour TMDB ID {tmdb_id}")
                return overview
            
            logger.debug(f"⚠️ Pas de synopsis français pour TMDB ID {tmdb_id}")
            return None
            
        except Exception as e:
            logger.debug(f"❌ Erreur récupération synopsis français: {e}")
            return None
    
    def get_netflix_releases(self, media_type="movie"):
        """
        Récupère les nouveautés Netflix en détectant les nouveaux ajouts à la liste
        (car les listes n'ont pas de dates de sortie précises, juste l'année)
        """
        list_info = NETFLIX_LISTS.get("movies" if media_type == "movie" else "shows")
        if not list_info:
            logger.error(f"❌ Type de média inconnu: {media_type}")
            return []
        
        username = list_info["username"]
        listname = list_info["listname"]
        
        try:
            # Utiliser l'export JSON public
            url = f"https://mdblist.com/lists/{username}/{listname}/json"
            
            logger.info(f"🔍 Récupération de la liste Netflix ({media_type}s)...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # L'export JSON retourne directement une liste
            all_items = response.json()
            
            if not isinstance(all_items, list):
                logger.error(f"❌ Format inattendu: {type(all_items)}")
                return []
            
            logger.info(f"📊 Total items dans la liste: {len(all_items)}")
            
            # Ces listes sont déjà filtrées pour les nouveautés
            # On prend les N premiers items (les plus récents)
            # Ajusté selon DAYS_BACK : plus de jours = plus d'items à vérifier
            max_items = min(DAYS_BACK * 10, 50)  # Max 50 items
            recent_items = all_items[:max_items]
            
            logger.info(f"✅ Examen des {len(recent_items)} items les plus récents (liste pré-filtrée)")
            
            return recent_items
            
        except Exception as e:
            logger.error(f"❌ Erreur API: {e}")
            return []
    
    def get_media_details(self, imdb_id=None, tmdb_id=None, media_type="movie"):
        """
        Récupère les détails d'un media via l'API mdblist
        Retourne des infos complètes avec notes, streaming, etc.
        """
        if not MDBLIST_API_KEY:
            return None
        
        if not imdb_id and not tmdb_id:
            return None
        
        try:
            # Construction de l'URL
            provider = "imdb" if imdb_id else "tmdb"
            media_id = imdb_id if imdb_id else tmdb_id
            url = f"{MDBLIST_API_BASE}/{provider}/{media_type}/{media_id}"
            
            params = {
                "apikey": MDBLIST_API_KEY,
                "append_to_response": "keyword,review"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.debug(f"Erreur détails media: {e}")
            return None
    
    def create_discord_embed(self, item):
        """
        Crée un embed Discord enrichi avec toutes les données disponibles
        """
        # Extraction des données de base
        title = item.get("title", "Titre inconnu")
        year = item.get("release_year", "N/A")
        imdb_id = item.get("imdb_id", "")
        tmdb_id = item.get("id") or item.get("tmdb_id")
        media_type = item.get("mediatype", "movie")
        
        # Différencier films et séries
        is_movie = media_type == "movie"
        emoji = "🎬" if is_movie else "📺"
        color = 0xE50914 if is_movie else 0x0099FF  # Rouge pour films, Bleu pour séries
        type_badge = "Film" if is_movie else "Série"
        
        # Construction de l'embed
        embed = {
            "title": f"{emoji} {title} ({year})",
            "color": color,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Description - Essayer d'abord en français via TMDB
        description = None
        
        # 1. Essayer de récupérer le synopsis français via TMDB
        if TMDB_API_KEY and tmdb_id:
            description = self.get_french_overview(tmdb_id, media_type)
        
        # 2. Sinon utiliser la description mdblist (souvent en anglais)
        if not description:
            description = item.get("description", "")
        
        # Ajouter le badge type au début de la description
        description_prefix = f"**[{type_badge}]**\n\n"
        
        # Limiter la longueur
        if description:
            if len(description) > 280:  # Réduit pour laisser place au badge
                description = description[:277] + "..."
            embed["description"] = description_prefix + description
        else:
            embed["description"] = description_prefix
        
        # Poster (si disponible) - IMAGE LARGE au lieu de thumbnail
        poster = item.get("poster")
        if poster:
            embed["image"] = {"url": poster}  # Grande image au lieu de thumbnail
        
        # Fields
        fields = []
        
        # Ratings (si disponibles dans l'item)
        ratings = item.get("ratings", [])
        if ratings:
            rating_text = []
            for rating in ratings[:3]:  # Top 3 ratings
                source = rating.get("source", "").upper()
                score = rating.get("score")
                if score:
                    rating_text.append(f"{source}: {score}/100")
            
            if rating_text:
                fields.append({
                    "name": "⭐ Notes",
                    "value": "\n".join(rating_text),
                    "inline": True
                })
        
        # Genres (si disponibles)
        genres = item.get("genres", [])
        if genres:
            # Les genres peuvent être des strings ou des dicts {"name": "Action"}
            genre_names = []
            for g in genres[:5]:
                if isinstance(g, dict):
                    genre_names.append(g.get("name", ""))
                elif isinstance(g, str):
                    genre_names.append(g)
            
            genre_text = ", ".join([g for g in genre_names if g])
            if genre_text:
                fields.append({
                    "name": "🎭 Genres",
                    "value": genre_text,
                    "inline": True
                })
        
        # Watch providers (si disponibles)
        watch_providers = item.get("watch_providers", [])
        if watch_providers:
            provider_names = [p.get("name") for p in watch_providers if p.get("name")]
            if provider_names:
                fields.append({
                    "name": "📺 Disponible sur",
                    "value": ", ".join(provider_names[:3]),
                    "inline": False
                })
        
        if fields:
            embed["fields"] = fields
        
        # Liens cliquables dans un field au lieu du footer
        links = []
        if imdb_id:
            links.append(f"[🎬 IMDb](https://www.imdb.com/title/{imdb_id})")
        if tmdb_id:
            tmdb_type = "tv" if media_type == "show" else "movie"
            links.append(f"[📊 TMDB](https://www.themoviedb.org/{tmdb_type}/{tmdb_id})")
        links.append(f"[🍿 Netflix](https://www.netflix.com/search?q={title.replace(' ', '%20')})")
        
        if links:
            # Ajouter les liens comme un field (le Markdown fonctionne dans les fields)
            if "fields" not in embed:
                embed["fields"] = []
            embed["fields"].append({
                "name": "🔗 Liens",
                "value": " • ".join(links),
                "inline": False
            })
        
        return embed
    
    def send_to_discord(self, embeds):
        """
        Envoie les embeds à Discord
        Limite: max 10 embeds par webhook
        """
        if not DISCORD_WEBHOOK:
            logger.error("❌ DISCORD_WEBHOOK non configuré!")
            return False
        
        if not embeds:
            logger.info("ℹ️ Aucun embed à envoyer")
            return True
        
        # Discord limite à 10 embeds par message
        for i in range(0, len(embeds), 10):
            batch = embeds[i:i+10]
            
            payload = {
                "username": "Netflix Notifier 🎬",
                "avatar_url": "https://cdn.icon-icons.com/icons2/2699/PNG/512/netflix_official_logo_icon_168085.png",
                "embeds": batch
            }
            
            try:
                response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"✅ Envoyé {len(batch)} notifications à Discord")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'envoi à Discord: {e}")
                return False
        
        return True
    
    def process_new_releases(self):
        """
        Traite les nouvelles sorties Netflix
        """
        logger.info("=" * 60)
        logger.info("🚀 Démarrage de la vérification des nouveautés Netflix")
        logger.info(f"📅 Période: {DAYS_BACK} derniers jours")
        logger.info("=" * 60)
        
        all_embeds = []
        
        # Traitement des films
        logger.info("📽️ Traitement des films...")
        movies = self.get_netflix_releases("movie")
        
        for movie in movies:
            movie_id = movie.get("id") or movie.get("tmdb_id")
            if not movie_id:
                continue
            
            if self.is_already_sent(movie_id):
                logger.debug(f"⏭️ Film déjà envoyé: {movie.get('title')}")
                continue
            
            # Enrichissement optionnel avec détails complets
            if MDBLIST_API_KEY:
                detailed = self.get_media_details(
                    imdb_id=movie.get("imdb_id"),
                    tmdb_id=movie_id,
                    media_type="movie"
                )
                if detailed:
                    # Fusion des données
                    movie.update(detailed)
            
            embed = self.create_discord_embed(movie)
            all_embeds.append(embed)
            self.mark_as_sent(movie_id, movie.get("title", ""))
            
            logger.info(f"➕ Nouveau film: {movie.get('title')} ({movie.get('release_year')})")
        
        # Traitement des séries
        logger.info("📺 Traitement des séries...")
        shows = self.get_netflix_releases("show")
        
        for show in shows:
            show_id = show.get("id") or show.get("tmdb_id")
            if not show_id:
                continue
            
            if self.is_already_sent(show_id):
                logger.debug(f"⏭️ Série déjà envoyée: {show.get('title')}")
                continue
            
            # Enrichissement optionnel
            if MDBLIST_API_KEY:
                detailed = self.get_media_details(
                    imdb_id=show.get("imdb_id"),
                    tmdb_id=show_id,
                    media_type="show"
                )
                if detailed:
                    show.update(detailed)
            
            embed = self.create_discord_embed(show)
            all_embeds.append(embed)
            self.mark_as_sent(show_id, show.get("title", ""))
            
            logger.info(f"➕ Nouvelle série: {show.get('title')} ({show.get('release_year')})")
        
        # Envoi des notifications
        if all_embeds:
            logger.info(f"📤 Envoi de {len(all_embeds)} nouvelles notifications...")
            self.send_to_discord(all_embeds)
            self.save_sent_ids()
            logger.info(f"✅ {len(all_embeds)} nouveautés envoyées avec succès!")
        else:
            logger.info("✅ Aucune nouvelle sortie à notifier")
        
        logger.info("=" * 60)
        logger.info("✨ Traitement terminé!")
        logger.info("=" * 60)


def main():
    """Point d'entrée principal"""
    logger.info("🎬 Bouba Discord Netflix Notifier v3.0")
    logger.info("📡 API: mdblist.com (officielle)")
    
    # Vérification de la configuration
    if not DISCORD_WEBHOOK:
        logger.error("❌ DISCORD_WEBHOOK n'est pas configuré!")
        return 1
    
    if not MDBLIST_API_KEY:
        logger.warning("⚠️ MDBLIST_API_KEY non configuré (fonctionnalités limitées)")
        logger.warning("⚠️ Les filtres de date et détails enrichis ne seront pas disponibles")
    
    if not TMDB_API_KEY:
        logger.info("ℹ️ TMDB_API_KEY non configuré (optionnel)")
    
    # Exécution
    try:
        notifier = NetflixNotifier()
        notifier.process_new_releases()
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
