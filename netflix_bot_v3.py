#!/usr/bin/env python3
"""
🎬 Bouba Discord Netflix Notifier - Version 3.2 (Fix mémoire + Fix rate limit Discord)
Bot Discord pour notifier des nouvelles sorties Netflix
Utilise l'API officielle mdblist.com avec tous les endpoints
"""

import os
import json
import logging
import time
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
        """
        Charge les IDs déjà envoyés.
        sent_ids.json n'est JAMAIS purgé : il accumule tous les IDs
        envoyés depuis le début pour éviter tout re-envoi.
        """
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
        """
        Sauvegarde TOUS les IDs envoyés, sans limite de date ni de taille.
        C'est volontaire : on conserve la mémoire complète pour ne jamais
        ré-envoyer un contenu déjà notifié, même des mois plus tard.
        """
        try:
            with open(MEMORY_FILE, 'w') as f:
                json.dump(self.sent_ids, f, indent=2)
            logger.info(f"✅ Sauvegardé {len(self.sent_ids)} IDs (mémoire complète)")
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
            tmdb_type = "tv" if media_type == "show" else "movie"
            url = f"{TMDB_BASE_URL}/{tmdb_type}/{tmdb_id}"
            params = {
                "api_key": TMDB_API_KEY,
                "language": "fr-FR"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

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
        Récupère TOUTE la liste Netflix sans limite d'items.

        ✅ FIX v3.1 : On ne coupe plus la liste à N items.
        La liste mdblist est déjà filtrée pour les nouveautés récentes.
        On récupère tout, et c'est sent_ids.json qui garantit
        qu'on n'envoie pas deux fois le même contenu.

        Ancienne logique (❌ BUGGUÉE) :
            max_items = min(DAYS_BACK * 10, 50)
            recent_items = all_items[:max_items]
        → Quand un item sort de la fenêtre des 50 premiers puis y revient,
          son ID n'est plus dans sent_ids → re-envoi.

        Nouvelle logique (✅ CORRECTE) :
            On prend TOUTE la liste, sent_ids.json filtre les doublons.
        """
        list_info = NETFLIX_LISTS.get("movies" if media_type == "movie" else "shows")
        if not list_info:
            logger.error(f"❌ Type de média inconnu: {media_type}")
            return []

        username = list_info["username"]
        listname = list_info["listname"]

        try:
            url = f"https://mdblist.com/lists/{username}/{listname}/json"

            logger.info(f"🔍 Récupération de la liste Netflix ({media_type}s)...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            all_items = response.json()

            if not isinstance(all_items, list):
                logger.error(f"❌ Format inattendu: {type(all_items)}")
                return []

            logger.info(f"📊 Total items dans la liste: {len(all_items)} (liste complète, pas de troncature)")

            # ✅ On retourne TOUTE la liste — sent_ids.json gère les doublons
            return all_items

        except Exception as e:
            logger.error(f"❌ Erreur API: {e}")
            return []

    def get_media_details(self, imdb_id=None, tmdb_id=None, media_type="movie"):
        """
        Récupère les détails d'un media via l'API mdblist
        """
        if not MDBLIST_API_KEY:
            return None

        if not imdb_id and not tmdb_id:
            return None

        try:
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
        title = item.get("title", "Titre inconnu")
        year = item.get("release_year", "N/A")
        imdb_id = item.get("imdb_id", "")
        tmdb_id = item.get("id") or item.get("tmdb_id")
        media_type = item.get("mediatype", "movie")

        embed = {
            "title": f"🎬 {title} ({year})",
            "color": 0xE50914,  # Rouge Netflix
            "timestamp": datetime.now().isoformat(),
        }

        # Description — français via TMDB en priorité
        description = None
        if TMDB_API_KEY and tmdb_id:
            description = self.get_french_overview(tmdb_id, media_type)
        if not description:
            description = item.get("description", "")
        if description:
            if len(description) > 300:
                description = description[:297] + "..."
            embed["description"] = description

        # Poster
        poster = item.get("poster")
        if poster:
            embed["image"] = {"url": poster}

        # Fields
        fields = []

        ratings = item.get("ratings", [])
        if ratings:
            rating_text = []
            for rating in ratings[:3]:
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

        genres = item.get("genres", [])
        if genres:
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

        # Liens
        links = []
        if imdb_id:
            links.append(f"[🎬 IMDb](https://www.imdb.com/title/{imdb_id})")
        if tmdb_id:
            tmdb_type = "tv" if media_type == "show" else "movie"
            links.append(f"[📊 TMDB](https://www.themoviedb.org/{tmdb_type}/{tmdb_id})")
        links.append(f"[🍿 Netflix](https://www.netflix.com/search?q={title.replace(' ', '%20')})")

        if links:
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
        Envoie les embeds à Discord (max 10 par message).
        Gère le rate limit 429 avec retry automatique et délai entre les batchs.
        """
        if not DISCORD_WEBHOOK:
            logger.error("❌ DISCORD_WEBHOOK non configuré!")
            return False

        if not embeds:
            logger.info("ℹ️ Aucun embed à envoyer")
            return True

        total_batches = (len(embeds) + 9) // 10
        for i in range(0, len(embeds), 10):
            batch = embeds[i:i+10]
            batch_num = (i // 10) + 1

            payload = {
                "username": "Netflix Notifier 🎬",
                "avatar_url": "https://cdn.icon-icons.com/icons2/2699/PNG/512/netflix_official_logo_icon_168085.png",
                "embeds": batch
            }

            # Retry jusqu'à 3 fois en cas de 429
            for attempt in range(3):
                try:
                    response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)

                    if response.status_code == 429:
                        retry_after = response.json().get("retry_after", 5)
                        logger.warning(f"⚠️ Rate limit Discord (batch {batch_num}/{total_batches}), attente {retry_after}s...")
                        time.sleep(float(retry_after) + 0.5)
                        continue  # retry

                    response.raise_for_status()
                    logger.info(f"✅ Batch {batch_num}/{total_batches} envoyé ({len(batch)} embeds)")
                    break

                except requests.exceptions.HTTPError as e:
                    logger.error(f"❌ Erreur HTTP lors de l'envoi du batch {batch_num}: {e}")
                    if attempt == 2:
                        return False
                except Exception as e:
                    logger.error(f"❌ Erreur lors de l'envoi du batch {batch_num}: {e}")
                    if attempt == 2:
                        return False

            # Délai de 2s entre chaque batch pour éviter le rate limit
            if i + 10 < len(embeds):
                time.sleep(2)

        return True

    def process_new_releases(self):
        """
        Traite les nouvelles sorties Netflix
        """
        logger.info("=" * 60)
        logger.info("🚀 Démarrage de la vérification des nouveautés Netflix")
        logger.info(f"📅 Mémoire active : {len(self.sent_ids)} IDs déjà envoyés")
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

            if MDBLIST_API_KEY:
                detailed = self.get_media_details(
                    imdb_id=movie.get("imdb_id"),
                    tmdb_id=movie_id,
                    media_type="movie"
                )
                if detailed:
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
    logger.info("🎬 Bouba Discord Netflix Notifier v3.2")
    logger.info("📡 API: mdblist.com (officielle)")

    if not DISCORD_WEBHOOK:
        logger.error("❌ DISCORD_WEBHOOK n'est pas configuré!")
        return 1

    if not MDBLIST_API_KEY:
        logger.warning("⚠️ MDBLIST_API_KEY non configuré (fonctionnalités limitées)")

    if not TMDB_API_KEY:
        logger.info("ℹ️ TMDB_API_KEY non configuré (optionnel)")

    try:
        notifier = NetflixNotifier()
        notifier.process_new_releases()
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
