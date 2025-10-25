from flask import Flask, request, jsonify, Response  # Response agregado
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

# ... (el resto del código de app.py se mantiene igual hasta la línea 425)

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
        
        # Devolver el archivo - CORREGIDO: usar Response directamente
        with open(filepath, 'rb') as f:
            response = Response(f.read(), content_type='application/pdf')  # CORREGIDO
            response.headers['Content-Disposition'] = f'attachment; filename=detalle_factura_{numero_factura}.pdf'
            return response
            
    except Exception as e:
        return jsonify({"error": f"Error generando reporte: {str(e)}"}), 500

# ... (el resto del código se mantiene igual)