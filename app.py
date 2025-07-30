import streamlit as st
from db import crear_tabla_productos, obtener_productos, agregar_producto
import pandas as pd

def main():
    st.title("Inventario Arte París")

    crear_tabla_productos()

    with st.form("formulario"):
        nombre = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad", min_value=0, step=1)
        precio_costo = st.number_input("Precio de costo", min_value=0.0, step=0.1)
        precio_venta = st.number_input("Precio de venta", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Agregar producto")
        if submitted:
            agregar_producto(nombre, cantidad, precio_costo, precio_venta)
            st.success("✅ Producto agregado exitosamente")

    st.subheader("📦 Productos en inventario")
    productos = obtener_productos()
    if productos:
        df = pd.DataFrame(productos, columns=["ID", "Nombre", "Cantidad", "Precio Costo", "Precio Venta"])
        st.dataframe(df)
    else:
        st.info("No hay productos registrados aún.")

if __name__ == "__main__":
    main()
