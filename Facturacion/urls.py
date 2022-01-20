from django.urls import path
from Facturacion import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('',views.logeo,name ='Inicio'),
    path('mis_facturas',views.Mis_facturas,name ='MisFacturas'),
    path('vista_previa',views.vista_prev_fact,name ='VistaPrevia'),
    path('reporte_general',views.reporte_general,name ='ReporteGeneral'),
    path('mis_datos',views.mis_datos ,name ='MisDatos')
    
]