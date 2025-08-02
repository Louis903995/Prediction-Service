import joblib
import pandas as pd
import numpy as np
import sqlite3
import json
import logging
import time
from datetime import datetime, timedelta
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mlops.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MLOpsPipeline:
    """
    Pipeline MLOps pour le projet de classification de tickets
    """
    
    def __init__(self):
        self.model_path = "modeles/logreg_model.joblib"
        self.vectorizer_path = "modeles/vectorizer.joblib"
        self.metrics_path = "modeles/metrics.json"
        self.version_path = "modeles/version.txt"
        self.backup_dir = "modeles/backups/"
        
        # Créer les dossiers nécessaires
        os.makedirs("modeles", exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def load_current_model(self):
        """Charge le modèle actuel"""
        try:
            model = joblib.load(self.model_path)
            vectorizer = joblib.load(self.vectorizer_path)
            return model, vectorizer
        except FileNotFoundError:
            logger.warning("Modèle actuel non trouvé")
            return None, None
    
    def backup_current_model(self):
        """Sauvegarde le modèle actuel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.exists(self.model_path):
            backup_model_path = f"{self.backup_dir}model_{timestamp}.joblib"
            backup_vectorizer_path = f"{self.backup_dir}vectorizer_{timestamp}.joblib"
            
            joblib.dump(joblib.load(self.model_path), backup_model_path)
            joblib.dump(joblib.load(self.vectorizer_path), backup_vectorizer_path)
            
            logger.info(f"✅ Modèle sauvegardé: {backup_model_path}")
            return backup_model_path
        return None
    
    def load_training_data(self):
        """Charge les données d'entraînement depuis la base de données"""
        conn = sqlite3.connect("base.db")
        
        query = """
        SELECT 
            c.categorie as Categories_OFF,
            COALESCE(p.product_name, 'Produit générique') as Produit
        FROM Categories c
        JOIN Tickets t ON c.id_ticket = t.id_ticket
        LEFT JOIN Products p ON p.product_name IS NOT NULL
        WHERE c.categorie IS NOT NULL
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Si pas assez de données, utiliser le fichier CSV
        if len(df) < 100:
            try:
                df = pd.read_csv("data/tickets_categorie_final.csv", sep=';')
                logger.info("Utilisation des données CSV de secours")
            except FileNotFoundError:
                logger.error("Aucune donnée d'entraînement disponible")
                return None
        
        return df
    
    def preprocess_data(self, df):
        """Prétraite les données pour l'entraînement"""
        logger.info("🔄 Prétraitement des données...")
        
        # Nettoyer les données
        df = df.dropna(subset=['Produit', 'Categories_OFF'])
        df['Produit'] = df['Produit'].str.lower()
        df['Produit'] = df['Produit'].str.strip()
        
        # Supprimer les catégories avec trop peu d'exemples
        category_counts = df['Categories_OFF'].value_counts()
        valid_categories = category_counts[category_counts >= 5].index
        df = df[df['Categories_OFF'].isin(valid_categories)]
        
        logger.info(f"✅ Données prétraitées: {len(df)} lignes, {df['Categories_OFF'].nunique()} catégories")
        return df
    
    def train_model(self, df):
        """Entraîne un nouveau modèle"""
        logger.info("🤖 Entraînement du nouveau modèle...")
        
        # Prétraitement
        df = self.preprocess_data(df)
        
        if len(df) < 50:
            logger.error("Pas assez de données pour l'entraînement")
            return False
        
        # Vectorisation
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = vectorizer.fit_transform(df['Produit'])
        y = df['Categories_OFF']
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Entraînement
        model = LogisticRegression(max_iter=1000, class_weight='balanced')
        model.fit(X_train, y_train)
        
        # Évaluation
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        # Métriques détaillées
        detailed_metrics = classification_report(y_test, y_pred, output_dict=True)
        
        # Sauvegarder les métriques
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'training_date': datetime.now().isoformat(),
            'n_samples': len(df),
            'n_categories': df['Categories_OFF'].nunique(),
            'detailed_metrics': detailed_metrics
        }
        
        with open(self.metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"✅ Modèle entraîné - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
        
        return model, vectorizer, metrics
    
    def validate_model(self, model, vectorizer, test_data=None):
        """Valide le modèle avec des tests automatisés"""
        logger.info("🧪 Validation du modèle...")
        
        validation_results = {
            'passed': True,
            'errors': [],
            'warnings': []
        }
        
        # Test 1: Vérifier que le modèle peut faire des prédictions
        try:
            test_products = ["pomme", "chocolat", "yaourt", "pain", "lait"]
            X_test = vectorizer.transform(test_products)
            predictions = model.predict(X_test)
            
            if len(predictions) != len(test_products):
                validation_results['passed'] = False
                validation_results['errors'].append("Nombre de prédictions incorrect")
            
            logger.info(f"✅ Test de prédiction réussi: {predictions}")
            
        except Exception as e:
            validation_results['passed'] = False
            validation_results['errors'].append(f"Erreur de prédiction: {str(e)}")
        
        # Test 2: Vérifier la performance minimale
        if os.path.exists(self.metrics_path):
            with open(self.metrics_path, 'r') as f:
                metrics = json.load(f)
            
            if metrics.get('accuracy', 0) < 0.5:
                validation_results['warnings'].append("Accuracy faible (< 0.5)")
            
            if metrics.get('f1_score', 0) < 0.4:
                validation_results['warnings'].append("F1-score faible (< 0.4)")
        
        # Test 3: Vérifier la diversité des prédictions
        try:
            diverse_products = ["pomme", "steak", "lait", "chocolat", "pain", "poisson"]
            X_diverse = vectorizer.transform(diverse_products)
            diverse_predictions = model.predict(X_diverse)
            
            unique_predictions = len(set(diverse_predictions))
            if unique_predictions < 3:
                validation_results['warnings'].append("Faible diversité des prédictions")
            
        except Exception as e:
            validation_results['errors'].append(f"Erreur test diversité: {str(e)}")
        
        logger.info(f"Validation {'réussie' if validation_results['passed'] else 'échouée'}")
        return validation_results
    
    def deploy_model(self, model, vectorizer, version=None):
        """Déploie le nouveau modèle"""
        logger.info("🚀 Déploiement du nouveau modèle...")
        
        # Sauvegarder l'ancien modèle
        self.backup_current_model()
        
        # Sauvegarder le nouveau modèle
        joblib.dump(model, self.model_path)
        joblib.dump(vectorizer, self.vectorizer_path)
        
        # Mettre à jour la version
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(self.version_path, 'w') as f:
            f.write(version)
        
        logger.info(f"✅ Modèle déployé - Version: {version}")
        return version
    
    def monitor_model_performance(self):
        """Surveille les performances du modèle en production"""
        logger.info("📊 Surveillance des performances...")
        
        # Charger les métriques actuelles
        if not os.path.exists(self.metrics_path):
            logger.warning("Aucune métrique disponible")
            return None
        
        with open(self.metrics_path, 'r') as f:
            metrics = json.load(f)
        
        # Vérifier la dégradation des performances
        current_accuracy = metrics.get('accuracy', 0)
        current_f1 = metrics.get('f1_score', 0)
        
        # Charger les métriques historiques
        historical_metrics = self.load_historical_metrics()
        
        if historical_metrics:
            # Calculer la tendance
            recent_metrics = historical_metrics[-5:]  # 5 dernières versions
            avg_accuracy = np.mean([m.get('accuracy', 0) for m in recent_metrics])
            avg_f1 = np.mean([m.get('f1_score', 0) for m in recent_metrics])
            
            # Détecter la dégradation
            accuracy_degradation = avg_accuracy - current_accuracy
            f1_degradation = avg_f1 - current_f1
            
            if accuracy_degradation > 0.1 or f1_degradation > 0.1:
                logger.warning(f"⚠️ Dégradation détectée - Accuracy: {accuracy_degradation:.3f}, F1: {f1_degradation:.3f}")
                return {
                    'status': 'degradation_detected',
                    'accuracy_degradation': accuracy_degradation,
                    'f1_degradation': f1_degradation
                }
        
        logger.info("✅ Performances stables")
        return {'status': 'stable'}
    
    def load_historical_metrics(self):
        """Charge les métriques historiques"""
        historical_metrics = []
        
        # Charger depuis les sauvegardes
        for file in os.listdir(self.backup_dir):
            if file.startswith("metrics_") and file.endswith(".json"):
                try:
                    with open(os.path.join(self.backup_dir, file), 'r') as f:
                        metrics = json.load(f)
                        historical_metrics.append(metrics)
                except:
                    continue
        
        return sorted(historical_metrics, key=lambda x: x.get('training_date', ''))
    
    def run_full_pipeline(self, force_retrain=False):
        """Exécute le pipeline MLOps complet"""
        logger.info("🚀 Démarrage du pipeline MLOps complet")
        print("=" * 50)
        
        # 1. Surveillance des performances
        monitoring_result = self.monitor_model_performance()
        
        # 2. Décision de réentraînement
        should_retrain = force_retrain or (
            monitoring_result and 
            monitoring_result.get('status') == 'degradation_detected'
        )
        
        if should_retrain:
            logger.info("🔄 Réentraînement nécessaire")
            
            # 3. Charger les données
            df = self.load_training_data()
            if df is None:
                logger.error("❌ Impossible de charger les données d'entraînement")
                return False
            
            # 4. Entraîner le modèle
            result = self.train_model(df)
            if not result:
                logger.error("❌ Échec de l'entraînement")
                return False
            
            model, vectorizer, metrics = result
            
            # 5. Valider le modèle
            validation = self.validate_model(model, vectorizer)
            if not validation['passed']:
                logger.error(f"❌ Validation échouée: {validation['errors']}")
                return False
            
            # 6. Déployer le modèle
            version = self.deploy_model(model, vectorizer)
            
            logger.info("🎉 Pipeline MLOps terminé avec succès")
            return True
        
        else:
            logger.info("✅ Aucun réentraînement nécessaire")
            return True

if __name__ == "__main__":
    mlops = MLOpsPipeline()
    
    # Exécuter le pipeline complet
    success = mlops.run_full_pipeline(force_retrain=True)
    
    if success:
        print("🎉 Pipeline MLOps exécuté avec succès !")
    else:
        print("❌ Échec du pipeline MLOps") 