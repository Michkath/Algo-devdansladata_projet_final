
import requests
import os
import pandas as pd
from pymongo import MongoClient

class DataIngestor:
    def __init__(self, db_uri="mongodb://admin:password@localhost:27017/", db_name="tourisme_db"):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.data_lake_dir = "data_lake"
        self._setup_storage()

    def _setup_storage(self):
        if not os.path.exists(self.data_lake_dir):
            os.makedirs(self.data_lake_dir)

    def download_data(self, url, target_name):

        file_path = os.path.join(self.data_lake_dir, target_name)
        try:
            response = requests.get(url, stream=True, timeout=20)
            response.raise_for_status() 
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024*8):
                    f.write(chunk)
            return file_path
        except Exception as e:
            print(f"Erreur lors du téléchargement : {e}")
            return None

    def save_to_raw_zone(self, file_path, collection_name):

        if not file_path or not os.path.exists(file_path):
            print("Fichier source introuvable.")
            return False

        try:
            df = pd.read_csv(file_path, sep=';', low_memory=False)
            
            collection = self.db[collection_name]
            collection.delete_many({})
            collection.insert_many(df.to_dict("records"))
            
            print(f"Ingestion réussie : {len(df)} lignes insérées.")
            return True
        except Exception as e:
            print(f"Erreur lors de l'ingestion MongoDB : {e}")
            return False