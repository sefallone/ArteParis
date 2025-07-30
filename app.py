import streamlit as st
from db import get_connection

def main():
    st.title("Prueba de conexión a PlanetScale")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        st.success("✅ Conexión exitosa a la base de datos")
        st.write("Tablas en la base de datos:", tablas)
        
    except Exception:
        st.error("❌ Conexión fallida")

if __name__ == "__main__":
    main()
