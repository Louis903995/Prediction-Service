import requests
import csv
import argparse
import os
import json
import time

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CATEGORIES_JSON = os.path.join(DATA_DIR, 'categories.json')

# --- Récupération automatique des slugs ---
def get_all_slugs(categories_json=CATEGORIES_JSON):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(categories_json):
        print("Téléchargement de la liste des catégories...")
        url = "https://world.openfoodfacts.org/categories.json"
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
        except Exception as e:
            print(f"Erreur lors du téléchargement des catégories : {e}")
            exit(1)
        with open(categories_json, 'w', encoding='utf-8') as f:
            f.write(r.text)
    try:
        with open(categories_json, encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier JSON des catégories : {e}")
        exit(1)
    slugs = [cat['id'].split(':')[-1] for cat in data.get('tags', []) if 'id' in cat]
    return slugs

def telecharger_tous_les_produits(slugs, max_pages=5, delay=1.0, output_file=None, max_products=None):
    all_products = []
    total_slugs = len(slugs)
    for i, slug in enumerate(slugs, 1):
        print(f"[{i}/{total_slugs}] Récupération slug : {slug}")
        for page in range(1, max_pages + 1):
            url = f"https://world.openfoodfacts.org/category/{slug}/{page}.json"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    print(f"  Erreur HTTP {response.status_code} sur {url}, on passe à la page suivante.")
                    break
                if 'application/json' not in response.headers.get('Content-Type', ''):
                    print(f"  Réponse non JSON sur {url}, on passe à la page suivante.")
                    # Pour debug, on peut afficher le début du contenu :
                    print(f"    Début de la réponse : {response.text[:200]}")
                    break
                data = response.json()
            except Exception as e:
                print(f"  Erreur sur {url} : {e}")
                print(f"    Début de la réponse : {response.text[:200] if 'response' in locals() else ''}")
                break
            page_produits = data.get('products', [])
            if not page_produits:
                break
            count_valid = 0
            for prod in page_produits:
                name = prod.get('product_name', '').strip().upper()
                categories_tags_list = prod.get('categories_tags', [])
                first_category = categories_tags_list[0] if categories_tags_list else ''
                if name and len(name) > 1 and first_category:
                    all_products.append((name, first_category))
                    count_valid += 1
                    if max_products and len(all_products) >= max_products:
                        print(f"Limite de {max_products} produits atteinte.")
                        if output_file:
                            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f, delimiter=';')
                                writer.writerow(['Produit', 'Categories_OFF'])
                                writer.writerows(all_products)
                            print(f"Fichier généré : {output_file}")
                        print(f"Total produits extraits : {len(all_products)}")
                        return all_products
            print(f"  Page {page} : {count_valid} produits valides récupérés pour {slug}")
            time.sleep(delay)
    if output_file:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Produit', 'Categories_OFF'])
            writer.writerows(all_products)
        print(f"Fichier généré : {output_file}")
    print(f"Total produits extraits : {len(all_products)}")
    return all_products

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraction produits et catégories OFF depuis Open Food Facts (toutes catégories)")
    parser.add_argument('--max_pages', type=int, default=5, help="Nombre de pages à télécharger par catégorie")
    parser.add_argument('--delay', type=float, default=1.0, help="Délai entre les requêtes (secondes)")
    parser.add_argument('--output', type=str, help="Fichier de sortie")
    parser.add_argument('--max_products', type=int, help="Nombre maximum de produits à extraire (optionnel)")
    args = parser.parse_args()

    slugs = get_all_slugs()
    output = args.output or os.path.join(DATA_DIR, "produits_openfoodfacts_brut.csv")
    telecharger_tous_les_produits(slugs, max_pages=args.max_pages, delay=args.delay, output_file=output, max_products=args.max_products)
