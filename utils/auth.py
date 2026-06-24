import streamlit as st
from firebase_config import get_db, get_auth
import hashlib
import datetime

def init_auth():
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

def login(username, password):
    try:
        db = get_db()
        
        # Verificar que la base de datos esté conectada
        if db is None:
            st.error("❌ Error de conexión a la base de datos")
            return False
        
        # Buscar usuario en Firestore
        users_ref = db.collection('usuarios')
        query = users_ref.where('username', '==', username).limit(1)
        docs = query.get()
        
        # Verificar si se encontró el usuario
        if not docs:
            st.error(f"❌ Usuario '{username}' no encontrado")
            return False
        
        for doc in docs:
            user_data = doc.to_dict()
            
            # Debug: Mostrar información (solo en desarrollo)
            print(f"🔍 Usuario encontrado: {username}")
            print(f"🔍 Hash en BD: {user_data.get('password_hash', 'NO HASH')}")
            print(f"🔍 Hash ingresado: {hashlib.sha256(password.encode()).hexdigest()}")
            
            # Verificar contraseña
            if verify_password(password, user_data.get('password_hash', '')):
                st.session_state.authenticated = True
                st.session_state.user_data = {
                    'id': doc.id,
                    'username': username,
                    'nombre': user_data.get('nombre', ''),
                    'rol': user_data.get('rol', 'usuario'),
                    'jerarquia': user_data.get('jerarquia', 0)
                }
                # Registrar login
                registrar_login(doc.id)
                return True
            else:
                st.error("❌ Contraseña incorrecta")
                return False
        
        return False
    except Exception as e:
        st.error(f"❌ Error en login: {str(e)}")
        print(f"Error detallado: {e}")
        return False

def verify_password(password, hashed):
    """Verifica la contraseña usando SHA256"""
    if not hashed:
        return False
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_login(user_id):
    try:
        db = get_db()
        if db:
            db.collection('logins').add({
                'user_id': user_id,
                'timestamp': datetime.datetime.now(),
                'fecha': datetime.date.today().isoformat()
            })
    except Exception as e:
        print(f"Error registrando login: {e}")

def logout():
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.cache_data.clear()

def check_permisos(jerarquia_requerida):
    if not st.session_state.authenticated:
        return False
    return st.session_state.user_data.get('jerarquia', 0) >= jerarquia_requerida

def get_current_user():
    return st.session_state.user_data
