# create_user.py - Versión actualizada
import os
import json
from services.firebase_service import FirebaseService
from models.usuario import Usuario
from config import Config

def crear_usuario_admin():
    print("=== CREAR USUARIO ADMINISTRADOR ===")
    
    # Inicializar Firebase
    firebase = FirebaseService()
    db = firebase.get_db()
    
    if not db:
        print("❌ Error: No se pudo conectar a Firebase")
        return
    
    print("✅ Conexión a Firebase exitosa")
    
    # Datos del usuario
    username = input("Nombre de usuario (ej: admin): ") or "admin"
    password = input("Contraseña (ej: admin123): ") or "admin123"
    nombre = input("Nombre completo (ej: Administrador): ") or "Administrador"
    email = input("Email: ") or "admin@delicafe.com"
    
    # Hash de la contraseña
    password_hash = Usuario.hash_password(password)
    
    # Datos del usuario
    user_data = {
        'username': username,
        'nombre': nombre,
        'email': email,
        'rol': 'administrador',
        'jerarquia': Config.get_rol_level('administrador'),
        'password_hash': password_hash,
        'activo': True,
        'fecha_creacion': datetime.now()
    }
    
    try:
        # Verificar si ya existe
        query = db.collection('usuarios').where('username', '==', username).limit(1)
        docs = query.get()
        
        if docs:
            print(f"⚠️ El usuario '{username}' ya existe")
            actualizar = input("¿Deseas actualizar su contraseña? (s/n): ")
            if actualizar.lower() == 's':
                for doc in docs:
                    doc.reference.update({'password_hash': password_hash})
                    print(f"✅ Contraseña actualizada para '{username}'")
            return
        
        # Guardar en Firestore
        doc_ref = db.collection('usuarios').add(user_data)
        print(f"✅ Usuario '{username}' creado exitosamente")
        print(f"📝 ID del documento: {doc_ref[1].id}")
        
        # Mostrar resumen
        print("\n=== RESUMEN DEL USUARIO ===")
        print(f"Usuario: {username}")
        print(f"Nombre: {nombre}")
        print(f"Email: {email}")
        print(f"Rol: administrador")
        print(f"Jerarquía: {Config.get_rol_level('administrador')} (Máximo)")
        print(f"Contraseña: {password}")
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")

if __name__ == "__main__":
    from datetime import datetime
    crear_usuario_admin()
