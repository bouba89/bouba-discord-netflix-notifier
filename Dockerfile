FROM python:3.14-alpine

LABEL maintainer="bouba89"
LABEL description="Bot Discord Netflix Notifier - Version 3.0 (API mdblist complète)"
LABEL version="3.0.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Europe/Paris

# 🔐 Dépendances système + fix CVE
RUN apk add --no-cache \
        dcron \
        tzdata \
        curl \
        bash && \
    apk upgrade --no-cache && \
    cp /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt .

# 🔐 Fix vuln Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY netflix_bot_v3.py netflix_bot.py
COPY web_interface.py .
COPY templates/ templates/
COPY crontab.txt .
COPY start.sh .

RUN chmod +x /app/start.sh && \
    mkdir -p /app/data /app/logs

VOLUME ["/app/data", "/app/logs"]

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["/app/start.sh"]
