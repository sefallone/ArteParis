import streamlit as st
from db import get_connection

def main():
    st.title("Conexión de prueba a PlanetScale")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        st.success("✅ Conexión exitosa")
        st.write("Tablas:", tablas)
    except:
        st.error("❌ Conexión fallida")

if __name__ == "__main__":
    main()
