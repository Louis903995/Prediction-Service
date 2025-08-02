import pandas as pd
import joblib

# Charger modèle et vectorizer
model = joblib.load("modeles/logreg_model.joblib")
vectorizer = joblib.load("modeles/vectorizer.joblib")

# Charger les nouvelles données
df_nouveau = pd.read_csv("data/tickets_categorie_final.csv", sep=';')

# Prétraitement
df_nouveau['Produit'] = df_nouveau['Produit'].str.lower()
df_nouveau['Produit'] = df_nouveau['Produit'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Vectorisation
X_nouveau = vectorizer.transform(df_nouveau['Produit'])

# Prédiction
df_nouveau['Prediction_Categorie'] = model.predict(X_nouveau)

# Sauvegarde
df_nouveau.to_csv("classification/nouveaux_tickets_predits.csv", sep=';', index=False)
print(df_nouveau[['Produit', 'Prediction_Categorie']].head())