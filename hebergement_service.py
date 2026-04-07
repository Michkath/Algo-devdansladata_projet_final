from psycopg2.extras import RealDictCursor
from db import get_connection

def get_all_hebergements(ville=None, type_hebergement=None, page=1, per_page=20):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT h.id_hebergement, h.nom_commercial,
               l.commune, t.typologie
        FROM hebergements h
        JOIN localisation l ON h.id_localisation = l.id_localisation
        JOIN type_hebergement t ON h.id_type_hebergement = t.id_type_hebergement
        WHERE 1=1
    """
    params = []

    if ville:
        query += " AND l.commune ILIKE %s"
        params.append(f"%{ville}%")

    if type_hebergement:
        query += " AND t.typologie ILIKE %s"
        params.append(f"%{type_hebergement}%")

    offset = (page - 1) * per_page
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def get_hebergement_by_id(hebergement_id):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT * FROM hebergements
        WHERE id_hebergement = %s
    """, (hebergement_id,))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result