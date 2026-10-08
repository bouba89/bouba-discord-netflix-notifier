#!/usr/bin/env python3
"""
🎬 Bouba Discord Netflix Notifier - Version 5.0
Bot Discord qui annonce les prochaines sorties Netflix & Disney+ (France)
Source : calendrier kinow.net, enrichi via TMDB (affiche, synopsis FR, genres, notes)
"""

import os
import re
import json
import logging
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

import kinow_source

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
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
COUNTRY = os.getenv("COUNTRY", "fr").lower()

# Calendrier Kinow (sorties à venir, avec dates)
KINOW_DAYS_AHEAD = int(os.getenv("KINOW_DAYS_AHEAD", "1"))   # 1 = sorties de demain
# URLs de base
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


# ─────────────────────────────────────────────
# Plateformes (service = valeur du paramètre ?service= de Kinow)
# ─────────────────────────────────────────────
PLATFORMS = {
    "netflix": {
        "service": "netflix",
        "label":  "Netflix",
        "color":  0xE50914,
        "emoji":  "🎬",
        "logo":   "https://cdn.icon-icons.com/icons2/2699/PNG/512/netflix_official_logo_icon_168085.png",
        "search_url": "https://www.netflix.com/search?q={title}",
    },
    "disney": {
        "service": "disney",
        "label":  "Disney+",
        "color":  0x113CCF,
        "emoji":  "✨",
        "logo":   "https://cdn.icon-icons.com/icons2/2699/PNG/512/disneyplus_logo_icon_168067.png",
        "search_url": "https://www.disneyplus.com/search/{title}",
    },
}


class StreamingNotifier:
    """Classe principale pour gérer les notifications Netflix & Disney+"""

    def __init__(self):
        self.sent_ids = self.load_sent_ids()

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

    # ── TMDB ─────────────────────────────────────────────────────────────────

    def get_tmdb_details(self, tmdb_id, media_type):
        """Détails TMDB (FR) utilisés pour les sorties Kinow : affiche, synopsis, genres, note."""
        if not TMDB_API_KEY or not tmdb_id:
            return {}
        try:
            tmdb_type = "tv" if media_type == "show" else "movie"
            resp = requests.get(
                f"{TMDB_BASE_URL}/{tmdb_type}/{tmdb_id}",
                params={"api_key": TMDB_API_KEY, "language": "fr-FR", "append_to_response": "external_ids"},
                timeout=10,
            )
            resp.raise_for_status()
            d = resp.json()
            out = {
                "description": d.get("overview") or "",
                "genres": [g.get("name") for g in d.get("genres", []) if g.get("name")],
                "release_year": (d.get("release_date") or d.get("first_air_date") or "")[:4] or None,
            }
            imdb_id = d.get("imdb_id") or (d.get("external_ids") or {}).get("imdb_id")
            if imdb_id:
                out["imdb_id"] = imdb_id
            if d.get("poster_path"):
                out["poster"] = TMDB_IMAGE_BASE + d["poster_path"]
            if d.get("vote_average"):
                out["ratings"] = [{"source": "tmdb", "score": round(d["vote_average"] * 10)}]
            return out
        except Exception as e:
            logger.debug(f"❌ Détails TMDB {tmdb_id}: {e}")
            return {}

    def process_platform(self, platform_key):
        """Annonce les sorties de la plateforme dans les KINOW_DAYS_AHEAD prochains jours."""
        pf = PLATFORMS[platform_key]
        today = datetime.now().date()
        limit = today + timedelta(days=KINOW_DAYS_AHEAD)

        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 [{pf['label']}] Sorties du {today:%d/%m} au {limit:%d/%m}")
        logger.info(f"{'='*60}")

        embeds = []
        for item in kinow_source.get_releases(pf["service"], COUNTRY, today):
            rd = item["release_date"]
            if rd is None or not (today <= rd <= limit):
                continue

            # une même sortie n'est annoncée qu'une fois (date comprise : une nouvelle saison = nouvelle annonce)
            memory_id = f"{item['mediatype']}-{item['id']}-{rd.isoformat()}"
            if self.is_already_sent(memory_id, platform_key):
                continue

            kinow_title = item["title"]  # garde "…, saison 2"
            item.update(self.get_tmdb_details(item["id"], item["mediatype"]))
            item["title"] = kinow_title
            item["kinow_date"] = kinow_source.format_date_fr(rd)

            embeds.append(self.create_discord_embed(item, platform_key))
            self.mark_as_sent(memory_id, kinow_title, platform_key)
            logger.info(f"➕ [{pf['label']}] {kinow_title} ({rd:%d/%m})")

        if embeds:
            self.send_to_discord(embeds, platform_key)
            logger.info(f"✅ [{pf['label']}] {len(embeds)} sorties envoyées!")
        else:
            logger.info(f"✅ [{pf['label']}] Aucune nouvelle sortie à notifier")

    # ── Embed Discord ─────────────────────────────────────────────────────────

    def create_discord_embed(self, item, platform_key):
        pf      = PLATFORMS[platform_key]
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

        description = item.get("description", "")
        if description:
            embed["description"] = description[:297] + "..." if len(description) > 300 else description

        if item.get("poster"):
            embed["image"] = {"url": item["poster"]}

        fields = []

        if item.get("kinow_date"):
            embed["footer"] = {"text": f"{pf['label']} • Prochainement"}
            fields.append({"name": "📅 Sortie", "value": item["kinow_date"].capitalize(), "inline": True})

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
        search_title = re.sub(r",?\s*saison\s+\d+\s*$", "", title, flags=re.I)  # "X, saison 2" -> "X"
        search_url = pf["search_url"].format(title=quote(search_title))
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

        pf = PLATFORMS[platform_key]
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

    def process_all(self):
        logger.info("=" * 60)
        logger.info("🎬 Démarrage — Netflix + Disney+")
        logger.info(f"📆 Annonce des sorties à J+{KINOW_DAYS_AHEAD} maximum")
        logger.info(f"🧠 Mémoire active : {len(self.sent_ids)} IDs déjà envoyés")
        logger.info("=" * 60)

        for platform_key in PLATFORMS:
            self.process_platform(platform_key)

        self.save_sent_ids()

        logger.info("=" * 60)
        logger.info("✨ Traitement terminé!")
        logger.info("=" * 60)


def main():
    logger.info("🎬 Bouba Discord Netflix + Disney Notifier v5.0")
    logger.info("📡 Source: kinow.net + TMDB")

    if not DISCORD_WEBHOOK:
        logger.error("❌ DISCORD_WEBHOOK n'est pas configuré!")
        return 1
    if not TMDB_API_KEY:
        logger.warning("⚠️ TMDB_API_KEY non configuré : pas d'affiche ni de synopsis")

    try:
        notifier = StreamingNotifier()
        notifier.process_all()
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
