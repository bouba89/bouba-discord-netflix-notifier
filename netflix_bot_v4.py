#!/usr/bin/env python3
"""
🎬 Bouba Discord Netflix Notifier - Version 4.1 (+ filtre année MIN_YEAR)
Bot Discord pour notifier des nouvelles sorties Netflix & Disney+
Utilise l'API officielle mdblist.com avec tous les endpoints
"""

import os
import re
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

# ✅ NOUVEAU : calendrier Kinow (sorties Netflix à venir, avec dates)
KINOW_ENABLED = os.getenv("KINOW_ENABLED", "true").lower() in ("1", "true", "yes")
KINOW_DAYS_AHEAD = int(os.getenv("KINOW_DAYS_AHEAD", "1"))   # 1 = sorties de demain
KINOW_URL = "https://kinow.net/sorties-streaming"
MOIS_FR = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "septembre": 9, "octobre": 10,
    "novembre": 11, "décembre": 12,
}

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

    def get_tmdb_details(self, tmdb_id, media_type):
        """Détails TMDB (FR) utilisés pour les sorties Kinow : affiche, synopsis, genres, note."""
        if not TMDB_API_KEY or not tmdb_id:
            return {}
        try:
            tmdb_type = "tv" if media_type == "show" else "movie"
            resp = requests.get(
                f"{TMDB_BASE_URL}/{tmdb_type}/{tmdb_id}",
                params={"api_key": TMDB_API_KEY, "language": "fr-FR"},
                timeout=10,
            )
            resp.raise_for_status()
            d = resp.json()
            out = {
                "description": d.get("overview") or "",
                "genres": [g.get("name") for g in d.get("genres", []) if g.get("name")],
                "release_year": (d.get("release_date") or d.get("first_air_date") or "")[:4] or None,
            }
            if d.get("poster_path"):
                out["poster"] = TMDB_IMAGE_BASE + d["poster_path"]
            if d.get("vote_average"):
                out["ratings"] = [{"source": "tmdb", "score": round(d["vote_average"] * 10)}]
            return out
        except Exception as e:
            logger.debug(f"❌ Détails TMDB {tmdb_id}: {e}")
            return {}

    # ── Kinow (calendrier des sorties) ────────────────────────────────────────

    @staticmethod
    def parse_kinow_date(texte, today):
        """'vendredi 9 octobre' -> date ; 'Date à confirmer' -> None"""
        m = re.search(r"(\d{1,2})\s+([a-zéûè]+)", texte.lower())
        if not m or m.group(2) not in MOIS_FR:
            return None
        jour, mois = int(m.group(1)), MOIS_FR[m.group(2)]
        annee = today.year
        if mois < today.month - 6:
            annee += 1
        try:
            return today.replace(year=annee, month=mois, day=jour)
        except ValueError:
            return None

    def get_kinow_releases(self, service="netflix", country="fr"):
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("❌ beautifulsoup4 manquant (pip install beautifulsoup4)")
            return []

        logger.info("🔍 [Kinow] Récupération du calendrier des sorties...")
        try:
            resp = requests.get(
                KINOW_URL,
                params={"country": country, "service": service},
                headers={"User-Agent": "Mozilla/5.0 (compatible; BoubaNetflixNotifier/4.2)"},
                timeout=20,
            )
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"❌ [Kinow] Erreur de récupération: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        today = datetime.now().date()
        releases = []

        for h2 in soup.find_all("h2"):
            release_date = self.parse_kinow_date(h2.get_text(strip=True), today)
            for el in h2.find_all_next():
                if el.name == "h2":
                    break
                if el.name != "a":
                    continue
                m = re.search(r"/(film|serie)/(\d+)", el.get("href", ""))
                if not m:
                    continue
                releases.append({
                    "title":        el.get_text(strip=True),
                    "mediatype":    "movie" if m.group(1) == "film" else "show",
                    "id":           int(m.group(2)),          # ID TMDB
                    "release_date": release_date,             # None = à confirmer
                    "kinow_url":    "https://kinow.net" + el["href"] if el["href"].startswith("/") else el["href"],
                })

        logger.info(f"📊 [Kinow] {len(releases)} sorties dans le calendrier")
        return releases

    @staticmethod
    def format_date_fr(d):
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        mois = {v: k for k, v in MOIS_FR.items()}
        return f"{jours[d.weekday()]} {d.day} {mois[d.month]}"

    def process_kinow(self):
        """Poste les sorties Netflix des KINOW_DAYS_AHEAD prochains jours (dédoublonnées)."""
        pf = PLATFORM_LISTS["netflix"]
        today = datetime.now().date()
        limit = today + timedelta(days=KINOW_DAYS_AHEAD)

        logger.info(f"\n{'='*60}")
        logger.info(f"📆 [Kinow] Sorties Netflix du {today:%d/%m} au {limit:%d/%m}")
        logger.info(f"{'='*60}")

        embeds = []
        for item in self.get_kinow_releases():
            rd = item["release_date"]
            if rd is None or not (today <= rd <= limit):
                continue

            # clé distincte de la mémoire MDBList pour ne pas mélanger les deux sources
            memory_id = f"kinow-{item['mediatype']}-{item['id']}-{rd.isoformat()}"
            if self.is_already_sent(memory_id, "netflix"):
                continue

            kinow_title = item["title"]  # garde "…, saison 2"
            item.update(self.get_tmdb_details(item["id"], item["mediatype"]))

            if MDBLIST_API_KEY:
                detailed = self.get_media_details(tmdb_id=item["id"], media_type=item["mediatype"])
                if detailed:
                    for k, v in detailed.items():     # ne pas écraser ce que TMDB a déjà fourni
                        item.setdefault(k, v)

            item["title"] = kinow_title
            item["kinow_date"] = self.format_date_fr(rd)
            embeds.append(self.create_discord_embed(item, "netflix"))
            self.mark_as_sent(memory_id, kinow_title, "netflix")
            logger.info(f"➕ [Kinow] {kinow_title} ({rd:%d/%m})")

        if embeds:
            self.send_to_discord(embeds, "netflix")
            logger.info(f"✅ [Kinow] {len(embeds)} sorties envoyées!")
        else:
            logger.info("✅ [Kinow] Aucune nouvelle sortie à notifier")

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

        if KINOW_ENABLED:
            self.process_kinow()

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
