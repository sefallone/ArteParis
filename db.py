import streamlit as st
import mysql.connector
import traceback

# Configuración directa (reemplaza con tus valores reales)
DB_CONFIG = {
    "host": "aws-us-east-2.connect.psdb.cloud",
    "user": "97fbg4jyqaaqxzxyupng",
    "password": "pscale_pw_luBSHFVPAeZLuC2IkJQtZJaWRbvh2KaURxDMlxlEOWX",
    "database": "arte_paris",
    "ssl_ca": "/etc/ssl/certs/ca-certificates.crt"
}

st.title("🔌 Test de conexión a PlanetScale (sin secrets.toml)")

try:
    st.write("🔄 Intentando conectar a la base de datos...")

    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        ssl_ca=DB_CONFIG["ssl_ca"]
    )

    st.success("✅ Conexión exitosa.")

    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tablas = cursor.fetchall()

    if tablas:
        st.subheader("📦 Tablas disponibles:")
        for tabla in tablas:
            st.write(f"- {tabla[0]}")
    else:
        st.warning("La base de datos no tiene tablas.")

    cursor.close()
    conn.close()

except Exception:
    st.error("❌ Error al conectar a la base de datos:")
    st.exception(traceback.format_exc())
