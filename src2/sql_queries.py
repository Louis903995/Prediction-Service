import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class DatabaseQueries:
    """
    Classe pour gérer les requêtes SQL d'extraction de données
    """
    
    def __init__(self, db_path="base.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def get_ticket_statistics(self, days=30):
        """
        Statistiques des tickets sur les X derniers jours
        """
        conn = self.get_connection()
        
        query = """
        SELECT 
            COUNT(DISTINCT t.id_ticket) as nb_tickets,
            COUNT(c.id_categorie) as nb_produits,
            AVG(s.prix_total) as prix_moyen,
            SUM(s.prix_total) as total_depense
        FROM Tickets t
        LEFT JOIN Categories c ON t.id_ticket = c.id_ticket
        LEFT JOIN Supermarche s ON t.id_ticket = s.id_ticket
        WHERE t.id_ticket IN (
            SELECT id_ticket FROM Supermarche 
            WHERE date_achat >= date('now', '-{} days')
        )
        """.format(days)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_category_distribution(self):
        """
        Distribution des catégories de produits
        """
        conn = self.get_connection()
        
        query = """
        SELECT 
            c.categorie,
            COUNT(*) as nb_produits,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Categories), 2) as pourcentage
        FROM Categories c
        GROUP BY c.categorie
        ORDER BY nb_produits DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_client_spending_analysis(self):
        """
        Analyse des dépenses par client
        """
        conn = self.get_connection()
        
        query = """
        SELECT 
            cl.nom,
            cl.prenom,
            cl.budget,
            COUNT(DISTINCT t.id_ticket) as nb_tickets,
            SUM(s.prix_total) as total_depense,
            AVG(s.prix_total) as panier_moyen,
            ROUND((SUM(s.prix_total) / cl.budget) * 100, 2) as pourcentage_budget
        FROM Clients cl
        LEFT JOIN Tickets t ON cl.client_id = t.client_id
        LEFT JOIN Supermarche s ON t.id_ticket = s.id_ticket
        GROUP BY cl.client_id, cl.nom, cl.prenom, cl.budget
        ORDER BY total_depense DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_products_by_category(self, category):
        """
        Récupère tous les produits d'une catégorie spécifique
        """
        conn = self.get_connection()
        
        query = """
        SELECT 
            c.categorie,
            t.libelle as ticket_description,
            s.nom_magasin,
            s.date_achat,
            s.prix_total
        FROM Categories c
        JOIN Tickets t ON c.id_ticket = t.id_ticket
        LEFT JOIN Supermarche s ON t.id_ticket = s.id_ticket
        WHERE c.categorie = ?
        ORDER BY s.date_achat DESC
        """
        
        df = pd.read_sql_query(query, conn, params=[category])
        conn.close()
        return df
    
    def get_monthly_trends(self):
        """
        Tendances mensuelles des achats
        """
        conn = self.get_connection()
        
        query = """
        SELECT 
            strftime('%Y-%m', s.date_achat) as mois,
            COUNT(DISTINCT t.id_ticket) as nb_tickets,
            SUM(s.prix_total) as total_depense,
            AVG(s.prix_total) as panier_moyen,
            COUNT(c.id_categorie) as nb_produits
        FROM Supermarche s
        JOIN Tickets t ON s.id_ticket = t.id_ticket
        LEFT JOIN Categories c ON t.id_ticket = c.id_ticket
        WHERE s.date_achat IS NOT NULL
        GROUP BY strftime('%Y-%m', s.date_achat)
        ORDER BY mois DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_products_from_openfoodfacts(self, limit=100):
        """
        Récupère les produits collectés depuis OpenFoodFacts
        """
        conn = self.get_connection()
        
        query = """
        SELECT 
            product_name,
            generic_name,
            categories,
            brands,
            quantity,
            nutrition_grade_fr,
            collected_at
        FROM Products
        WHERE product_name IS NOT NULL AND product_name != ''
        ORDER BY collected_at DESC
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        return df
    
    def export_data_for_ml(self):
        """
        Exporte les données formatées pour l'entraînement ML
        """
        conn = self.get_connection()
        
        query = """
        SELECT 
            c.categorie as Categories_OFF,
            COALESCE(p.product_name, 'Produit générique') as Produit,
            s.prix_total,
            s.nom_magasin,
            s.date_achat
        FROM Categories c
        JOIN Tickets t ON c.id_ticket = t.id_ticket
        LEFT JOIN Supermarche s ON t.id_ticket = s.id_ticket
        LEFT JOIN Products p ON p.product_name LIKE '%' || c.categorie || '%'
        WHERE c.categorie IS NOT NULL
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Sauvegarder pour l'entraînement ML
        df.to_csv("data/ml_training_data.csv", index=False, sep=';')
        print(f"✅ Données exportées pour ML: {len(df)} lignes")
        return df
    
    def get_database_summary(self):
        """
        Résumé complet de la base de données
        """
        conn = self.get_connection()
        
        summary = {}
        
        # Nombre de clients
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Clients")
        summary['nb_clients'] = cursor.fetchone()[0]
        
        # Nombre de tickets
        cursor.execute("SELECT COUNT(*) FROM Tickets")
        summary['nb_tickets'] = cursor.fetchone()[0]
        
        # Nombre de catégories
        cursor.execute("SELECT COUNT(*) FROM Categories")
        summary['nb_categories'] = cursor.fetchone()[0]
        
        # Nombre de produits OpenFoodFacts
        cursor.execute("SELECT COUNT(*) FROM Products")
        summary['nb_products'] = cursor.fetchone()[0]
        
        # Dernière mise à jour
        cursor.execute("SELECT MAX(collected_at) FROM Products")
        summary['derniere_maj'] = cursor.fetchone()[0]
        
        conn.close()
        return summary

if __name__ == "__main__":
    queries = DatabaseQueries()
    
    print("📊 Statistiques de la base de données")
    print("=" * 40)
    
    # Résumé général
    summary = queries.get_database_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    print("\n📈 Distribution des catégories:")
    cat_dist = queries.get_category_distribution()
    print(cat_dist.head(10))
    
    print("\n💰 Analyse des dépenses par client:")
    spending = queries.get_client_spending_analysis()
    print(spending.head())
    
    # Export pour ML
    queries.export_data_for_ml() 