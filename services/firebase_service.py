# services/firebase_service.py
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
from config import Config

class FirebaseService:
    """Servicio para manejar la conexión a Firebase"""
    
    _instance = None
    _app = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._app is None:
            self._inicializar()
    
    def _inicializar(self):
        """Inicializa la conexión a Firebase"""
        if not firebase_admin._apps:
            try:
                # Intentar desde variable de entorno (Render)
                service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
                
                if service_account_json:
                    cred_dict = json.loads(service_account_json)
                    cred = credentials.Certificate(cred_dict)
                    self._app = firebase_admin.initialize_app(cred)
                else:
                    # Desarrollo local
                    try:
                        cred = credentials.Certificate('firebase-credentials.json')
                        self._app = firebase_admin.initialize_app(cred)
                    except FileNotFoundError:
                        print("⚠️ No se encontró archivo de credenciales de Firebase")
                        return
                
                self._db = firestore.client()
                print("✅ Firebase inicializado correctamente")
                
            except Exception as e:
                print(f"❌ Error inicializando Firebase: {e}")
                self._app = None
                self._db = None
    
    def get_db(self):
        """Retorna la instancia de Firestore"""
        return self._db
    
    def get_auth(self):
        """Retorna el cliente de autenticación"""
        return auth
    
    def is_connected(self) -> bool:
        """Verifica si la conexión está activa"""
        return self._db is not None
    
    @staticmethod
    def get_instance():
        """Obtiene la instancia única del servicio"""
        return FirebaseService()
