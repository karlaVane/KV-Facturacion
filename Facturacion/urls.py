from unicodedata import name
from django.urls import path
from Facturacion import views
from django.contrib.auth.views import LoginView,LogoutView


urlpatterns = [
    path('',LoginView.as_view(template_name='Facturacion/login.html', redirect_authenticated_user=True),name='login'),
    path('mis_facturas',views.Mis_facturas,name ='MisFacturas'),
    path('vista_previa',views.vista_prev_fact,name ='VistaPrevia'),
    path('reporte_general',views.reporte_general,name ='ReporteGeneral'),
    path('mis_datos',views.mis_datos ,name ='MisDatos'),
]