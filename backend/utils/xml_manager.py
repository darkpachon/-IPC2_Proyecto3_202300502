import xml.etree.ElementTree as ET
import os
from datetime import datetime
from models import Sistema, Recurso, Categoria, Configuracion, Cliente, Instancia, Consumo, Factura, DetalleFactura

class XMLManager:
    def __init__(self, base_path="database"):
        self.base_path = base_path
        self.ensure_directory_exists()
    
    def ensure_directory_exists(self):
        """Asegura que el directorio de base de datos exista"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
    
    def guardar_sistema(self, sistema: Sistema):
        """Guarda todo el sistema en archivos XML"""
        self.guardar_recursos(sistema.recursos)
        self.guardar_categorias(sistema.categorias)
        self.guardar_clientes(sistema.clientes)
        self.guardar_consumos(sistema.consumos)
        self.guardar_facturas(sistema.facturas)
        self.guardar_metadata(sistema)
    
    def cargar_sistema(self) -> Sistema:
        """Carga todo el sistema desde archivos XML"""
        sistema = Sistema()
        
        # Cargar en orden para mantener referencias
        sistema.recursos = self.cargar_recursos()
        sistema.categorias = self.cargar_categorias(sistema)
        sistema.clientes = self.cargar_clientes()
        sistema.consumos = self.cargar_consumos()
        sistema.facturas = self.cargar_facturas()
        
        # Cargar metadata
        metadata = self.cargar_metadata()
        sistema.proximo_id_factura = metadata.get('proximo_id_factura', 1)
        sistema.proximo_id_consumo = metadata.get('proximo_id_consumo', 1)
        
        return sistema
    
    def guardar_recursos(self, recursos):
        """Guarda los recursos en XML"""
        root = ET.Element("recursos")
        for recurso in recursos:
            recurso_elem = ET.SubElement(root, "recurso")
            recurso_elem.set("id", str(recurso.id))
            
            ET.SubElement(recurso_elem, "nombre").text = recurso.nombre
            ET.SubElement(recurso_elem, "abreviatura").text = recurso.abreviatura
            ET.SubElement(recurso_elem, "metrica").text = recurso.metrica
            ET.SubElement(recurso_elem, "tipo").text = recurso.tipo
            ET.SubElement(recurso_elem, "valorXhora").text = str(recurso.valor_x_hora)
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.base_path}/recursos.xml", encoding="utf-8", xml_declaration=True)
    
    def cargar_recursos(self):
        """Carga los recursos desde XML"""
        try:
            tree = ET.parse(f"{self.base_path}/recursos.xml")
            root = tree.getroot()
            
            recursos = []
            for recurso_elem in root.findall("recurso"):
                recurso = Recurso(
                    id=int(recurso_elem.get("id")),
                    nombre=recurso_elem.find("nombre").text,
                    abreviatura=recurso_elem.find("abreviatura").text,
                    metrica=recurso_elem.find("metrica").text,
                    tipo=recurso_elem.find("tipo").text,
                    valor_x_hora=float(recurso_elem.find("valorXhora").text)
                )
                recursos.append(recurso)
            
            return recursos
        except (FileNotFoundError, ET.ParseError):
            return []
    
    def guardar_categorias(self, categorias):
        """Guarda las categorías en XML"""
        root = ET.Element("categorias")
        for categoria in categorias:
            categoria_elem = ET.SubElement(root, "categoria")
            categoria_elem.set("id", str(categoria.id))
            
            ET.SubElement(categoria_elem, "nombre").text = categoria.nombre
            ET.SubElement(categoria_elem, "descripcion").text = categoria.descripcion
            ET.SubElement(categoria_elem, "cargaTrabajo").text = categoria.carga_trabajo
            
            configuraciones_elem = ET.SubElement(categoria_elem, "configuraciones")
            for config in categoria.configuraciones:
                config_elem = ET.SubElement(configuraciones_elem, "configuracion")
                config_elem.set("id", str(config.id))
                
                ET.SubElement(config_elem, "nombre").text = config.nombre
                ET.SubElement(config_elem, "descripcion").text = config.descripcion
                
                recursos_config_elem = ET.SubElement(config_elem, "recursos")
                for recurso_id, cantidad in config.recursos.items():
                    recurso_config_elem = ET.SubElement(recursos_config_elem, "recurso")
                    recurso_config_elem.set("id", str(recurso_id))
                    recurso_config_elem.text = str(cantidad)
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.base_path}/categorias.xml", encoding="utf-8", xml_declaration=True)
    
    def cargar_categorias(self, sistema: Sistema):
        """Carga las categorías desde XML"""
        try:
            tree = ET.parse(f"{self.base_path}/categorias.xml")
            root = tree.getroot()
            
            categorias = []
            for categoria_elem in root.findall("categoria"):
                categoria = Categoria(
                    id=int(categoria_elem.get("id")),
                    nombre=categoria_elem.find("nombre").text,
                    descripcion=categoria_elem.find("descripcion").text,
                    carga_trabajo=categoria_elem.find("cargaTrabajo").text
                )
                
                configuraciones_elem = categoria_elem.find("configuraciones")
                if configuraciones_elem is not None:
                    for config_elem in configuraciones_elem.findall("configuracion"):
                        config = Configuracion(
                            id=int(config_elem.get("id")),
                            nombre=config_elem.find("nombre").text,
                            descripcion=config_elem.find("descripcion").text
                        )
                        
                        recursos_config_elem = config_elem.find("recursos")
                        if recursos_config_elem is not None:
                            for recurso_config_elem in recursos_config_elem.findall("recurso"):
                                recurso_id = int(recurso_config_elem.get("id"))
                                cantidad = float(recurso_config_elem.text)
                                config.agregar_recurso(recurso_id, cantidad)
                        
                        categoria.agregar_configuracion(config)
                
                categorias.append(categoria)
            
            return categorias
        except (FileNotFoundError, ET.ParseError):
            return []
    
    def guardar_clientes(self, clientes):
        """Guarda los clientes en XML"""
        root = ET.Element("clientes")
        for cliente in clientes:
            cliente_elem = ET.SubElement(root, "cliente")
            cliente_elem.set("nit", cliente.nit)
            
            ET.SubElement(cliente_elem, "nombre").text = cliente.nombre
            ET.SubElement(cliente_elem, "usuario").text = cliente.usuario
            ET.SubElement(cliente_elem, "clave").text = cliente.clave
            ET.SubElement(cliente_elem, "direccion").text = cliente.direccion
            ET.SubElement(cliente_elem, "correoElectronico").text = cliente.correo_electronico
            
            instancias_elem = ET.SubElement(cliente_elem, "instancias")
            for instancia in cliente.instancias:
                instancia_elem = ET.SubElement(instancias_elem, "instancia")
                instancia_elem.set("id", str(instancia.id))
                
                ET.SubElement(instancia_elem, "idConfiguracion").text = str(instancia.id_configuracion)
                ET.SubElement(instancia_elem, "nombre").text = instancia.nombre
                ET.SubElement(instancia_elem, "fechaInicio").text = instancia.fecha_inicio
                ET.SubElement(instancia_elem, "estado").text = instancia.estado
                
                if instancia.fecha_final:
                    ET.SubElement(instancia_elem, "fechaFinal").text = instancia.fecha_final
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.base_path}/clientes.xml", encoding="utf-8", xml_declaration=True)
    
    def cargar_clientes(self):
        """Carga los clientes desde XML"""
        try:
            tree = ET.parse(f"{self.base_path}/clientes.xml")
            root = tree.getroot()
            
            clientes = []
            for cliente_elem in root.findall("cliente"):
                cliente = Cliente(
                    nit=cliente_elem.get("nit"),
                    nombre=cliente_elem.find("nombre").text,
                    usuario=cliente_elem.find("usuario").text,
                    clave=cliente_elem.find("clave").text,
                    direccion=cliente_elem.find("direccion").text,
                    correo_electronico=cliente_elem.find("correoElectronico").text
                )
                
                instancias_elem = cliente_elem.find("instancias")
                if instancias_elem is not None:
                    for instancia_elem in instancias_elem.findall("instancia"):
                        instancia = Instancia(
                            id=int(instancia_elem.get("id")),
                            id_configuracion=int(instancia_elem.find("idConfiguracion").text),
                            nombre=instancia_elem.find("nombre").text,
                            fecha_inicio=instancia_elem.find("fechaInicio").text,
                            estado=instancia_elem.find("estado").text
                        )
                        
                        fecha_final_elem = instancia_elem.find("fechaFinal")
                        if fecha_final_elem is not None and fecha_final_elem.text:
                            instancia.fecha_final = fecha_final_elem.text
                        
                        cliente.agregar_instancia(instancia)
                
                clientes.append(cliente)
            
            return clientes
        except (FileNotFoundError, ET.ParseError):
            return []
    
    def guardar_consumos(self, consumos):
        """Guarda los consumos en XML"""
        root = ET.Element("consumos")
        for consumo in consumos:
            consumo_elem = ET.SubElement(root, "consumo")
            consumo_elem.set("id", str(consumo.id))
            consumo_elem.set("nitCliente", consumo.nit_cliente)
            consumo_elem.set("idInstancia", str(consumo.id_instancia))
            consumo_elem.set("facturado", str(consumo.facturado).lower())
            
            ET.SubElement(consumo_elem, "tiempo").text = str(consumo.tiempo)
            ET.SubElement(consumo_elem, "fechahora").text = consumo.fechahora
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.base_path}/consumos.xml", encoding="utf-8", xml_declaration=True)
    
    def cargar_consumos(self):
        """Carga los consumos desde XML"""
        try:
            tree = ET.parse(f"{self.base_path}/consumos.xml")
            root = tree.getroot()
            
            consumos = []
            for consumo_elem in root.findall("consumo"):
                consumo = Consumo(
                    id=int(consumo_elem.get("id")),
                    nit_cliente=consumo_elem.get("nitCliente"),
                    id_instancia=int(consumo_elem.get("idInstancia")),
                    tiempo=float(consumo_elem.find("tiempo").text),
                    fechahora=consumo_elem.find("fechahora").text,
                    facturado=consumo_elem.get("facturado", "false").lower() == "true"
                )
                consumos.append(consumo)
            
            return consumos
        except (FileNotFoundError, ET.ParseError):
            return []
    
    def guardar_facturas(self, facturas):
        """Guarda las facturas en XML"""
        root = ET.Element("facturas")
        for factura in facturas:
            factura_elem = ET.SubElement(root, "factura")
            factura_elem.set("numero", factura.numero_factura)
            factura_elem.set("nitCliente", factura.nit_cliente)
            factura_elem.set("fecha", factura.fecha)
            factura_elem.set("montoTotal", str(factura.monto_total))
            
            detalles_elem = ET.SubElement(factura_elem, "detalles")
            for detalle in factura.detalles:
                detalle_elem = ET.SubElement(detalles_elem, "detalle")
                detalle_elem.set("idInstancia", str(detalle.id_instancia))
                detalle_elem.set("nombreInstancia", detalle.nombre_instancia)
                detalle_elem.set("tiempoConsumido", str(detalle.tiempo_consumido))
                detalle_elem.set("montoInstancia", str(detalle.monto_instancia))
                
                recursos_elem = ET.SubElement(detalle_elem, "recursos")
                for recurso_det in detalle.detalles_recursos:
                    recurso_det_elem = ET.SubElement(recursos_elem, "recurso")
                    recurso_det_elem.set("id", str(recurso_det['id_recurso']))
                    recurso_det_elem.set("nombre", recurso_det['nombre_recurso'])
                    recurso_det_elem.set("cantidad", str(recurso_det['cantidad']))
                    recurso_det_elem.set("valorXhora", str(recurso_det['valor_x_hora']))
                    recurso_det_elem.set("costo", str(recurso_det['costo']))
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.base_path}/facturas.xml", encoding="utf-8", xml_declaration=True)
    
    def cargar_facturas(self):
        """Carga las facturas desde XML"""
        try:
            tree = ET.parse(f"{self.base_path}/facturas.xml")
            root = tree.getroot()
            
            facturas = []
            for factura_elem in root.findall("factura"):
                factura = Factura(
                    numero_factura=factura_elem.get("numero"),
                    nit_cliente=factura_elem.get("nitCliente"),
                    fecha=factura_elem.get("fecha"),
                    monto_total=float(factura_elem.get("montoTotal"))
                )
                
                detalles_elem = factura_elem.find("detalles")
                if detalles_elem is not None:
                    for detalle_elem in detalles_elem.findall("detalle"):
                        detalles_recursos = []
                        recursos_elem = detalle_elem.find("recursos")
                        if recursos_elem is not None:
                            for recurso_elem in recursos_elem.findall("recurso"):
                                recurso_det = {
                                    'id_recurso': int(recurso_elem.get("id")),
                                    'nombre_recurso': recurso_elem.get("nombre"),
                                    'cantidad': float(recurso_elem.get("cantidad")),
                                    'valor_x_hora': float(recurso_elem.get("valorXhora")),
                                    'costo': float(recurso_elem.get("costo"))
                                }
                                detalles_recursos.append(recurso_det)
                        
                        detalle = DetalleFactura(
                            id_instancia=int(detalle_elem.get("idInstancia")),
                            nombre_instancia=detalle_elem.get("nombreInstancia"),
                            tiempo_consumido=float(detalle_elem.get("tiempoConsumido")),
                            monto_instancia=float(detalle_elem.get("montoInstancia")),
                            detalles_recursos=detalles_recursos
                        )
                        factura.agregar_detalle(detalle)
                
                facturas.append(factura)
            
            return facturas
        except (FileNotFoundError, ET.ParseError):
            return []
    
    def guardar_metadata(self, sistema: Sistema):
        """Guarda metadatos del sistema"""
        root = ET.Element("metadata")
        ET.SubElement(root, "proximoIdFactura").text = str(sistema.proximo_id_factura)
        ET.SubElement(root, "proximoIdConsumo").text = str(sistema.proximo_id_consumo)
        ET.SubElement(root, "ultimaActualizacion").text = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        tree = ET.ElementTree(root)
        tree.write(f"{self.base_path}/metadata.xml", encoding="utf-8", xml_declaration=True)
    
    def cargar_metadata(self):
        """Carga metadatos del sistema"""
        try:
            tree = ET.parse(f"{self.base_path}/metadata.xml")
            root = tree.getroot()
            
            metadata = {}
            proximo_id_factura = root.find("proximoIdFactura")
            if proximo_id_factura is not None:
                metadata['proximo_id_factura'] = int(proximo_id_factura.text)
            
            proximo_id_consumo = root.find("proximoIdConsumo")
            if proximo_id_consumo is not None:
                metadata['proximo_id_consumo'] = int(proximo_id_consumo.text)
            
            return metadata
        except (FileNotFoundError, ET.ParseError):
            return {'proximo_id_factura': 1, 'proximo_id_consumo': 1}