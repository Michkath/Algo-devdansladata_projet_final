from psycopg2.extras import RealDictCursor
from db import get_connection

def get_all_hebergements(ville=None, type_hebergement=None, classement_filtre=None, page=1, per_page=20):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. Préparation des filtres dynamiques
    conditions = " WHERE 1=1"
    params = []

    if ville:
        conditions += " AND l.commune ILIKE %s"
        params.append(f"%{ville}%")

    if type_hebergement:
        conditions += " AND t.typologie ILIKE %s"
        params.append(f"%{type_hebergement}%")
        
    if classement_filtre:
        conditions += " AND c.classement ILIKE %s"
        params.append(f"%{classement_filtre}%")

    # 2. Requête pour compter le TOTAL (indispensable pour les boutons de page)
    count_query = """
        SELECT COUNT(*) 
        FROM hebergements h
        LEFT JOIN localisation l ON h.id_localisation = l.id_localisation
        LEFT JOIN type_hebergement t ON h.id_type_hebergement = t.id_type_hebergement
        LEFT JOIN classement c ON h.id_classement = c.id_classement
    """ + conditions
    
    cursor.execute(count_query, params)
    total = cursor.fetchone()['count']

    # 3. Requête principale avec TOUTES les jointures
    data_query = """
        SELECT 
            h.id_hebergement AS id,
            h.nom_commercial,
            l.adresse,
            l.code_postal,
            l.commune AS ville,
            h.site_internet,
            t.typologie AS type_hebergement,
            c.classement,
            t.categorie,
            t.mention,
            t.type_sejour,
            h.capacite_accueil,
            h.nombre_chambres,
            h.nombre_emplacements,
            h.nombre_unites,
            h.nombre_logements,
            c.date_classement,
            c.classement_proroge
        FROM hebergements h
        LEFT JOIN localisation l ON h.id_localisation = l.id_localisation
        LEFT JOIN type_hebergement t ON h.id_type_hebergement = t.id_type_hebergement
        LEFT JOIN classement c ON h.id_classement = c.id_classement
    """ + conditions

    
    offset = (page - 1) * per_page
    data_query += " LIMIT %s OFFSET %s"
    
    data_params = params.copy()
    data_params.extend([per_page, offset])

    cursor.execute(data_query, data_params)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

   
    return results, total

def get_hebergement_by_id(hebergement_id):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT 
            h.id_hebergement AS id,
            h.nom_commercial,
            l.adresse,
            l.code_postal,
            l.commune AS ville,
            h.site_internet,
            t.typologie AS type_hebergement,
            c.classement,
            t.categorie,
            t.mention,
            t.type_sejour,
            h.capacite_accueil,
            h.nombre_chambres,
            h.nombre_emplacements,
            h.nombre_unites,
            h.nombre_logements,
            c.date_classement,
            c.classement_proroge
        FROM hebergements h
        LEFT JOIN localisation l ON h.id_localisation = l.id_localisation
        LEFT JOIN type_hebergement t ON h.id_type_hebergement = t.id_type_hebergement
        LEFT JOIN classement c ON h.id_classement = c.id_classement
        WHERE h.id_hebergement = %s
    """, (hebergement_id,))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result