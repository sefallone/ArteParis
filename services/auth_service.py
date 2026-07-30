# services/auth_service.py
import streamlit as st
from datetime import datetime
from models.usuario import Usuario
from services.firebase_service import FirebaseService
from services.tasa_service import TasaService

class AuthService:
    """Servicio de autenticación y gestión de usuarios"""
    
    def __init__(self):
        self.db = FirebaseService.get_instance().get_db()
        self.tasa_service = TasaService()
    
    def login(self, username: str, password: str) -> bool:
        """Intenta iniciar sesión"""
        try:
            if self.db is None:
                st.error("❌ Error de conexión a la base de datos")
                return False
            
            # Buscar usuario
            users_ref = self.db.collection('usuarios')
            query = users_ref.where('username', '==', username).where('activo', '==', True).limit(1)
            docs = query.get()
            
            if not docs:
                st.error("❌ Usuario no encontrado o inactivo")
                return False
            
            for doc in docs:
                data = doc.to_dict()
                usuario = Usuario(data, doc.id)
                
                if usuario.verificar_password(password):
                    # Guardar en sesión
                    st.session_state.authenticated = True
                    st.session_state.user_data = {
                        'id': usuario.id,
                        'username': usuario.username,
                        'nombre': usuario.nombre,
                        'rol': usuario.rol,
                        'jerarquia': usuario.jerarquia
                    }
                    st.session_state.usuario = usuario
                    
                    # Verificar tasa del día
                    self._verificar_tasa()
                    
                    # Registrar login
                    self._registrar_login(usuario.id)
                    return True
                else:
                    st.error("❌ Contraseña incorrecta")
                    return False
            
            return False
            
        except Exception as e:
            st.error(f"❌ Error en login: {str(e)}")
            return False
    
    def logout(self):
        """Cierra la sesión"""
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.usuario = None
        st.cache_data.clear()
    
    def get_current_user(self) -> Usuario:
        """Obtiene el usuario actual"""
        return st.session_state.get('usuario', None)
    
    def is_authenticated(self) -> bool:
        """Verifica si hay sesión activa"""
        return st.session_state.get('authenticated', False)
    
    def has_role(self, rol_requerido: str) -> bool:
        """Verifica si el usuario tiene un rol específico"""
        if not self.is_authenticated():
            return False
        usuario = self.get_current_user()
        if usuario is None:
            return False
        return usuario.tiene_permiso(rol_requerido)
    
    def _registrar_login(self, user_id: str):
        """Registra el login en el historial"""
        try:
            if self.db:
                self.db.collection('logins').add({
                    'user_id': user_id,
                    'timestamp': datetime.now(),
                    'fecha': date.today().isoformat()
                })
        except Exception as e:
            print(f"Error registrando login: {e}")
    
    def _verificar_tasa(self):
        """Verifica si necesita configurar la tasa del día"""
        if self.tasa_service.necesita_actualizar():
            st.session_state['necesita_tasa'] = True
        else:
            st.session_state['necesita_tasa'] = False
            st.session_state['tasa_actual'] = self.tasa_service.get_tasa()
