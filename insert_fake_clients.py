import sqlite3
import random
from datetime import datetime, timedelta

def insert_fake_clients():
    """
    Insère des données fictives dans la table Clients existante
    """
    # Données fictives pour les noms et prénoms
    noms = [
        "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
        "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
        "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "Andre", "Lefevre",
        "Mercier", "Dupont", "Lambert", "Bonnet", "Francois", "Martinez", "Legrand"
    ]
    
    prenoms = [
        "Jean", "Pierre", "Michel", "Andre", "Philippe", "Claude", "Daniel", "Jacques",
        "Marie", "Sophie", "Isabelle", "Nathalie", "Catherine", "Francoise", "Monique",
        "Christine", "Martine", "Brigitte", "Anne", "Sylvie", "Nicole", "Chantal",
        "Dominique", "Laurence", "Véronique", "Sandrine", "Stéphanie", "Valérie",
        "Caroline", "Aurélie", "Julie", "Céline", "Audrey", "Emilie", "Marine"
    ]
    
    # Budgets réalistes (en euros)
    budgets = [50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 750, 1000]
    
    # Connexion à la base de données
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()
    
    # Vérifier si la table Clients existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Clients'")
    if not cursor.fetchone():
        print("❌ La table Clients n'existe pas !")
        return
    
    # Vérifier le nombre de clients existants
    cursor.execute("SELECT COUNT(*) FROM Clients")
    existing_count = cursor.fetchone()[0]
    print(f"📊 Nombre de clients existants : {existing_count}")
    
    # Nombre de nouveaux clients à créer
    nb_new_clients = 50
    
    print(f"\n👥 Création de {nb_new_clients} nouveaux clients...")
    
    # Générer des dates d'enregistrement récentes (derniers 6 mois)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Préparer les données
    clients_data = []
    for i in range(nb_new_clients):
        nom = random.choice(noms)
        prenom = random.choice(prenoms)
        budget = random.choice(budgets)
        
        # Date d'enregistrement aléatoire dans les 6 derniers mois
        random_days = random.randint(0, 180)
        date_enregistrement = (end_date - timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        clients_data.append((nom, prenom, budget, date_enregistrement))
    
    # Insérer les données
    cursor.executemany(
        "INSERT INTO Clients (nom, prenom, budget, date_enregistrement) VALUES (?, ?, ?, ?)",
        clients_data
    )
    
    # Valider les changements
    conn.commit()
    
    # Vérifier l'insertion
    cursor.execute("SELECT COUNT(*) FROM Clients")
    total_count = cursor.fetchone()[0]
    print(f"✅ {nb_new_clients} nouveaux clients ajoutés")
    print(f"📈 Total clients dans la base : {total_count}")
    
    # Afficher quelques exemples
    print("\n👤 Exemples de clients créés :")
    cursor.execute("""
        SELECT nom, prenom, budget, date_enregistrement 
        FROM Clients 
        ORDER BY client_id DESC 
        LIMIT 10
    """)
    examples = cursor.fetchall()
    for nom, prenom, budget, date in examples:
        print(f"  - {prenom} {nom} (Budget: {budget}€, Inscrit le: {date})")
    
    # Statistiques des budgets
    print("\n💰 Statistiques des budgets :")
    cursor.execute("""
        SELECT 
            MIN(budget) as min_budget,
            MAX(budget) as max_budget,
            AVG(budget) as avg_budget,
            COUNT(*) as total_clients
        FROM Clients
    """)
    stats = cursor.fetchone()
    print(f"  - Budget minimum : {stats[0]}€")
    print(f"  - Budget maximum : {stats[1]}€")
    print(f"  - Budget moyen : {stats[2]:.2f}€")
    print(f"  - Total clients : {stats[3]}")
    
    # Répartition par mois d'inscription
    print("\n📅 Répartition par mois d'inscription :")
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', date_enregistrement) as mois,
            COUNT(*) as nb_clients
        FROM Clients
        GROUP BY mois
        ORDER BY mois DESC
    """)
    monthly_stats = cursor.fetchall()
    for mois, nb in monthly_stats:
        print(f"  - {mois} : {nb} clients")
    
    # Fermer la connexion
    conn.close()
    print(f"\n🎉 Insertion des clients fictifs terminée !")

if __name__ == "__main__":
    insert_fake_clients() 