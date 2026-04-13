import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_ping():
    """Vérifie que l'API est allumée et répond."""
    r = requests.get(f"{BASE_URL}/ping")
    assert r.status_code == 200 

def test_hebergements_list_and_filters():
    """Vérifie que la liste et les filtres fonctionnent."""
    r = requests.get(f"{BASE_URL}/hebergements", params={"ville":"Paris","type":"HÔTEL","page":1,"per_page":5})
    
    assert r.status_code == 200
    data = r.json()
    
    assert isinstance(data, list)
    assert len(data) <= 5
    
    if len(data) > 0:
        assert data[0].get("ville") == "Paris"

def test_hebergement_detail():
    """Vérifie qu'on peut récupérer le détail d'un hébergement précis."""
    # On teste avec un ID arbitraire (ex: 1)
    r = requests.get(f"{BASE_URL}/hebergements/1")
    
    # Même si l'ID 1 n'existe pas, l'API ne doit pas crasher (elle doit renvoyer 200 OK ou 404 Not Found)
    assert r.status_code in [200, 404]
    
    if r.status_code == 200:
        assert "nom_commercial" in r.json()