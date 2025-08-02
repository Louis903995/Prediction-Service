import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import os
import joblib

print("Répertoire courant :", os.getcwd())
print("Fichiers dans ce dossier :", os.listdir())

# 1. Chargement des données CSV
data = pd.read_csv("data/tickets_categorie_final.csv", sep=';')

# 2. Pré-traitement (optionnel mais recommandé)
data['Produit'] = data['Produit'].str.lower()  # mettre en minuscule
data['Produit'] = data['Produit'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')  # enlever les accents si nécessaire

# 3. TF-Idata Vectorization
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['Produit'])  # transforme en vecteur TF-Idata
y = data['Categories_OFF']  # Labels (catégories)

# 4. Division en données d’entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Modèle 1 : Logistic Regression
print("=== Logistic Regression ===")
lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)
print(classification_report(y_test, y_pred_lr))

# 6. Modèle 2 : SVM
print("\n=== Support Vector Machine (SVM) ===")
svm_model = SVC(kernel='linear', probability=True)
svm_model.fit(X_train, y_train)
y_pred_svm = svm_model.predict(X_test)
print(classification_report(y_test, y_pred_svm))

# Création du dossier 'modeles' s'il n'existe pas
#os.makedirs("modeles", exist_ok=True)

# Sauvegarde du modèle de régression logistique
joblib.dump(lr_model, "modeles/logreg_model.joblib")

# Sauvegarde du vectorizer
joblib.dump(vectorizer, "modeles/vectorizer.joblib")