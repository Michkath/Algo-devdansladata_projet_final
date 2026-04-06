import psycopg2

try:
    conn = psycopg2.connect(
        dbname="tourisme_dw",
        user="postgres",      
        password="root",  
        host="localhost",
        port="5432"
    )

    print("Connexion PostgreSQL réussie")

    conn.close()

except Exception as e:
    print("Erreur de connexion :", e)
    
