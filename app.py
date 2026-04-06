from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


conn = psycopg2.connect(
    dbname="tourisme_dw",
    user="postgres",
    password="root",
    host="localhost",
    port="5432"
)


@app.route("/ping")
def ping():
    return "pong"


@app.route("/hebergements", methods=["GET"])
def get_hebergements():
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    
    ville = request.args.get("ville")
    typologie = request.args.get("type")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    offset = (page - 1) * per_page

    
    query = """
        SELECT h.id_hebergement, h.nom_commercial, h.site_internet,
               l.adresse, l.code_postal, l.commune,
               t.typologie, t.categorie, t.type_sejour, t.mention,
               c.classement, c.date_classement, c.classement_proroge,
               h.capacite_accueil, h.nombre_chambres, h.nombre_emplacements,
               h.nombre_unites, h.nombre_logements
        FROM hebergements h
        JOIN localisation l ON h.id_localisation = l.id_localisation
        JOIN type_hebergement t ON h.id_type_hebergement = t.id_type_hebergement
        JOIN classement c ON h.id_classement = c.id_classement
        WHERE 1=1
    """
    params = []

    if ville:
        query += " AND l.commune ILIKE %s"
        params.append(f"%{ville}%")
    if typologie:
        query += " AND t.typologie ILIKE %s"
        params.append(f"%{typologie}%")

    
    query += " ORDER BY h.id_hebergement LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()

    return jsonify(results)


@app.route("/hebergements/<int:hebergement_id>", methods=["GET"])
def get_hebergement(hebergement_id):
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT h.id_hebergement, h.nom_commercial, h.site_internet,
               l.adresse, l.code_postal, l.commune,
               t.typologie, t.categorie, t.type_sejour, t.mention,
               c.classement, c.date_classement, c.classement_proroge,
               h.capacite_accueil, h.nombre_chambres, h.nombre_emplacements,
               h.nombre_unites, h.nombre_logements
        FROM hebergements h
        JOIN localisation l ON h.id_localisation = l.id_localisation
        JOIN type_hebergement t ON h.id_type_hebergement = t.id_type_hebergement
        JOIN classement c ON h.id_classement = c.id_classement
        WHERE h.id_hebergement = %s
    """, (hebergement_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Hébergement non trouvé"}), 404


if __name__ == "__main__":
    app.run(debug=True)