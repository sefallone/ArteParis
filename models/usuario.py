# models/usuario.py
from datetime import datetime
import hashlib
from config import Config

class Usuario:
    """Clase que representa un usuario del sistema"""
    
    def __init__(self, data: dict, doc_id: str = None):
        self.id = doc_id
        self.username = data.get('username', '')
        self.nombre = data.get('nombre', '')
        self.email = data.get('email', '')
        self.rol = data.get('rol', 'auxiliar')  # administrador, gerente, cajero, auxiliar
        self.jerarquia = data.get('jerarquia', Config.get_rol_level('auxiliar'))
        self.password_hash = data.get('password_hash', '')
        self.activo = data.get('activo', True)
        self.fecha_creacion = data.get('fecha_creacion', datetime.now())
        self.ultimo_login = data.get('ultimo_login', None)
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para guardar en Firestore"""
        return {
            'username': self.username,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'jerarquia': self.jerarquia,
            'password_hash': self.password_hash,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion,
            'ultimo_login': self.ultimo_login
        }
    
    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña coincide"""
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera el hash de una contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def tiene_permiso(self, rol_requerido: str) -> bool:
        """Verifica si el usuario tiene el rol requerido o superior"""
        nivel_requerido = Config.get_rol_level(rol_requerido)
        return self.jerarquia >= nivel_requerido
    
    def es_admin(self) -> bool:
        """Verifica si es administrador"""
        return self.rol == 'administrador'
    
    def puede_editar(self) -> bool:
        """Verifica si puede editar (admin o gerente)"""
        return self.jerarquia >= Config.get_rol_level('gerente')
    
    def __str__(self):
        return f"{self.nombre} ({self.rol})"
