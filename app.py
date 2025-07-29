import streamlit as st

def main():
    st.title("Prueba de conexión a secretos")

    # Mostrar lo que hay en st.secrets para debug
    st.write("Secrets:", st.secrets)

    # Ahora llama a la función que usa st.secrets
    from db import obtener_productos_por_sucursal
    sucursal = st.selectbox("Sucursal", ["centro", "unicentro"])
    productos = obtener_productos_por_sucursal(sucursal)
    st.dataframe(productos)

if __name__ == "__main__":
    main()

