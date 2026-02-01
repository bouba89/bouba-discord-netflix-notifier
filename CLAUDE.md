# CLAUDE.md - AI Assistant Guide

This document provides essential context for AI assistants working with the Bouba Discord Netflix Notifier codebase.

## Project Overview

**Bouba Discord Netflix Notifier** is a Python-based Discord bot that automatically notifies Discord servers about new Netflix releases across multiple countries. It features:

- **Discord Webhook Integration**: Sends rich embedded notifications about new Netflix content
- **Flask Web Dashboard**: Netflix-styled interface for monitoring, configuration, and manual bot execution
- **Multi-country Support**: Monitors Netflix releases in 25+ countries simultaneously
- **Duplicate Prevention**: Memory system to prevent sending the same content twice
- **TMDB Enrichment**: Fetches posters, synopses, and ratings from The Movie Database API

**Primary Language**: Python 3.11
**Documentation Language**: French
**Author**: Bouba89

## Repository Structure

```
bouba-discord-netflix-notifier/
├── netflix_bot.py           # Core bot logic (API fetching, filtering, Discord sending)
├── web_interface.py         # Flask web server (auth, dashboard, API endpoints)
├── templates/
│   ├── login.html           # Netflix-styled login page
│   ├── index.html           # Main dashboard
│   └── settings.html        # Configuration interface
├── Dockerfile               # Multi-stage Alpine-based Docker image
├── docker-compose.yml       # Container orchestration
├── start.sh                 # Container initialization script
├── crontab.txt              # Scheduled bot execution (default: 8:00 AM daily)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── data/                    # Persistent data (Docker volume)
│   ├── sent_ids.json        # Anti-duplicate memory (Netflix IDs already sent)
│   └── users.json           # User credentials storage
├── logs/                    # Log files (Docker volume)
│   ├── netflix_bot_debug.log
│   └── cron.log
└── README.md                # User documentation (French)
```

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `netflix_bot.py` | Main bot: UNOGS API calls, TMDB enrichment, Discord webhooks | ~415 |
| `web_interface.py` | Flask app: authentication, dashboard, settings API | ~570 |
| `templates/index.html` | Dashboard with stats, logs, controls | ~1088 |
| `templates/settings.html` | Country and cron configuration UI | ~638 |
| `templates/login.html` | Netflix-style login page | ~438 |

## Technology Stack

### Backend
- **Python 3.11** with Flask 3.0.0
- **Werkzeug 3.0.1** for password hashing (bcrypt)
- **requests 2.31.0** for HTTP API calls
- **python-dotenv 1.0.0** for environment variables

### External APIs
- **UNOGS API** (via RapidAPI): Netflix catalog data
- **TMDB API**: Movie/series metadata enrichment
- **Discord Webhooks**: Notification delivery

### Infrastructure
- **Docker** with multi-stage Alpine build
- **dcron** for scheduled execution
- **Docker Compose** for orchestration

### Frontend
- Vanilla HTML5/CSS3/JavaScript (no frameworks)
- Netflix-inspired dark theme with animations
- Responsive design (mobile/tablet/desktop)

## Development Commands

### Docker Operations
```bash
# Build and start
docker-compose up --build -d

# View logs
docker logs -f bouba_discord_netflix_notifier

# Restart container
docker-compose restart

# Stop container
docker-compose stop

# Enter container shell
docker exec -it bouba_discord_netflix_notifier bash

# Run bot manually
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py

# Check cron status
docker exec -it bouba_discord_netflix_notifier crontab -l
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run web interface
python web_interface.py

# Run bot directly
python netflix_bot.py
```

## Environment Variables

Required in `.env` file:

| Variable | Description |
|----------|-------------|
| `RAPIDAPI_KEY` | UNOGS API key from RapidAPI |
| `TMDB_API_KEY` | The Movie Database API key |
| `DISCORD_WEBHOOK` | Discord webhook URL for notifications |
| `COUNTRIES` | Comma-separated ISO country codes (e.g., `FR,US,CA,GB`) |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions (generate with `secrets.token_hex(32)`) |

## Code Conventions

### Logging
- Uses Python's `logging` module with DEBUG level
- Dual output: file (`logs/netflix_bot_debug.log`) and console
- Emoji prefixes for visual clarity in logs
- API debug responses saved to `logs/api_debug_last_*.json`

### Naming Conventions
- **Variables/Functions**: snake_case (e.g., `sent_ids`, `fetch_titles`)
- **Constants**: UPPERCASE (e.g., `API_KEY`, `WEBHOOK_URL`)
- **Comments**: French language

### Error Handling
- Try-catch blocks around all API calls
- Graceful fallbacks for missing data
- Detailed error messages with context
- Timeouts configured for all HTTP requests

### Security Practices
- Password hashing with bcrypt via Werkzeug
- Session management with 24-hour timeout
- Environment variables for all secrets
- Non-root Docker user (UID 1000)
- API keys masked in logs (first 10 chars + `***`)

## Architecture Patterns

### Bot Execution Flow (netflix_bot.py)
1. Load environment variables and configure logging
2. Load sent_ids.json (anti-duplicate memory)
3. For each configured country:
   - Fetch Netflix catalog from UNOGS API
   - Filter by date (last 7 days)
   - Remove already-sent items
   - Enrich with TMDB data (poster, synopsis, rating)
   - Send to Discord webhook (max 10 embeds per message)
4. Save updated sent_ids.json

### Web Interface Routes (web_interface.py)
- `/` - Dashboard (requires auth)
- `/login`, `/logout` - Authentication
- `/settings` - Configuration page
- `/api/status` - Bot and cron status
- `/api/stats` - Detailed statistics
- `/api/logs` - Log retrieval
- `/api/run` - Manual bot execution
- `/api/config/*` - Configuration management
- `/api/reset` - Memory reset
- `/download/logs/<type>` - Log file downloads
- `/health` - Docker health check endpoint

### Data Persistence
- `data/sent_ids.json`: Array of Netflix IDs already sent
- `data/users.json`: User credentials with hashed passwords
- Docker volumes mount these directories for persistence

## Common Tasks

### Adding a New Country
1. Via web UI: Settings > "Pays a Surveiller" > Add country code
2. Via .env: Add ISO code to `COUNTRIES` variable

### Changing Cron Schedule
1. Via web UI: Settings > Modify hour/minute
2. Manual: Edit `crontab.txt`, reinstall with `crontab /app/crontab.txt`

### Resetting Duplicate Memory
1. Via web UI: Dashboard > "Reset Memoire" button
2. Manual: `echo '[]' > data/sent_ids.json`

### Testing Discord Webhook
Run the bot manually and check logs for webhook responses.

## Known Issues

1. **Flask Debug Mode**: `app.run(debug=True)` in production - should be disabled
2. **Hard-coded Paths**: Many paths assume `/app/` directory (Docker-only)
3. **No Type Hints**: Python code lacks type annotations

## Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change password immediately after first login via the web interface.

## API Rate Limits

- **UNOGS API**: Check RapidAPI plan limits
- **TMDB API**: 40 requests per 10 seconds
- **Discord Webhooks**: 30 requests per 60 seconds per webhook

## File Paths Reference

When working in Docker container, all paths are relative to `/app/`:
- Bot script: `/app/netflix_bot.py`
- Web interface: `/app/web_interface.py`
- Templates: `/app/templates/`
- Data directory: `/app/data/`
- Logs directory: `/app/logs/`
- Crontab: `/app/crontab.txt`

## Testing

No automated test suite exists. Testing is done manually:
1. Run bot with `python netflix_bot.py`
2. Check logs for errors
3. Verify Discord messages received
4. Use web interface to monitor status

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Open Pull Request

## Dependencies

From `requirements.txt`:
```
requests==2.31.0
python-dotenv==1.0.0
Flask==3.0.0
Werkzeug==3.0.1
```
