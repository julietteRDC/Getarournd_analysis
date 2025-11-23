# GetAround Analysis & Pricing

Projet d'analyse et de prédiction pour GetAround, plateforme de location de voitures entre particuliers.

## Vue d'ensemble

Ce projet comporte **trois composants principaux** :

1. **Analyse des retards** : Dashboard interactif Streamlit pour optimiser les délais entre locations
2. **Modèle de pricing** : API FastAPI pour prédire les prix de location
3. **Déploiement** : Containerisation Docker et déploiement cloud

---

## Partie 1 : Analyse des Retards

### Objectif
Aider le Product Manager à décider :
- **Quel seuil** de délai minimum entre deux locations ?
- **Quelle portée** : toutes les voitures ou Connect uniquement ?
- **Quel impact** sur les revenus ?

### Dashboard Streamlit

Le dashboard permet de :
- Visualiser la distribution des retards au checkout
- Comparer les retards par type de checkin (Connect vs Mobile)
- Simuler l'impact de différents seuils (0-360 minutes)
- Analyser le trade-off efficacité / impact sur les revenus

**Fonctionnalités clés** :
- Filtrage par scope (All / Connect only)
- Simulation interactive du seuil
- Métriques en temps réel : cas résolus, locations bloquées, perte de revenu
- Graphiques Plotly interactifs

### Installation & Lancement

```bash
cd delay_analysis

# Installer les dépendances
pip install -r requirements.txt

# Lancer le dashboard
streamlit run streamlit_app.py
```

Le dashboard sera accessible à `http://localhost:8501`

### Dépendances
```
streamlit==1.46.0
pandas==2.3.0
numpy==2.3.1
openpyxl==3.1.5
plotly==6.1.2
```

---

## Partie 2 : Modèle de Pricing

### Objectif
Prédire le **prix de location journalier** d'un véhicule à partir de ses caractéristiques.

### Modèle ML

**Type** : Régression supervisée

**Features (13)** :
- `model_key` : Marque du véhicule
- `mileage` : Kilométrage
- `engine_power` : Puissance moteur
- `fuel` : Type de carburant
- `paint_color` : Couleur
- `car_type` : Type de véhicule (sedan, SUV, etc.)
- `private_parking_available` : Parking privé (bool)
- `has_gps` : GPS (bool)
- `has_air_conditioning` : Climatisation (bool)
- `automatic_car` : Boîte automatique (bool)
- `has_getaround_connect` : GetAround Connect (bool)
- `has_speed_regulator` : Régulateur de vitesse (bool)
- `winter_tires` : Pneus hiver (bool)

**Modèles testés** :
- Linear Regression
- Ridge Regression
- Random Forest Regressor
- Gradient Boosting Regressor

**Pipeline** :
```python
Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ])),
    ('regressor', RandomForestRegressor())
])
```

**Métriques** : R², RMSE, MAE, Cross-validation

### API FastAPI

L'API expose le modèle entraîné via plusieurs endpoints.

#### Installation & Lancement

```bash
cd pricing_model

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'API
uvicorn api:app --reload --host 0.0.0.0 --port 8006
```

L'API sera accessible à `http://localhost:8006`

#### Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil |
| `/predict` | POST | Prédiction (format raw list) |
| `/predict_features` | POST | Prédiction (format JSON nommé) |
| `/health` | GET | Health check |
| `/docs` | GET | Documentation Swagger interactive |
| `/docs_custom` | GET | Documentation HTML personnalisée |

#### Exemple d'utilisation

**Avec curl** :
```bash
curl -X POST "http://localhost:8006/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      ["Citroën", 140411, 100, "diesel", "black", "convertible", 
       true, true, false, false, true, true, true]
    ]
  }'
```

**Avec Python** :
```python
import requests

response = requests.post("http://localhost:8006/predict", json={
    "input": [
        ["Citroën", 140411, 100, "diesel", "black", "convertible", 
         True, True, False, False, True, True, True]
    ]
})

print(response.json())
# {"prediction": [106]}
```

#### Dépendances API
```
fastapi==0.104.1
uvicorn==0.24.0
scikit-learn==1.3.2
pandas==2.1.3
joblib==1.3.2
```

---

## Partie 3 : Déploiement Docker

### Dashboard Streamlit

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build & Run** :
```bash
docker build -t getaround-dashboard .
docker run -p 8501:8501 getaround-dashboard
```

### API FastAPI

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8006
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8006"]
```

**Build & Run** :
```bash
docker build -t getaround-api .
docker run -p 8006:8006 getaround-api
```

---

## Déploiement Cloud

### Option 1 : Heroku

```bash
# Dashboard
heroku create getaround-dashboard
git push heroku main

# API
heroku create getaround-api
git push heroku main
```

### Option 2 : Hugging Face Spaces

1. Créer un Space (Streamlit pour le dashboard, Gradio/Docker pour l'API)
2. Upload des fichiers
3. Le Space build automatiquement

### Option 3 : AWS / GCP / Azure

Utiliser les Dockerfiles fournis pour déployer sur :
- AWS ECS / Elastic Beanstalk
- GCP Cloud Run
- Azure Container Instances

---

## Résultats & Insights

### Analyse des Retards

- **~35-40%** des locations se terminent en retard
- Les retards moyens sont d'environ **20-30 minutes**
- Recommandation : **Seuil de 120 minutes** sur **Connect uniquement**
- Impact estimé : **~5-8%** des locations bloquées

### Modèle de Pricing

- **R² > 0.75** sur le test set
- Meilleur modèle : **Random Forest** ou **Gradient Boosting**
- Features les plus importantes : `engine_power`, `mileage`, `car_type`
- API prête pour la production

---

## Technologies

**Python 3.9+**

**Data Science** :
- pandas, numpy
- scikit-learn
- matplotlib, seaborn, plotly

**Web & API** :
- Streamlit
- FastAPI, uvicorn
- pydantic

**Déploiement** :
- Docker
- joblib (sérialisation modèle)
- gunicorn (production WSGI)

**Optionnel** :
- MLflow (tracking expérimentations)
- boto3 (AWS S3 pour les données)
- psycopg2 (base de données)
