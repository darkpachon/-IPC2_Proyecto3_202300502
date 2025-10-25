from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import xml.etree.ElementTree as ET
from models import Sistema, Recurso, Categoria, Configuracion, Cliente, Instancia, Consumo, Factura, DetalleFactura
from utils.validators import Validador
from utils.xml_manager import XMLManager
from utils.pdf_generator import PDFGenerator
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Inicializar el sistema global con persistencia
xml_manager = XMLManager()
sistema = xml_manager.cargar_sistema()
pdf_generator = PDFGenerator()

def guardar_sistema():
    """Guarda el estado del sistema en XML"""
    xml_manager.guardar_sistema(sistema)

@app.route('/')
def home():
    return jsonify({"message": "API de Tecnologías Chapinas, S.A."})

@app.route('/api/configuracion', methods=['POST'])
def procesar_configuracion():
    """Procesa mensaje XML de configuración"""
    try:
        if not request.data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        xml_data = request.data.decode('utf-8')
        
        # Procesar el XML
        root = ET.fromstring(xml_data)
        
        # Contadores para respuesta
        recursos_creados = 0
        categorias_creadas = 0
        clientes_creados = 0
        instancias_creadas = 0
        
        # Procesar recursos
        lista_recursos = root.find('.//listaRecursos')
        if lista_recursos is not None:
            for recurso_elem in lista_recursos.findall('recurso'):
                recurso_id = int(recurso_elem.get('id'))
                
                # Verificar si el recurso ya existe
                if sistema.obtener_recurso_por_id(recurso_id) is None:
                    tipo = recurso_elem.find('tipo').text.strip()
                    tipo_normalizado = Validador.normalizar_tipo_recurso(tipo)
                    if not Validador.validar_tipo_recurso(tipo):
                        return jsonify({"error": f"Tipo de recurso inválido: {tipo}"}), 400
                    
                    recurso = Recurso(
                        id=recurso_id,
                        nombre=recurso_elem.find('nombre').text.strip(),
                        abreviatura=recurso_elem.find('abreviatura').text.strip(),
                        metrica=recurso_elem.find('metrica').text.strip(),
                        tipo=tipo_normalizado,
                        valor_x_hora=float(recurso_elem.find('valorXhora').text)
                    )
                    sistema.agregar_recurso(recurso)
                    recursos_creados += 1
        
        # Procesar categorías
        lista_categorias = root.find('.//listaCategoria')
        if lista_categorias is None:
            lista_categorias = root.find('.//listaCategorias')
            
        if lista_categorias is not None:
            for categoria_elem in lista_categorias.findall('categoria'):
                categoria_id = int(categoria_elem.get('id'))
                
                if sistema.obtener_categoria_por_id(categoria_id) is None:
                    # Manejar diferentes nombres de tags
                    nombre_elem = categoria_elem.find('nombre')
                    descripcion_elem = categoria_elem.find('description')
                    if descripcion_elem is None:
                        descripcion_elem = categoria_elem.find('descripcion')
                    carga_trabajo_elem = categoria_elem.find('cargaTrabajo')
                    
                    categoria = Categoria(
                        id=categoria_id,
                        nombre=nombre_elem.text.strip() if nombre_elem is not None else "",
                        descripcion=descripcion_elem.text.strip() if descripcion_elem is not None else "",
                        carga_trabajo=carga_trabajo_elem.text.strip() if carga_trabajo_elem is not None else ""
                    )
                    
                    # Procesar configuraciones de la categoría
                    lista_configs = categoria_elem.find('.//listaConfigurationes')
                    if lista_configs is None:
                        lista_configs = categoria_elem.find('.//listaConfiguraciones')
                        
                    if lista_configs is not None:
                        for config_elem in lista_configs.findall('configuration'):
                            config_id = int(config_elem.get('id'))
                            
                            # Manejar diferentes nombres de tags
                            config_nombre_elem = config_elem.find('nombre')
                            config_descripcion_elem = config_elem.find('description')
                            if config_descripcion_elem is None:
                                config_descripcion_elem = config_elem.find('descripcion')
                            
                            configuracion = Configuracion(
                                id=config_id,
                                nombre=config_nombre_elem.text.strip() if config_nombre_elem is not None else "",
                                descripcion=config_descripcion_elem.text.strip() if config_descripcion_elem is not None else ""
                            )
                            
                            # Procesar recursos de la configuración
                            recursos_config = config_elem.find('.//recurso%Configuration')
                            if recursos_config is None:
                                recursos_config = config_elem.find('.//recursosConfiguracion')
                                
                            if recursos_config is not None:
                                for recurso_config in recursos_config.findall('recurso'):
                                    recurso_id_config = int(recurso_config.get('id'))
                                    cantidad = float(recurso_config.text)
                                    configuracion.agregar_recurso(recurso_id_config, cantidad)
                            
                            categoria.agregar_configuracion(configuracion)
                    
                    sistema.agregar_categoria(categoria)
                    categorias_creadas += 1
        
        # Procesar clientes
        lista_clientes = root.find('.//listaClientes')
        if lista_clientes is not None:
            for cliente_elem in lista_clientes.findall('cliente'):
                # Manejar diferentes nombres de atributos
                nit = cliente_elem.get('nlt')
                if nit is None:
                    nit = cliente_elem.get('nit')
                
                # Validar NIT
                if not Validador.validar_nit(nit):
                    return jsonify({"error": f"NIT inválido: {nit}"}), 400
                
                if sistema.obtener_cliente_por_nit(nit) is None:
                    cliente = Cliente(
                        nit=nit,
                        nombre=cliente_elem.find('nombre').text.strip(),
                        usuario=cliente_elem.find('usuario').text.strip(),
                        clave=cliente_elem.find('clave').text.strip(),
                        direccion=cliente_elem.find('direccion').text.strip(),
                        correo_electronico=cliente_elem.find('correoElectronico').text.strip()
                    )
                    
                    # Procesar instancias del cliente
                    lista_instancias = cliente_elem.find('.//listaInstancia')
                    if lista_instancias is None:
                        lista_instancias = cliente_elem.find('.//listaInstancias')
                        
                    if lista_instancias is not None:
                        for instancia_elem in lista_instancias.findall('instancia'):
                            instancia_id = int(instancia_elem.get('id'))
                            
                            # Extraer fecha de inicio
                            fecha_inicio_texto = instancia_elem.find('fechaInicio').text
                            fecha_inicio = Validador.extraer_fecha(fecha_inicio_texto)
                            if not fecha_inicio:
                                return jsonify({"error": f"Fecha de inicio inválida: {fecha_inicio_texto}"}), 400
                            
                            estado = instancia_elem.find('estado').text.strip()
                            estado_normalizado = Validador.normalizar_estado_instancia(estado)
                            if not Validador.validar_estado_instancia(estado):
                                return jsonify({"error": f"Estado de instancia inválido: {estado}"}), 400
                            
                            # Manejar diferentes nombres de tags
                            id_configuracion_elem = instancia_elem.find('idConfiguration')
                            if id_configuracion_elem is None:
                                id_configuracion_elem = instancia_elem.find('idConfiguracion')
                            
                            instancia = Instancia(
                                id=instancia_id,
                                id_configuracion=int(id_configuracion_elem.text),
                                nombre=instancia_elem.find('nombre').text.strip(),
                                fecha_inicio=fecha_inicio,
                                estado=estado_normalizado
                            )
                            
                            # Si tiene fecha final, extraerla
                            fecha_final_elem = instancia_elem.find('fechaFinal')
                            if fecha_final_elem is not None and fecha_final_elem.text:
                                fecha_final = Validador.extraer_fecha(fecha_final_elem.text)
                                if fecha_final:
                                    instancia.fecha_final = fecha_final
                            
                            cliente.agregar_instancia(instancia)
                            instancias_creadas += 1
                    
                    sistema.agregar_cliente(cliente)
                    clientes_creados += 1
        
        # Guardar cambios en XML
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Configuración procesada exitosamente",
            "detalle": {
                "recursos_creados": recursos_creados,
                "categorias_creadas": categorias_creadas,
                "clientes_creados": clientes_creados,
                "instancias_creadas": instancias_creadas
            }
        }), 200
        
    except ET.ParseError as e:
        return jsonify({"error": f"Error parsing XML: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error procesando configuración: {str(e)}"}), 500

@app.route('/api/consumo', methods=['POST'])
def procesar_consumo():
    """Procesa mensaje XML de consumo"""
    try:
        xml_data = request.data.decode('utf-8')
        root = ET.fromstring(xml_data)
        
        consumos_procesados = 0
        
        for consumo_elem in root.findall('.//consumo'):
            # Manejar diferentes nombres de atributos
            nit_cliente = consumo_elem.get('nicClientes')
            if nit_cliente is None:
                nit_cliente = consumo_elem.get('nitCliente')
                
            id_instancia = int(consumo_elem.get('idInstanceia'))
            if id_instancia is None:
                id_instancia = int(consumo_elem.get('idInstancia'))
                
            tiempo = float(consumo_elem.find('tiempo').text)
            
            # Manejar diferentes nombres de tags
            fechahora_elem = consumo_elem.find('fechahora')
            if fechahora_elem is None:
                fechahora_elem = consumo_elem.find('fechaHora')
            fechahora_texto = fechahora_elem.text.strip()
            
            # Extraer fecha y hora
            fechahora = Validador.extraer_fecha_hora(fechahora_texto)
            if not fechahora:
                return jsonify({"error": f"Fecha/hora inválida: {fechahora_texto}"}), 400

            # Verificar que el cliente existe
            cliente = sistema.obtener_cliente_por_nit(nit_cliente)
            if not cliente:
                return jsonify({"error": f"Cliente con NIT {nit_cliente} no encontrado"}), 404

            # Verificar que la instancia existe y pertenece al cliente
            instancia = cliente.obtener_instancia_por_id(id_instancia)
            if not instancia:
                return jsonify({"error": f"Instancia {id_instancia} no encontrada para el cliente {nit_cliente}"}), 404

            # Crear consumo con ID único
            consumo = Consumo(
                id=sistema.generar_id_consumo(),
                nit_cliente=nit_cliente,
                id_instancia=id_instancia,
                tiempo=tiempo,
                fechahora=fechahora,
                facturado=False
            )
            sistema.agregar_consumo(consumo)
            consumos_procesados += 1
        
        # Guardar cambios en XML
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Consumo procesado exitosamente",
            "consumos_procesados": consumos_procesados
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error procesando consumo: {str(e)}"}), 500

# ... (los demás endpoints se mantienen igual que en la versión anterior)

@app.route('/api/reset', methods=['POST'])
def resetear_sistema():
    """Resetea todos los datos del sistema"""
    global sistema
    sistema = Sistema()
    guardar_sistema()
    return jsonify({"mensaje": "Sistema reseteado exitosamente"})

@app.route('/api/datos', methods=['GET'])
def obtener_datos():
    """Obtiene todos los datos del sistema"""
    return jsonify(sistema.to_dict())

# Endpoints CRUD para Categorías
@app.route('/api/categorias', methods=['GET'])
def obtener_categorias():
    """Obtiene todas las categorías"""
    categorias_data = [categoria.to_dict() for categoria in sistema.categorias]
    return jsonify(categorias_data)

@app.route('/api/categorias', methods=['POST'])
def crear_categoria():
    """Crea una nueva categoría"""
    try:
        data = request.json
        categoria_id = max([c.id for c in sistema.categorias], default=0) + 1
        
        categoria = Categoria(
            id=categoria_id,
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            carga_trabajo=data['carga_trabajo']
        )
        
        sistema.agregar_categoria(categoria)
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Categoría creada exitosamente",
            "categoria": categoria.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Error creando categoría: {str(e)}"}), 500

@app.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
def eliminar_categoria(categoria_id):
    """Elimina una categoría"""
    try:
        categoria = sistema.obtener_categoria_por_id(categoria_id)
        if not categoria:
            return jsonify({"error": "Categoría no encontrada"}), 404
        
        # Verificar que la categoría no tenga configuraciones
        if categoria.configuraciones:
            return jsonify({"error": "No se puede eliminar una categoría con configuraciones"}), 400
        
        sistema.categorias = [c for c in sistema.categorias if c.id != categoria_id]
        guardar_sistema()
        
        return jsonify({"mensaje": "Categoría eliminada exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Error eliminando categoría: {str(e)}"}), 500

# Endpoints CRUD para Recursos
@app.route('/api/recursos', methods=['GET'])
def obtener_recursos():
    """Obtiene todos los recursos"""
    recursos_data = [recurso.to_dict() for recurso in sistema.recursos]
    return jsonify(recursos_data)

@app.route('/api/recursos', methods=['POST'])
def crear_recurso():
    """Crea un nuevo recurso"""
    try:
        data = request.json
        
        # Validar tipo de recurso
        if not Validador.validar_tipo_recurso(data['tipo']):
            return jsonify({"error": "Tipo de recurso inválido. Debe ser 'Hardware' o 'Software'"}), 400
        
        recurso_id = max([r.id for r in sistema.recursos], default=0) + 1
        
        recurso = Recurso(
            id=recurso_id,
            nombre=data['nombre'],
            abreviatura=data['abreviatura'],
            metrica=data['metrica'],
            tipo=data['tipo'],
            valor_x_hora=float(data['valor_x_hora'])
        )
        
        sistema.agregar_recurso(recurso)
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Recurso creado exitosamente",
            "recurso": recurso.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Error creando recurso: {str(e)}"}), 500

@app.route('/api/recursos/<int:recurso_id>', methods=['DELETE'])
def eliminar_recurso(recurso_id):
    """Elimina un recurso"""
    try:
        recurso = sistema.obtener_recurso_por_id(recurso_id)
        if not recurso:
            return jsonify({"error": "Recurso no encontrado"}), 404
        
        # Verificar que el recurso no esté en uso en configuraciones
        for categoria in sistema.categorias:
            for configuracion in categoria.configuraciones:
                if recurso_id in configuracion.recursos:
                    return jsonify({"error": "No se puede eliminar un recurso que está en uso"}), 400
        
        sistema.recursos = [r for r in sistema.recursos if r.id != recurso_id]
        guardar_sistema()
        
        return jsonify({"mensaje": "Recurso eliminado exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Error eliminando recurso: {str(e)}"}), 500

# Endpoints CRUD para Clientes
@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    """Obtiene todos los clientes"""
    clientes_data = [cliente.to_dict() for cliente in sistema.clientes]
    return jsonify(clientes_data)

@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    """Crea un nuevo cliente"""
    try:
        data = request.json
        
        # Validar NIT
        if not Validador.validar_nit(data['nit']):
            return jsonify({"error": "NIT inválido. Formato: 12345-6"}), 400
        
        # Verificar que el NIT no exista
        if sistema.obtener_cliente_por_nit(data['nit']):
            return jsonify({"error": "Ya existe un cliente con este NIT"}), 400
        
        cliente = Cliente(
            nit=data['nit'],
            nombre=data['nombre'],
            usuario=data['usuario'],
            clave=data['clave'],
            direccion=data['direccion'],
            correo_electronico=data['correo_electronico']
        )
        
        sistema.agregar_cliente(cliente)
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Cliente creado exitosamente",
            "cliente": cliente.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Error creando cliente: {str(e)}"}), 500

@app.route('/api/clientes/<string:nit>', methods=['DELETE'])
def eliminar_cliente(nit):
    """Elimina un cliente"""
    try:
        cliente = sistema.obtener_cliente_por_nit(nit)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404
        
        sistema.clientes = [c for c in sistema.clientes if c.nit != nit]
        guardar_sistema()
        
        return jsonify({"mensaje": "Cliente eliminado exitosamente"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Error eliminando cliente: {str(e)}"}), 500

# Endpoints CRUD para Instancias
@app.route('/api/instancias', methods=['GET'])
def obtener_instancias():
    """Obtiene todas las instancias de todos los clientes"""
    instancias_data = []
    for cliente in sistema.clientes:
        for instancia in cliente.instancias:
            instancia_data = instancia.to_dict()
            instancia_data['cliente_nit'] = cliente.nit
            instancia_data['cliente_nombre'] = cliente.nombre
            instancias_data.append(instancia_data)
    
    return jsonify(instancias_data)

@app.route('/api/instancias', methods=['POST'])
def crear_instancia():
    """Crea una nueva instancia"""
    try:
        data = request.json
        
        # Validar cliente
        cliente = sistema.obtener_cliente_por_nit(data['cliente_nit'])
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404
        
        # Validar configuración
        configuracion = sistema.obtener_configuracion_por_id(int(data['configuracion_id']))
        if not configuracion:
            return jsonify({"error": "Configuración no encontrada"}), 404
        
        # Extraer fecha
        fecha_inicio = Validador.extraer_fecha(data['fecha_inicio'])
        if not fecha_inicio:
            return jsonify({"error": "Fecha de inicio inválida"}), 400
        
        # Generar ID de instancia
        instancia_id = max([i.id for c in sistema.clientes for i in c.instancias], default=0) + 1
        
        instancia = Instancia(
            id=instancia_id,
            id_configuracion=int(data['configuracion_id']),
            nombre=data['nombre'],
            fecha_inicio=fecha_inicio,
            estado="Vigente"
        )
        
        cliente.agregar_instancia(instancia)
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Instancia creada exitosamente",
            "instancia": instancia.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Error creando instancia: {str(e)}"}), 500

@app.route('/api/instancias/cancelar', methods=['POST'])
def cancelar_instancia():
    """Cancela una instancia"""
    try:
        data = request.json
        cliente_nit = data['cliente_nit']
        instancia_id = int(data['instancia_id'])
        
        cliente = sistema.obtener_cliente_por_nit(cliente_nit)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404
        
        instancia = cliente.obtener_instancia_por_id(instancia_id)
        if not instancia:
            return jsonify({"error": "Instancia no encontrada"}), 404
        
        if instancia.estado == "Cancelada":
            return jsonify({"error": "La instancia ya está cancelada"}), 400
        
        fecha_final = datetime.now().strftime("%d/%m/%Y")
        instancia.cancelar(fecha_final)
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Instancia cancelada exitosamente",
            "instancia": instancia.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error cancelando instancia: {str(e)}"}), 500

# Endpoints para Configuraciones
@app.route('/api/configuraciones', methods=['GET'])
def obtener_configuraciones():
    """Obtiene todas las configuraciones de todas las categorías"""
    configuraciones_data = []
    for categoria in sistema.categorias:
        for configuracion in categoria.configuraciones:
            config_data = configuracion.to_dict()
            config_data['categoria_id'] = categoria.id
            config_data['categoria_nombre'] = categoria.nombre
            configuraciones_data.append(config_data)
    
    return jsonify(configuraciones_data)

@app.route('/api/configuraciones', methods=['POST'])
def crear_configuracion():
    """Crea una nueva configuración"""
    try:
        data = request.json
        
        # Validar categoría
        categoria = sistema.obtener_categoria_por_id(int(data['categoria_id']))
        if not categoria:
            return jsonify({"error": "Categoría no encontrada"}), 404
        
        configuracion_id = max([c.id for cat in sistema.categorias for c in cat.configuraciones], default=0) + 1
        
        configuracion = Configuracion(
            id=configuracion_id,
            nombre=data['nombre'],
            descripcion=data['descripcion']
        )
        
        # Agregar recursos a la configuración
        for recurso_data in data.get('recursos', []):
            configuracion.agregar_recurso(
                int(recurso_data['id']),
                float(recurso_data['cantidad'])
            )
        
        categoria.agregar_configuracion(configuracion)
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Configuración creada exitosamente",
            "configuracion": configuracion.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Error creando configuración: {str(e)}"}), 500

# Endpoints para Facturación
@app.route('/api/facturacion/generar', methods=['POST'])
def generar_facturacion():
    """Genera facturas para un rango de fechas"""
    try:
        data = request.json
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Validar fechas
        fecha_inicio_dt = Validador.extraer_fecha(fecha_inicio)
        fecha_fin_dt = Validador.extraer_fecha(fecha_fin)
        if not fecha_inicio_dt or not fecha_fin_dt:
            return jsonify({"error": "Fechas inválidas"}), 400

        # Generar facturación
        facturas_generadas = sistema.generar_facturacion(fecha_inicio_dt, fecha_fin_dt)
        
        # Guardar cambios
        guardar_sistema()
        
        return jsonify({
            "mensaje": "Facturación generada exitosamente",
            "facturas_generadas": len(facturas_generadas),
            "facturas": [factura.to_dict() for factura in facturas_generadas]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error generando facturación: {str(e)}"}), 500

@app.route('/api/facturas', methods=['GET'])
def obtener_facturas():
    """Obtiene todas las facturas del sistema"""
    facturas_data = [factura.to_dict() for factura in sistema.facturas]
    return jsonify(facturas_data)

@app.route('/api/facturas/<numero_factura>', methods=['GET'])
def obtener_factura(numero_factura):
    """Obtiene una factura específica por número"""
    for factura in sistema.facturas:
        if factura.numero_factura == numero_factura:
            return jsonify(factura.to_dict())
    return jsonify({"error": "Factura no encontrada"}), 404

# Endpoints para Reportes PDF
@app.route('/api/reportes/detalle-factura/<numero_factura>', methods=['GET'])
def generar_reporte_detalle_factura(numero_factura):
    """Genera un PDF con el detalle de una factura"""
    try:
        # Buscar la factura
        factura = None
        for f in sistema.facturas:
            if f.numero_factura == numero_factura:
                factura = f
                break
        
        if not factura:
            return jsonify({"error": "Factura no encontrada"}), 404
        
        # Buscar el cliente
        cliente = sistema.obtener_cliente_por_nit(factura.nit_cliente)
        
        # Generar PDF
        filepath = pdf_generator.generar_detalle_factura(factura, cliente)
        
        # Devolver el archivo
        with open(filepath, 'rb') as f:
            response = Response(f.read(), content_type='application/pdf')
            response.headers['Content-Disposition'] = f'attachment; filename=detalle_factura_{numero_factura}.pdf'
            return response
            
    except Exception as e:
        return jsonify({"error": f"Error generando reporte: {str(e)}"}), 500

@app.route('/api/reportes/analisis-ventas', methods=['POST'])
def generar_reporte_analisis_ventas():
    """Genera un PDF con análisis de ventas"""
    try:
        data = request.json
        tipo_analisis = data.get('tipo_analisis')  # 'categorias' o 'recursos'
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        # Validar fechas
        fecha_inicio_dt = Validador.extraer_fecha(fecha_inicio)
        fecha_fin_dt = Validador.extraer_fecha(fecha_fin)
        if not fecha_inicio_dt or not fecha_fin_dt:
            return jsonify({"error": "Fechas inválidas"}), 400
        
        # Obtener datos para el análisis
        if tipo_analisis == 'categorias':
            datos = _obtener_datos_analisis_categorias(fecha_inicio_dt, fecha_fin_dt)
        else:
            datos = _obtener_datos_analisis_recursos(fecha_inicio_dt, fecha_fin_dt)
        
        # Generar PDF
        rango_fechas = {'inicio': fecha_inicio_dt, 'fin': fecha_fin_dt}
        filepath = pdf_generator.generar_analisis_ventas(tipo_analisis, datos, rango_fechas)
        
        # Devolver el archivo
        with open(filepath, 'rb') as f:
            response = Response(f.read(), content_type='application/pdf')
            filename = f"analisis_ventas_{tipo_analisis}_{fecha_inicio_dt}_{fecha_fin_dt}.pdf"
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            return response
            
    except Exception as e:
        return jsonify({"error": f"Error generando reporte: {str(e)}"}), 500

def _obtener_datos_analisis_categorias(fecha_inicio, fecha_fin):
    """Obtiene datos para análisis por categorías"""
    datos = []
    
    for categoria in sistema.categorias:
        ingreso_categoria = 0
        configuraciones_data = []
        
        for configuracion in categoria.configuraciones:
            # Calcular ingreso de esta configuración
            ingreso_config = 0
            
            # Buscar facturas que incluyan esta configuración en el rango de fechas
            for factura in sistema.facturas:
                # Verificar si la factura está en el rango
                fecha_factura = Validador.extraer_fecha(factura.fecha)
                if fecha_factura and fecha_inicio <= fecha_factura <= fecha_fin:
                    for detalle in factura.detalles:
                        instancia = sistema.obtener_instancia_por_id(detalle.id_instancia)
                        if instancia and instancia.id_configuracion == configuracion.id:
                            # Sumar el monto de esta instancia
                            ingreso_config += detalle.monto_instancia
            
            if ingreso_config > 0:
                configuraciones_data.append({
                    'nombre': configuracion.nombre,
                    'ingreso': ingreso_config
                })
                ingreso_categoria += ingreso_config
        
        if ingreso_categoria > 0:
            datos.append({
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion,
                'carga_trabajo': categoria.carga_trabajo,
                'ingreso_total': ingreso_categoria,
                'configuraciones': configuraciones_data
            })
    
    # Ordenar por ingreso descendente
    datos.sort(key=lambda x: x['ingreso_total'], reverse=True)
    return datos

def _obtener_datos_analisis_recursos(fecha_inicio, fecha_fin):
    """Obtiene datos para análisis por recursos"""
    datos = []
    
    for recurso in sistema.recursos:
        ingreso_total = 0
        
        # Buscar en todas las facturas en el rango
        for factura in sistema.facturas:
            fecha_factura = Validador.extraer_fecha(factura.fecha)
            if fecha_factura and fecha_inicio <= fecha_factura <= fecha_fin:
                for detalle in factura.detalles:
                    for recurso_det in detalle.detalles_recursos:
                        if recurso_det['id_recurso'] == recurso.id:
                            ingreso_total += recurso_det['costo']
        
        if ingreso_total > 0:
            datos.append({
                'nombre': recurso.nombre,
                'tipo': recurso.tipo,
                'metrica': recurso.metrica,
                'valor_x_hora': recurso.valor_x_hora,
                'ingreso_total': ingreso_total
            })
    
    # Ordenar por ingreso descendente
    datos.sort(key=lambda x: x['ingreso_total'], reverse=True)
    return datos

if __name__ == '__main__':
    app.run(debug=True, port=5000)