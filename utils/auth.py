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
        # Buscar usuario en Firestore
        users_ref = db.collection('usuarios')
        query = users_ref.where('username', '==', username).limit(1)
        docs = query.get()
        
        for doc in docs:
            user_data = doc.to_dict()
            # Verificar contraseña (hash simple para demo)
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
        
        return False
    except Exception as e:
        print(f"Error en login: {e}")
        return False

def verify_password(password, hashed):
    # Hash simple para demo (usar bcrypt en producción)
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_login(user_id):
    try:
        db = get_db()
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

# utils/auth.py - Agregar esta función
def crear_usuario(username, password, nombre, email):
    """Crea un nuevo usuario en Firebase"""
    try:
        db = get_db()
        
        # Verificar que el usuario no exista
        users_ref = db.collection('usuarios')
        query = users_ref.where('username', '==', username).limit(1)
        docs = query.get()
        
        if len(list(docs)) > 0:
            return {'success': False, 'message': 'El usuario ya existe'}
        
        # Crear usuario
        user_data = {
            'username': username,
            'password_hash': hash_password(password),
            'nombre': nombre,
            'email': email,
            'rol': 'usuario',
            'jerarquia': 1,
            'fecha_creacion': datetime.now()
        }
        
        doc_ref = db.collection('usuarios').add(user_data)
        
        return {'success': True, 'message': 'Usuario creado exitosamente', 'id': doc_ref[1].id}
    
    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}
