#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netflix Bot - Interface Web Flask avec Authentification
Interface de monitoring et configuration du bot Netflix
"""

from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)

# Configuration de sécurité
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'netflix-bot-super-secret-key-change-me-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuration
DATA_DIR = "/app/data"
LOGS_DIR = "/app/logs"
MEMORY_FILE = f"{DATA_DIR}/sent_ids.json"
DEBUG_API_FILE = f"{DATA_DIR}/api_responses_debug.json"
LOG_FILE = f"{LOGS_DIR}/netflix_bot_debug.log"
CRON_LOG_FILE = f"{LOGS_DIR}/cron.log"
ENV_FILE = "/app/.env_for_cron"
USERS_FILE = f"{DATA_DIR}/users.json"

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
        'service': 'netflix-bot-web'
    }), 200

@app.route('/api/status')
@login_required
def get_status():
    """API: Récupérer le statut du bot"""
    try:
        # Vérifier si cron tourne (compatible Alpine)
        import subprocess
        try:
            result = subprocess.run(['pgrep', 'crond'], capture_output=True, timeout=5)
            cron_running = result.returncode == 0
        except:
            # Fallback : vérifier les fichiers PID classiques
            cron_running = os.path.exists('/var/run/crond.pid') or os.path.exists('/var/run/cron.pid')
        
        # Récupérer les variables d'environnement
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
            with open(MEMORY_FILE, 'r') as f:
                sent_ids = json.load(f)
                sent_count = len(sent_ids)
        
        # Dernière exécution depuis les logs (format propre)
        last_run = "Jamais"
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if "🏁 TERMINÉ" in line:
                        try:
                            # Format original: 2026-02-01 03:06:18,418 - INFO - 🏁 TERMINÉ
                            timestamp_str = line.split(' - ')[0]
                            # Parser et reformater proprement
                            dt = datetime.strptime(timestamp_str.split(',')[0], '%Y-%m-%d %H:%M:%S')
                            last_run = dt.strftime('%d/%m/%Y %H:%M:%S')  # Format français propre
                        except:
                            last_run = timestamp_str  # Fallback si parsing échoue
                        break
        
        return jsonify({
            'status': 'running' if cron_running else 'stopped',
            'cron_active': cron_running,
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
    """API: Récupérer les statistiques détaillées"""
    try:
        stats = {
            'total_content': 0,
            'by_country': {},
            'by_country_total': {},  # ← NOUVEAU : Stats cumulées par pays
            'recent_notifications': [],
            'last_run': {
                'total_treated': 0,
                'new_sent': 0,
                'date': 'N/A'
            }
        }
        
        # Lire les IDs envoyés
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                sent_ids = json.load(f)
                stats['total_content'] = len(sent_ids)
        
        # ✅ NOUVEAU : Analyser tous les logs pour stats cumulées par pays
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Stats cumulées (tous les runs)
            country_totals = {}
            
            # Stats du dernier run uniquement
            current_country = None
            last_run_countries = {}
            in_last_run = False
            
            for line in lines:
                # Détecter le début du dernier run
                if "🎬 Netflix Bot - " in line:
                    in_last_run = True
                    last_run_countries = {}
                    current_country = None
                
                # Stats cumulées (tous les runs)
                if "📨 ENVOI DISCORD POUR" in line:
                    try:
                        country = line.split("📨 ENVOI DISCORD POUR")[1].strip()
                        if country not in country_totals:
                            country_totals[country] = 0
                    except:
                        pass
                
                if "nouveaux titres (non envoyés)" in line and "✨" in line:
                    try:
                        # Extraire le nombre
                        count = int(line.split("✨")[1].split("nouveaux")[0].strip())
                        
                        # Pour le dernier run
                        if in_last_run and current_country:
                            last_run_countries[current_country] = count
                        
                        # Pour les stats cumulées
                        if current_country and count > 0:
                            if current_country not in country_totals:
                                country_totals[current_country] = 0
                            country_totals[current_country] += count
                    except:
                        pass
                
                if "TRAITEMENT DU PAYS:" in line:
                    try:
                        country = line.split("TRAITEMENT DU PAYS:")[1].strip()
                        current_country = country
                    except:
                        pass
            
            # Parser le dernier run pour infos détaillées
            for line in reversed(lines[-500:]):
                if "Contenus traités:" in line or "Pays traités:" in line:
                    try:
                        stats['last_run']['total_treated'] = int(line.split(":")[1].split()[0])
                    except:
                        pass
                
                if "Nouveaux envoyés:" in line:
                    try:
                        stats['last_run']['new_sent'] = int(line.split("Nouveaux envoyés:")[1].split()[0])
                    except:
                        pass
                
                if "🏁 TERMINÉ" in line:
                    try:
                        timestamp_str = line.split(' - ')[0]
                        dt = datetime.strptime(timestamp_str.split(',')[0], '%Y-%m-%d %H:%M:%S')
                        stats['last_run']['date'] = dt.strftime('%d/%m/%Y %H:%M:%S')
                    except:
                        stats['last_run']['date'] = timestamp_str
                    break
            
            stats['by_country'] = last_run_countries
            stats['by_country_total'] = country_totals
        
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
        
        with open(log_file, 'r') as f:
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
            ['/app/run_netflix.sh'],
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
    """API: Voir/Modifier la configuration"""
    if request.method == 'GET':
        try:
            config_data = {}
            
            # Liste des variables à afficher (whitelist)
            allowed_vars = ['COUNTRIES', 'DISCORD_WEBHOOK', 'RAPIDAPI_KEY', 'TMDB_API_KEY', 'FLASK_SECRET_KEY']
            
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            
                            # Filtrer : garder uniquement les variables importantes
                            if key in allowed_vars:
                                # Masquer les clés sensibles
                                if 'KEY' in key or 'WEBHOOK' in key or 'SECRET' in key:
                                    config_data[key] = value[:10] + '***' if len(value) > 10 else '***'
                                else:
                                    config_data[key] = value
            
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        return jsonify({'error': 'Modification non implémentée pour la sécurité'}), 501

@app.route('/api/config/countries', methods=['GET', 'POST'])
@login_required
def config_countries():
    """API: Gérer la configuration des pays"""
    if request.method == 'GET':
        try:
            countries = []
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    for line in f:
                        if line.startswith('COUNTRIES='):
                            countries_str = line.split('=', 1)[1].strip()
                            countries = [c.strip() for c in countries_str.split(',')]
                            break
            return jsonify({'countries': countries})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            new_countries = request.json.get('countries', [])
            
            if not new_countries:
                return jsonify({'success': False, 'error': 'Au moins un pays requis'}), 400
            
            # Valider les codes pays (2 lettres en majuscules)
            for country in new_countries:
                if not country.isalpha() or len(country) != 2:
                    return jsonify({'success': False, 'error': f'Code pays invalide: {country}'}), 400
            
            # Lire le fichier .env
            env_lines = []
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    env_lines = f.readlines()
            
            # Mettre à jour la ligne COUNTRIES
            countries_str = ','.join([c.upper() for c in new_countries])
            updated = False
            for i, line in enumerate(env_lines):
                if line.startswith('COUNTRIES='):
                    env_lines[i] = f'COUNTRIES={countries_str}\n'
                    updated = True
                    break
            
            # Si COUNTRIES n'existe pas, l'ajouter
            if not updated:
                env_lines.append(f'COUNTRIES={countries_str}\n')
            
            # Sauvegarder
            with open(ENV_FILE, 'w') as f:
                f.writelines(env_lines)
            
            return jsonify({'success': True, 'countries': new_countries})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config/cron', methods=['GET', 'POST'])
@login_required
def config_cron():
    """API: Gérer la configuration du cron"""
    if request.method == 'GET':
        try:
            # Lire le crontab actuel
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'run_netflix.sh' in line and not line.startswith('#'):
                        # Parser la ligne cron
                        parts = line.split()
                        if len(parts) >= 5:
                            return jsonify({
                                'minute': parts[0],
                                'hour': parts[1],
                                'enabled': True
                            })
            return jsonify({'minute': '0', 'hour': '8', 'enabled': False})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            hour = request.json.get('hour', '8')
            minute = request.json.get('minute', '0')
            
            # Valider
            try:
                hour_int = int(hour)
                minute_int = int(minute)
                if not (0 <= hour_int <= 23) or not (0 <= minute_int <= 59):
                    raise ValueError()
            except:
                return jsonify({'success': False, 'error': 'Heure invalide'}), 400
            
            # Lire le fichier crontab.txt
            crontab_path = '/app/crontab.txt'
            if os.path.exists(crontab_path):
                with open(crontab_path, 'r') as f:
                    lines = f.readlines()
                
                # Mettre à jour la ligne du cron
                for i, line in enumerate(lines):
                    if 'run_netflix.sh' in line and not line.strip().startswith('#'):
                        # Remplacer les deux premiers champs (minute et heure)
                        parts = line.split()
                        if len(parts) >= 5:
                            parts[0] = minute
                            parts[1] = hour
                            lines[i] = ' '.join(parts) + '\n'
                            break
                
                # Sauvegarder
                with open(crontab_path, 'w') as f:
                    f.writelines(lines)
                
                # Réinstaller le crontab
                subprocess.run(['crontab', crontab_path], check=True)
                
                # Redémarrer cron
                subprocess.run(['service', 'cron', 'restart'], check=True)
                
                return jsonify({'success': True, 'hour': hour, 'minute': minute})
            else:
                return jsonify({'success': False, 'error': 'Fichier crontab.txt introuvable'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
@login_required
def reset_memory():
    """API: Réinitialiser la mémoire (anti-doublons)"""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump([], f)
        return jsonify({'success': True, 'message': 'Mémoire réinitialisée'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug')
@login_required
def get_debug():
    """API: Récupérer les données de debug API"""
    try:
        if not os.path.exists(DEBUG_API_FILE):
            return jsonify({'data': []})
        
        with open(DEBUG_API_FILE, 'r') as f:
            debug_data = json.load(f)
            return jsonify({'data': debug_data[-20:]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/logs/<log_type>')
@login_required
def download_logs(log_type):
    """Télécharger les logs"""
    try:
        if log_type == 'debug':
            return send_file(LOG_FILE, as_attachment=True, download_name='netflix_bot_debug.log')
        elif log_type == 'cron':
            return send_file(CRON_LOG_FILE, as_attachment=True, download_name='cron.log')
        elif log_type == 'api':
            return send_file(DEBUG_API_FILE, as_attachment=True, download_name='api_debug.json')
        else:
            return "Type de log inconnu", 404
    except Exception as e:
        return str(e), 500

# ============================================================================
# TEMPLATE HTML
# ============================================================================

@app.route('/templates/index.html')
@login_required
def serve_template():
    """Servir le template (pour dev)"""
    return render_template('index.html', username=session.get('username'))

@app.route('/settings')
@login_required
def settings():
    """Page de configuration"""
    return render_template('settings.html', username=session.get('username'))

if __name__ == '__main__':
    # Créer le dossier templates s'il n'existe pas
    os.makedirs('templates', exist_ok=True)
    
    # Lancer Flask en mode debug sur toutes les interfaces
    print("=" * 60)
    print("🎬 Netflix Bot - Interface Web")
    print("=" * 60)
    print("🌐 Interface accessible sur: http://localhost:5000")
    print("👤 Compte par défaut: admin / admin123")
    print("⚠️  CHANGEZ LE MOT DE PASSE IMMÉDIATEMENT!")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
