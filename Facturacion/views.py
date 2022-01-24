from django.shortcuts import redirect, render
from Facturacion.models import Pedido, Usuario,Tipo_comprobante
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Facturacion.Core import Actualizacion_pedido, Woocommerce, Sincronizacion,Contribuyente, Actualizaciones

# Create your views here.

def login(request):
    return render(request,'Facturacion/login.html')

    
@login_required
def Mis_facturas(request):
    us= request.user.id #obtengo el id de quien inició sesión
    a = Contribuyente.objects.get(usuario_id = us)
    
    if request.method == 'POST':
        fun = Actualizacion_pedido()
        wc = Woocommerce(us)
        sincro = Sincronizacion()
        pedidos_noC = fun.obtener_pedidos_noCompletado()
        nuevos_pedidos,cant_pedidos = wc.get_nuevos_pedidos()
        
        if (len(pedidos_noC) !=0):
            fun.modificar_estado_pedido(us,pedidos_noC)
            messages.success(request,"Pedidos actualizados")
        else:
            messages.success(request,"No hay pedidos por actualizar")
        
        if (len(nuevos_pedidos) == 0):
            messages.info(request,"No hay pedidor por agregar")
        elif (len(nuevos_pedidos) !=0):
            sincro.guardar_todo(us)
            messages.success(request,"Nuevos Pedidos Agregados")
        elif (len(nuevos_pedidos)==cant_pedidos):
            messages.warning(request,"Hay q seguir consultando")
    act = Actualizaciones.objects.order_by('id').last()
    pedidos = Pedido.objects.filter(id_contribuyente_id =a)
    return render(request,'Facturacion/mis_facturas.html',{'pedidos': pedidos, 'act':act.fecha_actualizacion})

@login_required
def vista_prev_fact(request):
    return render(request,'Facturacion/vista_previa.html')

@login_required
def reporte_general(request):
    return render(request,'Facturacion/reporte_general.html')

@login_required
def mis_datos(request):
    us= request.user.id #obtengo el id de quien inició sesión
    a = Contribuyente.objects.get(usuario_id = us)
    datos2 = Usuario.objects.get(id= us)
    return render(request,'Facturacion/mis_datos.html',{'datos': a, 'datos2': datos2})
