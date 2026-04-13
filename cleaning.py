import os
import pandas as pd
from pymongo import MongoClient
import json

class DataTransformer:
    def __init__(self, db_uri=None):
        self.mongo_uri = db_uri or os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
        self.cols_numeriques = [
            "CAPACITÉ D'ACCUEIL (PERSONNES)", "NOMBRE DE CHAMBRES", 
            "NOMBRE D'EMPLACEMENTS", "NOMBRE D'UNITES D'HABITATION (résidences de tourisme)",
            "NOMBRE DE LOGEMENTS (villages de vacances)"
        ]


    def clean_dataframe(self, df):

        df = df.drop_duplicates()
        df = df.dropna(subset=['NOM COMMERCIAL'])
        
        df = df.replace("-", None)

        if 'DATE DE CLASSEMENT' in df.columns:
            df['DATE DE CLASSEMENT'] = pd.to_datetime(df['DATE DE CLASSEMENT'], format='%d/%m/%Y', errors='coerce')

        for col in self.cols_numeriques:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)


        excluded_cols = self.cols_numeriques + ['DATE DE CLASSEMENT', '_id']
        for col in df.columns:
            if col not in excluded_cols:
                df[col] = df[col].fillna("non renseigne")


        return df.drop(columns=['_id'], errors='ignore')
    

    def save_to_json_file(self, df: pd.DataFrame, filename: str = "hebergements_propres.json"):
       
        folder_path = "data_lake/processed"
        os.makedirs(folder_path, exist_ok=True)
        
        file_path = os.path.join(folder_path, filename)

        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
        
        records = df.to_dict(orient="records") 
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
            
        print(f"Fichier sauvegardé avec succès dans : {file_path}")
        return file_path


    def run_pipeline(self):

        try:
            client = MongoClient(self.mongo_uri)
            db = client["tourisme_db"]
            
            # Extraction
            raw_data = list(db["raw_hebergements"].find())
            if not raw_data:
                return False
            
            # Transformation
            df_cleaned = self.clean_dataframe(pd.DataFrame(raw_data))

            # stockage
            self.save_to_json_file(pd.DataFrame(raw_data)) 

            # Chargement
            db["cleaned_hebergements"].delete_many({})
            db["cleaned_hebergements"].insert_many(df_cleaned.to_dict("records"))
            return True
        except Exception as e:
            print(f"Pipeline Error: {e}")
            return False