import mysql.connector
import streamlit as st

def get_connection():
    # Usar st.secrets solo dentro de esta función (que se llama dentro de main)
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],  # <-- coma al final
        autocommit=True,
        ssl_mode="VERIFY_IDENTITY",
        ssl={ "ca": "/etc/ssl/certs/ca-certificates.crt" }
    )

def obtener_productos_por_sucursal(sucursal):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario WHERE sucursal = %s", (sucursal,))
    productos = cursor.fetchall()
    conn.close()
    return productos
