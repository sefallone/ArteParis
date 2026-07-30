# config.py - Configuración central de la aplicación
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración central de la aplicación"""
    
    # --- Firebase ---
    FIREBASE_SERVICE_ACCOUNT = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')
    
    # --- App ---
    APP_NAME = "Arte París - DELICAFE"
    APP_SUBTITLE = "Gestión Administrativa para Inversiones FLG, C.A."
    APP_ICON = "☕"
    
    # --- Roles y Jerarquías ---
    ROLES = {
        'administrador': 5,
        'gerente': 4,
        'cajero': 3,
        'auxiliar': 2
    }
    
    # --- Monedas ---
    MONEDA_LOCAL = "Bs."
    MONEDA_EXTRANJERA = "$"
    
    # --- Tasa de Cambio por Defecto ---
    TASA_DEFAULT = 790.00  # Cambia esto según tu país
    
    # --- Rutas ---
    ASSETS_PATH = "assets"
    LOGO_PATH = "assets/logo_nuevo.jpg"
    
    @classmethod
    def get_rol_name(cls, nivel):
        """Obtiene el nombre del rol según el nivel"""
        for nombre, nivel_rol in cls.ROLES.items():
            if nivel_rol == nivel:
                return nombre.capitalize()
        return "Usuario"
    
    @classmethod
    def get_rol_level(cls, nombre_rol):
        """Obtiene el nivel de un rol"""
        return cls.ROLES.get(nombre_rol.lower(), 0)
