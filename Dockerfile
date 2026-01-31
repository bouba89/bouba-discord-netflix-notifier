FROM python:3.11-slim

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copier les fichiers de dépendances avec les bons droits
COPY --chown=appuser:appuser requirements.txt .

# Mettre à jour pip et installer les dépendances (supprimer le warning root)
RUN pip install --no-cache-dir --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copier le reste des fichiers avec les bons droits
COPY --chown=appuser:appuser . .

# Créer le répertoire data avec les bons droits
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Passer à l'utilisateur non-root
USER appuser

# Exposer le port pour l'interface web
EXPOSE 5000

# Commande de démarrage
CMD ["python3", "netflix_bot.py"]
