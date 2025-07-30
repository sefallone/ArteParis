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
            autocommit=True
        )
        return conn
    except Exception as e:
        st.error("❌ Error al conectar a la base de datos:")
        st.error(traceback.format_exc())
        raise
