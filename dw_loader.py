from pymongo import MongoClient
import psycopg2


mongo_client = MongoClient("mongodb://admin:password@localhost:27017/")
mongo_db = mongo_client["tourisme_db"]
collection = mongo_db["cleaned_hebergements"]


conn = psycopg2.connect(
    dbname="tourisme_dw",
    user="postgres",
    password="root",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()


tables = ["hebergements", "localisation", "type_hebergement", "classement"]
for t in tables:
    cursor.execute(f"DELETE FROM {t};")
conn.commit()


def safe_int(value):
    """Convertit en int ou renvoie None si impossible"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def get_or_create_localisation(adresse, code_postal, commune):
    cursor.execute("""
        SELECT id_localisation FROM localisation
        WHERE adresse=%s AND code_postal=%s AND commune=%s
    """, (adresse, code_postal, commune))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute("""
        INSERT INTO localisation (adresse, code_postal, commune)
        VALUES (%s, %s, %s) RETURNING id_localisation
    """, (adresse, code_postal, commune))
    return cursor.fetchone()[0]

def get_or_create_type(typologie, categorie, type_sejour, mention):
    cursor.execute("""
        SELECT id_type_hebergement FROM type_hebergement
        WHERE typologie=%s AND categorie=%s AND type_sejour=%s AND mention=%s
    """, (typologie, categorie, type_sejour, mention))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute("""
        INSERT INTO type_hebergement (typologie, categorie, type_sejour, mention)
        VALUES (%s, %s, %s, %s) RETURNING id_type_hebergement
    """, (typologie, categorie, type_sejour, mention))
    return cursor.fetchone()[0]

def get_or_create_classement(classement_val, date_classement, classement_proroge):
    proroge_bool = True if str(classement_proroge).lower() == "oui" else False
    cursor.execute("""
        SELECT id_classement FROM classement
        WHERE classement=%s AND date_classement=%s AND classement_proroge=%s
    """, (classement_val, date_classement, proroge_bool))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute("""
        INSERT INTO classement (classement, date_classement, classement_proroge)
        VALUES (%s, %s, %s) RETURNING id_classement
    """, (classement_val, date_classement, proroge_bool))
    return cursor.fetchone()[0]


for doc in collection.find():
    id_localisation = get_or_create_localisation(
        doc.get("ADRESSE", ""),
        doc.get("CODE POSTAL", ""),
        doc.get("COMMUNE", "")
    )

    id_type = get_or_create_type(
        doc.get("TYPOLOGIE ÉTABLISSEMENT", ""),
        doc.get("CATÉGORIE", ""),
        doc.get("TYPE DE SÉJOUR", ""),
        doc.get("MENTION (villages de vacances)", "")
    )

    id_classement = get_or_create_classement(
        doc.get("CLASSEMENT", ""),
        doc.get("DATE DE CLASSEMENT"),
        doc.get("classement prorogé", "non")
    )

    cursor.execute("""
        INSERT INTO hebergements (
            nom_commercial, site_internet, 
            id_localisation, id_type_hebergement, id_classement,
            capacite_accueil, nombre_chambres, nombre_emplacements,
            nombre_unites, nombre_logements
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        doc.get("NOM COMMERCIAL", ""),
        doc.get("SITE INTERNET", ""),
        id_localisation,
        id_type,
        id_classement,
        safe_int(doc.get("CAPACITÉ D'ACCUEIL (PERSONNES)")),
        safe_int(doc.get("NOMBRE DE CHAMBRES")),
        safe_int(doc.get("NOMBRE D'EMPLACEMENTS")),
        safe_int(doc.get("NOMBRE D'UNITES D'HABITATION (résidences de tourisme)")),
        safe_int(doc.get("NOMBRE DE LOGEMENTS (villages de vacances)"))
    ))


conn.commit()
cursor.close()
conn.close()

print("Données transférées vers PostgreSQL avec succès !")