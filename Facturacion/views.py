from django.shortcuts import render
from Facturacion.models import Pedido, Contribuyente,Tipo_comprobante
from django.http import HttpResponse

# Create your views here.

def logeo(request):

    return render(request,'Facturacion/login.html')

def Mis_facturas(request):
    pedidos = Pedido.objects.all()
    contribuyente = Contribuyente.objects.all()
    return render(request,'Facturacion/mis_facturas.html',{'pedidos': pedidos,'contribuyente':contribuyente})

def vista_prev_fact(request):

    return render(request,'Facturacion/vista_previa.html')

def reporte_general(request):

    return render(request,'Facturacion/reporte_general.html')

def mis_datos(request):

    return render(request,'Facturacion/mis_datos.html')
