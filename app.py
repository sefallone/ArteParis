# app.py
import streamlit as st
from db import crear_tabla_productos, obtener_productos

def main():
    st.title("Inventario Arte París")

    crear_tabla_productos()  # Aseguramos que la tabla exista

    productos = obtener_productos()

    if productos:
        st.table(productos)
    else:
        st.write("No hay productos aún.")

if __name__ == "__main__":
    main()

