from flask import Flask, render_template, jsonify, request
import csv
import os

app = Flask(__name__)

# Chemin vers le CSV
CSV_PATH = os.path.join(os.path.dirname(__file__), "data_lake", "hebergements_classes.csv")

def load_csv():
    hebergements = []
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for i, row in enumerate(reader):
            hebergements.append({
                "id": i + 1,
                "nom_commercial": row.get("NOM COMMERCIAL", "").strip() or None,
                "adresse": row.get("ADRESSE", "").strip() or None,
                "code_postal": row.get("CODE POSTAL", "").strip() or None,
                "ville": row.get("COMMUNE", "").strip() or None,
                "site_internet": row.get("SITE INTERNET", "").strip() or None,
                "type_hebergement": row.get("TYPOLOGIE ÉTABLISSEMENT", "").strip() or None,
                "classement": row.get("CLASSEMENT", "").strip() or None,
                "categorie": row.get("CATÉGORIE", "").strip() or None,
                "mention": row.get("MENTION (villages de vacances)", "").strip() or None,
                "type_sejour": row.get("TYPE DE SÉJOUR", "").strip() or None,
                "capacite_accueil": to_int(row.get("CAPACITÉ D'ACCUEIL (PERSONNES)")),
                "nombre_chambres": to_int(row.get("NOMBRE DE CHAMBRES")),
                "nombre_emplacements": to_int(row.get("NOMBRE D'EMPLACEMENTS")),
                "nombre_unites": to_int(row.get("NOMBRE D'UNITES D'HABITATION (résidences de tourisme)")),
                "nombre_logements": to_int(row.get("NOMBRE DE LOGEMENTS (villages de vacances)")),
                "date_classement": row.get("DATE DE CLASSEMENT", "").strip() or None,
                "classement_proroge": row.get("classement prorogé", "").strip().lower() == "oui",
            })
    return hebergements

def to_int(val):
    try:
        v = str(val).strip()
        return int(v) if v and v != "-" else None
    except:
        return None

# Chargement en mémoire au démarrage
print("Chargement du CSV...")
DATA = load_csv()
print(f"{len(DATA)} hébergements chargés.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "message": "pong"})


@app.route("/hebergements")
def hebergements():
    ville = request.args.get("ville", "").strip().lower()
    type_h = request.args.get("type", "").strip().lower()
    classement = request.args.get("classement", "").strip().lower()
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 20))))
    sort_by = request.args.get("sort_by", "nom_commercial")
    sort_order = request.args.get("sort_order", "asc")

    results = DATA

    if ville:
        results = [h for h in results if h["ville"] and ville in h["ville"].lower()]
    if type_h:
        results = [h for h in results if h["type_hebergement"] and type_h in h["type_hebergement"].lower()]
    if classement:
        results = [h for h in results if h["classement"] and classement in h["classement"].lower()]

    if sort_by in ("nom_commercial", "ville", "classement", "capacite_accueil", "nombre_chambres"):
        reverse = sort_order == "desc"
        results = sorted(results, key=lambda h: (h.get(sort_by) or ""), reverse=reverse)

    total = len(results)
    start = (page - 1) * per_page
    page_data = results[start:start + per_page]

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "hebergements": page_data
    })


@app.route("/hebergements/<int:id>")
def hebergement_detail(id):
    for h in DATA:
        if h["id"] == id:
            return jsonify(h)
    return jsonify({"error": "Not found"}), 404


@app.route("/hebergements/export")
def hebergements_export():
    """Retourne tous les hébergements d'un coup (pour le dashboard BI)."""
    ville = request.args.get("ville", "").strip().lower()
    type_h = request.args.get("type", "").strip().lower()
    classement = request.args.get("classement", "").strip().lower()

    results = DATA
    if ville:
        results = [h for h in results if h["ville"] and ville in h["ville"].lower()]
    if type_h:
        results = [h for h in results if h["type_hebergement"] and type_h in h["type_hebergement"].lower()]
    if classement:
        results = [h for h in results if h["classement"] and classement in h["classement"].lower()]

    return jsonify({"total": len(results), "hebergements": results})


@app.route("/stats")
def stats():
    """Retourne des statistiques agrégées pour le dashboard BI."""
    from collections import Counter
    types_count = Counter(h["type_hebergement"] for h in DATA if h["type_hebergement"])
    villes_count = Counter(h["ville"] for h in DATA if h["ville"])
    classements_count = Counter(h["classement"] for h in DATA if h["classement"])
    total_capacite = sum(h["capacite_accueil"] or 0 for h in DATA)
    nb_communes = len(set(h["ville"] for h in DATA if h["ville"]))

    return jsonify({
        "total_etablissements": len(DATA),
        "total_capacite_accueil": total_capacite,
        "nb_communes": nb_communes,
        "repartition_types": dict(types_count.most_common()),
        "top_10_villes": dict(villes_count.most_common(10)),
        "repartition_classements": dict(classements_count.most_common()),
    })


if __name__ == "__main__":
    app.run(debug=True)