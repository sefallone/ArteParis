import streamlit as st
from db import obtener_productos_por_sucursal

def main():
    st.title("📦 Inventario - Arte París")
    
    sucursal = st.selectbox("Selecciona la sucursal", ["centro", "unicentro"])
    
    # Llama a la función para obtener productos aquí, dentro de main
    productos = obtener_productos_por_sucursal(sucursal)
    
    st.dataframe(productos, use_container_width=True)

if __name__ == "__main__":
    main()

