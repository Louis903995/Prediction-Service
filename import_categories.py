import pandas as pd
import sqlite3
import os

def import_categories_to_db():
    """
    Importe les données de tickets_categorie_final.csv dans la base de données
    """
    # Chemin vers le fichier CSV
    csv_path = "data/tickets_categorie_final.csv"
    db_path = "base.db"
    
    # Vérifier que le fichier CSV existe
    if not os.path.exists(csv_path):
        print(f"❌ Fichier {csv_path} non trouvé")
        return
    
    # Lire le fichier CSV
    print(f"📖 Lecture du fichier {csv_path}...")
    df = pd.read_csv(csv_path, sep=';')
    print(f"✅ {len(df)} lignes lues")
    
    # Afficher les premières lignes
    print("\n📋 Aperçu des données :")
    print(df.head())
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer une nouvelle table pour les catégories de produits
    print("\n🗄️ Création de la table Categories_Produits...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories_Produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libelle TEXT NOT NULL,
            categorie TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Vider la table si elle existe déjà (optionnel)
    cursor.execute("DELETE FROM Categories_Produits")
    
    # Préparer les données pour l'insertion
    data_to_insert = []
    for _, row in df.iterrows():
        produit = row['Produit'].strip()
        categorie = row['Categories_OFF'].strip()
        if produit and categorie:  # Vérifier que les données ne sont pas vides
            data_to_insert.append((produit, categorie))
    
    # Insérer les données
    print(f"\n💾 Insertion de {len(data_to_insert)} produits dans la base...")
    cursor.executemany(
        "INSERT INTO Categories_Produits (libelle, categorie) VALUES (?, ?)",
        data_to_insert
    )
    
    # Valider les changements
    conn.commit()
    
    # Vérifier l'insertion
    cursor.execute("SELECT COUNT(*) FROM Categories_Produits")
    count = cursor.fetchone()[0]
    print(f"✅ {count} produits insérés avec succès")
    
    # Afficher quelques exemples
    print("\n📊 Exemples de produits insérés :")
    cursor.execute("SELECT libelle, categorie FROM Categories_Produits LIMIT 5")
    examples = cursor.fetchall()
    for produit, categorie in examples:
        print(f"  - {produit} → {categorie}")
    
    # Afficher les statistiques par catégorie
    print("\n📈 Statistiques par catégorie :")
    cursor.execute("""
        SELECT categorie, COUNT(*) as count 
        FROM Categories_Produits 
        GROUP BY categorie 
        ORDER BY count DESC
    """)
    stats = cursor.fetchall()
    for categorie, count in stats:
        print(f"  - {categorie}: {count} produits")
    
    # Fermer la connexion
    conn.close()
    print(f"\n🎉 Import terminé avec succès !")

if __name__ == "__main__":
    import_categories_to_db() 