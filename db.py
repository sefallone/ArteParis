import streamlit as st
import mysql.connector

st.title("Conexión a la Base de Datos")

host = st.text_input("Host", value="aws-us-east-2.connect.psdb.cloud")
user = st.text_input("Usuario", value="tu_usuario")
password = st.text_input("Contraseña", type="password")
database = st.text_input("Base de datos", value="arte_paris")

if st.button("Conectar"):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            ssl_ca="/etc/ssl/certs/ca-certificates.crt"
        )
        st.success("✅ Conexión exitosa")
    except Exception as e:
        st.error("❌ Error al conectar:")
        st.error(e)
