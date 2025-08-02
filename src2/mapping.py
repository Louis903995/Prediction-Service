import pandas as pd
import json

# Charger le mapping depuis le fichier JSON
with open("data/mapping.json", "r", encoding="utf-8") as f:
    categorie_mapping = json.load(f)

# Charger les données nettoyées
df = pd.read_csv("data/tickets_nettoye.csv", sep=";")

# Fonction de regroupement
def regrouper_categorie(categorie):
    for cat_regroupee, sous_categories in categorie_mapping.items():
        if categorie in sous_categories:
            return cat_regroupee
    return "Autres / Divers"  # Par sécurité

# Appliquer le mapping
df["Categories_OFF"] = df["Categories_OFF"].apply(regrouper_categorie)

# Sauvegarder le fichier mappé
df.to_csv("data/tickets_categorie_final.csv", sep=";", index=False)

print("Mapping des catégories terminé et fichier exporté sous data/tickets_categorie_final.csv")
