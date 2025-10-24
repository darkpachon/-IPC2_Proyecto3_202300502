from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime

class PDFGenerator:
    def __init__(self, output_path="reports"):
        self.output_path = output_path
        self.ensure_directory_exists()
    
    def ensure_directory_exists(self):
        """Asegura que el directorio de reportes exista"""
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
    
    def generar_detalle_factura(self, factura, cliente, output_filename=None):
        """Genera un PDF con el detalle de una factura"""
        if output_filename is None:
            output_filename = f"detalle_factura_{factura.numero_factura}.pdf"
        
        filepath = os.path.join(self.output_path, output_filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = styles["Normal"]
        
        # Título
        title = Paragraph("Tecnologías Chapinas, S.A.", title_style)
        elements.append(title)
        elements.append(Paragraph("Detalle de Factura", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Información de la factura
        factura_data = [
            ["Número de Factura:", factura.numero_factura],
            ["Fecha de Emisión:", factura.fecha],
            ["NIT del Cliente:", factura.nit_cliente],
            ["Nombre del Cliente:", cliente.nombre if cliente else "N/A"],
            ["Dirección:", cliente.direccion if cliente else "N/A"],
            ["Correo Electrónico:", cliente.correo_electronico if cliente else "N/A"],
            ["Monto Total:", f"Q {factura.monto_total:.2f}"]
        ]
        
        factura_table = Table(factura_data, colWidths=[2*inch, 4*inch])
        factura_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(factura_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detalle de instancias
        elements.append(Paragraph("Detalle por Instancias", heading_style))
        
        for detalle in factura.detalles:
            # Información de la instancia
            instancia_data = [
                ["Instancia:", detalle.nombre_instancia],
                ["ID Instancia:", str(detalle.id_instancia)],
                ["Tiempo Consumido:", f"{detalle.tiempo_consumido} horas"],
                ["Monto de Instancia:", f"Q {detalle.monto_instancia:.2f}"]
            ]
            
            instancia_table = Table(instancia_data, colWidths=[1.5*inch, 4.5*inch])
            instancia_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.beige),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(instancia_table)
            
            # Detalle de recursos de la instancia
            recursos_data = [["Recurso", "Cantidad", "Valor x Hora", "Tiempo (h)", "Costo"]]
            
            for recurso_det in detalle.detalles_recursos:
                recursos_data.append([
                    recurso_det['nombre_recurso'],
                    str(recurso_det['cantidad']),
                    f"Q {recurso_det['valor_x_hora']:.2f}",
                    f"{detalle.tiempo_consumido}",
                    f"Q {recurso_det['costo']:.2f}"
                ])
            
            recursos_table = Table(recursos_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            recursos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(recursos_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Gracias por su confianza", styles["Normal"]))
        elements.append(Paragraph("Tecnologías Chapinas, S.A. - Servicios de Infraestructura en la Nube", styles["Normal"]))
        
        # Generar PDF
        doc.build(elements)
        return filepath
    
    def generar_analisis_ventas(self, tipo_analisis, datos, rango_fechas, output_filename=None):
        """Genera un PDF con análisis de ventas"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"analisis_ventas_{tipo_analisis}_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_path, output_filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Título
        title = Paragraph("Tecnologías Chapinas, S.A.", title_style)
        elements.append(title)
        
        if tipo_analisis == "categorias":
            elements.append(Paragraph("Análisis de Ventas por Categorías y Configuraciones", title_style))
        else:
            elements.append(Paragraph("Análisis de Ventas por Recursos", title_style))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Rango de fechas
        fecha_text = f"Período analizado: {rango_fechas['inicio']} - {rango_fechas['fin']}"
        elements.append(Paragraph(fecha_text, styles["Normal"]))
        elements.append(Spacer(1, 0.3*inch))
        
        if tipo_analisis == "categorias":
            self._generar_analisis_categorias(elements, datos, heading_style, styles)
        else:
            self._generar_analisis_recursos(elements, datos, heading_style, styles)
        
        # Pie de página
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Reporte generado automáticamente", styles["Normal"]))
        elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        
        # Generar PDF
        doc.build(elements)
        return filepath
    
    def _generar_analisis_categorias(self, elements, datos, heading_style, styles):
        """Genera la sección de análisis por categorías"""
        elements.append(Paragraph("Categorías y Configuraciones con Mayor Ingreso", heading_style))
        
        if not datos:
            elements.append(Paragraph("No hay datos disponibles para el período seleccionado.", styles["Normal"]))
            return
        
        for categoria in datos:
            # Información de la categoría
            cat_data = [
                ["Categoría:", categoria['nombre']],
                ["Descripción:", categoria['descripcion']],
                ["Carga de Trabajo:", categoria['carga_trabajo']],
                ["Ingreso Total:", f"Q {categoria['ingreso_total']:.2f}"]
            ]
            
            cat_table = Table(cat_data, colWidths=[1.5*inch, 4.5*inch])
            cat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(cat_table)
            
            # Configuraciones de la categoría
            if categoria['configuraciones']:
                config_data = [["Configuración", "Ingreso"]]
                for config in categoria['configuraciones']:
                    config_data.append([
                        config['nombre'],
                        f"Q {config['ingreso']:.2f}"
                    ])
                
                config_table = Table(config_data, colWidths=[4*inch, 2*inch])
                config_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(config_table)
            
            elements.append(Spacer(1, 0.3*inch))
    
    def _generar_analisis_recursos(self, elements, datos, heading_style, styles):
        """Genera la sección de análisis por recursos"""
        elements.append(Paragraph("Recursos con Mayor Ingreso", heading_style))
        
        if not datos:
            elements.append(Paragraph("No hay datos disponibles para el período seleccionado.", styles["Normal"]))
            return
        
        # Tabla de recursos
        recursos_data = [["Recurso", "Tipo", "Métrica", "Valor x Hora", "Ingreso Total"]]
        
        for recurso in datos:
            recursos_data.append([
                recurso['nombre'],
                recurso['tipo'],
                recurso['metrica'],
                f"Q {recurso['valor_x_hora']:.2f}",
                f"Q {recurso['ingreso_total']:.2f}"
            ])
        
        recursos_table = Table(recursos_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.2*inch, 1.3*inch])
        recursos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(recursos_table)