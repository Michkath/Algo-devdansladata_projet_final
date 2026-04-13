import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scrapping import DataIngestor


@pytest.fixture
def ingestor():
    # On utilise une DB de test pour ne pas polluer ta vraie base
    return DataIngestor(db_name="test_unit_db")

def test_storage_creation(ingestor):
    """Vérifie que le dossier de stockage est bien géré."""
    assert os.path.exists(ingestor.data_lake_dir)

def test_ingestion_invalid_file(ingestor):
    """Vérifie que le code ne crashe pas si le fichier est corrompu/absent."""
    result = ingestor.save_to_raw_zone("fake_file.csv", "test_collection")
    assert result is False

def test_download_error_handling(ingestor):
    """Vérifie que la gestion d'erreur réseau fonctionne."""
    # On donne une URL qui n'existe pas
    path = ingestor.download_data("https://invalid-url-123.com/data.csv", "test.csv")
    assert path is None
    