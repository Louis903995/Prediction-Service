from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import onnxruntime as ort
import json
from sklearn.feature_extraction.text import TfidfVectorizer

# === Chargement du vectorizer TF-IDF depuis JSON ===
with open("modeles/tfidf_params.json", "r", encoding="utf-8") as f:
    tfidf_data = json.load(f)

vectorizer = TfidfVectorizer()
vectorizer.vocabulary_ = tfidf_data["vocabulary"]
vectorizer.idf_ = np.array(tfidf_data["idf"])
vectorizer._tfidf._idf_diag = np.diag(vectorizer.idf_)

# === Chargement du modèle ONNX ===
onnx_model_path = "modeles/lr_model.onnx"
session = ort.InferenceSession(onnx_model_path)

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# === Application FastAPI ===
app = FastAPI()

class ProductInput(BaseModel):
    produits: list[str]

@app.get("/")
def home():
    return {"message": "API de prédiction de catégorie alimentaire"}

@app.post("/predict")
def predict_categories(data: ProductInput):
    # Nettoyage des entrées
    produits = [p.strip() for p in data.produits if p.strip()]
    
    # Vectorisation
    vects = vectorizer.transform(produits)
    vects_array = vects.astype(np.float32).toarray()  

    # Prédiction
    predictions = session.run([output_name], {input_name: vects_array})[0]

    # Si sortie = probabilités, on prend l'index du max (catégorie prédite)
    if len(predictions.shape) > 1 and predictions.shape[1] > 1:
        predicted_classes = np.argmax(predictions, axis=1)
    else:
        predicted_classes = predictions

    return {
        "predictions": [
            {"produit": p, "categorie": str(c)}
            for p, c in zip(produits, predicted_classes)
        ]
    }
