import os
import requests
import json
from datetime import datetime, timedelta

# --- Config ---
API_KEY = os.environ.get("RAPIDAPI_KEY")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
COUNTRIES = os.environ.get("COUNTRIES", "FR,US,CA").split(",")
MEMORY_FILE = "/app/data/sent_ids.json"
API_HOST = "unogsng.p.rapidapi.com"

# --- Dates ---
today = datetime.utcnow().date()
yesterday = today - timedelta(days=1)


# --- Anti-doublons ---
# S'assurer que le répertoire existe
os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

# S'assurer que le fichier existe et est vide si besoin
if not os.path.isfile(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

# Charger les nfid déjà envoyés
with open(MEMORY_FILE, "r") as f:
    sent_ids = json.load(f)

print(f"📋 {len(sent_ids)} contenus déjà envoyés chargés depuis {MEMORY_FILE}")

# --- Fonction fetch titres uNoGS ---
def fetch_titles():
    url = f"https://{API_HOST}/search"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {
        "limit": 100,
        "orderby": "date_added"
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        results = r.json().get("results", [])
        print(f"✅ Total titres récupérés: {len(results)}")
        return results
    except Exception as e:
        print(f"❌ Erreur API uNoGS: {e}")
        return []

# --- Vérifier disponibilité par pays ---
def is_available_in_country(title, country_code):
    if not title.get("clist"):
        return False
    clist_str = "{" + title["clist"] + "}"
    try:
        clist_dict = json.loads(clist_str)
        return country_code in clist_dict
    except Exception as e:
        print(f"⚠️  Erreur parsing clist: {e} / {title['title']}")
        return False

# --- Enrichir via TMDB ---
def enrich_with_tmdb(title, year, vtype="movie"):
    if not TMDB_API_KEY:
        return "", ""
    base_url = "https://api.themoviedb.org/3/search/"
    endpoint = "movie" if vtype == "movie" else "tv"
    url = f"{base_url}{endpoint}"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "year": year if vtype=="movie" else None,
        "first_air_date_year": year if vtype=="series" else None,
        "language": "fr-FR"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        if not results:
            return "", ""
        tmdb_data = results[0]
        poster = f"https://image.tmdb.org/t/p/w500{tmdb_data.get('poster_path')}" if tmdb_data.get("poster_path") else ""
        overview = tmdb_data.get("overview", "")
        return poster, overview
    except Exception as e:
        print(f"⚠️  Erreur TMDB pour {title}: {e}")
        return "", ""

def send_discord(movies, series, country):
    if not movies and not series:
        print(f"ℹ️  Aucune nouvelle sortie Netflix détectée pour {country}.")
        return

    embeds = []

    def format_embed(t):
        title = t['title']
        year = t.get('year', 'N/A')
        vtype = t.get('vtype', 'movie')

        # Enrichir via TMDB si possible
        tmdb_poster, tmdb_synopsis = enrich_with_tmdb(title, year, vtype)
        poster = tmdb_poster or t.get('img') or t.get('poster') or ""
        synopsis = tmdb_synopsis or t.get('synopsis', '')

        # URL TMDB
        tmdb_id = ""
        if TMDB_API_KEY:
            search_type = "movie" if vtype=="movie" else "tv"
            try:
                r = requests.get(
                    f"https://api.themoviedb.org/3/search/{search_type}",
                    params={"api_key": TMDB_API_KEY, "query": title, "year": year if vtype=="movie" else None, "first_air_date_year": year if vtype=="series" else None},
                    timeout=10
                )
                r.raise_for_status()
                results = r.json().get("results", [])
                if results:
                    tmdb_id = results[0].get("id", "")
            except:
                pass

        tmdb_url = f"https://www.themoviedb.org/{search_type}/{tmdb_id}" if tmdb_id else ""

        embed = {
            "title": f"{title} ({year})",
            "description": synopsis or "Pas de synopsis disponible.",
            "color": 0xE50914,
            "url": tmdb_url,
        }
        if poster:
            embed["image"] = {"url": poster}
        return embed

    for t in movies:
        embeds.append(format_embed(t))
    for t in series:
        embeds.append(format_embed(t))

    # Discord limite à 10 embeds par message
    for i in range(0, len(embeds), 10):
        chunk = embeds[i:i+10]
        try:
            r = requests.post(WEBHOOK_URL, json={"embeds": chunk}, timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"❌ Erreur envoi Discord: {e}")

    print(f"✅ Message Discord envoyé pour {country}.")


# --- Script principal ---
print("\n" + "="*60)
print(f"🎬 Netflix Bot - {datetime.now()}")
print("="*60)

all_titles = fetch_titles()
total_new = 0  # Compteur de nouveautés

for country_code in COUNTRIES:
    country_code = country_code.strip()
    print(f"\n🌍 Traitement du pays: {country_code}")
    
    # Filtrer par pays
    titles_country = [t for t in all_titles if is_available_in_country(t, country_code)]
    print(f"  📺 {len(titles_country)} titres disponibles")
    
    # Filtrer last 24h
    titles_recent = []
    for t in titles_country:
        try:
            title_date = datetime.strptime(t['titledate'], "%Y-%m-%d").date()
            if title_date >= yesterday:
                titles_recent.append(t)
        except Exception as e:
            print(f"⚠️  Erreur parsing date: {e} / {t.get('title','')}")
    
    print(f"  🆕 {len(titles_recent)} titres récents (dernières 24h)")
    
    # Filtrer anti-doublons
    new_titles = [t for t in titles_recent if t['nfid'] not in sent_ids]
    print(f"  ✨ {len(new_titles)} nouveaux titres (non envoyés)")
    
    if new_titles:
        # Ajouter les IDs
        new_ids = [t['nfid'] for t in new_titles]
        sent_ids.extend(new_ids)
        total_new += len(new_titles)
        
        # Séparer films / séries
        movies = [t for t in new_titles if t.get('vtype') == 'movie']
        series = [t for t in new_titles if t.get('vtype') == 'series']
        
        print(f"  🎥 Films: {len(movies)} | 📺 Séries: {len(series)}")
        
        # Envoyer Discord
        send_discord(movies, series, country_code)

# ✅ CRITIQUE: SAUVEGARDER LA MÉMOIRE (après la boucle, sans indentation)
try:
    with open(MEMORY_FILE, "w") as f:
        json.dump(sent_ids, f, indent=2)
    print(f"\n💾 {len(sent_ids)} IDs sauvegardés dans {MEMORY_FILE}")
    print(f"✨ {total_new} nouveaux contenus envoyés ce run")
except Exception as e:
    print(f"\n❌ ERREUR CRITIQUE lors de la sauvegarde: {e}")

print("\n" + "="*60)
print("🏁 Terminé")
print("="*60)