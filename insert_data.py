import sqlite3
import json
from datetime import datetime

def inserer_donnees_depuis_json(fichier_json):
    """
    Insère des données depuis un fichier JSON dans la base de données SQLite
    """
    
    # Connexion à la base de données
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    
    try:
        # Charger les données JSON
        print(f"📂 Lecture du fichier {fichier_json}...")
        with open(fichier_json, 'r', encoding='utf-8') as f:
            donnees = json.load(f)
        
        # Insérer les clients
        if 'clients' in donnees:
            print("👥 Insertion des clients...")
            for client in donnees['clients']:
                cursor.execute("""
                    INSERT INTO Clients (nom, prenom, budget, date_enregistrement)
                    VALUES (?, ?, ?, ?)
                """, (
                    client.get('nom'),
                    client.get('prenom'), 
                    client.get('budget'),
                    client.get('date_enregistrement', datetime.now().strftime('%Y-%m-%d'))
                ))
            print(f"✅ {len(donnees['clients'])} clients insérés")
        
        # Insérer les tickets
        if 'tickets' in donnees:
            print("🎫 Insertion des tickets...")
            for ticket in donnees['tickets']:
                cursor.execute("""
                    INSERT INTO Tickets (client_id, libelle)
                    VALUES (?, ?)
                """, (
                    ticket.get('client_id'),
                    ticket.get('libelle')
                ))
            print(f"✅ {len(donnees['tickets'])} tickets insérés")
        
        # Insérer les catégories
        if 'categories' in donnees:
            print("📂 Insertion des catégories...")
            for categorie in donnees['categories']:
                cursor.execute("""
                    INSERT INTO Categories (id_ticket, categorie)
                    VALUES (?, ?)
                """, (
                    categorie.get('id_ticket'),
                    categorie.get('categorie')
                ))
            print(f"✅ {len(donnees['categories'])} catégories insérées")
        
        # Insérer les supermarchés
        if 'supermarches' in donnees:
            print("🏪 Insertion des supermarchés...")
            for supermarche in donnees['supermarches']:
                cursor.execute("""
                    INSERT INTO Supermarche (id_ticket, nom_magasin, date_achat, prix_total)
                    VALUES (?, ?, ?, ?)
                """, (
                    supermarche.get('id_ticket'),
                    supermarche.get('nom_magasin'),
                    supermarche.get('date_achat'),
                    supermarche.get('prix_total')
                ))
            print(f"✅ {len(donnees['supermarches'])} supermarchés insérés")
        
        # Valider les changements
        conn.commit()
        print("🎉 Toutes les données ont été insérées avec succès !")
        
    except FileNotFoundError:
        print(f"❌ Fichier {fichier_json} non trouvé !")
    except json.JSONDecodeError:
        print(f"❌ Erreur de format JSON dans {fichier_json}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        conn.rollback()
    
    finally:
        conn.close()

def creer_exemple_json():
    """
    Crée un fichier JSON d'exemple pour tester
    """
    donnees_exemple = {
        "clients": [
            {
                "nom": "Dupont",
                "prenom": "Marie",
                "budget": 150.50,
                "date_enregistrement": "2024-01-15"
            },
            {
                "nom": "Martin",
                "prenom": "Pierre",
                "budget": 200.00,
                "date_enregistrement": "2024-01-16"
            }
        ],
        "tickets": [
            {
                "client_id": 1,
                "libelle": "Courses hebdomadaires"
            },
            {
                "client_id": 2,
                "libelle": "Courses mensuelles"
            }
        ],
        "categories": [
            {
                "id_ticket": 1,
                "categorie": "Alimentaire"
            },
            {
                "id_ticket": 1,
                "categorie": "Hygiène"
            }
        ],
        "supermarches": [
            {
                "id_ticket": 1,
                "nom_magasin": "Carrefour",
                "date_achat": "2024-01-15",
                "prix_total": 85.40
            },
            {
                "id_ticket": 2,
                "nom_magasin": "Leclerc",
                "date_achat": "2024-01-16",
                "prix_total": 120.80
            }
        ]
    }
    
    with open('donnees.json', 'w', encoding='utf-8') as f:
        json.dump(donnees_exemple, f, ensure_ascii=False, indent=2)
    
    print("📄 Fichier 'donnees.json' créé avec des données d'exemple !")

if __name__ == "__main__":
    print("🚀 Insertion de données JSON dans SQLite")
    print("=" * 40)
    
    # Créer un exemple si besoin
    creer_exemple_json()
    
    # Insérer les données
    inserer_donnees_depuis_json('donnees.json')