#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netflix Bot v3 - Interface Web Flask avec Authentification
Interface de monitoring et configuration du bot Netflix (API mdblist)
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

# Configuration de sécurité
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'netflix-bot-v3-super-secret-key-change-me')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuration
DATA_DIR = "/app/data"
LOGS_DIR = "/app/logs"
MEMORY_FILE = f"{DATA_DIR}/sent_ids.json"
LOG_FILE = f"{LOGS_DIR}/netflix_bot.log"
CRON_LOG_FILE = f"{LOGS_DIR}/cron.log"
ENV_FILE = "/app/.env_for_cron"
USERS_FILE = f"{DATA_DIR}/users.json"

# Configurer le logging pour écrire dans le fichier de logs
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Créer le fichier users.json s'il n'existe pas
def init_users_file():
    """Initialiser le fichier users avec un compte admin par défaut"""
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
        print("⚠️  CHANGEZ LE MOT DE PASSE IMMÉDIATEMENT!")

# Initialiser au démarrage
init_users_file()

# ============================================================================
# FONCTIONS D'AUTHENTIFICATION
# ============================================================================

def login_required(f):
    """Décorateur pour protéger les routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            # Si c'est une route API, retourner JSON au lieu de rediriger
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Non authentifié', 'redirect': '/login'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_users():
    """Récupérer tous les utilisateurs"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Sauvegarder les utilisateurs"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def verify_user(username, password):
    """Vérifier les credentials d'un utilisateur"""
    users = get_users()
    if username in users:
        return check_password_hash(users[username]['password'], password)
    return False

# ============================================================================
# ROUTES D'AUTHENTIFICATION
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if verify_user(username, password):
            session['username'] = username
            session['role'] = get_users()[username].get('role', 'user')
            if remember:
                session.permanent = True
            
            # Log de connexion
            users = get_users()
            users[username]['last_login'] = datetime.now().isoformat()
            save_users(users)
            
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Identifiants incorrects')
    
    # Si déjà connecté, rediriger vers le dashboard
    if 'username' in session:
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Changer le mot de passe"""
    try:
        current_password = request.json.get('current_password')
        new_password = request.json.get('new_password')
        username = session.get('username')
        
        users = get_users()
        
        # Vérifier le mot de passe actuel
        if not check_password_hash(users[username]['password'], current_password):
            return jsonify({'success': False, 'error': 'Mot de passe actuel incorrect'}), 401
        
        # Mettre à jour le mot de passe
        users[username]['password'] = generate_password_hash(new_password)
        users[username]['password_changed_at'] = datetime.now().isoformat()
        save_users(users)
        
        return jsonify({'success': True, 'message': 'Mot de passe changé avec succès'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ROUTES PRINCIPALES (PROTÉGÉES)
# ============================================================================

@app.route('/')
@login_required
def index():
    """Page d'accueil - Dashboard"""
    return render_template('index.html', username=session.get('username'))

@app.route('/health')
def health():
    """Healthcheck endpoint pour Docker (public, pas de login requis)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'netflix-bot-v3-web',
        'version': '3.0'
    }), 200

@app.route('/api/status')
@login_required
def get_status():
    """API: Récupérer le statut du bot v3"""
    try:
        # Vérifier si cron tourne (support cron et crond)
        try:
            # Essayer avec pgrep (cherche cron OU crond)
            result = subprocess.run(['pgrep', '-f', 'cron'], capture_output=True, timeout=5)
            cron_running = result.returncode == 0
        except:
            # Fallback : vérifier les fichiers PID
            cron_running = os.path.exists('/var/run/crond.pid') or os.path.exists('/var/run/cron.pid')
        
        # Récupérer les variables d'environnement v3
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
        
        # Récupérer les statistiques
        sent_count = 0
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    sent_ids = json.load(f)
                    if isinstance(sent_ids, (dict, list)):
                        sent_count = len(sent_ids)
            except:
                sent_count = 0
        
        # Dernière exécution depuis les logs
        last_run = "Jamais"
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if "✨ Traitement terminé" in line or "🏁 TERMINÉ" in line:
                        try:
                            timestamp_str = line.split(' - ')[0]
                            dt = datetime.strptime(timestamp_str.split(',')[0], '%Y-%m-%d %H:%M:%S')
                            last_run = dt.strftime('%d/%m/%Y %H:%M:%S')
                        except:
                            last_run = timestamp_str
                        break
        
        return jsonify({
            'status': 'running' if cron_running else 'stopped',
            'cron_active': cron_running,
            'version': '3.0',
            'api_source': 'mdblist.com',
            'environment': env_vars,
            'statistics': {
                'total_sent': sent_count,
                'last_run': last_run
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
@login_required
def get_stats():
    """API: Récupérer les statistiques détaillées v3"""
    try:
        stats = {
            'total_content': 0,
            'recent_notifications': [],
            'last_run': {
                'movies_found': 0,
                'shows_found': 0,
                'new_sent': 0,
                'date': 'N/A'
            }
        }
        
        # Lire les IDs envoyés
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    sent_ids = json.load(f)
                    # Gérer dict ou list
                    if isinstance(sent_ids, dict):
                        stats['total_content'] = len(sent_ids)
                    elif isinstance(sent_ids, list):
                        stats['total_content'] = len(sent_ids)
                    else:
                        stats['total_content'] = 0
            except:
                stats['total_content'] = 0
        
        # Analyser les logs du dernier run
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Parser le dernier run
            for line in reversed(lines[-200:]):
                if "✅ Trouvé" in line and "movies" in line:
                    try:
                        count = int(line.split("✅ Trouvé")[1].split("movies")[0].strip())
                        stats['last_run']['movies_found'] = count
                    except:
                        pass
                
                if "✅ Trouvé" in line and "shows" in line:
                    try:
                        count = int(line.split("✅ Trouvé")[1].split("shows")[0].strip())
                        stats['last_run']['shows_found'] = count
                    except:
                        pass
                
                if "✅" in line and "notifications envoyées" in line:
                    try:
                        count = int(line.split("✅")[1].split("notifications")[0].strip())
                        stats['last_run']['new_sent'] = count
                    except:
                        pass
                
                if "✨ Traitement terminé" in line:
                    try:
                        timestamp_str = line.split(' - ')[0]
                        dt = datetime.strptime(timestamp_str.split(',')[0], '%Y-%m-%d %H:%M:%S')
                        stats['last_run']['date'] = dt.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        stats['last_run']['date'] = timestamp_str
                    break
        
        return jsonify(stats)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/logs')
@login_required
def get_logs():
    """API: Récupérer les logs"""
    try:
        log_type = request.args.get('type', 'debug')
        lines = int(request.args.get('lines', 100))
        
        if log_type == 'cron':
            log_file = CRON_LOG_FILE
        else:
            log_file = LOG_FILE
        
        if not os.path.exists(log_file):
            return jsonify({'logs': 'Aucun log disponible'})
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
        return jsonify({'logs': ''.join(last_lines)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run', methods=['POST'])
@login_required
def run_bot():
    """API: Exécuter le bot manuellement"""
    try:
        result = subprocess.run(
            ['python', '/app/netflix_bot.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout (>5min)'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
@login_required
def config():
    """API: Voir/Modifier la configuration v3"""
    if request.method == 'GET':
        try:
            config_data = {}
            
            # Variables v3
            allowed_vars = ['DISCORD_WEBHOOK', 'MDBLIST_API_KEY', 'TMDB_API_KEY', 'DAYS_BACK']
            
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            
                            if key in allowed_vars:
                                # Masquer les clés sensibles
                                if 'KEY' in key or 'WEBHOOK' in key:
                                    config_data[key] = value[:10] + '***' if len(value) > 10 else '***'
                                else:
                                    config_data[key] = value
            
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        return jsonify({'error': 'Modification via API non implémentée pour la sécurité'}), 501

@app.route('/api/config/days_back', methods=['GET', 'POST'])
@login_required
def config_days_back():
    """API: Gérer DAYS_BACK"""
    if request.method == 'GET':
        try:
            days_back = 1  # Défaut
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    for line in f:
                        if line.startswith('DAYS_BACK='):
                            days_back = int(line.split('=')[1].strip())
                            break
            return jsonify({'days_back': days_back})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            new_days = request.json.get('days_back', 1)
            
            # Valider
            try:
                days_int = int(new_days)
                if not (1 <= days_int <= 30):
                    return jsonify({'success': False, 'error': 'DAYS_BACK doit être entre 1 et 30'}), 400
            except:
                return jsonify({'success': False, 'error': 'Valeur invalide'}), 400
            
            # Lire et mettre à jour
            env_lines = []
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    env_lines = f.readlines()
            
            updated = False
            for i, line in enumerate(env_lines):
                if line.startswith('DAYS_BACK='):
                    env_lines[i] = f'DAYS_BACK={days_int}\n'
                    updated = True
                    break
            
            if not updated:
                env_lines.append(f'DAYS_BACK={days_int}\n')
            
            with open(ENV_FILE, 'w') as f:
                f.writelines(env_lines)
            
            return jsonify({'success': True, 'days_back': days_int})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
@login_required
def reset_memory():
    """API: Réinitialiser la mémoire (anti-doublons)"""
    # Définir logger en premier
    logger = logging.getLogger(__name__)
    
    try:
        # Compter combien d'IDs avant suppression
        ids_before = 0
        titles_deleted = []
        
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    old_data = json.load(f)
                    if isinstance(old_data, dict):
                        ids_before = len(old_data)
                        # Récupérer tous les titres
                        titles_deleted = [v.get('title', 'Inconnu') for k, v in old_data.items() if isinstance(v, dict)]
            except:
                pass
        
        # Logger dans le fichier de logs
        logger.info("=" * 60)
        logger.info("🔄 RÉINITIALISATION DE LA MÉMOIRE")
        logger.info("=" * 60)
        logger.info(f"👤 Utilisateur: {session.get('username', 'inconnu')}")
        logger.info(f"📊 IDs en mémoire: {ids_before}")
        
        if titles_deleted:
            logger.info(f"🎬 Titres supprimés ({len(titles_deleted)}):")
            for title in titles_deleted[:20]:  # Limiter à 20
                logger.info(f"   • {title}")
            if len(titles_deleted) > 20:
                logger.info(f"   ... et {len(titles_deleted) - 20} autres")
        
        # Réinitialiser
        with open(MEMORY_FILE, 'w') as f:
            json.dump({}, f)
        
        logger.info("✅ Mémoire réinitialisée avec succès")
        logger.info("💡 Ces notifications seront renvoyées lors de la prochaine exécution")
        logger.info("=" * 60)
        
        return jsonify({
            'success': True, 
            'message': f'Mémoire réinitialisée : {ids_before} IDs supprimés',
            'details': {
                'ids_deleted': ids_before,
                'sample_titles': titles_deleted[:5]
            }
        })
    except Exception as e:
        logger.error(f"❌ Erreur lors de la réinitialisation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/cron', methods=['GET', 'POST'])
@login_required
def config_cron():
    """API: Configurer le crontab"""
    if request.method == 'GET':
        try:
            # Lire le crontab actuel
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True, timeout=5)
            
            print(f"[DEBUG CRON] returncode: {result.returncode}")
            print(f"[DEBUG CRON] stdout: {result.stdout}")
            
            if result.returncode == 0:
                cron_lines = result.stdout.strip().split('\n')
                print(f"[DEBUG CRON] nombre de lignes: {len(cron_lines)}")
                
                # Chercher la ligne du bot (ignorer les commentaires)
                for line in cron_lines:
                    print(f"[DEBUG CRON] ligne: {line}")
                    if line.strip() and not line.strip().startswith('#'):
                        # Si la ligne contient des mots-clés du bot
                        keywords = ['netflix', 'run_netflix', '.env_for_cron', 'bot']
                        found_keywords = [kw for kw in keywords if kw in line]
                        print(f"[DEBUG CRON] mots-clés trouvés: {found_keywords}")
                        
                        if any(keyword in line for keyword in keywords):
                            parts = line.split()
                            print(f"[DEBUG CRON] parts: {parts[:5]}")
                            if len(parts) >= 5:
                                try:
                                    minute = int(parts[0])
                                    hour = int(parts[1])
                                    print(f"[DEBUG CRON] SUCCÈS - heure: {hour}, minute: {minute}")
                                    return jsonify({
                                        'hour': hour,
                                        'minute': minute,
                                        'enabled': True
                                    })
                                except (ValueError, IndexError) as e:
                                    print(f"[DEBUG CRON] erreur parsing: {e}")
                                    pass
            
            # Par défaut 9h00
            print("[DEBUG CRON] ÉCHEC - retour valeurs par défaut")
            return jsonify({'hour': 9, 'minute': 0, 'enabled': False})
        except Exception as e:
            print(f"[DEBUG CRON] Exception: {e}")
            return jsonify({'hour': 9, 'minute': 0, 'enabled': False, 'error': str(e)})
    
    try:
        data = request.json
        hour = int(data.get('hour', 9))
        minute = int(data.get('minute', 0))
        
        if hour < 0 or hour > 23:
            return jsonify({'success': False, 'error': 'Heure invalide (0-23)'}), 400
        
        if minute < 0 or minute > 59:
            return jsonify({'success': False, 'error': 'Minute invalide (0-59)'}), 400
        
        # Créer la nouvelle ligne crontab
        cron_line = f"{minute} {hour} * * * cd /app && /usr/local/bin/python3 netflix_bot.py >> /app/logs/cron.log 2>&1"
        
        # Mettre à jour le crontab
        with open('/tmp/new_crontab', 'w') as f:
            f.write(cron_line + '\n')
        
        # Installer le nouveau crontab
        result = subprocess.run(['crontab', '/tmp/new_crontab'], capture_output=True, timeout=5)
        
        if result.returncode == 0:
            if os.path.exists('/tmp/new_crontab'):
                os.remove('/tmp/new_crontab')
            return jsonify({'success': True, 'hour': hour, 'minute': minute})
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de la mise à jour du crontab'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/logs/<log_type>')
@login_required
def download_logs(log_type):
    """Télécharger les logs"""
    try:
        if log_type == 'debug':
            return send_file(LOG_FILE, as_attachment=True, download_name='netflix_bot_v3.log')
        elif log_type == 'cron':
            return send_file(CRON_LOG_FILE, as_attachment=True, download_name='cron.log')
        else:
            return "Type de log inconnu", 404
    except Exception as e:
        return str(e), 500

# ============================================================================
# PAGES
# ============================================================================

@app.route('/settings')
@login_required
def settings():
    """Page de configuration"""
    return render_template('settings.html', username=session.get('username'))

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs('templates', exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Lancer Flask
    print("=" * 60)
    print("🎬 Netflix Bot v3.0 - Interface Web")
    print("=" * 60)
    print("🌐 Interface: http://localhost:5000")
    print("👤 Login: admin / admin123")
    print("📡 API: mdblist.com (gratuite)")
    print("⚠️  CHANGEZ LE MOT DE PASSE!")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
