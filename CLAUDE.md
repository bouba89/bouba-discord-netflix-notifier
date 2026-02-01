# CLAUDE.md - AI Assistant Guidelines

## Project Overview

**Bouba Discord Netflix Notifier** is a Python-based Discord bot that automatically notifies users of new Netflix releases across multiple countries. It features a modern web dashboard for monitoring and configuration.

**Tech Stack:**
- Python 3.11
- Flask (web framework)
- Docker & Docker Compose
- Cron (scheduled execution)
- External APIs: UNOGS (Netflix data), TMDB (enrichment), Discord Webhooks

## Project Structure

```
bouba-discord-netflix-notifier/
├── netflix_bot.py          # Core bot logic (fetches Netflix data, sends Discord notifications)
├── web_interface.py        # Flask web server (dashboard, API, authentication)
├── templates/              # Flask HTML templates
│   ├── login.html          # Authentication page
│   ├── index.html          # Dashboard
│   └── settings.html       # Configuration page
├── data/                   # Persistent data (mounted volume)
│   └── sent_ids.json       # Anti-duplicate tracker
├── logs/                   # Application logs (mounted volume)
│   ├── cron.log
│   └── netflix_bot.log
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Multi-container orchestration
├── start.sh                # Container startup script
├── crontab.txt             # Cron schedule configuration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # User documentation (French)
```

## Key Components

### netflix_bot.py (414 lines)
Main bot engine that:
- Fetches titles from UNOGS API (Netflix catalog)
- Filters by country availability and recency (last 24 hours)
- Checks against `sent_ids.json` to prevent duplicates
- Enriches data via TMDB API (posters, synopses, ratings)
- Sends formatted Discord embeds via webhook

**Key functions:**
- `fetch_titles()` - Retrieves titles from UNOGS API
- `is_available_in_country()` - Checks country availability
- `enrich_with_tmdb()` - Fetches movie/series details
- `send_discord()` - Formats and sends Discord messages
- `save_api_debug()` - Logs API interactions

### web_interface.py (548 lines)
Flask-based web dashboard providing:
- User authentication with bcrypt password hashing
- Real-time status monitoring and statistics
- Log viewing and downloading
- Manual bot execution
- Cron schedule configuration
- Country/region management

**Key routes:**
- `/login` - Authentication
- `/` - Main dashboard
- `/settings` - Configuration
- `/api/status`, `/api/stats` - Bot status and statistics
- `/api/run` - Manual bot execution
- `/api/config/*` - Configuration management

## Development Commands

### Build and Run
```bash
# Build and start container
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

### Manual Execution
```bash
# Run bot manually inside container
docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py

# Or via web interface: POST /api/run
```

### Container Shell Access
```bash
docker exec -it bouba_discord_netflix_notifier bash
```

## Environment Variables

Required in `.env` file (copy from `.env.example`):
```env
RAPIDAPI_KEY=<UNOGS API key from RapidAPI>
TMDB_API_KEY=<TMDB API key>
DISCORD_WEBHOOK=<Discord webhook URL>
FLASK_SECRET_KEY=<random hex string for Flask sessions>
COUNTRIES=FR,US,CA  # Comma-separated country codes
```

## Code Conventions

### Python Style
- Use `snake_case` for functions and variables
- Use `UPPERCASE` for constants
- Extensive logging with emoji prefixes for visibility
- Try-except blocks with specific exception handling
- Graceful fallbacks (return empty lists/strings on API errors)

### Logging Pattern
```python
logger.info("🎬 Fetching Netflix titles...")
logger.debug(f"📊 Found {len(titles)} titles")
logger.error(f"❌ API error: {e}")
```

### API Integration Pattern
```python
try:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    save_api_debug(filename, data)  # Debug logging
    return data
except Exception as e:
    logger.error(f"API error: {e}")
    save_api_debug(filename, {"error": str(e)})
    return []
```

### Web Interface Design
- Netflix red (#E50914) as primary color
- Dark theme with glassmorphism effects
- Responsive CSS grid layout
- CSS custom properties for theming

## Data Flow

```
UNOGS API → netflix_bot.py → Filter → Enrich (TMDB) → Discord Webhook
                                ↓
                        sent_ids.json (anti-duplicate)
```

## Important Files

| File | Purpose | Notes |
|------|---------|-------|
| `sent_ids.json` | Stores IDs of sent notifications | Prevents duplicates; can be reset via web UI |
| `users.json` | Stores user accounts | Created by web interface; bcrypt hashed passwords |
| `crontab.txt` | Cron schedule | Default: daily at 8:00 AM |
| `.env_for_cron` | Environment for cron jobs | Auto-generated by start.sh |

## Security Considerations

- Default credentials are `admin/admin123` - should be changed in production
- Flask sessions expire after 24 hours
- API keys are masked in web interface responses
- Never commit `.env` file (it's in `.gitignore`)
- Use strong `FLASK_SECRET_KEY` for session security

## Testing

No formal test suite. Manual testing via:
1. Run bot: `docker exec -it bouba_discord_netflix_notifier python /app/netflix_bot.py`
2. Check logs in `./logs/netflix_bot.log`
3. Verify Discord notifications in target channel
4. Access web dashboard at `http://localhost:5000`

## Common Tasks for AI Assistants

### Adding a New Country
1. Update the `COUNTRIES` environment variable in `.env`
2. Restart the container or update via web interface `/settings`

### Modifying Discord Embed Format
Edit `send_discord()` function in `netflix_bot.py` (around line 300+)

### Adding New Web API Endpoints
1. Add route in `web_interface.py`
2. Add `@login_required` decorator if authentication needed
3. Follow existing pattern for JSON responses

### Changing Cron Schedule
1. Edit `crontab.txt` for default schedule
2. Or use web interface `/settings` to modify at runtime

### Debugging API Issues
1. Check `logs/netflix_bot.log` for detailed API responses
2. Look for `save_api_debug()` output files
3. Verify API keys are valid and have quota remaining

## Architecture Notes

- **Containerized:** Runs in Docker with volume mounts for data persistence
- **Two-process model:** Bot runs in background, Flask runs in foreground
- **Stateless bot:** All state stored in `sent_ids.json`
- **Timezone:** Configured for Europe/Paris in docker-compose.yml

## Documentation Language

- README.md is in French
- Code comments are in English
- Maintain this convention for consistency
