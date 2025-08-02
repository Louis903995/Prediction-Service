import sqlite3


def creer_base_donnees():
    """
    Crée la base de données SQLite avec toutes les tables
    """
    # Créer ou ouvrir la base de données SQLite

    # Créer ou ouvrir la base de données SQLite
    conn = sqlite3.connect("base.db")
    cursor = conn.cursor()

    # Table Clients
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            prenom TEXT,
            budget REAL,
            date_enregistrement DATE
        )
    """)

    # Table Tickets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tickets (
            id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            libelle TEXT
        )
    """)

    # Table Categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ticket INTEGER,
            libelle TEXT,
            categorie TEXT
        )
    """)

    # Table Supermarché (corrigée)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Supermarche (
            id_supermarche INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ticket INTEGER,
            nom_magasin TEXT,
            date_achat DATE,
            prix_total REAL
        )
    """)

    # Valider les changements
    conn.commit()

    # Fermer proprement la connexion
    conn.close()


if __name__ == "__main__":
    creer_base_donnees()