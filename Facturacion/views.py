from django.shortcuts import redirect, render
from Facturacion.models import Pedido, Contribuyente,Tipo_comprobante
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Facturacion.Core import Actualizacion_pedido, Woocommerce, Sincronizacion

# Create your views here.

def login(request):
    return render(request,'Facturacion/login.html')

    
@login_required
def Mis_facturas(request):
    if request.method == 'POST':
        fun = Actualizacion_pedido()
        wc = Woocommerce()
        sincro = Sincronizacion()
        pedidos_noC = fun.obtener_pedidos_noCompletado()
        nuevos_pedidos,cant_pedidos = wc.get_nuevos_pedidos()

        ## PREGUNTAR SI ESTÁ BIEN 
        if (len(pedidos_noC) !=0):
            fun.modificar_estado_pedido(pedidos_noC)
            messages.success(request,"Pedidos actualizados")
        
        if (len(nuevos_pedidos) == 0 or len(pedidos_noC == 0 )):
            messages.info(request,"No hay pedidos por actualizar")
        elif (len(nuevos_pedidos) !=0):
            sincro.guardar_todo()
            messages.success(request,"Nuevos Pedidos Agregados")
        elif (len(nuevos_pedidos)==cant_pedidos):
            messages.warning(request,"Hay q seguir consultando")

    pedidos = Pedido.objects.all()
    contribuyente = Contribuyente.objects.all()
    return render(request,'Facturacion/mis_facturas.html',{'pedidos': pedidos,'contribuyente':contribuyente, })

@login_required
def vista_prev_fact(request):
    return render(request,'Facturacion/vista_previa.html')

@login_required
def reporte_general(request):
    return render(request,'Facturacion/reporte_general.html')

@login_required
def mis_datos(request):
    return render(request,'Facturacion/mis_datos.html')
