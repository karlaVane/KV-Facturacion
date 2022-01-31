from tkinter.messagebox import NO
from django.shortcuts import redirect, render
from Facturacion.models import Pedido, Usuario,Contribuyente, Actualizaciones,Consumidor,Detalle_pedido,Establecimiento, Punto_emision, Documento
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Facturacion.Core import Actualizacion_pedido, Woocommerce, Sincronizacion
from datetime import datetime
from Facturacion.forms import FormularioConsumidor
from Facturacion.documento import DocumentoXML


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
    if (act == None):
        ultima_actualizacion = "Primera vez en tus facturas"
    else:
        ultima_actualizacion = act.fecha_actualizacion
    pedidos = Pedido.objects.filter(id_contribuyente_id =a).order_by('-num_pedido')
    return render(request,'Facturacion/mis_facturas.html',{'pedidos': pedidos, 'act':ultima_actualizacion })

########## nucleo del proyecto para facturar
@login_required
def vista_prev_fact(request,num_pedido):
    sum=0
    fecha_emision = datetime.today().strftime('%d/%m/%Y')
    fecha2 = datetime.today().strftime('%d%m%Y')
    us= request.user.id
    emisor = Contribuyente.objects.get(usuario_id = us)
    pedido = Pedido.objects.get(num_pedido = num_pedido)
    consumidor = Consumidor.objects.get(identificacion = pedido.id_consumidor_id)
    detalle_pedido = Detalle_pedido.objects.filter(id_pedido_id = num_pedido)
    
    ##
    doc = DocumentoXML()
    establecimiento = Establecimiento.objects.get(id_usuario_id = emisor.RUC) 
    num_emision = Punto_emision.objects.get(establecimiento_id = establecimiento.num_establecimiento)
    num_comprobante = Documento.objects.order_by('num_comprobante').last()
    if (num_comprobante == None):
        num_comprobante = "1".zfill(9)       
    else:
        num_comprobante = str(int(num_comprobante.num_comprobante)+1).zfill(9)
    num_factura = str(establecimiento.num_establecimiento)+"-"+str(num_emision.num_punto_emision)+"-"+num_comprobante
    ambiente = 1
    serie = str(establecimiento.num_establecimiento)+str(num_emision.num_punto_emision)
    tipo_comprobante = '01'
    cod_numerico = doc.generar_cod_numerico()
    tipo_emision = "1"
    clave_acceso = str(fecha2)+ tipo_comprobante+emisor.RUC + str(ambiente)+serie+num_comprobante+cod_numerico+tipo_emision
    dig_verificador = doc.digito_verificador(clave_acceso)
    clave_acceso = clave_acceso+dig_verificador
    
    ##
    for det in detalle_pedido:
        sum+= det.subtotal 
    if request.method == 'POST':
        consumidor = Consumidor.objects.get(identificacion= pedido.id_consumidor_id)
        doc.generar_XML(str(ambiente),tipo_emision, clave_acceso,tipo_comprobante,str(establecimiento.num_establecimiento),
        str(num_emision.num_punto_emision),num_comprobante, fecha2,emisor,consumidor,pedido,detalle_pedido)
        print("hay q facturar")
        print(consumidor.identificacion)
        print(num_pedido)
    
    return render(request,'Facturacion/vista_previa.html',
    {"num_pedido":num_pedido, "emisor": emisor, "fecha": fecha_emision,
     "consumidor":consumidor, "detalle":detalle_pedido,"pedido":pedido,"sum":sum,
     "comprobante": num_factura, "ambiente":ambiente, "clave": clave_acceso,})

##############

@login_required
def reporte_general(request):
    return render(request,'Facturacion/reporte_general.html')

@login_required
def mis_datos(request):
    us= request.user.id #obtengo el id de quien inició sesión
    a = Contribuyente.objects.get(usuario_id = us)
    datos2 = Usuario.objects.get(id= us)
    return render(request,'Facturacion/mis_datos.html',{'datos': a, 'datos2': datos2})

@login_required
def editar_consumidor(request, identificacion,num_pedido):
    consumidor = Consumidor.objects.filter(identificacion= identificacion).first()
    form = FormularioConsumidor(instance=consumidor)
    if request.method == 'POST':
        print("ENTROOOOOO")
        print(num_pedido)
        consumidor = Consumidor.objects.get(identificacion= identificacion)
        form = FormularioConsumidor(request.POST, instance=consumidor)
        if form.is_valid():
            form.save()
        messages.success(request,"Cambios guardados exitosamente")
    return render(request, 'Facturacion/editar_consumidor.html',{"form": form, "consumidor":consumidor, "num":num_pedido})

