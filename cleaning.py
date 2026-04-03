import os
import pandas as pd
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

def apply_cleaning_rules(df):
    df = df.dropna(subset=['NOM COMMERCIAL'])
    df = df.replace("-", None)

    if 'DATE DE CLASSEMENT' in df.columns:
        df['DATE DE CLASSEMENT'] = pd.to_datetime(df['DATE DE CLASSEMENT'], format='%d/%m/%Y', errors='coerce')

    cols_numeriques = [
        "CAPACITÉ D'ACCUEIL (PERSONNES)", 
        "NOMBRE DE CHAMBRES", 
        "NOMBRE D'EMPLACEMENTS",
        "NOMBRE D'UNITES D'HABITATION (résidences de tourisme)",
        "NOMBRE DE LOGEMENTS (villages de vacances)"

    ]
    
    for col in cols_numeriques:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in df.columns:
        if col not in cols_numeriques and col != 'DATE DE CLASSEMENT' and col != '_id':
            print(col)
            df[col] = df[col].fillna("non renseigne")

    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
        
    return df

def store_cleaned_data(df_cleaned):
    try:
        client = MongoClient(MONGO_URI)
        db = client["tourisme_db"]
        
        collection = db["cleaned_hebergements"]
        collection.delete_many({})
        collection.insert_many(df_cleaned.to_dict("records"))

        return True
    except Exception as e:
        print(f"Storage Error: {e}")
        return False