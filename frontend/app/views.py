from datetime import datetime

def index(request):
    try:
        # Obtener datos del backend
        response = requests.get(f"{settings.BACKEND_URL}/datos")
        if response.status_code == 200:
            datos = response.json()
            # Calcular estadísticas
            stats = {
                'total_clients': len(datos.get('clientes', [])),
                'active_instances': sum(1 for cliente in datos.get('clientes', []) 
                                      for instancia in cliente.get('instancias', [])
                                      if instancia.get('estado') == 'Vigente'),
                'total_categories': len(datos.get('categorias', [])),
                'monthly_revenue': sum(factura.get('monto_total', 0) 
                                     for factura in datos.get('facturas', []))
            }
        else:
            stats = {
                'total_clients': 0,
                'active_instances': 0,
                'total_categories': 0,
                'monthly_revenue': 0
            }
    except:
        stats = {
            'total_clients': 0,
            'active_instances': 0,
            'total_categories': 0,
            'monthly_revenue': 0
        }
    
    context = {
        'stats': stats,
        'current_date': datetime.now().strftime('%A, %d de %B de %Y')
    }
    return render(request, 'index.html', context)