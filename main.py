import time
from scrapping import download_data, ingest_raw_data
import pandas as pd
from pymongo import MongoClient
from cleaning import apply_cleaning_rules, store_cleaned_data


def run_pipeline():
    file_path = download_data()
    
    if file_path and ingest_raw_data(file_path):
        # 1. On récupère les données brutes depuis Mongo
        client = MongoClient("mongodb://localhost:27017/")
        raw_docs = list(client["tourisme_db"]["raw_hebergements"].find())
        df_raw = pd.DataFrame(raw_docs)

        # 2. Nettoyage (Logique métier)
        df_cleaned = apply_cleaning_rules(df_raw)

        # 3. Stockage (Logique technique)
        if store_cleaned_data(df_cleaned):
            print("ETL Pipeline Success")
    else:
        print("ETL Pipeline Failed")

if __name__ == "__main__":
    run_pipeline()