import re
from datetime import datetime

class Validador:
    @staticmethod
    def validar_nit(nit: str) -> bool:
        """Valida el formato de NIT: 1234567-8 o 1234567-K"""
        patron = r'^\d+-\d$|^\d+-[Kk]$'
        return bool(re.match(patron, nit))
    
    @staticmethod
    def extraer_fecha(texto: str) -> str:
        """Extrae una fecha en formato dd/mm/yyyy del texto"""
        patron = r'\b(\d{2}/\d{2}/\d{4})\b'
        match = re.search(patron, texto)
        return match.group(1) if match else None
    
    @staticmethod
    def extraer_fecha_hora(texto: str) -> str:
        """Extrae una fecha y hora en formato dd/mm/yyyy hh24:mi del texto"""
        patron = r'\b(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\b'
        match = re.search(patron, texto)
        return match.group(1) if match else None
    
    @staticmethod
    def validar_estado_instancia(estado: str) -> bool:
        """Valida que el estado sea 'Vigente' o 'Cancelada'"""
        return estado in ["Vigente", "Cancelada"]
    
    @staticmethod
    def validar_tipo_recurso(tipo: str) -> bool:
        """Valida que el tipo de recurso sea 'Hardware' o 'Software'"""
        return tipo in ["Hardware", "Software"]