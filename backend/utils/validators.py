import re
from datetime import datetime

class Validador:
    @staticmethod
    def validar_nit(nit: str) -> bool:
        """Valida el formato de NIT: 1234567-8 o 1234567-K (case insensitive)"""
        if not nit:
            return False
        patron = r'^\d+-\d$|^\d+-[Kk]$'
        return bool(re.match(patron, nit))
    
    @staticmethod
    def extraer_fecha(texto: str) -> str:
        """Extrae una fecha en formato dd/mm/yyyy del texto"""
        if not texto:
            return None
        patron = r'\b(\d{2}/\d{2}/\d{4})\b'
        match = re.search(patron, texto)
        return match.group(1) if match else None
    
    @staticmethod
    def extraer_fecha_hora(texto: str) -> str:
        """Extrae una fecha y hora en formato dd/mm/yyyy hh24:mi del texto"""
        if not texto:
            return None
        patron = r'\b(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\b'
        match = re.search(patron, texto)
        return match.group(1) if match else None
    
    @staticmethod
    def validar_estado_instancia(estado: str) -> bool:
        """Valida que el estado sea 'Vigente' o 'Cancelada' (case insensitive)"""
        if not estado:
            return False
        return estado.lower() in ["vigente", "cancelada"]
    
    @staticmethod
    def normalizar_estado_instancia(estado: str) -> str:
        """Normaliza el estado a 'Vigente' o 'Cancelada'"""
        if not estado:
            return "Vigente"
        estado_lower = estado.lower()
        if estado_lower == "vigente":
            return "Vigente"
        elif estado_lower == "cancelada":
            return "Cancelada"
        return estado
    
    @staticmethod
    def validar_tipo_recurso(tipo: str) -> bool:
        """Valida que el tipo de recurso sea 'Hardware' o 'Software' (case insensitive)"""
        if not tipo:
            return False
        return tipo.lower() in ["hardware", "software"]
    
    @staticmethod
    def normalizar_tipo_recurso(tipo: str) -> str:
        """Normaliza el tipo a 'Hardware' o 'Software'"""
        if not tipo:
            return "Hardware"
        tipo_lower = tipo.lower()
        if tipo_lower == "hardware":
            return "Hardware"
        elif tipo_lower == "software":
            return "Software"
        return tipo