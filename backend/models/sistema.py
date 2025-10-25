from typing import List
from .recurso import Recurso
from .categoria import Categoria
from .configuracion import Configuracion
from .cliente import Cliente
from .instancia import Instancia
from .consumo import Consumo
from .factura import Factura, DetalleFactura

class Sistema:
    def __init__(self):
        self.recursos: List[Recurso] = []
        self.categorias: List[Categoria] = []
        self.clientes: List[Cliente] = []
        self.consumos: List[Consumo] = []
        self.facturas: List[Factura] = []
        self.proximo_id_factura = 1
        self.proximo_id_consumo = 1
    
    # MÉTODOS FALTANTES AGREGADOS
    def agregar_recurso(self, recurso: Recurso):
        """Agrega un recurso al sistema"""
        self.recursos.append(recurso)
    
    def agregar_categoria(self, categoria: Categoria):
        """Agrega una categoría al sistema"""
        self.categorias.append(categoria)
    
    def agregar_cliente(self, cliente: Cliente):
        """Agrega un cliente al sistema"""
        self.clientes.append(cliente)
    
    def agregar_factura(self, factura: Factura):
        """Agrega una factura al sistema"""
        self.facturas.append(factura)
    
    def obtener_recurso_por_id(self, recurso_id: int):
        """Obtiene un recurso por su ID"""
        for recurso in self.recursos:
            if recurso.id == recurso_id:
                return recurso
        return None
    
    def obtener_categoria_por_id(self, categoria_id: int):
        """Obtiene una categoría por su ID"""
        for categoria in self.categorias:
            if categoria.id == categoria_id:
                return categoria
        return None
    
    def obtener_cliente_por_nit(self, nit: str):
        """Obtiene un cliente por su NIT"""
        for cliente in self.clientes:
            if cliente.nit == nit:
                return cliente
        return None
    
    def obtener_configuracion_por_id(self, configuracion_id: int):
        """Obtiene una configuración por su ID"""
        for categoria in self.categorias:
            for configuracion in categoria.configuraciones:
                if configuracion.id == configuracion_id:
                    return configuracion
        return None
    
    def obtener_instancia_por_id(self, instancia_id: int):
        """Obtiene una instancia por su ID"""
        for cliente in self.clientes:
            for instancia in cliente.instancias:
                if instancia.id == instancia_id:
                    return instancia
        return None
    
    def generar_numero_factura(self):
        """Genera un número de factura único"""
        numero = f"FACT-{self.proximo_id_factura:06d}"
        self.proximo_id_factura += 1
        return numero
    
    def generar_id_consumo(self) -> int:
        """Genera un ID único para consumo"""
        id_actual = self.proximo_id_consumo
        self.proximo_id_consumo += 1
        return id_actual
    
    def agregar_consumo(self, consumo: Consumo):
        """Agrega un consumo al sistema"""
        self.consumos.append(consumo)
    
    def obtener_consumos_no_facturados(self, nit_cliente: str = None):
        """Obtiene consumos no facturados, opcionalmente filtrados por cliente"""
        consumos_no_facturados = [c for c in self.consumos if not c.facturado]
        
        if nit_cliente:
            consumos_no_facturados = [c for c in consumos_no_facturados if c.nit_cliente == nit_cliente]
        
        return consumos_no_facturados
    
    def obtener_consumos_por_instancia(self, id_instancia: int):
        """Obtiene todos los consumos de una instancia"""
        return [c for c in self.consumos if c.id_instancia == id_instancia]
    
    def generar_facturacion(self, fecha_inicio: str, fecha_fin: str):
        """Genera facturas para todos los clientes con consumos no facturados en el rango de fechas"""
        from utils.validators import Validador
        
        facturas_generadas = []
        
        # Extraer fechas válidas
        fecha_inicio_dt = Validador.extraer_fecha(fecha_inicio)
        fecha_fin_dt = Validador.extraer_fecha(fecha_fin)
        
        if not fecha_inicio_dt or not fecha_fin_dt:
            raise ValueError("Fechas inválidas")
        
        # Para cada cliente, generar factura si tiene consumos no facturados
        for cliente in self.clientes:
            consumos_cliente = self.obtener_consumos_no_facturados(cliente.nit)
            
            if consumos_cliente:
                factura = self._generar_factura_cliente(cliente, consumos_cliente, fecha_fin)
                if factura:
                    facturas_generadas.append(factura)
                    
                    # Marcar consumos como facturados
                    for consumo in consumos_cliente:
                        consumo.marcar_como_facturado()
        
        return facturas_generadas
    
    def _generar_factura_cliente(self, cliente: Cliente, consumos: List[Consumo], fecha_factura: str):
        """Genera una factura para un cliente específico"""
        monto_total = 0
        detalles_factura = []
        
        # Agrupar consumos por instancia
        consumos_por_instancia = {}
        for consumo in consumos:
            if consumo.id_instancia not in consumos_por_instancia:
                consumos_por_instancia[consumo.id_instancia] = []
            consumos_por_instancia[consumo.id_instancia].append(consumo)
        
        # Procesar cada instancia
        for id_instancia, consumos_instancia in consumos_por_instancia.items():
            instancia = cliente.obtener_instancia_por_id(id_instancia)
            if not instancia:
                continue
                
            configuracion = self.obtener_configuracion_por_id(instancia.id_configuracion)
            if not configuracion:
                continue
            
            # Calcular tiempo total de la instancia
            tiempo_total = sum(consumo.tiempo for consumo in consumos_instancia)
            
            # Calcular costo de la instancia y detalle de recursos
            monto_instancia = 0
            detalles_recursos = []
            
            for recurso_id, cantidad in configuracion.recursos.items():
                recurso = self.obtener_recurso_por_id(recurso_id)
                if recurso:
                    costo_recurso = recurso.calcular_costo(tiempo_total, cantidad)
                    monto_instancia += costo_recurso
                    
                    detalles_recursos.append({
                        'id_recurso': recurso.id,
                        'nombre_recurso': recurso.nombre,
                        'cantidad': cantidad,
                        'valor_x_hora': recurso.valor_x_hora,
                        'costo': costo_recurso
                    })
            
            monto_total += monto_instancia
            
            # Crear detalle de factura para esta instancia
            detalle = DetalleFactura(
                id_instancia=instancia.id,
                nombre_instancia=instancia.nombre,
                tiempo_consumido=tiempo_total,
                monto_instancia=monto_instancia,
                detalles_recursos=detalles_recursos
            )
            detalles_factura.append(detalle)
        
        if monto_total > 0:
            factura = Factura(
                numero_factura=self.generar_numero_factura(),
                nit_cliente=cliente.nit,
                fecha=fecha_factura,
                monto_total=monto_total
            )
            
            for detalle in detalles_factura:
                factura.agregar_detalle(detalle)
            
            self.agregar_factura(factura)
            return factura
        
        return None

    def to_dict(self):
        """Convierte todo el sistema a diccionario para serialización"""
        return {
            'recursos': [recurso.to_dict() for recurso in self.recursos],
            'categorias': [categoria.to_dict() for categoria in self.categorias],
            'clientes': [cliente.to_dict() for cliente in self.clientes],
            'consumos': [consumo.to_dict() for consumo in self.consumos],
            'facturas': [factura.to_dict() for factura in self.facturas],
            'proximo_id_factura': self.proximo_id_factura,
            'proximo_id_consumo': self.proximo_id_consumo
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Reconstruye el sistema desde un diccionario"""
        sistema = cls()
        
        # Reconstruir recursos
        for recurso_data in data.get('recursos', []):
            recurso = Recurso.from_dict(recurso_data)
            sistema.agregar_recurso(recurso)
        
        # Reconstruir categorías
        for categoria_data in data.get('categorias', []):
            categoria = Categoria.from_dict(categoria_data)
            sistema.agregar_categoria(categoria)
        
        # Reconstruir clientes
        for cliente_data in data.get('clientes', []):
            cliente = Cliente.from_dict(cliente_data)
            sistema.agregar_cliente(cliente)
        
        # Reconstruir consumos
        for consumo_data in data.get('consumos', []):
            consumo = Consumo.from_dict(consumo_data)
            sistema.consumos.append(consumo)
        
        # Reconstruir facturas
        for factura_data in data.get('facturas', []):
            factura = Factura.from_dict(factura_data)
            sistema.agregar_factura(factura)
        
        sistema.proximo_id_factura = data.get('proximo_id_factura', 1)
        sistema.proximo_id_consumo = data.get('proximo_id_consumo', 1)
        
        return sistema