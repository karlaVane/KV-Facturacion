from unicodedata import name
from django.urls import path
from Facturacion import views
from django.contrib.auth.views import LoginView,LogoutView


urlpatterns = [
    path('',LoginView.as_view(template_name='Facturacion/login.html', redirect_authenticated_user=True),name='login'),
    path('mis_facturas',views.Mis_facturas,name ='MisFacturas'),
    path('vista_previa/<int:num_pedido>',views.vista_prev_fact,name ='VistaPrevia'),
    path('editar_consumidor/<str:identificacion>/<int:num_pedido>',views.editar_consumidor, name="Editar"),
    path('reporte_general',views.reporte_general,name ='ReporteGeneral'),
    path('mis_datos',views.mis_datos ,name ='MisDatos'), 
    path('facturar/<str:identificacion>/<int:num_pedido>',views.vista_prev_fact, name="Facturar"),
]