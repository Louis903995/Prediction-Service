from extraction import get_all_slugs
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SLUGS_FILE = os.path.join(DATA_DIR, 'all_slugs.txt')

slugs = get_all_slugs()

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

with open(SLUGS_FILE, 'w', encoding='utf-8') as f:
    for slug in slugs:
        f.write(slug + '\n')

print(f"{len(slugs)} slugs exportés dans {SLUGS_FILE}") 