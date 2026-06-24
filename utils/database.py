import streamlit as st
from firebase_config import get_db
import datetime
from typing import Dict, List, Optional

def get_tasa_cambio(fecha=None):
    """Obtiene la tasa de cambio para una fecha específica"""
    if fecha is None:
        fecha = datetime.date.today().isoformat()
    
    db = get_db()
    try:
        # Buscar tasa de cambio para la fecha
        tasa_ref = db.collection('tasas_cambio').where('fecha', '==', fecha).limit(1)
        docs = tasa_ref.get()
        
        for doc in docs:
            return doc.to_dict().get('tasa', 621.52)  # Valor por defecto
        
        # Si no hay tasa, buscar la más reciente
        tasa_ref = db.collection('tasas_cambio').order_by('fecha', direction='DESCENDING').limit(1)
        docs = tasa_ref.get()
        for doc in docs:
            return doc.to_dict().get('tasa', 621.52)
        
        return 621.52  # Valor por defecto
    except Exception as e:
        print(f"Error obteniendo tasa: {e}")
        return 621.52

def guardar_tasa_cambio(tasa, fecha=None):
    """Guarda la tasa de cambio para una fecha"""
    if fecha is None:
        fecha = datetime.date.today().isoformat()
    
    db = get_db()
    try:
        db.collection('tasas_cambio').add({
            'fecha': fecha,
            'tasa': tasa,
            'actualizado': datetime.datetime.now()
        })
        return True
    except Exception as e:
        print(f"Error guardando tasa: {e}")
        return False

def guardar_producto(data: Dict):
    """Guarda un producto en la base de datos"""
    db = get_db()
    try:
        data['fecha_creacion'] = datetime.datetime.now()
        data['fecha_actualizacion'] = datetime.datetime.now()
        doc_ref = db.collection('productos').add(data)
        return doc_ref[1].id
    except Exception as e:
        print(f"Error guardando producto: {e}")
        return None

def get_productos(tipo=None):
    """Obtiene productos filtrados por tipo"""
    db = get_db()
    try:
        query = db.collection('productos')
        if tipo:
            query = query.where('tipo', '==', tipo)
        
        productos = []
        docs = query.get()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            productos.append(data)
        
        return productos
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
        return []

def guardar_venta(data: Dict):
    """Guarda una venta en la base de datos"""
    db = get_db()
    try:
        # Obtener tasa del día
        tasa = get_tasa_cambio()
        data['tasa_cambio'] = tasa
        data['fecha_creacion'] = datetime.datetime.now()
        data['fecha'] = datetime.date.today().isoformat()
        
        # Guardar venta
        doc_ref = db.collection('ventas').add(data)
        return doc_ref[1].id
    except Exception as e:
        print(f"Error guardando venta: {e}")
        return None

def get_ventas(fecha_inicio=None, fecha_fin=None):
    """Obtiene ventas en un rango de fechas"""
    db = get_db()
    try:
        query = db.collection('ventas')
        
        if fecha_inicio:
            query = query.where('fecha', '>=', fecha_inicio)
        if fecha_fin:
            query = query.where('fecha', '<=', fecha_fin)
        
        ventas = []
        docs = query.order_by('fecha', direction='DESCENDING').get()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            ventas.append(data)
        
        return ventas
    except Exception as e:
        print(f"Error obteniendo ventas: {e}")
        return []

def guardar_compra(data: Dict):
    """Guarda una compra/orden en la base de datos"""
    db = get_db()
    try:
        # Obtener tasa del día
        tasa = get_tasa_cambio()
        data['tasa_cambio'] = tasa
        data['fecha_creacion'] = datetime.datetime.now()
        data['fecha'] = datetime.date.today().isoformat()
        
        doc_ref = db.collection('compras').add(data)
        return doc_ref[1].id
    except Exception as e:
        print(f"Error guardando compra: {e}")
        return None

def get_compras(fecha_inicio=None, fecha_fin=None):
    """Obtiene compras en un rango de fechas"""
    db = get_db()
    try:
        query = db.collection('compras')
        
        if fecha_inicio:
            query = query.where('fecha', '>=', fecha_inicio)
        if fecha_fin:
            query = query.where('fecha', '<=', fecha_fin)
        
        compras = []
        docs = query.order_by('fecha', direction='DESCENDING').get()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            compras.append(data)
        
        return compras
    except Exception as e:
        print(f"Error obteniendo compras: {e}")
        return []

def guardar_balance_diario(data: Dict):
    """Guarda el balance diario"""
    db = get_db()
    try:
        data['fecha'] = datetime.date.today().isoformat()
        data['fecha_creacion'] = datetime.datetime.now()
        doc_ref = db.collection('balances_diarios').add(data)
        return doc_ref[1].id
    except Exception as e:
        print(f"Error guardando balance: {e}")
        return None

def get_balance_diario(fecha=None):
    """Obtiene el balance diario para una fecha"""
    if fecha is None:
        fecha = datetime.date.today().isoformat()
    
    db = get_db()
    try:
        query = db.collection('balances_diarios').where('fecha', '==', fecha).limit(1)
        docs = query.get()
        
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        
        return None
    except Exception as e:
        print(f"Error obteniendo balance: {e}")
        return None

def convertir_moneda(monto_bs, tasa=None):
    """Convierte Bs a USD o viceversa"""
    if tasa is None:
        tasa = get_tasa_cambio()
    
    return {
        'bs': monto_bs,
        'usd': monto_bs / tasa if tasa > 0 else 0,
        'tasa': tasa
    }
