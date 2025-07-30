import streamlit as st
from db import crear_tabla_productos, obtener_productos

def main():
    st.title("Inventario Arte París")

    # Crear tabla productos si no existe (solo la primera vez)
    crear_tabla_productos()

    # Mostrar productos
    productos = obtener_productos()

    if productos:
        # Mostrar en dataframe
        st.dataframe(productos)
    else:
        st.write("No hay productos en el inventario.")

if __name__ == "__main__":
    main()
