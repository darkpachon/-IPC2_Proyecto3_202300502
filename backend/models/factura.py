from datetime import datetime
from typing import List, Dict

class DetalleFactura:
    def __init__(self, id_instancia: int, nombre_instancia: str, tiempo_consumido: float, monto_instancia: float, detalles_recursos: List[Dict]):
        self.id_instancia = id_instancia
        self.nombre_instancia = nombre_instancia
        self.tiempo_consumido = tiempo_consumido
        self.monto_instancia = monto_instancia
        self.detalles_recursos = detalles_recursos  # Lista de dicts con info de recursos

class Factura:
    def __init__(self, numero_factura: str, nit_cliente: str, fecha: str, monto_total: float):
        self.numero_factura = numero_factura
        self.nit_cliente = nit_cliente
        self.fecha = fecha
        self.monto_total = monto_total
        self.detalles = []  # Lista de DetalleFactura
    
    def agregar_detalle(self, detalle: DetalleFactura):
        """Agrega un detalle a la factura"""
        self.detalles.append(detalle)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'numero_factura': self.numero_factura,
            'nit_cliente': self.nit_cliente,
            'fecha': self.fecha,
            'monto_total': self.monto_total,
            'detalles': [
                {
                    'id_instancia': detalle.id_instancia,
                    'nombre_instancia': detalle.nombre_instancia,
                    'tiempo_consumido': detalle.tiempo_consumido,
                    'monto_instancia': detalle.monto_instancia,
                    'detalles_recursos': detalle.detalles_recursos
                } for detalle in self.detalles
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Factura desde un diccionario"""
        factura = cls(
            numero_factura=data['numero_factura'],
            nit_cliente=data['nit_cliente'],
            fecha=data['fecha'],
            monto_total=data['monto_total']
        )
        # Reconstruir detalles
        for detalle_data in data.get('detalles', []):
            detalle = DetalleFactura(
                id_instancia=detalle_data['id_instancia'],
                nombre_instancia=detalle_data['nombre_instancia'],
                tiempo_consumido=detalle_data['tiempo_consumido'],
                monto_instancia=detalle_data['monto_instancia'],
                detalles_recursos=detalle_data['detalles_recursos']
            )
            factura.agregar_detalle(detalle)
        return factura