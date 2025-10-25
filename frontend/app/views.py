import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from datetime import datetime

def index(request):
    try:
        # Obtener datos del backend
        response = requests.get(f"{settings.BACKEND_URL}/datos")
        if response.status_code == 200:
            datos = response.json()
            # Calcular estadísticas
            total_instancias = sum(len(cliente.get('instancias', [])) for cliente in datos.get('clientes', []))
            active_instances = sum(1 for cliente in datos.get('clientes', []) 
                                  for instancia in cliente.get('instancias', [])
                                  if instancia.get('estado') == 'Vigente')
            
            stats = {
                'total_clients': len(datos.get('clientes', [])),
                'active_instances': active_instances,
                'total_categories': len(datos.get('categorias', [])),
                'total_resources': len(datos.get('recursos', [])),
                'total_configurations': sum(len(cat.get('configuraciones', [])) for cat in datos.get('categorias', [])),
                'total_invoices': len(datos.get('facturas', [])),
                'total_consumptions': len(datos.get('consumos', [])),
                'monthly_revenue': sum(factura.get('monto_total', 0) for factura in datos.get('facturas', []))
            }
        else:
            stats = {
                'total_clients': 0,
                'active_instances': 0,
                'total_categories': 0,
                'total_resources': 0,
                'total_configurations': 0,
                'total_invoices': 0,
                'total_consumptions': 0,
                'monthly_revenue': 0
            }
    except Exception as e:
        stats = {
            'total_clients': 0,
            'active_instances': 0,
            'total_categories': 0,
            'total_resources': 0,
            'total_configurations': 0,
            'total_invoices': 0,
            'total_consumptions': 0,
            'monthly_revenue': 0
        }
    
    context = {
        'stats': stats,
        'current_date': datetime.now().strftime('%d/%m/%Y')
    }
    return render(request, 'index.html', context)

def categorias(request):
    try:
        response = requests.get(f"{settings.BACKEND_URL}/categorias")
        categorias = response.json() if response.status_code == 200 else []
    except:
        categorias = []
    
    return render(request, 'categorias.html', {'categorias': categorias})

def configuraciones(request):
    try:
        response_cat = requests.get(f"{settings.BACKEND_URL}/categorias")
        categorias = response_cat.json() if response_cat.status_code == 200 else []
        
        response_rec = requests.get(f"{settings.BACKEND_URL}/recursos")
        recursos = response_rec.json() if response_rec.status_code == 200 else []
        
        response_config = requests.get(f"{settings.BACKEND_URL}/configuraciones")
        configuraciones = response_config.json() if response_config.status_code == 200 else []
    except:
        categorias = []
        recursos = []
        configuraciones = []
    
    return render(request, 'configuraciones.html', {
        'categorias': categorias,
        'recursos': recursos,
        'configuraciones': configuraciones
    })

def recursos(request):
    try:
        response = requests.get(f"{settings.BACKEND_URL}/recursos")
        recursos = response.json() if response.status_code == 200 else []
    except:
        recursos = []
    
    return render(request, 'recursos.html', {'recursos': recursos})

def clientes(request):
    try:
        response = requests.get(f"{settings.BACKEND_URL}/clientes")
        clientes = response.json() if response.status_code == 200 else []
    except:
        clientes = []
    
    return render(request, 'clientes.html', {'clientes': clientes})

def instancias(request):
    try:
        response_clientes = requests.get(f"{settings.BACKEND_URL}/clientes")
        clientes = response_clientes.json() if response_clientes.status_code == 200 else []
        
        response_categorias = requests.get(f"{settings.BACKEND_URL}/categorias")
        categorias = response_categorias.json() if response_categorias.status_code == 200 else []
    except:
        clientes = []
        categorias = []
    
    return render(request, 'instancias.html', {
        'clientes': clientes,
        'categorias': categorias
    })

def crear_categoria(request):
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.POST['nombre'],
                'descripcion': request.POST['descripcion'],
                'carga_trabajo': request.POST['carga_trabajo']
            }
            response = requests.post(f"{settings.BACKEND_URL}/categorias", json=data)
            if response.status_code == 201:
                messages.success(request, 'Categoría creada exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al crear categoría: {str(e)}')
    
    return redirect('categorias')

def crear_recurso(request):
    if request.method == 'POST':
        try:
            data = {
                'nombre': request.POST['nombre'],
                'abreviatura': request.POST['abreviatura'],
                'metrica': request.POST['metrica'],
                'tipo': request.POST['tipo'],
                'valor_x_hora': float(request.POST['valor_x_hora'])
            }
            response = requests.post(f"{settings.BACKEND_URL}/recursos", json=data)
            if response.status_code == 201:
                messages.success(request, 'Recurso creado exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al crear recurso: {str(e)}')
    
    return redirect('recursos')

def crear_cliente(request):
    if request.method == 'POST':
        try:
            data = {
                'nit': request.POST['nit'],
                'nombre': request.POST['nombre'],
                'usuario': request.POST['usuario'],
                'clave': request.POST['clave'],
                'direccion': request.POST['direccion'],
                'correo_electronico': request.POST['correo_electronico']
            }
            response = requests.post(f"{settings.BACKEND_URL}/clientes", json=data)
            if response.status_code == 201:
                messages.success(request, 'Cliente creado exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    return redirect('clientes')

def crear_instancia(request):
    if request.method == 'POST':
        try:
            data = {
                'cliente_nit': request.POST['cliente_nit'],
                'configuracion_id': int(request.POST['configuracion_id']),
                'nombre': request.POST['nombre'],
                'fecha_inicio': request.POST['fecha_inicio']
            }
            response = requests.post(f"{settings.BACKEND_URL}/instancias", json=data)
            if response.status_code == 201:
                messages.success(request, 'Instancia creada exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al crear instancia: {str(e)}')
    
    return redirect('instancias')

def eliminar_categoria(request):
    if request.method == 'POST':
        try:
            categoria_id = int(request.POST['categoria_id'])
            response = requests.delete(f"{settings.BACKEND_URL}/categorias/{categoria_id}")
            if response.status_code == 200:
                messages.success(request, 'Categoría eliminada exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al eliminar categoría: {str(e)}')
    
    return redirect('categorias')

def eliminar_recurso(request):
    if request.method == 'POST':
        try:
            recurso_id = int(request.POST['recurso_id'])
            response = requests.delete(f"{settings.BACKEND_URL}/recursos/{recurso_id}")
            if response.status_code == 200:
                messages.success(request, 'Recurso eliminado exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al eliminar recurso: {str(e)}')
    
    return redirect('recursos')

def eliminar_cliente(request):
    if request.method == 'POST':
        try:
            cliente_nit = request.POST['cliente_nit']
            response = requests.delete(f"{settings.BACKEND_URL}/clientes/{cliente_nit}")
            if response.status_code == 200:
                messages.success(request, 'Cliente eliminado exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al eliminar cliente: {str(e)}')
    
    return redirect('clientes')

def cancelar_instancia(request):
    if request.method == 'POST':
        try:
            data = {
                'cliente_nit': request.POST['cliente_nit'],
                'instancia_id': int(request.POST['instancia_id'])
            }
            response = requests.post(f"{settings.BACKEND_URL}/instancias/cancelar", json=data)
            if response.status_code == 200:
                messages.success(request, 'Instancia cancelada exitosamente')
            else:
                error_data = response.json()
                messages.error(request, f'Error: {error_data.get("error", "Error desconocido")}')
        except Exception as e:
            messages.error(request, f'Error al cancelar instancia: {str(e)}')
    
    return redirect('instancias')

def enviar_configuracion(request):
    if request.method == 'POST' and request.FILES.get('archivo_xml'):
        archivo_xml = request.FILES['archivo_xml']
        try:
            xml_data = archivo_xml.read().decode('utf-8')
            response = requests.post(
                f"{settings.BACKEND_URL}/configuracion",
                data=xml_data,
                headers={'Content-Type': 'application/xml'}
            )
            if response.status_code == 200:
                resultado = response.json()
                messages.success(request, resultado.get('mensaje', 'Configuración procesada exitosamente'))
            else:
                error_data = response.json()
                messages.error(request, error_data.get('error', 'Error al procesar configuración'))
        except Exception as e:
            messages.error(request, f'Error al procesar archivo: {str(e)}')
    
    return render(request, 'configuracion.html')

def enviar_consumo(request):
    if request.method == 'POST' and request.FILES.get('archivo_xml'):
        archivo_xml = request.FILES['archivo_xml']
        try:
            xml_data = archivo_xml.read().decode('utf-8')
            response = requests.post(
                f"{settings.BACKEND_URL}/consumo",
                data=xml_data,
                headers={'Content-Type': 'application/xml'}
            )
            if response.status_code == 200:
                resultado = response.json()
                messages.success(request, resultado.get('mensaje', 'Consumo procesado exitosamente'))
            else:
                error_data = response.json()
                messages.error(request, error_data.get('error', 'Error al procesar consumo'))
        except Exception as e:
            messages.error(request, f'Error al procesar archivo: {str(e)}')
    
    return render(request, 'consumo.html')

def inicializar_sistema(request):
    if request.method == 'POST':
        try:
            response = requests.post(f"{settings.BACKEND_URL}/reset")
            if response.status_code == 200:
                messages.success(request, 'Sistema inicializado exitosamente')
            else:
                messages.error(request, 'Error al inicializar sistema')
        except Exception as e:
            messages.error(request, f'Error al inicializar sistema: {str(e)}')
        return redirect('index')
    
    return render(request, 'inicializar.html')

def consultar_datos(request):
    try:
        response = requests.get(f"{settings.BACKEND_URL}/datos")
        if response.status_code == 200:
            datos = response.json()
        else:
            datos = {}
    except:
        datos = {}
    
    return render(request, 'consultar.html', {'datos': datos})

def facturacion(request):
    facturas = []
    if request.method == 'POST':
        try:
            data = {
                'fecha_inicio': request.POST.get('fecha_inicio'),
                'fecha_fin': request.POST.get('fecha_fin')
            }
            response = requests.post(f"{settings.BACKEND_URL}/facturacion/generar", json=data)
            if response.status_code == 200:
                resultado = response.json()
                messages.success(request, resultado.get('mensaje', 'Facturación generada exitosamente'))
                facturas = resultado.get('facturas', [])
            else:
                error_data = response.json()
                messages.error(request, error_data.get('error', 'Error al generar facturación'))
        except Exception as e:
            messages.error(request, f'Error al generar facturación: {str(e)}')
    
    return render(request, 'facturacion.html', {'facturas': facturas})

def reportes(request):
    return render(request, 'reportes.html')

def ayuda(request):
    return render(request, 'ayuda.html')