class Recurso:
    def __init__(self, id: int, nombre: str, abreviatura: str, metrica: str, tipo: str, valor_x_hora: float):
        self.id = id
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.metrica = metrica
        self.tipo = tipo  # "Hardware" o "Software"
        self.valor_x_hora = valor_x_hora
    
    def calcular_costo(self, horas: float, cantidad: float = 1) -> float:
        """Calcula el costo total del recurso para un tiempo y cantidad dados"""
        return self.valor_x_hora * horas * cantidad
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'abreviatura': self.abreviatura,
            'metrica': self.metrica,
            'tipo': self.tipo,
            'valor_x_hora': self.valor_x_hora
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Recurso desde un diccionario"""
        return cls(
            id=data['id'],
            nombre=data['nombre'],
            abreviatura=data['abreviatura'],
            metrica=data['metrica'],
            tipo=data['tipo'],
            valor_x_hora=data['valor_x_hora']
        )