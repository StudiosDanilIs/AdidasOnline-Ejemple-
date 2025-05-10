from django.urls import path
from . import views

urlpatterns = [
    # URLs principales
    path('', views.home, name='home'),
    path('categorias/', views.categorias, name='categorias'),
    path('patrocinados/', views.patrocicado, name='patrocicado'),
    path('politicas/', views.politica, name='politica'),
    
    # URLs del Carrito
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar-del-carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('actualizar-cantidad/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    
    # URLs de Compras
    path('completar-compra/', views.completar_compra, name='completar_compra'),
    path('compra-exitosa/', views.compra_exitosa, name='compra_exitosa'),
    path('descargar-comprobante/', views.descargar_comprobante, name='descargar_comprobante'),
    
    # URLs de Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperar-cuenta/', views.recuperar_cuenta, name='recuperar_cuenta'),
    
    path('perfil/', views.perfil_usuario, name='perfil'),
]