import streamlit as st
from db import obtener_productos_por_sucursal, agregar_producto

st.set_page_config(page_title="Inventario Arte París", layout="wide")

st.title("📦 Inventario - Arte París")

# Selección de sucursal
sucursal = st.selectbox("Selecciona la sucursal", ["centro", "unicentro"])

# Mostrar inventario actual
st.subheader(f"Inventario actual - Sucursal {sucursal.capitalize()}")
productos = obtener_productos_por_sucursal(sucursal)
st.dataframe(productos, use_container_width=True)

# Formulario para agregar producto
st.subheader("➕ Agregar producto al inventario")
with st.form("agregar_producto"):
    nombre = st.text_input("Nombre del producto")
    cantidad = st.number_input("Cantidad", min_value=0, step=1)
    precio_costo = st.number_input("Precio de costo", min_value=0.0, step=0.1)
    precio_venta = st.number_input("Precio de venta", min_value=0.0, step=0.1)
    enviar = st.form_submit_button("Agregar")

    if enviar:
        if nombre and cantidad >= 0:
            agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta)
            st.success("✅ Producto agregado correctamente.")
            st.experimental_rerun()
        else:
            st.warning("Por favor completa todos los campos correctamente.")
