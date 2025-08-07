import pandas as pd
import onnxruntime as ort
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os 


# Charger le vectorizer TF-IDF
with open("modeles_onnx/tfidf_params.json", "r") as f:
    tfidf_data = json.load(f)

vectorizer = TfidfVectorizer()
vectorizer.vocabulary_ = tfidf_data["vocabulary"]
vectorizer.idf_ = np.array(tfidf_data["idf"])
vectorizer._tfidf._idf_diag = np.diag(vectorizer.idf_)

# Charger le modèle ONNX
session = ort.InferenceSession("modeles_onnx/lr_model.onnx")
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# Charger les nouvelles données
df_nouveau = pd.read_csv("data/Open_food_fact/tickets_categorie_final.csv", sep=';')

# Prétraitement
df_nouveau['Produit'] = df_nouveau['Produit'].str.lower()
df_nouveau['Produit'] = df_nouveau['Produit'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Vectorisation
X_nouveau = vectorizer.transform(df_nouveau['Produit'])

# Prédiction
X_nouveau_array = X_nouveau.toarray().astype(np.float32)
preds = session.run([output_name], {input_name: X_nouveau_array})[0]
df_nouveau['Prediction_Categorie'] = preds

# Sauvegarde
os.makedirs("classification", exist_ok=True)
df_nouveau.to_csv("classification/nouveaux_tickets_predits.onnx", sep=';', index=False)
print(df_nouveau[['Produit', 'Prediction_Categorie']].head())