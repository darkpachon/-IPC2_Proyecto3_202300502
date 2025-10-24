from .instancia import Instancia

class Cliente:
    def __init__(self, nit: str, nombre: str, usuario: str, clave: str, direccion: str, correo_electronico: str):
        self.nit = nit
        self.nombre = nombre
        self.usuario = usuario
        self.clave = clave
        self.direccion = direccion
        self.correo_electronico = correo_electronico
        self.instancias = []  # Lista de objetos Instancia
    
    def agregar_instancia(self, instancia: Instancia):
        """Agrega una instancia al cliente"""
        self.instancias.append(instancia)
    
    def obtener_instancia_por_id(self, instancia_id: int):
        """Obtiene una instancia por su ID"""
        for instancia in self.instancias:
            if instancia.id == instancia_id:
                return instancia
        return None
    
    def cancelar_instancia(self, instancia_id: int, fecha_final: str):
        """Cancela una instancia del cliente"""
        instancia = self.obtener_instancia_por_id(instancia_id)
        if instancia:
            instancia.cancelar(fecha_final)
            return True
        return False
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'nit': self.nit,
            'nombre': self.nombre,
            'usuario': self.usuario,
            'clave': self.clave,
            'direccion': self.direccion,
            'correo_electronico': self.correo_electronico,
            'instancias': [instancia.to_dict() for instancia in self.instancias]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Cliente desde un diccionario"""
        cliente = cls(
            nit=data['nit'],
            nombre=data['nombre'],
            usuario=data['usuario'],
            clave=data['clave'],
            direccion=data['direccion'],
            correo_electronico=data['correo_electronico']
        )
        # Reconstruir instancias
        for instancia_data in data.get('instancias', []):
            instancia = Instancia.from_dict(instancia_data)
            cliente.agregar_instancia(instancia)
        return cliente