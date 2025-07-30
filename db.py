# db.py
import psycopg2
import streamlit as st

def get_connection():
    return psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        database=st.secrets["postgres"]["database"],
        port=st.secrets["postgres"]["port"]
    )

def crear_tabla_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        cantidad INT NOT NULL,
        precio_costo NUMERIC(10,2),
        precio_venta NUMERIC(10,2)
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos;")
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados
