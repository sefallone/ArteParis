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
            # Leer credenciales desde variable de entorno
            cred_json = os.getenv('FIREBASE_CREDENTIALS')
            if cred_json:
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
            else:
                # Para desarrollo local
                cred = credentials.Certificate('firebase-credentials.json')
            
            firebase_app = firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("Firebase inicializado correctamente")
        except Exception as e:
            print(f"Error inicializando Firebase: {e}")
    
    return firebase_app, db

def get_db():
    return db

def get_auth():
    return auth
