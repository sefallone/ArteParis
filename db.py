import mysql.connector
import streamlit as st

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
)

def obtener_productos_por_sucursal(sucursal):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario WHERE sucursal = %s", (sucursal,))
    productos = cursor.fetchall()
    conn.close()
    return productos

def agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO inventario (sucursal, nombre_producto, cantidad, precio_costo, precio_venta)
        VALUES (%s, %s, %s, %s, %s)
    """, (sucursal, nombre, cantidad, precio_costo, precio_venta))
    conn.commit()
    conn.close()
