import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_ping():
    """Vérifie que l'API est allumée et répond."""
    r = requests.get(f"{BASE_URL}/ping")
    assert r.status_code == 200 

def test_hebergements_list_and_filters():
    """Vérifie que la liste et les filtres fonctionnent."""
    r = requests.get(f"{BASE_URL}/hebergements", params={"ville":"Paris","type":"HÔTEL DE TOURISME","page":1,"per_page":5})
    
    assert r.status_code == 200
    data = r.json()
    
    assert "hebergements" in data
    assert "total" in data
    assert isinstance(data["hebergements"], list)
    assert len(data["hebergements"]) <= 5
    
    if len(data["hebergements"]) > 0:
        assert "PARIS" in data["hebergements"][0].get("ville", "").upper()

def test_hebergement_detail():
    """Vérifie qu'on peut récupérer le détail d'un hébergement précis."""
    r = requests.get(f"{BASE_URL}/hebergements/1")
    
    assert r.status_code in [200, 404]
    
    if r.status_code == 200:
        assert "nom_commercial" in r.json()
