from datetime import datetime

class Instancia:
    def __init__(self, id: int, id_configuracion: int, nombre: str, fecha_inicio: str, estado: str = "Vigente", fecha_final: str = None):
        self.id = id
        self.id_configuracion = id_configuracion
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.estado = estado  # "Vigente" o "Cancelada"
        self.fecha_final = fecha_final
        self.consumos = []  # Lista de horas consumidas
    
    def cancelar(self, fecha_final: str):
        """Cancela la instancia"""
        self.estado = "Cancelada"
        self.fecha_final = fecha_final
    
    def agregar_consumo(self, horas: float):
        """Agrega horas de consumo a la instancia"""
        self.consumos.append(horas)
    
    def get_total_consumo(self) -> float:
        """Obtiene el total de horas consumidas"""
        return sum(self.consumos)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'id': self.id,
            'id_configuracion': self.id_configuracion,
            'nombre': self.nombre,
            'fecha_inicio': self.fecha_inicio,
            'estado': self.estado,
            'fecha_final': self.fecha_final,
            'total_consumo': self.get_total_consumo()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Instancia desde un diccionario"""
        instancia = cls(
            id=data['id'],
            id_configuracion=data['id_configuracion'],
            nombre=data['nombre'],
            fecha_inicio=data['fecha_inicio'],
            estado=data.get('estado', 'Vigente'),
            fecha_final=data.get('fecha_final')
        )
        # Los consumos se manejan por separado
        return instancia