import streamlit as st
from db import get_connection

def crear_tabla():
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id serial PRIMARY KEY,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_costo NUMERIC NOT NULL,
                precio_venta NUMERIC NOT NULL,
                sucursal TEXT NOT NULL
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        st.success("✅ Tabla creada correctamente")

def mostrar_productos():
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM productos;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        st.write("📦 Productos:")
        for row in rows:
            st.write(row)

st.title("Inventario Arte París")
if st.button("Crear tabla productos"):
    crear_tabla()
if st.button("Ver productos"):
    mostrar_productos()
