import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="mental_health_db",
        user="postgres",
        password="Jinalba@2811"
    )