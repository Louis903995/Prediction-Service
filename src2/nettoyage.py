"""
import pandas as pd
import unidecode
import re

def clean_product_name(name):
    name = name.upper()
    name = unidecode.unidecode(name)  # Enlève les accents
    name = name.strip()
    # Supprime les quantités (ex: 1KG, 500ML, 4X125G)
    name = re.sub(r'\\b\\d+[Xx]?\\d*[A-Z]+\\b', '', name)
    # Supprime les caractères spéciaux
    name = re.sub(r'[^A-Z0-9 ]', '', name)
    # Supprime les espaces multiples
    name = re.sub(r' +', ' ', name)
    return name.strip()

df = pd.read_csv('tickets_pv.csv', sep=';')
df['Produit'] = df['Produit'].apply(clean_product_name)
df = df.drop_duplicates()
df = df.dropna(subset=['Produit', 'Catégorie'])

# Nettoyage des catégories
df['Catégorie'] = df['Catégorie'].str.strip()  # Enlève les espaces début/fin
df['Catégorie'] = df['Catégorie'].str.replace(r'\\s+', ' ', regex=True)  # Espaces multiples
df['Catégorie'] = df['Catégorie'].str.title()  # Met la première lettre en majuscule

# Transformation en CSV
df.to_csv('tickets_pv_clean.csv', sep=';', index=False)
"""

import pandas as pd
import unicodedata

# Fonction pour garder uniquement les lettres latines (et tout le reste sauf les lettres non latines)
def garder_caracteres_latin(texte):
    if pd.isnull(texte):  # Si la valeur est NaN
        return texte
    texte = str(texte)
    resultat = ''
    for char in texte:
        if char.isalpha():
            nom = unicodedata.name(char, '')
            if 'LATIN' in nom:
                resultat += char  # Lettre latine OK
            # Sinon, on supprime
        else:
            resultat += char  # On garde chiffres, ponctuation, espaces, symboles
    return resultat

# Lire le fichier CSV
df = pd.read_csv('data/produits_openfoodfacts_brut.csv', sep=';')

# Colonnes à nettoyer
colonnes_a_nettoyer = ['Produit']

# Nettoyage des colonnes
for col in colonnes_a_nettoyer:
    df[col] = df[col].apply(garder_caracteres_latin)

# Supprimer les lignes où la colonne 'Produit' est vide ou NaN
df = df.dropna(subset=['Produit'])  # Supprime les lignes où 'Produit' est NaN
df = df[df['Produit'].str.strip() != '']  # Supprime les lignes où 'Produit' est vide après nettoyage

# supprimer les "en:" dans la colonne Categories_OFF
df['Categories_OFF'] = df['Categories_OFF'].str.removeprefix('en:')

# Résultat final
print(df.head())

# Enregistrer le fichier nettoyé
df.to_csv('data/tickets_nettoye.csv', index=False, sep=';')
