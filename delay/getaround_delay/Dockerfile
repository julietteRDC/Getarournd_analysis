FROM python:3.12-slim

# Ajout de paquets système pour compiler les dépendances Python natives
RUN apt update && apt install -y \
    build-essential gcc g++ python3-dev \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non-root
RUN useradd -m -u 1000 user

# Répertoire de travail
WORKDIR /app

# Copier requirements.txt 
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt --prefer-binary

# Copier le reste de l'application
COPY --chown=user ./src .

# Utilisateur non-root
USER user

# Exposer le port Streamlit
EXPOSE 7860

# Exécution
 CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=7860"]