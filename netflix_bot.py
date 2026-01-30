#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netflix Bot Discord Notifier - Version avec Debug Complet
Auteur: Bouba89
Description: Bot qui notifie les nouveautés Netflix sur Discord avec logging détaillé
"""

import os
import requests
import json
from datetime import datetime, timedelta
import logging
import html  # Pour décoder les entités HTML

# ============================================================================
# CONFIGURATION DU LOGGING DÉTAILLÉ
# ============================================================================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/netflix_bot_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIG
# ============================================================================
API_KEY = os.environ.get("RAPIDAPI_KEY")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
COUNTRIES = os.environ.get("COUNTRIES", "FR,US,CA").split(",")
MEMORY_FILE = "/app/data/sent_ids.json"
DEBUG_API_FILE = "/app/data/api_responses_debug.json"
API_HOST = "unogsng.p.rapidapi.com"

# Dates
today = datetime.utcnow().date()
yesterday = today - timedelta(days=1)

logger.info("="*80)
logger.info("🎬 NETFLIX BOT - DÉMARRAGE")
logger.info("="*80)
logger.info(f"📅 Date UTC: {today}")
logger.info(f"🌍 Pays configurés: {COUNTRIES}")
logger.info(f"🔑 RapidAPI Key: {'✅ Configurée' if API_KEY else '❌ Manquante'}")
logger.info(f"🔑 TMDB API Key: {'✅ Configurée' if TMDB_API_KEY else '❌ Manquante'}")
logger.info(f"🔗 Discord Webhook: {'✅ Configuré' if WEBHOOK_URL else '❌ Manquant'}")

# ============================================================================
# FONCTION DE DEBUG API
# ============================================================================
def save_api_debug(api_name, endpoint, params, response_data, status_code, error=None):
    """Sauvegarde toutes les requêtes API pour analyse"""
    debug_entry = {
        "timestamp": datetime.now().isoformat(),
        "api": api_name,
        "endpoint": endpoint,
        "params": params,
        "status_code": status_code,
        "response": response_data if not error else {"error": str(error)},
        "error": str(error) if error else None
    }
    
    try:
        # Charger les données existantes
        if os.path.exists(DEBUG_API_FILE):
            with open(DEBUG_API_FILE, 'r', encoding='utf-8') as f:
                debug_data = json.load(f)
        else:
            debug_data = []
        
        # Ajouter la nouvelle entrée (garder les 100 dernières)
        debug_data.append(debug_entry)
        debug_data = debug_data[-100:]
        
        # Sauvegarder
        os.makedirs(os.path.dirname(DEBUG_API_FILE), exist_ok=True)
        with open(DEBUG_API_FILE, 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"💾 Debug API sauvegardé: {api_name} -> {DEBUG_API_FILE}")
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde debug: {e}")

# ============================================================================
# ANTI-DOUBLONS
# ============================================================================
os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

if not os.path.isfile(MEMORY_FILE):
    logger.info(f"📁 Création nouveau fichier: {MEMORY_FILE}")
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)

with open(MEMORY_FILE, "r") as f:
    sent_ids = json.load(f)

logger.info(f"📋 {len(sent_ids)} contenus déjà envoyés chargés depuis {MEMORY_FILE}")

# ============================================================================
# FONCTION FETCH TITRES uNoGS (avec debug)
# ============================================================================
def fetch_titles():
    logger.info("\n" + "="*60)
    logger.info("🔍 RÉCUPÉRATION DES TITRES uNoGS")
    logger.info("="*60)
    
    url = f"https://{API_HOST}/search"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {
        "limit": 100,
        "orderby": "date_added"
    }
    
    logger.debug(f"📤 Requête uNoGS:")
    logger.debug(f"   URL: {url}")
    logger.debug(f"   Params: {json.dumps(params, indent=2)}")
    logger.debug(f"   Headers: X-RapidAPI-Key=***, X-RapidAPI-Host={API_HOST}")
    
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        logger.info(f"📥 Réponse uNoGS: Status {r.status_code}")
        
        r.raise_for_status()
        response_json = r.json()
        results = response_json.get("results", [])
        
        # Sauvegarder pour debug
        save_api_debug("uNoGS", url, params, response_json, r.status_code)
        
        logger.info(f"✅ Total titres récupérés: {len(results)}")
        
        # Afficher un exemple de titre
        if results:
            logger.debug(f"📋 Exemple de titre récupéré:")
            logger.debug(json.dumps(results[0], indent=2, ensure_ascii=False)[:500])
        
        return results
        
    except requests.exceptions.Timeout:
        logger.error("⏱️  Timeout lors de la requête uNoGS (>30s)")
        save_api_debug("uNoGS", url, params, None, None, "Timeout")
        return []
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ Erreur HTTP uNoGS: {e}")
        try:
            error_data = r.json()
            logger.error(f"📄 Détails erreur: {json.dumps(error_data, indent=2)}")
            save_api_debug("uNoGS", url, params, error_data, r.status_code, str(e))
        except:
            logger.error(f"📄 Réponse brute: {r.text[:500]}")
            save_api_debug("uNoGS", url, params, {"raw": r.text}, r.status_code, str(e))
        return []
    except Exception as e:
        logger.error(f"❌ Erreur API uNoGS: {e}")
        save_api_debug("uNoGS", url, params, None, None, str(e))
        return []

# ============================================================================
# VÉRIFIER DISPONIBILITÉ PAR PAYS
# ============================================================================
def is_available_in_country(title, country_code):
    title_name = title.get('title', 'N/A')
    
    # NOUVEAU: Si pas de clist, on ACCEPTE le contenu
    if not title.get("clist"):
        logger.info(f"  ✅ '{title_name}' - Pas de clist, ACCEPTÉ automatiquement")
        return True
    
    clist_str = "{" + title["clist"] + "}"
    try:
        clist_dict = json.loads(clist_str)
        available = country_code in clist_dict
        logger.debug(f"  {'✅' if available else '❌'} '{title_name}' - {country_code}")
        return available
    except Exception as e:
        logger.warning(f"⚠️  Erreur parsing clist: {e} / {title_name}")
        return True  # En cas d'erreur, accepter quand même

# ============================================================================
# ENRICHIR VIA TMDB (avec debug)
# ============================================================================
def enrich_with_tmdb(title, year, vtype="movie"):
    logger.debug(f"🎬 TMDB enrichissement: {title} ({year}) - Type: {vtype}")
    
    if not TMDB_API_KEY:
        logger.warning("⚠️  TMDB API Key manquante, enrichissement ignoré")
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
    # Nettoyer les params None
    params = {k: v for k, v in params.items() if v is not None}
    
    logger.debug(f"📤 Requête TMDB: {url}")
    logger.debug(f"   Query: {title}")
    logger.debug(f"   Params: {params}")
    
    try:
        r = requests.get(url, params=params, timeout=10)
        logger.debug(f"📥 TMDB Status: {r.status_code}")
        
        r.raise_for_status()
        response_json = r.json()
        results = response_json.get("results", [])
        
        # Sauvegarder pour debug
        save_api_debug("TMDB", url, params, response_json, r.status_code)
        
        if not results:
            logger.warning(f"⚠️  Aucun résultat TMDB pour '{title}'")
            return "", ""
        
        tmdb_data = results[0]
        logger.debug(f"✅ Résultat TMDB trouvé: {tmdb_data.get('title') or tmdb_data.get('name')}")
        logger.debug(f"   Poster: {tmdb_data.get('poster_path', 'N/A')}")
        logger.debug(f"   Synopsis: {tmdb_data.get('overview', 'N/A')[:100]}...")
        
        poster = f"https://image.tmdb.org/t/p/w500{tmdb_data.get('poster_path')}" if tmdb_data.get("poster_path") else ""
        overview = tmdb_data.get("overview", "")
        
        return poster, overview
        
    except Exception as e:
        logger.error(f"❌ Erreur TMDB pour {title}: {e}")
        save_api_debug("TMDB", url, params, None, None, str(e))
        return "", ""

# ============================================================================
# ENVOYER DISCORD (avec debug)
# ============================================================================
def send_discord(movies, series, country):
    logger.info(f"\n📨 ENVOI DISCORD POUR {country}")
    logger.info(f"   🎥 Films: {len(movies)} | 📺 Séries: {len(series)}")
    
    if not movies and not series:
        logger.info(f"ℹ️  Aucune nouvelle sortie Netflix détectée pour {country}.")
        return

    embeds = []

    def format_embed(t):
        title = t['title']
        year = t.get('year', 'N/A')
        vtype = t.get('vtype', 'movie')

        logger.debug(f"  📝 Formatage embed: {title} ({year})")

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

    logger.info(f"📦 {len(embeds)} embeds préparés (max 10 par message)")

    # Discord limite à 10 embeds par message
    for i in range(0, len(embeds), 10):
        chunk = embeds[i:i+10]
        payload = {"embeds": chunk}
        
        logger.debug(f"📤 Envoi chunk {i//10 + 1}/{(len(embeds)-1)//10 + 1}")
        logger.debug(f"   Payload: {json.dumps(payload, indent=2, ensure_ascii=False)[:300]}...")
        
        try:
            r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            logger.info(f"📥 Discord Status: {r.status_code}")
            
            r.raise_for_status()
            logger.info(f"✅ Chunk {i//10 + 1} envoyé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi Discord chunk {i//10 + 1}: {e}")
            if hasattr(r, 'text'):
                logger.error(f"   Réponse: {r.text[:200]}")

    logger.info(f"✅ Message Discord envoyé pour {country}.")

# ============================================================================
# SCRIPT PRINCIPAL
# ============================================================================
logger.info("\n" + "="*80)
logger.info(f"🎬 Netflix Bot - {datetime.now()}")
logger.info("="*80)

all_titles = fetch_titles()
total_new = 0

for country_code in COUNTRIES:
    country_code = country_code.strip()
    logger.info(f"\n{'='*60}")
    logger.info(f"🌍 TRAITEMENT DU PAYS: {country_code}")
    logger.info(f"{'='*60}")
    
    # Filtrer par pays
    logger.debug(f"🔍 Filtrage par pays {country_code}...")
    titles_country = [t for t in all_titles if is_available_in_country(t, country_code)]
    logger.info(f"  📺 {len(titles_country)} titres disponibles dans {country_code}")
    
    # Filtrer last 24h
    logger.debug(f"🔍 Filtrage par date (>= {yesterday})...")
    titles_recent = []
    for t in titles_country:
        try:
            title_date = datetime.strptime(t['titledate'], "%Y-%m-%d").date()
            if title_date >= yesterday:
                titles_recent.append(t)
                logger.debug(f"  ✅ {t['title']} - Date: {title_date}")
            else:
                logger.debug(f"  ⏭️  {t['title']} - Trop ancien: {title_date}")
        except Exception as e:
            logger.warning(f"⚠️  Erreur parsing date: {e} / {t.get('title','')}")
    
    logger.info(f"  🆕 {len(titles_recent)} titres récents (dernières 24h)")
    
    # Filtrer anti-doublons
    logger.debug(f"🔍 Filtrage anti-doublons...")
    new_titles = []
    for t in titles_recent:
        if t['nfid'] not in sent_ids:
            new_titles.append(t)
            logger.debug(f"  ✨ Nouveau: {t['title']} (nfid: {t['nfid']})")
        else:
            logger.debug(f"  ⏭️  Déjà envoyé: {t['title']} (nfid: {t['nfid']})")
    
    logger.info(f"  ✨ {len(new_titles)} nouveaux titres (non envoyés)")
    
    if new_titles:
        # Ajouter les IDs
        new_ids = [t['nfid'] for t in new_titles]
        sent_ids.extend(new_ids)
        total_new += len(new_titles)
        
        # Séparer films / séries
        movies = [t for t in new_titles if t.get('vtype') == 'movie']
        series = [t for t in new_titles if t.get('vtype') == 'series']
        
        logger.info(f"  🎥 Films: {len(movies)} | 📺 Séries: {len(series)}")
        
        # Envoyer Discord
        send_discord(movies, series, country_code)
    else:
        logger.info(f"  ℹ️  Rien de nouveau à envoyer pour {country_code}")

# ============================================================================
# SAUVEGARDE MÉMOIRE
# ============================================================================
logger.info("\n" + "="*60)
logger.info("💾 SAUVEGARDE DE LA MÉMOIRE")
logger.info("="*60)

try:
    with open(MEMORY_FILE, "w") as f:
        json.dump(sent_ids, f, indent=2)
    logger.info(f"✅ {len(sent_ids)} IDs sauvegardés dans {MEMORY_FILE}")
    logger.info(f"✨ {total_new} nouveaux contenus envoyés ce run")
except Exception as e:
    logger.error(f"❌ ERREUR CRITIQUE lors de la sauvegarde: {e}")

logger.info("\n" + "="*80)
logger.info("🏁 TERMINÉ")
logger.info(f"📊 Résumé:")
logger.info(f"   - Contenus traités: {len(all_titles)}")
logger.info(f"   - Nouveaux envoyés: {total_new}")
logger.info(f"   - Total en mémoire: {len(sent_ids)}")
logger.info(f"📁 Fichiers de debug:")
logger.info(f"   - Logs: /app/logs/netflix_bot_debug.log")
logger.info(f"   - API Debug: {DEBUG_API_FILE}")
logger.info("="*80)
