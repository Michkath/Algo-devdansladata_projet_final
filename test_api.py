import requests

BASE_URL = "http://127.0.0.1:5000"

def test_ping():
    r = requests.get(f"{BASE_URL}/ping")
    print("Ping:", r.text)

def test_hebergements_list():
    # Liste complète
    r = requests.get(f"{BASE_URL}/hebergements")
    print(f"Nombre d'hébergements (page 1): {len(r.json())}")

    # Pagination & filtre
    r2 = requests.get(f"{BASE_URL}/hebergements", params={"ville":"Paris","type":"HÔTEL","page":1,"per_page":5})
    print("Filtre Paris + type HÔTEL, page 1, 5 résultats")
    for h in r2.json():
        print(h["nom_commercial"], "-", h.get("ville"))

def test_hebergement_detail(id_example=1):
    r = requests.get(f"{BASE_URL}/hebergements/{id_example}")
    print(f"Détail hébergement ID {id_example}:")
    print(r.json())

if __name__ == "__main__":
    test_ping()
    print("-"*40)
    test_hebergements_list()
    print("-"*40)
    test_hebergement_detail()