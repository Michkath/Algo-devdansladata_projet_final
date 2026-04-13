import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="tourisme_dw",
        user="postgres",
        password="root",
        host="localhost",
        port="5433"
    )