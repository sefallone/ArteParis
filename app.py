import streamlit as st
from db import (
    crear_tabla_productos,
    obtener_productos_por_sucursal,
    agregar_producto,
    modificar_producto,
    eliminar_producto,
    buscar_producto
)

def mostrar_productos(sucursal):
    productos = obtener_productos_por_sucursal(sucursal)
    if productos:
        st.subheader("📦 Inventario actual")
        for p in productos:
            st.write(f"🆔 {p[0]} | 📍 {p[1]} | 🍰 {p[2]} | 📦 Cant: {p[3]} | 💰 Costo: {p[4]} | 💸 Venta: {p[5]}")
    else:
        st.info("No hay productos registrados aún para esta sucursal.")

def main():
    st.set_page_config(page_title="Inventario Arte París", layout="centered")
    st.title("📋 Inventario Arte París")
    crear_tabla_productos()

    sucursal = st.selectbox("Selecciona la sucursal", ["Arte París Centro", "Arte París Unicentro"])

    st.markdown("### ➕ Agregar nuevo producto")
    with st.form("agregar_form"):
        nombre = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad", min_value=0, step=1)
        precio_costo = st.number_input("Precio de costo", min_value=0.0, step=0.1)
        precio_venta = st.number_input("Precio de venta", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Agregar")

        if submitted:
            if nombre:
                agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta)
                st.success("✅ Producto agregado exitosamente.")
                st.experimental_rerun()
            else:
                st.warning("⚠️ El nombre del producto no puede estar vacío.")

    st.markdown("### 🔍 Buscar y editar/eliminar producto")
    nombre_buscar = st.text_input("Buscar producto por nombre")
    if nombre_buscar:
        producto = buscar_producto(sucursal, nombre_buscar)
        if producto:
            st.success(f"✅ Producto encontrado: {producto[2]}")

            with st.expander("✏️ Modificar producto"):
                nuevo_nombre = st.text_input("Nuevo nombre", value=producto[2])
                nueva_cantidad = st.number_input("Nueva cantidad", min_value=0, value=producto[3])
                nuevo_precio_costo = st.number_input("Nuevo precio costo", min_value=0.0, value=producto[4])
                nuevo_precio_venta = st.number_input("Nuevo precio venta", min_value=0.0, value=producto[5])
                if st.button("Actualizar"):
                    modificar_producto(producto[0], nuevo_nombre, nueva_cantidad, nuevo_precio_costo, nuevo_precio_venta)
                    st.success("✅ Producto actualizado.")
                    st.experimental_rerun()

            if st.button("🗑️ Eliminar producto"):
                eliminar_producto(producto[0])
                st.warning("❌ Producto eliminado.")
                st.experimental_rerun()
        else:
            st.error("❌ Producto no encontrado.")

    st.markdown("### 📦 Ver inventario")
    mostrar_productos(sucursal)

if __name__ == "__main__":
    main()

