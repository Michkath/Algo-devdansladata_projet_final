import requests
import os
import pandas as pd
from pymongo import MongoClient

URL_STABLE = "https://www.data.gouv.fr/api/1/datasets/r/3ce290bf-07ec-4d63-b12b-d0496193a535"
DATA_LAKE_DIR = "data_lake"

def download_data():
   
    if not os.path.exists(DATA_LAKE_DIR):
        os.makedirs(DATA_LAKE_DIR)
        print(f"Dossier cree : {DATA_LAKE_DIR}")

    file_path = os.path.join(DATA_LAKE_DIR, "hebergements_classes.csv")
    
   
    print("Telechargement en cours depuis l'URL stable...")
    
    try:
        
        response = requests.get(URL_STABLE, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Succes : Fichier enregistre dans {file_path}")
            
          
            taille = os.path.getsize(file_path) / (1024 * 1024)
            print(f"Taille du fichier : {taille:.2f} Mo")
            return file_path
        else:
            print(f"Erreur de telechargement : Code {response.status_code}")
            
    except Exception as e:
        print(f"Une erreur est survenue : {e}")


# MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
MONGO_URI = "mongodb://localhost:27017/"

def ingest_raw_data(file_path):
    try:
        client = MongoClient(MONGO_URI)
        db = client["tourisme_db"]
        collection = db["raw_hebergements"]

        df = pd.read_csv(file_path, sep=';', low_memory=False)
        data_dict = df.to_dict("records")

        collection.delete_many({}) 
        collection.insert_many(data_dict)

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False