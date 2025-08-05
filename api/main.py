from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Charger le modèle
model = joblib.load('modeles/logreg_model.joblib')
vectorizer = joblib.load("modeles/vectorizer.joblib")

app = FastAPI()

class ProductInput(BaseModel):
    produits: list[str]

@app.get("/")
def home():
    return {"message": "API de prédiction de catégorie de produit"}


@app.post("/predict")
def predict_categories(data: ProductInput):
    produits = [p.strip() for p in data.produits if p.strip()]
    vects = vectorizer.transform(produits)
    predictions = model.predict(vects)

    return {
        "predictions": [
            {"produit": p, "categorie": c}
            for p, c in zip(produits, predictions)
        ]
    }