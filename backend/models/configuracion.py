from typing import Dict

class Configuracion:
    def __init__(self, id: int, nombre: str, descripcion: str):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.recursos = {}  # {recurso_id: cantidad}
    
    def agregar_recurso(self, recurso_id: int, cantidad: float):
        """Agrega un recurso a la configuración"""
        self.recursos[recurso_id] = cantidad
    
    def calcular_costo_hora(self, sistema) -> float:
        """Calcula el costo por hora de esta configuración"""
        costo_total = 0
        for recurso_id, cantidad in self.recursos.items():
            recurso = sistema.obtener_recurso_por_id(recurso_id)
            if recurso:
                costo_total += recurso.calcular_costo(1, cantidad)
        return costo_total
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'recursos': self.recursos
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Configuracion desde un diccionario"""
        configuracion = cls(
            id=data['id'],
            nombre=data['nombre'],
            descripcion=data['descripcion']
        )
        configuracion.recursos = data.get('recursos', {})
        return configuracion