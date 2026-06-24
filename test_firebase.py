# test_firebase.py
import streamlit as st
from firebase_config import init_firebase, get_db

def test_connection():
    """Prueba la conexión a Firebase"""
    print("🔧 Inicializando Firebase...")
    init_firebase()
    
    db = get_db()
    if db is None:
        print("❌ Error: No se pudo obtener la base de datos")
        return False
    
    print("✅ Conexión a Firebase establecida")
    
    # Intentar leer un documento
    try:
        docs = db.collection('usuarios').limit(1).get()
        print(f"✅ Colección 'usuarios' accesible. Documentos encontrados: {len(list(docs))}")
        return True
    except Exception as e:
        print(f"❌ Error al leer la colección: {e}")
        return False

if __name__ == "__main__":
    test_connection()
