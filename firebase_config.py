import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json

firebase_app = None
db = None

def init_firebase():
    global firebase_app, db
    
    if not firebase_admin._apps:
        try:
            # Leer credenciales desde variables de entorno individuales
            service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
            
            if service_account_json:
                # Parsear el JSON de la cuenta de servicio
                cred_dict = json.loads(service_account_json)
                cred = credentials.Certificate(cred_dict)
                firebase_app = firebase_admin.initialize_app(cred)
            else:
                # Para desarrollo local - usar archivo
                try:
                    cred = credentials.Certificate('firebase-credentials.json')
                    firebase_app = firebase_admin.initialize_app(cred)
                except:
                    print("No se encontró credencial de Firebase")
                    return None, None
            
            db = firestore.client()
            print("Firebase inicializado correctamente")
            
        except Exception as e:
            print(f"Error inicializando Firebase: {e}")
            return None, None
    
    return firebase_app, db

def get_db():
    return db

def get_auth():
    return auth

def get_firebase_config():
    """Obtiene la configuración de Firebase para el cliente"""
    return {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID') or os.getenv('FIREBASE_STORAGE_BUCKET', '').split('.')[0],
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID')
    }
