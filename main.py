import os
from scrapping import DataIngestor
from cleaning import DataTransformer
from dw_loader import run_dw_loader          

def run_pipeline():
    URL_STABLE = "https://www.data.gouv.fr/api/1/datasets/r/3ce290bf-07ec-4d63-b12b-d0496193a535"
    DB_URI = os.getenv("MONGO_URI", "mongodb://admin:password@mongodb:27017/")
    
    ingestor = DataIngestor(db_uri=DB_URI)
    transformer = DataTransformer(db_uri=DB_URI)

    print("Demarrage du Pipeline ETL")

    file_path = ingestor.download_data(URL_STABLE, "hebergements_classes.csv")
    
    if not file_path or not ingestor.save_to_raw_zone(file_path, "raw_hebergements"):
        print("Erreur : Echec lors de l'ingestion des donnees brutes.")
        return

    if transformer.run_pipeline():
        print("Succes : Transformation et stockage en base reussis.")
        run_dw_loader()                         
        print("ETL Pipeline Success")
    else:
        print("Erreur : Echec lors de la transformation des donnees.")

if __name__ == "__main__":
    run_pipeline()