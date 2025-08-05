# Prediction API

## PDM
### Créer une image docker : 

*pdm run build_docker*
Cela créé une image avec 2 tags: l'un est le numéro de version du pyproject.toml, l'autre est latest (il y a toujours au moins un latest)

### Run un container :
*pdm run container* 
Cela lance le container en local avec la dernière version d'image créée (latest). Le port 80 du container est lié au port 80 de l'hôte
Pour tester avec curl: 
curl -X POST -H "Content-Type: application/json" -d '{"produits": ["tomate"]}' http://localhost/predict
résultat:
{"predictions":[{"produit":"tomate","categorie":"Fruits & Légumes"}]}


### Run fastapi en local (pour debugger)
*pdm run fastapi*

Dans ce cas, fastapi est lancé sur le port par défaut (8000)

Pour tester avec curl: 
curl -X POST -H "Content-Type: application/json" -d '{"produits": ["tomate"]}' http://localhost:8000/predict
résultat:
{"predictions":[{"produit":"tomate","categorie":"Fruits & Légumes"}]}
