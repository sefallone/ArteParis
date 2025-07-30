import streamlit as st
from db import crear_tabla_productos, agregar_producto, obtener_productos_por_sucursal, actualizar_producto, eliminar_producto

def main():
    st.title("Inventario Arte París")
    crear_tabla_productos()

    sucursal = st.selectbox("Selecciona la sucursal", ["centro", "unicentro"])

    st.subheader("Agregar nuevo producto")
    with st.form("agregar_form"):
        nombre = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad", min_value=0, step=1)
        precio_costo = st.number_input("Precio de costo", min_value=0.0, step=0.01)
        precio_venta = st.number_input("Precio de venta", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Agregar")
        if submitted and nombre:
            agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta)
            st.success(f"Producto '{nombre}' agregado con éxito.")

    st.subheader(f"Inventario de sucursal: {sucursal.capitalize()}")
    productos = obtener_productos_por_sucursal(sucursal)

    if productos:
        for p in productos:
            with st.expander(f"{p[1].capitalize()} (ID: {p[0]})"):
                nombre_edit = st.text_input("Nombre", value=p[2], key=f"n_{p[0]}")
                cantidad_edit = st.number_input("Cantidad", value=p[3], key=f"c_{p[0]}")
                costo_edit = st.number_input("Precio costo", value=p[4], key=f"pc_{p[0]}")
                venta_edit = st.number_input("Precio venta", value=p[5], key=f"pv_{p[0]}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Actualizar", key=f"upd_{p[0]}"):
                        actualizar_producto(p[0], nombre_edit, cantidad_edit, costo_edit, venta_edit)
                        st.success("Producto actualizado.")
                        st.experimental_rerun()
                with col2:
                    if st.button("Eliminar", key=f"del_{p[0]}"):
                        eliminar_producto(p[0])
                        st.warning("Producto eliminado.")
                        st.experimental_rerun()
    else:
        st.info("No hay productos registrados para esta sucursal.")

if __name__ == "__main__":
    main()
