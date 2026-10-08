"""
Source de données : calendrier des sorties streaming de kinow.net.

Kinow affiche une page par plateforme et par pays :
    https://kinow.net/sorties-streaming?country=fr&service=netflix
    https://kinow.net/sorties-streaming?country=fr&service=disney

Chaque jour est un <h2> ("vendredi 9 octobre", ou "Date à confirmer") suivi
de liens /film/<id> ou /serie/<id>, où <id> est l'identifiant TMDB.
"""

import logging
import re
from datetime import date

import requests

logger = logging.getLogger(__name__)

KINOW_URL = "https://kinow.net/sorties-streaming"
USER_AGENT = "Mozilla/5.0 (compatible; BoubaNetflixNotifier/5.0)"

MOIS_FR = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "septembre": 9, "octobre": 10,
    "novembre": 11, "décembre": 12,
}
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def parse_date(texte, today):
    """'vendredi 9 octobre' -> date ; 'Date à confirmer' -> None.

    Kinow n'indique pas l'année : on prend l'année en cours, sauf si le mois
    est très en arrière (ex. janvier vu en décembre) -> année suivante.
    """
    m = re.search(r"(\d{1,2})\s+([a-zéûè]+)", texte.lower())
    if not m or m.group(2) not in MOIS_FR:
        return None
    jour, mois = int(m.group(1)), MOIS_FR[m.group(2)]
    annee = today.year
    if mois < today.month - 6:
        annee += 1
    try:
        return date(annee, mois, jour)
    except ValueError:
        return None


def format_date_fr(d):
    """date -> 'vendredi 9 octobre'"""
    mois = {v: k for k, v in MOIS_FR.items()}
    return f"{JOURS_FR[d.weekday()]} {d.day} {mois[d.month]}"


def get_releases(service, country="fr", today=None):
    """Retourne les sorties du calendrier Kinow pour une plateforme.

    Chaque sortie est un dict :
        title        titre affiché par Kinow (avec ", saison N" pour les séries)
        mediatype    "movie" ou "show"
        id           identifiant TMDB
        release_date date, ou None si "Date à confirmer"
        kinow_url    lien vers la fiche Kinow

    Retourne une liste vide (et journalise l'erreur) si Kinow est injoignable
    ou si beautifulsoup4 n'est pas installé.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("❌ beautifulsoup4 manquant (pip install beautifulsoup4)")
        return []

    today = today or date.today()
    logger.info(f"🔍 [Kinow] Récupération du calendrier ({service}/{country})...")
    try:
        resp = requests.get(
            KINOW_URL,
            params={"country": country, "service": service},
            headers={"User-Agent": USER_AGENT},
            timeout=20,
        )
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"❌ [Kinow] Erreur de récupération: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    releases = []

    for h2 in soup.find_all("h2"):
        release_date = parse_date(h2.get_text(strip=True), today)
        for el in h2.find_all_next():
            if el.name == "h2":
                break
            if el.name != "a":
                continue
            href = el.get("href", "")
            m = re.search(r"/(film|serie)/(\d+)", href)
            if not m:
                continue
            releases.append({
                "title":        el.get_text(strip=True),
                "mediatype":    "movie" if m.group(1) == "film" else "show",
                "id":           int(m.group(2)),
                "release_date": release_date,
                "kinow_url":    "https://kinow.net" + href if href.startswith("/") else href,
            })

    if not releases:
        logger.warning("⚠️ [Kinow] Aucune sortie trouvée : la structure de la page a peut-être changé")
    else:
        logger.info(f"📊 [Kinow] {len(releases)} sorties dans le calendrier")
    return releases
