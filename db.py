import mysql.connector
import streamlit as st

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            autocommit=True,
            ssl_ca="/etc/ssl/certs/ca-certificates.crt",
            ssl_verify_cert=True
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error al conectar a la base de datos: {err}")
        raise

def obtener_productos_por_sucursal(sucursal):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario WHERE sucursal = %s", (sucursal,))
    productos = cursor.fetchall()
    conn.close()
    return productos
