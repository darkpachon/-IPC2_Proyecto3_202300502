from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Nuevas vistas para las secciones
    path('categorias/', views.categorias, name='categorias'),
    path('configuraciones/', views.configuraciones, name='configuraciones'),
    path('recursos/', views.recursos, name='recursos'),
    path('clientes/', views.clientes, name='clientes'),
    path('instancias/', views.instancias, name='instancias'),
    
    # Acciones CRUD
    path('crear-categoria/', views.crear_categoria, name='crear_categoria'),
    path('crear-recurso/', views.crear_recurso, name='crear_recurso'),
    path('crear-cliente/', views.crear_cliente, name='crear_cliente'),
    path('crear-instancia/', views.crear_instancia, name='crear_instancia'),
    path('eliminar-categoria/', views.eliminar_categoria, name='eliminar_categoria'),
    path('eliminar-recurso/', views.eliminar_recurso, name='eliminar_recurso'),
    path('eliminar-cliente/', views.eliminar_cliente, name='eliminar_cliente'),
    path('cancelar-instancia/', views.cancelar_instancia, name='cancelar_instancia'),
    
    # Vistas existentes
    path('configuracion/', views.enviar_configuracion, name='configuracion'),
    path('consumo/', views.enviar_consumo, name='consumo'),
    path('inicializar/', views.inicializar_sistema, name='inicializar'),
    path('consultar/', views.consultar_datos, name='consultar'),
    path('facturacion/', views.facturacion, name='facturacion'),
    path('reportes/', views.reportes, name='reportes'),
    path('ayuda/', views.ayuda, name='ayuda'),
]