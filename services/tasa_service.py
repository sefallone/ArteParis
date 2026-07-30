# services/tasa_service.py
from datetime import datetime, date
from services.firebase_service import FirebaseService
from config import Config

class TasaService:
    """Servicio para manejar la tasa de cambio"""
    
    def __init__(self):
        self.db = FirebaseService.get_instance().get_db()
    
    def get_tasa(self, fecha=None) -> float:
        """Obtiene la tasa de cambio para una fecha específica"""
        if fecha is None:
            fecha = date.today().isoformat()
        
        try:
            if self.db is None:
                return Config.TASA_DEFAULT
            
            # Buscar tasa para la fecha
            tasa_ref = self.db.collection('tasas_cambio').where('fecha', '==', fecha).limit(1)
            docs = tasa_ref.get()
            
            for doc in docs:
                return doc.to_dict().get('tasa', Config.TASA_DEFAULT)
            
            # Si no hay tasa para hoy, buscar la más reciente
            tasa_ref = self.db.collection('tasas_cambio').order_by('fecha', direction='DESCENDING').limit(1)
            docs = tasa_ref.get()
            for doc in docs:
                return doc.to_dict().get('tasa', Config.TASA_DEFAULT)
            
            return Config.TASA_DEFAULT
            
        except Exception as e:
            print(f"Error obteniendo tasa: {e}")
            return Config.TASA_DEFAULT
    
    def guardar_tasa(self, tasa: float, fecha=None) -> bool:
        """Guarda la tasa de cambio para una fecha"""
        if fecha is None:
            fecha = date.today().isoformat()
        
        try:
            if self.db is None:
                return False
            
            # Verificar si ya existe tasa para esta fecha
            existing = self.db.collection('tasas_cambio').where('fecha', '==', fecha).limit(1).get()
            for doc in existing:
                # Actualizar
                doc.reference.update({'tasa': tasa, 'actualizado': datetime.now()})
                return True
            
            # Crear nueva
            self.db.collection('tasas_cambio').add({
                'fecha': fecha,
                'tasa': tasa,
                'actualizado': datetime.now()
            })
            return True
            
        except Exception as e:
            print(f"Error guardando tasa: {e}")
            return False
    
    def necesita_actualizar(self) -> bool:
        """Verifica si la tasa del día necesita ser configurada"""
        fecha_hoy = date.today().isoformat()
        tasa_hoy = self.get_tasa(fecha_hoy)
        return tasa_hoy == Config.TASA_DEFAULT
    
    def convertir(self, monto: float, tasa: float = None) -> dict:
        """Convierte un monto entre monedas"""
        if tasa is None:
            tasa = self.get_tasa()
        
        return {
            'bs': monto,
            'usd': monto / tasa if tasa > 0 else 0,
            'tasa': tasa
        }
