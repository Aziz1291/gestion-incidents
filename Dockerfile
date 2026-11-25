# 1. Image de base : on ne part jamais de zéro
FROM python:3.12-slim

# Relie l'image publiée dans GHCR au dépôt GitHub (affiché dans l'onglet Packages)
LABEL org.opencontainers.image.source="https://github.com/aziz1291/gestion-incidents"
LABEL org.opencontainers.image.description="Application Flask de gestion des incidents informatiques"

# Version de l'application (le pipeline CD y met le SHA du commit)
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/app/data/incidents.db

# 2. Répertoire de travail dans le conteneur
WORKDIR /app

# 3. Copier d'abord requirements.txt (pour profiter du cache des couches)
COPY requirements.txt .

# 4. Installer les dépendances (exécuté au moment du build)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier le code de l'application
COPY . .

# Dossier où SQLite stocke la base (monté sur un volume par Compose)
RUN mkdir -p /app/data

# 6. Port utilisé par l'application (documentation)
EXPOSE 5000

# 7. Commande exécutée au démarrage du conteneur
CMD ["python", "run.py"]
