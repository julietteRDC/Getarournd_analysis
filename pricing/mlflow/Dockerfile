# Construire à partir d'une version allégée LINUX d'Anaconda
FROM continuumio/miniconda3

# Mettre à jour les packages et installer nano unzip et curl
# nano- pouvoir éditer les fichiers directement depuis la console
# curl- pouvoir télécharger des fichiers
# unzip- pouvoir décompresser des fichiers
RUN apt-get update
RUN apt-get install nano unzip curl -y

# Installer AWS cli - Nécessaire pour interagir avec S3
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# nouvel utilisateur nommé « user » avec un ID de 1000
RUN useradd -m -u 1000 user
# On passe de « root » (utilisateur par défaut lors de la création d'une image) à « user »
USER user
# Nous définissons deux variables d'environnement
# afin de pouvoir attribuer ultérieurement la propriété à tous les fichiers qu'elles contiennent.
# Nous ajoutons également /home/user/.local/bin à la variable d'environnement $PATH.
# La variable d'environnement PATH définit les chemins d'accès pour rechercher les binaires installés.
# Nous la mettons à jour pour que Linux sache où rechercher les binaires si nous les installons avec « user ».

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    AWS_DEFAULT_REGION=eu-west-3

# Nous définissons le répertoire de travail sur $HOME/app (<=> /home/user/app)
WORKDIR $HOME/app

# Copiez tous les fichiers locaux dans /home/user/app avec « user » comme propriétaire de ces fichiers
# Utilisez toujours --chown=user avec HUGGINGFACE pour éviter les erreurs d'autorisation.
COPY --chown=user . $HOME/app

# Copier et installer les dépendances
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Exposer le port 7860
EXPOSE 7860

# Lancer le serveur mlflow
CMD mlflow server -p 7860 \
    --host 0.0.0.0 \
    --backend-store-uri $BACKEND_STORE_URI \
    --default-artifact-root $ARTIFACT_STORE_URI