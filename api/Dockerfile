FROM python:3.10-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers de l'application
COPY api.py .
COPY model.joblib .
COPY docs.html .

# Exposer le port 7860 (requis par Hugging Face)
EXPOSE 7860

# Lancer l'application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
