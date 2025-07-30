import psycopg2
import streamlit as st

# Configura tus datos de conexión aquí directamente
SUPABASE_HOST = "tu-host.supabase.co"
SUPABASE_DB = "postgres"
SUPABASE_USER = "tu-usuario"
SUPABASE_PASSWORD = "tu-contraseña"
SUPABASE_PORT = 5432

def get_connection():
    try:
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            database=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            port=SUPABASE_PORT
        )
        return conn
    except Exception as e:
        st.error(f"❌ Error al conectar: {e}")
        return None
