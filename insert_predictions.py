import sqlite3
import pandas as pd
import joblib
from datetime import datetime

def inserer_predictions_depuis_csv(csv_file, client_id=1):
    """
    Insère les prédictions de catégories depuis un CSV dans la base de données
    """
    
    # Charger le modèle et vectorizer
    model = joblib.load("modeles/logreg_model.joblib")
    vectorizer = joblib.load("modeles/vectorizer.joblib")
    
    # Connexion à la base de données
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    
    try:
        # Charger les données CSV
        print(f"📂 Lecture du fichier {csv_file}...")
        df = pd.read_csv(csv_file, sep=';')
        
        # Prétraitement des produits
        df['Produit'] = df['Produit'].str.lower()
        df['Produit'] = df['Produit'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
        
        # Prédictions
        X = vectorizer.transform(df['Produit'])
        predictions = model.predict(X)
        df['Prediction_Categorie'] = predictions
        
        # Insérer le ticket principal
        print("🎫 Insertion du ticket...")
        cursor.execute("""
            INSERT INTO Tickets (client_id, libelle)
            VALUES (?, ?)
        """, (client_id, f"Ticket du {datetime.now().strftime('%Y-%m-%d')}"))
        
        ticket_id = cursor.lastrowid
        
        # Insérer les catégories prédites
        print("📂 Insertion des catégories prédites...")
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO Categories (id_ticket, categorie)
                VALUES (?, ?)
            """, (ticket_id, row['Prediction_Categorie']))
        
        # Insérer les informations du supermarché (si disponibles)
        if 'Prix' in df.columns:
            prix_total = df['Prix'].sum()
            cursor.execute("""
                INSERT INTO Supermarche (id_ticket, nom_magasin, date_achat, prix_total)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, "Supermarche", datetime.now().strftime('%Y-%m-%d'), prix_total))
        
        # Valider les changements
        conn.commit()
        print(f"✅ {len(df)} produits classifiés et insérés dans le ticket {ticket_id}")
        
        # Afficher un résumé
        print("\n📊 Résumé des catégories prédites :")
        print(df['Prediction_Categorie'].value_counts())
        
    except FileNotFoundError:
        print(f"❌ Fichier {csv_file} non trouvé !")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        conn.rollback()
    
    finally:
        conn.close()

def afficher_statistiques():
    """
    Affiche les statistiques de la base de données
    """
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    
    print("\n📊 Statistiques de la base de données :")
    print("=" * 40)
    
    # Nombre de clients
    cursor.execute("SELECT COUNT(*) FROM Clients")
    nb_clients = cursor.fetchone()[0]
    print(f"👥 Clients : {nb_clients}")
    
    # Nombre de tickets
    cursor.execute("SELECT COUNT(*) FROM Tickets")
    nb_tickets = cursor.fetchone()[0]
    print(f"🎫 Tickets : {nb_tickets}")
    
    # Nombre de catégories
    cursor.execute("SELECT COUNT(*) FROM Categories")
    nb_categories = cursor.fetchone()[0]
    print(f"📂 Catégories : {nb_categories}")
    
    # Top 5 des catégories
    cursor.execute("""
        SELECT categorie, COUNT(*) as nb
        FROM Categories 
        GROUP BY categorie 
        ORDER BY nb DESC 
        LIMIT 5
    """)
    top_categories = cursor.fetchall()
    print("\n🏆 Top 5 des catégories :")
    for cat, nb in top_categories:
        print(f"  - {cat} : {nb} produits")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Insertion des prédictions de classification")
    print("=" * 50)
    
    # Insérer les prédictions depuis un CSV
    # Remplace par le nom de ton fichier CSV
    inserer_predictions_depuis_csv("data/tickets_pv_clean.csv")
    
    # Afficher les statistiques
    afficher_statistiques() 