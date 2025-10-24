class Consumo:
    def __init__(self, id: int, nit_cliente: str, id_instancia: int, tiempo: float, fechahora: str, facturado: bool = False):
        self.id = id
        self.nit_cliente = nit_cliente
        self.id_instancia = id_instancia
        self.tiempo = tiempo  # Horas consumidas
        self.fechahora = fechahora
        self.facturado = facturado
    
    def marcar_como_facturado(self):
        """Marca el consumo como facturado"""
        self.facturado = True
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'id': self.id,
            'nit_cliente': self.nit_cliente,
            'id_instancia': self.id_instancia,
            'tiempo': self.tiempo,
            'fechahora': self.fechahora,
            'facturado': self.facturado
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Consumo desde un diccionario"""
        return cls(
            id=data['id'],
            nit_cliente=data['nit_cliente'],
            id_instancia=data['id_instancia'],
            tiempo=data['tiempo'],
            fechahora=data['fechahora'],
            facturado=data.get('facturado', False)
        )