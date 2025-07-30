import streamlit as st
#from db import obtener_productos_por_sucursal

def main():
    st.title("Inventario Arte París")

    sucursal = st.selectbox("Selecciona la sucursal", ["centro", "unicentro"])
   # productos = obtener_productos_por_sucursal(sucursal)
   # st.dataframe(productos)

if __name__ == "__main__":
    main()
