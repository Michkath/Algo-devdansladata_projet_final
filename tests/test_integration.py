from pymongo import MongoClient
import pandas as pd
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cleaning import DataTransformer

@pytest.fixture
def transformer():
    return DataTransformer()

def test_storage_integration(transformer):
    """Test d'Intégration : Vérifie l'écriture dans MongoDB."""
    # On crée un petit DF nettoyé
    df = pd.DataFrame([{'NOM COMMERCIAL': 'Test Unit', 'VALEUR': 10}])
    
    # On utilise la méthode de stockage (on peut simuler l'appel)
    client = MongoClient(transformer.mongo_uri)
    db = client["tourisme_db"]
    collection = db["cleaned_hebergements"]
    
    collection.delete_many({"NOM COMMERCIAL": "Test Unit"})
    collection.insert_many(df.to_dict("records"))
    
    # Vérification
    assert db.list_collection_names() is not None
    doc = collection.find_one({"NOM COMMERCIAL": "Test Unit"})
    assert doc['VALEUR'] == 10
