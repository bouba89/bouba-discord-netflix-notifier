#!/usr/bin/env python3
"""
🎬 Bouba Discord Netflix Notifier - Version 4.1 (+ filtre année MIN_YEAR)
Bot Discord pour notifier des nouvelles sorties Netflix & Disney+
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
DAYS_BACK = int(os.getenv("DAYS_BACK", "7"))

# ✅ NOUVEAU : année minimale — tout contenu plus ancien est ignoré
MIN_YEAR = int(os.getenv("MIN_YEAR", "2025"))

# URLs de base
MDBLIST_API_BASE = "https://api.mdblist.com"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


# ─────────────────────────────────────────────
# Listes mdblist par plateforme
# ─────────────────────────────────────────────
PLATFORM_LISTS = {
    "netflix": {
        "label":  "Netflix",
        "color":  0xE50914,
        "emoji":  "🎬",
        "logo":   "https://cdn.icon-icons.com/icons2/2699/PNG/512/netflix_official_logo_icon_168085.png",
        "search_url": "https://www.netflix.com/search?q={title}",
        "lists": {
            "movies": {"username": "thebirdod", "listname": "new-on-netflix-movies"},
            "shows":  {"username": "thebirdod", "listname": "new-on-netflix-shows"},
        },
    },
    "disney": {
        "label":  "Disney+",
        "color":  0x113CCF,
        "emoji":  "✨",
        "logo":   "https://cdn.icon-icons.com/icons2/2699/PNG/512/disneyplus_logo_icon_168067.png",
        "search_url": "https://www.disneyplus.com/search/{title}",
        "lists": {
            "movies": {"username": "thebirdod", "listname": "new-on-disney-movies"},
            "shows":  {"username": "thebirdod", "listname": "new-on-disney-shows"},
        },
    },
}


class StreamingNotifier:
    """Classe principale pour gérer les notifications Netflix & Disney+"""

    def __init__(self):
        self.sent_ids = self.load_sent_ids()
        self.api_headers = {}
        if MDBLIST_API_KEY:
            self.api_headers = {"apikey": MDBLIST_API_KEY}

    # ── Mémoire ──────────────────────────────────────────────────────────────

    def load_sent_ids(self):
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                    logger.info(f"✅ Chargé {len(data)} IDs depuis le fichier de mémoire")
                    return data
            except Exception as e:
                logger.error(f"❌ Erreur chargement mémoire: {e}")
                return {}
        return {}

    def save_sent_ids(self):
        try:
            with open(MEMORY_FILE, 'w') as f:
                json.dump(self.sent_ids, f, indent=2)
            logger.info(f"✅ Sauvegardé {len(self.sent_ids)} IDs (mémoire complète)")
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")

    def is_already_sent(self, item_id, platform):
        return f"{platform}:{item_id}" in self.sent_ids

    def mark_as_sent(self, item_id, title, platform):
        self.sent_ids[f"{platform}:{item_id}"] = {
            "title":    title,
            "platform": platform,
            "sent_at":  datetime.now().isoformat(),
        }

    # ── Filtre année ──────────────────────────────────────────────────────────

    def is_recent_enough(self, item):
        """Retourne True si le contenu est sorti en MIN_YEAR ou après."""
        year = item.get("release_year") or item.get("year")
        if year:
            try:
                return int(year) >= MIN_YEAR
            except (ValueError, TypeError):
                pass
        # Date de sortie complète ex: "2026-03-15"
        premiered = item.get("premiered") or item.get("release_date", "")
        if premiered and len(premiered) >= 4:
            try:
                return int(premiered[:4]) >= MIN_YEAR
            except (ValueError, TypeError):
                pass
        # Année inconnue → on laisse passer par prudence
        return True

    # ── TMDB ─────────────────────────────────────────────────────────────────

    def get_french_overview(self, tmdb_id, media_type):
        if not TMDB_API_KEY or not tmdb_id:
            return None
        try:
            tmdb_type = "tv" if media_type == "show" else "movie"
            url = f"{TMDB_BASE_URL}/{tmdb_type}/{tmdb_id}"
            resp = requests.get(url, params={"api_key": TMDB_API_KEY, "language": "fr-FR"}, timeout=10)
            resp.raise_for_status()
            return resp.json().get("overview") or None
        except Exception as e:
            logger.debug(f"❌ Synopsis français: {e}")
            return None

    # ── mdblist ───────────────────────────────────────────────────────────────

    def get_list_items(self, username, listname, media_type, platform):
        url = f"https://mdblist.com/lists/{username}/{listname}/json"
        logger.info(f"🔍 [{platform}] Récupération liste {media_type}s ({username}/{listname})...")
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            items = resp.json()
            if not isinstance(items, list):
                logger.error(f"❌ Format inattendu: {type(items)}")
                return []
            logger.info(f"📊 [{platform}] {len(items)} items dans la liste {media_type}s")
            return items
        except Exception as e:
            logger.error(f"❌ [{platform}] Erreur API liste {media_type}s: {e}")
            return []

    def get_media_details(self, imdb_id=None, tmdb_id=None, media_type="movie"):
        if not MDBLIST_API_KEY or (not imdb_id and not tmdb_id):
            return None
        try:
            provider = "imdb" if imdb_id else "tmdb"
            mid      = imdb_id if imdb_id else tmdb_id
            url      = f"{MDBLIST_API_BASE}/{provider}/{media_type}/{mid}"
            resp = requests.get(url, params={"apikey": MDBLIST_API_KEY, "append_to_response": "keyword,review"}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.debug(f"Erreur détails media: {e}")
            return None

    # ── Embed Discord ─────────────────────────────────────────────────────────

    def create_discord_embed(self, item, platform_key):
        pf      = PLATFORM_LISTS[platform_key]
        title   = item.get("title", "Titre inconnu")
        year    = item.get("release_year", "N/A")
        imdb_id = item.get("imdb_id", "")
        tmdb_id = item.get("id") or item.get("tmdb_id")
        mtype   = item.get("mediatype", "movie")

        embed = {
            "title":     f"{pf['emoji']} {title} ({year})",
            "color":     pf["color"],
            "timestamp": datetime.now().isoformat(),
            "footer":    {"text": pf["label"]},
        }

        description = None
        if TMDB_API_KEY and tmdb_id:
            description = self.get_french_overview(tmdb_id, mtype)
        if not description:
            description = item.get("description", "")
        if description:
            embed["description"] = description[:297] + "..." if len(description) > 300 else description

        if item.get("poster"):
            embed["image"] = {"url": item["poster"]}

        fields = []

        ratings = item.get("ratings", [])
        if ratings:
            rating_text = [
                f"{r.get('source','').upper()}: {r['score']}/100"
                for r in ratings[:3] if r.get("score")
            ]
            if rating_text:
                fields.append({"name": "⭐ Notes", "value": "\n".join(rating_text), "inline": True})

        genres = item.get("genres", [])
        if genres:
            names = [
                g.get("name", "") if isinstance(g, dict) else g
                for g in genres[:5]
            ]
            genre_text = ", ".join(n for n in names if n)
            if genre_text:
                fields.append({"name": "🎭 Genres", "value": genre_text, "inline": True})

        links = []
        if imdb_id:
            links.append(f"[🎬 IMDb](https://www.imdb.com/title/{imdb_id})")
        if tmdb_id:
            tmdb_type = "tv" if mtype == "show" else "movie"
            links.append(f"[📊 TMDB](https://www.themoviedb.org/{tmdb_type}/{tmdb_id})")
        search_url = pf["search_url"].format(title=title.replace(" ", "%20"))
        links.append(f"[{'🍿' if platform_key == 'netflix' else '🏰'} {pf['label']}]({search_url})")

        if links:
            fields.append({"name": "🔗 Liens", "value": " • ".join(links), "inline": False})

        if fields:
            embed["fields"] = fields

        return embed

    # ── Discord ───────────────────────────────────────────────────────────────

    def send_to_discord(self, embeds, platform_key):
        if not DISCORD_WEBHOOK:
            logger.error("❌ DISCORD_WEBHOOK non configuré!")
            return False
        if not embeds:
            return True

        pf = PLATFORM_LISTS[platform_key]
        total_batches = (len(embeds) + 9) // 10

        for i in range(0, len(embeds), 10):
            batch     = embeds[i:i+10]
            batch_num = (i // 10) + 1
            payload   = {
                "username":   f"{pf['label']} Notifier {pf['emoji']}",
                "avatar_url": pf["logo"],
                "embeds":     batch,
            }

            for attempt in range(3):
                try:
                    resp = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
                    if resp.status_code == 429:
                        retry_after = resp.json().get("retry_after", 5)
                        logger.warning(f"⚠️ Rate limit Discord (batch {batch_num}/{total_batches}), attente {retry_after}s...")
                        time.sleep(float(retry_after) + 0.5)
                        continue
                    resp.raise_for_status()
                    logger.info(f"✅ [{pf['label']}] Batch {batch_num}/{total_batches} envoyé ({len(batch)} embeds)")
                    break
                except requests.exceptions.HTTPError as e:
                    logger.error(f"❌ HTTP batch {batch_num}: {e}")
                    if attempt == 2:
                        return False
                except Exception as e:
                    logger.error(f"❌ Erreur batch {batch_num}: {e}")
                    if attempt == 2:
                        return False

            if i + 10 < len(embeds):
                time.sleep(2)

        return True

    # ── Traitement principal ──────────────────────────────────────────────────

    def process_platform(self, platform_key):
        pf = PLATFORM_LISTS[platform_key]
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 [{pf['label']}] Vérification des nouveautés...")
        logger.info(f"📅 Filtre : contenus >= {MIN_YEAR}")
        logger.info(f"{'='*60}")

        all_embeds = []

        for media_type, list_info in pf["lists"].items():
            mtype = "movie" if media_type == "movies" else "show"
            label = "films" if mtype == "movie" else "séries"
            logger.info(f"📽️ [{pf['label']}] Traitement des {label}...")

            items = self.get_list_items(
                list_info["username"],
                list_info["listname"],
                mtype,
                platform_key,
            )

            skipped_old = 0
            for item in items:
                # ✅ FILTRE ANNÉE
                if not self.is_recent_enough(item):
                    skipped_old += 1
                    logger.debug(f"⏭️ Trop ancien ({item.get('release_year')}): {item.get('title')}")
                    continue

                item_id = item.get("id") or item.get("tmdb_id")
                if not item_id:
                    continue

                if self.is_already_sent(item_id, platform_key):
                    logger.debug(f"⏭️ Déjà envoyé: {item.get('title')}")
                    continue

                if MDBLIST_API_KEY:
                    detailed = self.get_media_details(
                        imdb_id=item.get("imdb_id"),
                        tmdb_id=item_id,
                        media_type=mtype,
                    )
                    if detailed:
                        item.update(detailed)

                embed = self.create_discord_embed(item, platform_key)
                all_embeds.append(embed)
                self.mark_as_sent(item_id, item.get("title", ""), platform_key)
                logger.info(f"➕ Nouveau(elle) {mtype}: {item.get('title')} ({item.get('release_year')})")

            if skipped_old:
                logger.info(f"🚫 [{pf['label']}] {skipped_old} {label} ignorés (année < {MIN_YEAR})")

        if all_embeds:
            logger.info(f"📤 [{pf['label']}] Envoi de {len(all_embeds)} notifications...")
            self.send_to_discord(all_embeds, platform_key)
            logger.info(f"✅ [{pf['label']}] {len(all_embeds)} nouveautés envoyées!")
        else:
            logger.info(f"✅ [{pf['label']}] Aucune nouvelle sortie à notifier")

    def process_all(self):
        logger.info("=" * 60)
        logger.info("🎬 Démarrage — Netflix + Disney+")
        logger.info(f"📅 Filtre MIN_YEAR : {MIN_YEAR}")
        logger.info(f"🧠 Mémoire active : {len(self.sent_ids)} IDs déjà envoyés")
        logger.info("=" * 60)

        for platform_key in PLATFORM_LISTS:
            self.process_platform(platform_key)

        self.save_sent_ids()

        logger.info("=" * 60)
        logger.info("✨ Traitement terminé!")
        logger.info("=" * 60)


def main():
    logger.info("🎬 Bouba Discord Netflix + Disney Notifier v4.1")
    logger.info("📡 API: mdblist.com (officielle)")

    if not DISCORD_WEBHOOK:
        logger.error("❌ DISCORD_WEBHOOK n'est pas configuré!")
        return 1
    if not MDBLIST_API_KEY:
        logger.warning("⚠️ MDBLIST_API_KEY non configuré (fonctionnalités limitées)")
    if not TMDB_API_KEY:
        logger.info("ℹ️ TMDB_API_KEY non configuré (optionnel)")

    try:
        notifier = StreamingNotifier()
        notifier.process_all()
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
