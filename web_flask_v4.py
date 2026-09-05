#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netflix + Disney Bot v4 - Interface Web Flask avec Authentification
"""

from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'streaming-bot-v4-super-secret-key-change-me')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuration
DATA_DIR      = "/app/data"
LOGS_DIR      = "/app/logs"
MEMORY_FILE   = f"{DATA_DIR}/sent_ids.json"
LOG_FILE      = f"{LOGS_DIR}/netflix_bot.log"
CRON_LOG_FILE = f"{LOGS_DIR}/cron.log"
ENV_FILE      = "/app/.env_for_cron"
USERS_FILE    = f"{DATA_DIR}/users.json"

# ── Plateformes supportées (pour les stats de mémoire) ──────────────────────
PLATFORMS = {
    "netflix": {"label": "Netflix", "emoji": "🎬", "color": "#E50914"},
    "disney":  {"label": "Disney+", "emoji": "✨", "color": "#113CCF"},
}

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def init_users_file():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "admin": {
                "password": generate_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        }
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)
        print("⚠️  Compte admin par défaut créé: admin / admin123")

init_users_file()

# ============================================================================
# AUTH
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Non authentifié', 'redirect': '/login'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def verify_user(username, password):
    users = get_users()
    if username in users:
        return check_password_hash(users[username]['password'], password)
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        if verify_user(username, password):
            session['username'] = username
            session['role'] = get_users()[username].get('role', 'user')
            if remember:
                session.permanent = True
            users = get_users()
            users[username]['last_login'] = datetime.now().isoformat()
            save_users(users)
            return redirect(url_for('index'))
        return render_template('login.html', error='Identifiants incorrects')
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        current_password = request.json.get('current_password')
        new_password     = request.json.get('new_password')
        username         = session.get('username')
        users = get_users()
        if not check_password_hash(users[username]['password'], current_password):
            return jsonify({'success': False, 'error': 'Mot de passe actuel incorrect'}), 401
        users[username]['password'] = generate_password_hash(new_password)
        users[username]['password_changed_at'] = datetime.now().isoformat()
        save_users(users)
        return jsonify({'success': True, 'message': 'Mot de passe changé avec succès'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ROUTES PRINCIPALES
# ============================================================================

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'streaming-bot-v4-web',
        'version': '4.0'
    }), 200

@app.route('/api/status')
@login_required
def get_status():
    try:
        try:
            result = subprocess.run(['pgrep', '-f', 'cron'], capture_output=True, timeout=5)
            cron_running = result.returncode == 0
        except:
            cron_running = (
                os.path.exists('/var/run/crond.pid') or
                os.path.exists('/var/run/cron.pid')
            )

        env_vars = {}
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if 'KEY' in key or 'WEBHOOK' in key:
                            env_vars[key] = value[:10] + '***' if len(value) > 10 else '***'
                        else:
                            env_vars[key] = value

        # ── Comptage par plateforme ──────────────────────────────────────────
        sent_count   = 0
        by_platform  = {k: 0 for k in PLATFORMS}

        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    sent_ids = json.load(f)
                if isinstance(sent_ids, dict):
                    sent_count = len(sent_ids)
                    for key in sent_ids:
                        for pf in PLATFORMS:
                            if key.startswith(f"{pf}:"):
                                by_platform[pf] += 1
                                break
                        else:
                            # ancienne clé sans préfixe → comptée comme netflix
                            by_platform["netflix"] += 1
            except:
                pass

        last_run = "Jamais"
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            for line in reversed(lines):
                if "✨ Traitement terminé" in line:
                    try:
                        ts = line.split(' - ')[0]
                        dt = datetime.strptime(ts.split(',')[0], '%Y-%m-%d %H:%M:%S')
                        last_run = dt.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        last_run = line.split(' - ')[0]
                    break

        return jsonify({
            'status':      'running' if cron_running else 'stopped',
            'cron_active': cron_running,
            'version':     '4.0',
            'api_source':  'mdblist.com',
            'environment': env_vars,
            'statistics': {
                'total_sent':   sent_count,
                'by_platform':  by_platform,
                'last_run':     last_run,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
@login_required
def get_stats():
    try:
        stats = {
            'total_content': 0,
            'by_platform':   {k: 0 for k in PLATFORMS},
            'recent_notifications': [],
            'last_run': {
                'movies_found': 0,
                'shows_found':  0,
                'new_sent':     0,
                'date':         'N/A'
            }
        }

        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    sent_ids = json.load(f)
                if isinstance(sent_ids, dict):
                    stats['total_content'] = len(sent_ids)
                    for key in sent_ids:
                        for pf in PLATFORMS:
                            if key.startswith(f"{pf}:"):
                                stats['by_platform'][pf] += 1
                                break
                        else:
                            stats['by_platform']['netflix'] += 1
            except:
                pass

        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line in reversed(lines[-200:]):
                # Nouveau format v4 : "➕ Nouveau(elle) movie: Titre (2025)"
                if "➕ Nouveau" in line and "movie" in line.lower():
                    stats['last_run']['movies_found'] += 1
                if "➕ Nouveau" in line and "show" in line.lower():
                    stats['last_run']['shows_found'] += 1
                if "nouveautés envoyées" in line:
                    try:
                        stats['last_run']['new_sent'] += int(
                            line.split("✅")[1].split("nouveauté")[0].strip()
                        )
                    except:
                        pass
                if "✨ Traitement terminé" in line:
                    try:
                        ts = line.split(' - ')[0]
                        dt = datetime.strptime(ts.split(',')[0], '%Y-%m-%d %H:%M:%S')
                        stats['last_run']['date'] = dt.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        stats['last_run']['date'] = line.split(' - ')[0]
                    break

        return jsonify(stats)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/logs')
@login_required
def get_logs():
    try:
        log_type = request.args.get('type', 'debug')
        lines    = int(request.args.get('lines', 100))
        log_file = CRON_LOG_FILE if log_type == 'cron' else LOG_FILE
        if not os.path.exists(log_file):
            return jsonify({'logs': 'Aucun log disponible'})
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
        return jsonify({'logs': ''.join(all_lines[-lines:] if len(all_lines) > lines else all_lines)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Lancement manuel ─────────────────────────────────────────────────────────

@app.route('/api/run', methods=['POST'])
@login_required
def run_bot():
    """Exécute netflix_bot_v4.py (Netflix + Disney+) manuellement."""
    try:
        result = subprocess.run(
            ['python3', '/app/netflix_bot_v4.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error':  result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout (>5min)'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── Config ───────────────────────────────────────────────────────────────────

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def config():
    if request.method == 'GET':
        try:
            config_data  = {}
            allowed_vars = ['DISCORD_WEBHOOK', 'MDBLIST_API_KEY', 'TMDB_API_KEY', 'DAYS_BACK']
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key in allowed_vars:
                                config_data[key] = (
                                    value[:10] + '***' if ('KEY' in key or 'WEBHOOK' in key) and len(value) > 10
                                    else value
                                )
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Modification via API non implémentée pour la sécurité'}), 501

@app.route('/api/config/days_back', methods=['GET', 'POST'])
@login_required
def config_days_back():
    if request.method == 'GET':
        try:
            days_back = 7
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    for line in f:
                        if line.startswith('DAYS_BACK='):
                            days_back = int(line.split('=')[1].strip())
                            break
            return jsonify({'days_back': days_back})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    try:
        new_days = int(request.json.get('days_back', 7))
        if not (1 <= new_days <= 30):
            return jsonify({'success': False, 'error': 'DAYS_BACK doit être entre 1 et 30'}), 400
        env_lines = []
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f:
                env_lines = f.readlines()
        updated = False
        for i, line in enumerate(env_lines):
            if line.startswith('DAYS_BACK='):
                env_lines[i] = f'DAYS_BACK={new_days}\n'
                updated = True
                break
        if not updated:
            env_lines.append(f'DAYS_BACK={new_days}\n')
        with open(ENV_FILE, 'w') as f:
            f.writelines(env_lines)
        return jsonify({'success': True, 'days_back': new_days})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── Reset mémoire complète ────────────────────────────────────────────────────

@app.route('/api/reset', methods=['POST'])
@login_required
def reset_memory():
    logger = logging.getLogger(__name__)
    try:
        ids_before     = 0
        titles_deleted = []
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    old_data = json.load(f)
                if isinstance(old_data, dict):
                    ids_before     = len(old_data)
                    titles_deleted = [v.get('title', 'Inconnu') for v in old_data.values() if isinstance(v, dict)]
            except:
                pass

        logger.info("=" * 60)
        logger.info(f"🔄 RESET MÉMOIRE par {session.get('username')} — {ids_before} IDs supprimés")
        logger.info("=" * 60)

        with open(MEMORY_FILE, 'w') as f:
            json.dump({}, f)

        return jsonify({
            'success': True,
            'message': f'Mémoire réinitialisée : {ids_before} IDs supprimés',
            'details': {'ids_deleted': ids_before, 'sample_titles': titles_deleted[:5]}
        })
    except Exception as e:
        logger.error(f"❌ Erreur reset: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ── Cron ─────────────────────────────────────────────────────────────────────

@app.route('/api/config/cron', methods=['GET', 'POST'])
@login_required
def config_cron():
    if request.method == 'GET':
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip() and not line.strip().startswith('#'):
                        if any(k in line for k in ['netflix_bot_v4', 'netflix', 'bot']):
                            parts = line.split()
                            if len(parts) >= 5:
                                try:
                                    return jsonify({'hour': int(parts[1]), 'minute': int(parts[0]), 'enabled': True})
                                except:
                                    pass
            return jsonify({'hour': 9, 'minute': 0, 'enabled': False})
        except Exception as e:
            return jsonify({'hour': 9, 'minute': 0, 'enabled': False, 'error': str(e)})

    try:
        data   = request.json
        hour   = int(data.get('hour', 9))
        minute = int(data.get('minute', 0))
        if not (0 <= hour <= 23):
            return jsonify({'success': False, 'error': 'Heure invalide (0-23)'}), 400
        if not (0 <= minute <= 59):
            return jsonify({'success': False, 'error': 'Minute invalide (0-59)'}), 400

        # ← pointe vers netflix_bot_v4.py
        cron_line = (
            f"{minute} {hour} * * * cd /app && "
            f"export $(cat /app/.env_for_cron | xargs) && "
            f"/usr/local/bin/python3 netflix_bot_v4.py >> /app/logs/cron.log 2>&1"
        )
        with open('/tmp/new_crontab', 'w') as f:
            f.write(cron_line + '\n')
        result = subprocess.run(['crontab', '/tmp/new_crontab'], capture_output=True, timeout=5)
        if os.path.exists('/tmp/new_crontab'):
            os.remove('/tmp/new_crontab')
        if result.returncode == 0:
            return jsonify({'success': True, 'hour': hour, 'minute': minute})
        return jsonify({'success': False, 'error': 'Erreur mise à jour crontab'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ── Cache / Purge ─────────────────────────────────────────────────────────────

@app.route('/api/cache/stats')
@login_required
def cache_stats():
    try:
        days_back = 7
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    if line.startswith('DAYS_BACK='):
                        try:
                            days_back = int(line.split('=')[1].strip())
                        except:
                            pass
                        break

        if not os.path.exists(MEMORY_FILE):
            return jsonify({'total': 0, 'fresh': 0, 'expired': 0, 'by_platform': {k: 0 for k in PLATFORMS}})

        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return jsonify({'total': len(data), 'fresh': 0, 'expired': 0, 'by_platform': {}})

        cutoff     = datetime.now() - timedelta(days=days_back)
        fresh      = 0
        expired    = 0
        by_platform = {k: 0 for k in PLATFORMS}

        for key, v in data.items():
            # comptage par plateforme
            for pf in PLATFORMS:
                if key.startswith(f"{pf}:"):
                    by_platform[pf] += 1
                    break
            else:
                by_platform['netflix'] += 1   # rétrocompat

            # frais vs expiré
            try:
                if datetime.fromisoformat(v["sent_at"]) > cutoff:
                    fresh += 1
                else:
                    expired += 1
            except:
                expired += 1

        return jsonify({'total': len(data), 'fresh': fresh, 'expired': expired, 'by_platform': by_platform})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cache/purge', methods=['POST'])
@login_required
def cache_purge():
    logger = logging.getLogger(__name__)
    mode = request.args.get('mode', 'partial')

    try:
        days_back = 7
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r') as f:
                for line in f:
                    if line.startswith('DAYS_BACK='):
                        try:
                            days_back = int(line.split('=')[1].strip())
                        except:
                            pass
                        break

        data = {}
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
            except:
                data = {}

        original_count = len(data)
        os.makedirs(DATA_DIR, exist_ok=True)

        if mode == 'full':
            with open(MEMORY_FILE, 'w') as f:
                json.dump({}, f)
            logger.info(f"💥 PURGE TOTALE par {session.get('username')} — {original_count} IDs supprimés")
            return jsonify({'success': True, 'message': f'{original_count} entrée(s) supprimée(s). Cache vidé.'})

        # partial
        cutoff  = datetime.now() - timedelta(days=days_back)
        cleaned = {
            k: v for k, v in data.items()
            if (lambda: (
                datetime.fromisoformat(v.get("sent_at", "")) > cutoff
                if isinstance(v, dict) and v.get("sent_at") else False
            ))()
        }
        purged = original_count - len(cleaned)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(cleaned, f, indent=2)
        logger.info(f"🧹 PURGE PARTIELLE par {session.get('username')} — {purged} expirés, {len(cleaned)} conservés")
        return jsonify({'success': True, 'message': f'{purged} entrée(s) expirée(s) supprimée(s). {len(cleaned)} conservée(s).'})

    except Exception as e:
        logger.error(f"❌ Erreur purge: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ── Download & Pages ──────────────────────────────────────────────────────────

@app.route('/download/logs/<log_type>')
@login_required
def download_logs(log_type):
    try:
        if log_type == 'debug':
            return send_file(LOG_FILE, as_attachment=True, download_name='streaming_bot_v4.log')
        elif log_type == 'cron':
            return send_file(CRON_LOG_FILE, as_attachment=True, download_name='cron.log')
        return "Type de log inconnu", 404
    except Exception as e:
        return str(e), 500

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', username=session.get('username'))

# ── API : liste des plateformes (pour le frontend) ────────────────────────────

@app.route('/api/platforms')
@login_required
def get_platforms():
    """Retourne la liste des plateformes configurées (utile pour le dashboard)."""
    return jsonify(PLATFORMS)

# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    print("=" * 60)
    print("🎬 Streaming Bot v4.0 - Netflix + Disney+")
    print("=" * 60)
    print("🌐 Interface: http://localhost:5000")
    print("👤 Login: admin / admin123")
    print("⚠️  CHANGEZ LE MOT DE PASSE!")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
    
