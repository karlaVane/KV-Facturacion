from django.shortcuts import redirect, render
from Facturacion.models import Pedido, Contribuyente,Tipo_comprobante
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
# Create your views here.

def login(request):
    """
    if request.method == 'POST':
        user = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=user, password=password)
        if user is None:
            messages.error(request,("mal"))
    """
    return render(request,'Facturacion/login.html')
    
@login_required
def Mis_facturas(request):
    pedidos = Pedido.objects.all()
    contribuyente = Contribuyente.objects.all()
    return render(request,'Facturacion/mis_facturas.html',{'pedidos': pedidos,'contribuyente':contribuyente})

@login_required
def vista_prev_fact(request):
    return render(request,'Facturacion/vista_previa.html')

@login_required
def reporte_general(request):
    return render(request,'Facturacion/reporte_general.html')

@login_required
def mis_datos(request):
    return render(request,'Facturacion/mis_datos.html')
