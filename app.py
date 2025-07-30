import streamlit as st
from db import crear_tabla_productos, obtener_productos_por_sucursal, agregar_producto, modificar_producto, eliminar_producto, buscar_producto

def main():
    if st.session_state.get("rerun"):
        st.session_state["rerun"] = False
        st.stop()

    st.title("Inventario Arte París")
    crear_tabla_productos()

    sucursal = st.selectbox("Selecciona la sucursal", ["centro", "unicentro"])

    st.header("Agregar nuevo producto")
    with st.form("agregar_producto"):
        nombre = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad", min_value=0)
        precio_costo = st.number_input("Precio de costo", min_value=0.0, format="%.2f")
        precio_venta = st.number_input("Precio de venta", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Agregar")

        if submitted:
            agregar_producto(sucursal, nombre, cantidad, precio_costo, precio_venta)
            st.success("Producto agregado correctamente.")
            st.session_state["rerun"] = True
            st.experimental_rerun()

    st.header("Buscar producto para modificar o eliminar")
    nombre_busqueda = st.text_input("Buscar por nombre")
    if nombre_busqueda:
        resultado = buscar_producto(sucursal, nombre_busqueda)
        if resultado:
            st.write("Producto encontrado:")
            st.write(resultado)

            nuevo_nombre = st.text_input("Nuevo nombre", value=resultado[2])
            nueva_cantidad = st.number_input("Nueva cantidad", value=resultado[3], min_value=0)
            nuevo_precio_costo = st.number_input("Nuevo precio de costo", value=float(resultado[4]), min_value=0.0, format="%.2f")
            nuevo_precio_venta = st.number_input("Nuevo precio de venta", value=float(resultado[5]), min_value=0.0, format="%.2f")

            if st.button("Modificar"):
                modificar_producto(resultado[0], nuevo_nombre, nueva_cantidad, nuevo_precio_costo, nuevo_precio_venta)
                st.success("Producto modificado correctamente.")
                st.session_state["rerun"] = True
                st.experimental_rerun()

            if st.button("Eliminar"):
                eliminar_producto(resultado[0])
                st.success("Producto eliminado correctamente.")
                st.session_state["rerun"] = True
                st.experimental_rerun()
        else:
            st.warning("Producto no encontrado.")

    st.header(f"Inventario - Sucursal {sucursal.capitalize()}")
    productos = obtener_productos_por_sucursal(sucursal)
    st.dataframe(productos, use_container_width=True)

if __name__ == "__main__":
    main()
