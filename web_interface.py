#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netflix Bot - Interface Web Flask
Interface de monitoring et configuration du bot Netflix
"""

from flask import Flask, render_template, jsonify, request, send_file
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Configuration
DATA_DIR = "/app/data"
LOGS_DIR = "/app/logs"
MEMORY_FILE = f"{DATA_DIR}/sent_ids.json"
DEBUG_API_FILE = f"{DATA_DIR}/api_responses_debug.json"
LOG_FILE = f"{LOGS_DIR}/netflix_bot_debug.log"
CRON_LOG_FILE = f"{LOGS_DIR}/cron.log"
ENV_FILE = "/app/.env_for_cron"

# ============================================================================
# ROUTES PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil - Dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """API: Récupérer le statut du bot"""
    try:
        # Vérifier si cron tourne
        cron_running = os.path.exists('/var/run/crond.pid')
        
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
        
        # Dernière exécution depuis les logs
        last_run = "Jamais"
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if "🏁 TERMINÉ" in line:
                        # Extraire la date du log
                        try:
                            timestamp = line.split(' - ')[0]
                            last_run = timestamp
                        except:
                            pass
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
def get_stats():
    """API: Récupérer les statistiques détaillées"""
    try:
        stats = {
            'total_content': 0,
            'by_country': {},
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
        
        # Lire les logs pour extraire les stats
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            current_country = None
            
            # Parcourir les logs en sens inverse pour avoir les stats les plus récentes
            for line in reversed(lines[-500:]):  # Dernières 500 lignes
                # Extraire les stats du dernier run
                if "Contenus traités:" in line:
                    try:
                        stats['last_run']['total_treated'] = int(line.split("Contenus traités:")[1].split()[0])
                    except:
                        pass
                
                if "Nouveaux envoyés:" in line:
                    try:
                        stats['last_run']['new_sent'] = int(line.split("Nouveaux envoyés:")[1].split()[0])
                    except:
                        pass
                
                if "🏁 TERMINÉ" in line:
                    try:
                        timestamp = line.split(' - ')[0]
                        stats['last_run']['date'] = timestamp
                    except:
                        pass
                
                # Stats par pays (recherche dans l'ordre chronologique)
                if "TRAITEMENT DU PAYS:" in line:
                    try:
                        country = line.split("TRAITEMENT DU PAYS:")[1].strip()
                        current_country = country
                        if country not in stats['by_country']:
                            stats['by_country'][country] = 0
                    except:
                        pass
                
                if "nouveaux titres (non envoyés)" in line and current_country:
                    try:
                        # Format: "✨ X nouveaux titres (non envoyés)"
                        count = int(line.split("✨")[1].split("nouveaux")[0].strip())
                        stats['by_country'][current_country] = count
                    except:
                        pass
        
        return jsonify(stats)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/logs')
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
def config():
    """API: Voir/Modifier la configuration"""
    if request.method == 'GET':
        try:
            config_data = {}
            if os.path.exists(ENV_FILE):
                with open(ENV_FILE, 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            # Masquer les clés sensibles
                            if 'KEY' in key or 'WEBHOOK' in key:
                                config_data[key] = value[:10] + '***'
                            else:
                                config_data[key] = value
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        return jsonify({'error': 'Modification non implémentée pour la sécurité'}), 501

@app.route('/api/reset', methods=['POST'])
def reset_memory():
    """API: Réinitialiser la mémoire (anti-doublons)"""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump([], f)
        return jsonify({'success': True, 'message': 'Mémoire réinitialisée'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug')
def get_debug():
    """API: Récupérer les données de debug API"""
    try:
        if not os.path.exists(DEBUG_API_FILE):
            return jsonify({'data': []})
        
        with open(DEBUG_API_FILE, 'r') as f:
            debug_data = json.load(f)
            # Limiter à 20 dernières requêtes pour ne pas surcharger
            return jsonify({'data': debug_data[-20:]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/logs/<log_type>')
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
# TEMPLATES HTML
# ============================================================================

@app.route('/templates/index.html')
def serve_template():
    """Servir le template (pour dev)"""
    return render_template('index.html')

if __name__ == '__main__':
    # Créer le dossier templates s'il n'existe pas
    os.makedirs('templates', exist_ok=True)
    
    # Lancer Flask en mode debug sur toutes les interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
