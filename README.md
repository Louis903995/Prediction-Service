# Mon projet Ticket

## Structure recommandée du projet

- `data/` : tous les fichiers de données (CSV, JSON)
- `scripts/` : tous les scripts Python (extraction, nettoyage, classification, conversion)
- `docs/` : documentation, README, fichiers explicatifs
- `venv/` : environnement virtuel Python

## Exemple d'organisation

```
Ticket/
├── data/
│   ├── tickets.csv
│   ├── tickets_pv.csv
│   ├── tickets_pv_clean.csv
│   ├── produits_tickets.csv
│   ├── produits_openfoodfacts.csv
│   ├── categories.json
│   ├── all_categories.txt
│   ├── unique_category_names.txt
│   ├── mapped_categories.txt
│
├── scripts/
│   ├── telechargement.py
│   ├── extract_products_by_category.py
│   ├── extract_categories.py
│   ├── convert_csv_delimiter.py
│   ├── modele_categorisation.py
│   ├── nettoyage.py
│   ├── main.py
│
├── docs/
│   ├── README.md
│   ├── README_categories_extraction.txt
│
├── requirements.txt
├── venv/
└── .git/
```

---

**Déplace chaque fichier dans le dossier correspondant pour t'y retrouver facilement !**
