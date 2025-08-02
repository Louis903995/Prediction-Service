import requests
import pandas as pd
import time
import json
from datetime import datetime
import sqlite3

class DataCollector:
    """
    Collecteur automatisé de données pour le projet de classification de tickets
    """
    
    def __init__(self):
        self.base_url = "https://world.openfoodfacts.org/cgi/search.pl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TicketClassifier/1.0 (louis@example.com)'
        })
    
    def collect_openfoodfacts_data(self, categories=None, limit=100):
        """
        Collecte des données depuis OpenFoodFacts
        """
        if categories is None:
            categories = [
                "fruits-vegetables-nuts",
                "meat-fish-eggs", 
                "dairy-eggs",
                "sweetened-beverages",
                "snacks",
                "cereals-and-potatoes"
            ]
        
        all_products = []
        
        for category in categories:
            print(f"🔍 Collecte de données pour la catégorie: {category}")
            
            params = {
                'action': 'process',
                'tagtype_0': 'categories',
                'tag_contains_0': 'contains',
                'tag_0': category,
                'sort_by': 'unique_scans_n',
                'page_size': limit,
                'json': 1
            }
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                products = data.get('products', [])
                
                for product in products:
                    product_data = {
                        'code': product.get('code', ''),
                        'product_name': product.get('product_name', ''),
                        'generic_name': product.get('generic_name', ''),
                        'categories': product.get('categories', ''),
                        'brands': product.get('brands', ''),
                        'quantity': product.get('quantity', ''),
                        'ingredients_text': product.get('ingredients_text', ''),
                        'nutrition_grade_fr': product.get('nutrition_grade_fr', ''),
                        'image_url': product.get('image_url', ''),
                        'collected_at': datetime.now().isoformat()
                    }
                    all_products.append(product_data)
                
                print(f"✅ {len(products)} produits collectés pour {category}")
                time.sleep(1)  # Respecter les limites de l'API
                
            except Exception as e:
                print(f"❌ Erreur lors de la collecte pour {category}: {e}")
        
        return all_products
    
    def save_to_database(self, products):
        """
        Sauvegarde les produits dans la base de données
        """
        conn = sqlite3.connect("base.db")
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                product_name TEXT,
                generic_name TEXT,
                categories TEXT,
                brands TEXT,
                quantity TEXT,
                ingredients_text TEXT,
                nutrition_grade_fr TEXT,
                image_url TEXT,
                collected_at TEXT
            )
        """)
        
        inserted = 0
        for product in products:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO Products 
                    (code, product_name, generic_name, categories, brands, 
                     quantity, ingredients_text, nutrition_grade_fr, image_url, collected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product['code'], product['product_name'], product['generic_name'],
                    product['categories'], product['brands'], product['quantity'],
                    product['ingredients_text'], product['nutrition_grade_fr'],
                    product['image_url'], product['collected_at']
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print(f"❌ Erreur insertion produit {product['code']}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ {inserted} nouveaux produits insérés dans la base")
    
    def export_to_csv(self, products, filename="collected_products.csv"):
        """
        Exporte les données collectées en CSV
        """
        df = pd.DataFrame(products)
        df.to_csv(f"data/{filename}", index=False, encoding='utf-8')
        print(f"✅ Données exportées vers data/{filename}")
    
    def run_daily_collection(self):
        """
        Lance la collecte quotidienne automatisée
        """
        print("🚀 Début de la collecte automatisée de données")
        print("=" * 50)
        
        # Collecter les données
        products = self.collect_openfoodfacts_data(limit=50)
        
        # Sauvegarder dans la base
        self.save_to_database(products)
        
        # Exporter en CSV
        self.export_to_csv(products, f"products_{datetime.now().strftime('%Y%m%d')}.csv")
        
        print("🎉 Collecte terminée !")

if __name__ == "__main__":
    collector = DataCollector()
    collector.run_daily_collection() 