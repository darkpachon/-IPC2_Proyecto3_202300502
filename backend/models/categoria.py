from .configuracion import Configuracion

class Categoria:
    def __init__(self, id: int, nombre: str, descripcion: str, carga_trabajo: str):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.carga_trabajo = carga_trabajo
        self.configuraciones = []  # Lista de objetos Configuracion
    
    def agregar_configuracion(self, configuracion: Configuracion):
        """Agrega una configuración a la categoría"""
        self.configuraciones.append(configuracion)
    
    def obtener_configuracion_por_id(self, configuracion_id: int):
        """Obtiene una configuración por su ID"""
        for config in self.configuraciones:
            if config.id == configuracion_id:
                return config
        return None
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'carga_trabajo': self.carga_trabajo,
            'configuraciones': [config.to_dict() for config in self.configuraciones]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Categoria desde un diccionario"""
        categoria = cls(
            id=data['id'],
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            carga_trabajo=data['carga_trabajo']
        )
        # Reconstruir configuraciones
        for config_data in data.get('configuraciones', []):
            configuracion = Configuracion.from_dict(config_data)
            categoria.agregar_configuracion(configuracion)
        return categoria