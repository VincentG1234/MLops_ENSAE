# Utiliser Python 3.10 sur Alpine
FROM python:3.10-alpine

# Installer Ollama et les dépendances système
RUN apk add --no-cache curl bash build-base libffi-dev openssl-dev bzip2-dev \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && apk del build-base

# Vérifier les versions installées
RUN python3 --version && pip3 --version && ollama --version

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances Python
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install "unstructured[md]"

# Copier le code de l'application
COPY ./app /app/

# Créer les dossiers nécessaires
RUN mkdir -p /app/backend/uploads /app/backend/FAISS

# Assurer les bonnes permissions
RUN chmod -R 755 /app

# Télécharger et préparer le modèle TinyLlama
RUN ollama pull tinyllama

# Exposer les ports nécessaires
EXPOSE 8000 11434

# Lancer Ollama et FastAPI en parallèle
CMD ["sh", "-c", "ollama serve & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
