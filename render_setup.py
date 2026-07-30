# render_setup.py - Script para ejecutar en Render Shell
import os
import sys
import json
from datetime import datetime

print("=" * 60)
print("🔄 CONFIGURACIÓN DE RENDER - ARTE PARÍS DELICAFE")
print("=" * 60)

# =====================================================
# PASO 1: Verificar variables de entorno
# =====================================================
print("\n📋 VERIFICANDO VARIABLES DE ENTORNO...")
print("-" * 40)

firebase_creds = os.getenv('FIREBASE_SERVICE_ACCOUNT')
if firebase_creds:
    print("✅ FIREBASE_SERVICE_ACCOUNT: Configurada")
    # Mostrar parte del contenido para verificar
    try:
        creds_dict = json.loads(firebase_creds)
        print(f"   📍 Project ID: {creds_dict.get('project_id', 'No disponible')}")
        print(f"   📍 Client Email: {creds_dict.get('client_email', 'No disponible')}")
    except:
        print("   ⚠️ No se pudo parsear el JSON. Verifica el formato.")
else:
    print("❌ FIREBASE_SERVICE_ACCOUNT: NO CONFIGURADA")
    print("   💡 Debes agregarla en Render → Environment Variables")
    sys.exit(1)

# =====================================================
# PASO 2: Inicializar Firebase
# =====================================================
print("\n🔥 INICIALIZANDO FIREBASE...")
print("-" * 40)

try:
    from services.firebase_service import FirebaseService
    firebase = FirebaseService()
    db = firebase.get_db()
    
    if db:
        print("✅ Firebase inicializado correctamente")
    else:
        print("❌ Error al inicializar Firebase")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# =====================================================
# PASO 3: Verificar/Crear usuario administrador
# =====================================================
print("\n👤 VERIFICANDO USUARIO ADMINISTRADOR...")
print("-" * 40)

from models.usuario import Usuario
import hashlib

# Datos del usuario admin por defecto
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_PASSWORD_HASH = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()

# Buscar usuario
users_ref = db.collection('usuarios')
query = users_ref.where('username', '==', ADMIN_USERNAME).limit(1)
docs = query.get()

if docs:
    print(f"✅ Usuario '{ADMIN_USERNAME}' ya existe")
    
    # Verificar hash
    for doc in docs:
        data = doc.to_dict()
        stored_hash = data.get('password_hash', '')
        
        if stored_hash == ADMIN_PASSWORD_HASH:
            print("✅ Hash de contraseña correcto")
        else:
            print("⚠️ Hash de contraseña incorrecto. Actualizando...")
            doc.reference.update({'password_hash': ADMIN_PASSWORD_HASH})
            print("✅ Hash actualizado correctamente")
        
        # Asegurar que está activo
        if not data.get('activo', True):
            print("⚠️ Usuario inactivo. Activando...")
            doc.reference.update({'activo': True})
            print("✅ Usuario activado")
        
        # Asegurar jerarquía máxima
        if data.get('jerarquia', 0) < 5:
            print("⚠️ Jerarquía incorrecta. Actualizando a 5...")
            doc.reference.update({'jerarquia': 5})
            print("✅ Jerarquía actualizada")
        
        # Asegurar rol
        if data.get('rol') != 'administrador':
            print("⚠️ Rol incorrecto. Actualizando...")
            doc.reference.update({'rol': 'administrador'})
            print("✅ Rol actualizado")
else:
    print(f"⚠️ Usuario '{ADMIN_USERNAME}' NO existe. Creando...")
    
    # Crear usuario admin
    user_data = {
        'username': ADMIN_USERNAME,
        'nombre': 'Administrador',
        'email': 'admin@delicafe.com',
        'rol': 'administrador',
        'jerarquia': 5,
        'password_hash': ADMIN_PASSWORD_HASH,
        'activo': True,
        'fecha_creacion': datetime.now()
    }
    
    try:
        doc_ref = db.collection('usuarios').add(user_data)
        print(f"✅ Usuario '{ADMIN_USERNAME}' creado exitosamente")
        print(f"   📝 ID del documento: {doc_ref[1].id}")
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        sys.exit(1)

# =====================================================
# PASO 4: Verificar tasa de cambio
# =====================================================
print("\n💱 VERIFICANDO TASA DE CAMBIO...")
print("-" * 40)

from services.tasa_service import TasaService

tasa_service = TasaService()
tasa = tasa_service.get_tasa()

if tasa > 0:
    print(f"✅ Tasa de cambio actual: 1 $ = {tasa:,.2f} Bs")
else:
    print("⚠️ No hay tasa configurada")
    print("💡 Se usará el valor por defecto al iniciar la app")

# =====================================================
# PASO 5: RESUMEN FINAL
# =====================================================
print("\n" + "=" * 60)
print("✅ SETUP COMPLETADO EXITOSAMENTE")
print("=" * 60)

print("\n📋 CREDENCIALES DE ACCESO:")
print("-" * 40)
print(f"   👤 Usuario: {ADMIN_USERNAME}")
print(f"   🔑 Contraseña: {ADMIN_PASSWORD}")
print(f"   🎭 Rol: Administrador")
print("-" * 40)

print("\n💡 PRÓXIMOS PASOS:")
print("   1. Ve a tu app en Render")
print("   2. Inicia sesión con admin/admin123")
print("   3. La app te pedirá configurar la tasa de cambio")
print("   4. ¡Listo! Comienza a usar el sistema")

print("\n" + "=" * 60)
print("🚀 ¡Arte París - DELICAFE está listo para usar!")
print("=" * 60)
