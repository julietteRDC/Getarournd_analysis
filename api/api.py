from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import joblib
import pandas as pd
from typing import List

# Initialisation de l'application FastAPI
app = FastAPI(
    title="GetAround Pricing API",
    description="API pour prédire le prix de location journalier d'un véhicule GetAround",
    version="1.0.0"
)

# Chargement du modèle
try:
    model = joblib.load('model.joblib')
except FileNotFoundError:
    raise Exception("Le fichier model.joblib est introuvable. Veuillez d'abord entraîner le modèle.")

# Schéma des données d'entrée
class CarFeatures(BaseModel):
    model_key: str
    mileage: int
    engine_power: int
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool
    
    class Config:
        schema_extra = {
            "example": {
                "model_key": "Citroën",
                "mileage": 140411,
                "engine_power": 100,
                "fuel": "diesel",
                "paint_color": "black",
                "car_type": "convertible",
                "private_parking_available": True,
                "has_gps": True,
                "has_air_conditioning": False,
                "automatic_car": False,
                "has_getaround_connect": True,
                "has_speed_regulator": True,
                "winter_tires": True
            }
        }

class PredictionInput(BaseModel):
    input: List[List]  # Format: [[feature1, feature2, ...], ...]
    
    class Config:
        schema_extra = {
            "example": {
                "input": [
                    ["Citroën", 140411, 100, "diesel", "black", "convertible", True, True, False, False, True, True, True],
                    ["Peugeot", 80000, 120, "petrol", "white", "sedan", False, True, True, True, False, True, False]
                ]
            }
        }

class PredictionOutput(BaseModel):
    prediction: List[int]

# Route racine
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l'API GetAround Pricing",
        "endpoints": {
            "/predict": "POST - Prédire le prix de location (format raw)",
            "/predict_features": "POST - Prédire le prix avec features nommées",
            "/docs": "Documentation interactive"
        }
    }

# Endpoint /predict - Format raw (comme demandé dans le projet)
@app.post("/predict", response_model=PredictionOutput)
def predict_raw(data: PredictionInput):
    """
    Prédire le prix de location journalier à partir de features brutes.
    
    Format attendu:
    ```json
    {
      "input": [
        [model_key, mileage, engine_power, fuel, paint_color, car_type, 
         private_parking_available, has_gps, has_air_conditioning, automatic_car, 
         has_getaround_connect, has_speed_regulator, winter_tires],
        ...
      ]
    }
    ```
    
    Retourne:
    ```json
    {
      "prediction": [price1, price2, ...]
    }
    ```
    """
    try:
        # Colonnes dans l'ordre attendu
        columns = [
            'model_key', 'mileage', 'engine_power', 'fuel', 'paint_color', 'car_type',
            'private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car',
            'has_getaround_connect', 'has_speed_regulator', 'winter_tires'
        ]
        
        # Conversion en DataFrame
        df = pd.DataFrame(data.input, columns=columns)
        
        # Prédiction
        predictions = model.predict(df)
        
        # Conversion en entiers
        predictions = [int(round(p)) for p in predictions]
        
        return {"prediction": predictions}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la prédiction: {str(e)}")

# Endpoint alternatif avec features nommées (plus user-friendly)
@app.post("/predict_features")
def predict_features(cars: List[CarFeatures]):
    """
    Prédire le prix de location avec des features nommées.
    
    Plus simple à utiliser que /predict car les features sont explicites.
    """
    try:
        # Conversion en DataFrame
        df = pd.DataFrame([car.dict() for car in cars])
        
        # Prédiction
        predictions = model.predict(df)
        
        # Conversion en entiers
        predictions = [int(round(p)) for p in predictions]
        
        return {"prediction": predictions}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la prédiction: {str(e)}")

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

# Documentation HTML
@app.get("/docs_custom", response_class=HTMLResponse)
def read_docs():
    """Page de documentation HTML personnalisée."""
    try:
        with open('docs.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Documentation non disponible</h1>"
