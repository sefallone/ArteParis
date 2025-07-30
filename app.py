import streamlit as st
from db import crear_tabla_productos, obtener_productos
import pandas as pd

def main():
    st.title("Inventario Arte París")
    
    crear_tabla_productos()

    productos = obtener_productos()

    if productos:
        df = pd.DataFrame(productos, columns=["ID", "Nombre", "Cantidad", "Precio Costo", "Precio Venta"])
        st.dataframe(df)
    else:
        st.info("No hay productos en la base de datos.")

if __name__ == "__main__":
    main()
