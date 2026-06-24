# create_user.py
import os
import json
from firebase_config import init_firebase, get_db
import hashlib
from datetime import datetime

def hash_password(password):
    """Genera un hash simple de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def crear_usuario():
    print("=== Crear Usuario en DELICAFE ===")
    
    # Inicializar Firebase
    init_firebase()
    db = get_db()
    
    if not db:
        print("❌ Error: No se pudo conectar a Firebase")
        return
    
    print("✅ Conexión a Firebase exitosa")
    
    # Datos del usuario
    username = input("Nombre de usuario: ")
    password = input("Contraseña: ")
    nombre = input("Nombre completo: ")
    email = input("Email: ")
    
    # Datos del usuario a guardar
    user_data = {
        'username': username,
        'password_hash': hash_password(password),
        'nombre': nombre,
        'rol': 'admin',
        'jerarquia': 5,  # 5 es el nivel más alto
        'email': email,
        'fecha_creacion': datetime.now()
    }
    
    try:
        # Guardar en Firestore
        doc_ref = db.collection('usuarios').add(user_data)
        print(f"✅ Usuario '{username}' creado exitosamente")
        print(f"📝 ID del documento: {doc_ref[1].id}")
        
        # Mostrar resumen
        print("\n=== Resumen del Usuario ===")
        print(f"Usuario: {username}")
        print(f"Nombre: {nombre}")
        print(f"Email: {email}")
        print(f"Rol: admin")
        print(f"Jerarquía: 5 (Máximo)")
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")

if __name__ == "__main__":
    crear_usuario()
