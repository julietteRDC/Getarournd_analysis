# GetAround Pricing API

API de prédiction de prix de location pour GetAround.

## Installation

```bash
pip install -r requirements.txt
```

## Fichiers nécessaires

Avant de lancer l'API, assurez-vous d'avoir :
- `model.joblib` (modèle entraîné)
- `api.py` (application FastAPI)
- `docs.html` (documentation)

## ▶️ Lancement en local

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible à : `http://localhost:8000`

## Documentation

- Documentation interactive Swagger : `http://localhost:8000/docs`
- Documentation personnalisée : `http://localhost:8000/docs_custom`

## Test de l'API

### Avec curl

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "input": [
      ["Citroën", 140411, 100, "diesel", "black", "convertible", 
       true, true, false, false, true, true, true]
    ]
  }'
```

### Avec Python

```python
import requests

response = requests.post("http://localhost:8000/predict", json={
    "input": [
        ["Citroën", 140411, 100, "diesel", "black", "convertible", 
         True, True, False, False, True, True, True]
    ]
})

print(response.json())
# {"prediction": [106]}
```

## Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Page d'accueil |
| `/predict` | POST | Prédiction (format raw) |
| `/predict_features` | POST | Prédiction (format nommé) |
| `/health` | GET | Health check |
| `/docs` | GET | Documentation Swagger |
| `/docs_custom` | GET | Documentation HTML |

## 🔧 Format des données

L'endpoint `/predict` attend 13 features dans cet ordre :

1. `model_key` (str) - Marque
2. `mileage` (int) - Kilométrage
3. `engine_power` (int) - Puissance
4. `fuel` (str) - Carburant
5. `paint_color` (str) - Couleur
6. `car_type` (str) - Type de voiture
7. `private_parking_available` (bool) - Parking
8. `has_gps` (bool) - GPS
9. `has_air_conditioning` (bool) - Climatisation
10. `automatic_car` (bool) - Boîte auto
11. `has_getaround_connect` (bool) - Connect
12. `has_speed_regulator` (bool) - Régulateur
13. `winter_tires` (bool) - Pneus hiver

## Déploiement sur Hugging Face

1. Créer un Space sur Hugging Face
2. Uploader les fichiers :
   - `api.py`
   - `model.joblib`
   - `requirements.txt`
   - `docs.html`
3. Créer un fichier `app.py` :

```python
import uvicorn
from api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

4. Le Space sera accessible à : `https://your-username-spacename.hf.space`
