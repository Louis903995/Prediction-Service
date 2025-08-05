FROM python:3.12-slim

WORKDIR /app

# Installer PDM
RUN pip install --upgrade pip
RUN pip install pdm

# Copier les fichiers de configuration PDM
COPY pyproject.toml pdm.lock* ./

# Installer les dépendances avec PDM (sans --no-dev)
RUN pdm install --prod

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["pdm", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]