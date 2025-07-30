import mysql.connector
import streamlit as st
import traceback

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            ssl_ca="/etc/ssl/certs/ca-certificates.crt",  # Certificado raíz del sistema (válido en Streamlit Cloud)
            ssl_verify_cert=True
        )
        return conn
    except Exception:
        st.error("❌ Error al conectar a la base de datos:")
        st.error(traceback.format_exc())
        raise
