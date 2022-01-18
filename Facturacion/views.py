from django.shortcuts import render
from Facturacion.models import Contribuyente,Tipo_comprobante
from django.http import HttpResponse

# Create your views here.

def logeo(request):

    return render(request,'Facturacion/login.html')

def Mis_facturas(request):

    return render(request,'Facturacion/mis_facturas.html')

def vista_prev_fact(request):

    return render(request,'Facturacion/vista_previa.html')

def reporte_general(request):

    return render(request,'Facturacion/reporte_general.html')

def mis_datos(request):

    return render(request,'Facturacion/mis_datos.html')
