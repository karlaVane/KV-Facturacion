from datetime import date
from django.http import request
from Facturacion.models import Contribuyente,Detalle_pedido, Pedido, Consumidor,Actualizaciones, Valores
from woocommerce import API
import time
import locale
from django.db.models import Avg, Sum
import datetime as dtime
from django.db.models import Count

class Woocommerce:
    def __init__(self,us_id):
        self.us_id = us_id
        cred1,cred2,url_t = self.obtener_credenciales(self.us_id)
        self.wcapi = API(
            url=url_t, 
            consumer_key = cred1,
            consumer_secret = cred2,
            wp_api=True, 
            version="wc/v3" 
        )
        
    def obtener_credenciales(self, us_id):
        for datos in Contribuyente.objects.filter(usuario_id= us_id):
            cred1=datos.consumer_key
            cred2=datos.consumer_secret
            url = datos.url_tienda
        return cred1,cred2,url
    
    def get_pedido(self, id_pedido):
        url = 'orders/' + str(id_pedido)
        print(url)
        pedido = self.wcapi.get(url).json()
        return pedido
    
    def get_nuevos_pedidos(self):
        cant_pedidos=100
        var = Actualizaciones.objects.order_by('ultima_fecha_pedido').last() #Obtengo la última fecha de actualizacion
        
        if (var == None):
            ultima_fecha = "2022-01-01T00:00:00"
        else:
            ultima_fecha= var.ultima_fecha_pedido
        url='orders/?per_page={}&after={}'.format(cant_pedidos,ultima_fecha)
        print(url)
        pedido = self.wcapi.get(url).json()
        return pedido,cant_pedidos

class Sincronizacion:
    ## --------------------------------------- Tabla Consumidor ----------------------------------
    def guardar_consumidor(self,identif,nombre, correo, direccion,tlf):
        identif = identif.replace(" ","")
        tlf = tlf.replace(" ", "")
        Consumidor.objects.create(
            identificacion = identif,
            nombre = nombre,
            correo = correo,
            direccion = direccion,
            telefono = tlf
        )
    ## --------------------------------------- Tabla Pedido ----------------------------------
    def guardar_pedidos(self,pedido,cedula,fecha,estado,href,total,t_imp, us_id):
        total_compra = float(total) + float(t_imp)
        if(estado=="cancelled"):
            esta_facturado = "No se factura"
        else:
            esta_facturado = "Sin facturar"
        Pedido.objects.create(
            num_pedido = pedido,
            id_consumidor = Consumidor.objects.get(identificacion=cedula),
            fecha_pedido = fecha,
            estado_pedido = estado,
            href_pedido = href,
            ## pedido_completo = str(json_completo), agregar como parametro
            valor_total = float(total),
            total_impuestos = float(t_imp),
            total_compra = total_compra,
            id_contribuyente = Contribuyente.objects.get(usuario_id =us_id),
            esta_facturado = esta_facturado
        )
    ## ---------------------------------- Tabla Detalle Pedido ----------------------------------
    def guardar_detalle_pedidos(self,id_pedido,sku,nombre_prod,cant,unitario,subtotal,sub_impuestos):
        Detalle_pedido.objects.create(
            id_pedido=Pedido.objects.get(num_pedido=id_pedido),
            sku = sku,
            nombre_prod=nombre_prod,
            cantidad = cant,
            valor_unitario = unitario,
            subtotal = float(subtotal),
            subtotal_impuestos = float(sub_impuestos)
        )
    
    ## ---------------------------------- Tabla Actualizaciones ---------------------------------
    def guardar_fecha_actualizaciones (self):
        locale.setlocale(locale.LC_ALL, 'es-ES')
        var = Pedido.objects.order_by('fecha_pedido').last() 
        ahora = time.strftime("%A %d de %B del %Y - %H:%M")
        Actualizaciones.objects.create(
            fecha_actualizacion= ahora,
            ultima_fecha_pedido=var.fecha_pedido,
            ultimo_num_pedido = var.num_pedido
        )
   
    ## --------------------------------------- Todo ----------------------------------
    def guardar_todo(self,us_id):
        datos_json = Woocommerce(us_id)
        pedidos, cant = datos_json.get_nuevos_pedidos() 
        for pedido in pedidos: 
            cedula_consumidor = ''
            
            if (pedido['billing']['address_2']==''):
                #cedula_consumidor = ''
                meta_data = pedido['meta_data']
                for data in meta_data:
                    if (data['key']=='cedula'):
                        cedula_consumidor = data['value']
            else:
                cedula_consumidor = pedido['billing']['address_2'] 
            if(pedido['billing']['first_name'] == ''):
                cedula_consumidor = '9999999999999'

            if (Consumidor.objects.filter(identificacion = cedula_consumidor).exists()): #Comprueba existencia del Consumidor
                self.guardar_pedidos(pedido['id'],cedula_consumidor,pedido['date_created'],pedido['status'],pedido['_links']['self'][0]['href'],pedido['total'],pedido['total_tax'],us_id)
            else:
                if (pedido['billing']['first_name']==''): ## Cuando es consumidor final
                    self.guardar_consumidor(cedula_consumidor,'CONSUMIDOR FINAL', '', '','')   
                else: 
                    self.guardar_consumidor(cedula_consumidor,pedido['billing']['first_name']+' '+pedido['billing']['last_name'], pedido['billing']['email'],pedido['billing']['address_1'],pedido['billing']['phone'])
                self.guardar_pedidos(pedido['id'],cedula_consumidor,pedido['date_created'],pedido['status'],pedido['_links']['self'][0]['href'],pedido['total'],pedido['total_tax'],us_id)
            
            detalle = pedido['line_items']
            for det in detalle:
                nombre_prod = det['name']
                cantidad = det['quantity']
                valor_unitario = det['price']
                subtotal = det['total']
                sku = det['sku']
                if (det['total_tax']=="0.00"):
                    subtotal_impuestos = 0
                else:
                    subtotal_impuestos = det['taxes'][0]['total']
                self.guardar_detalle_pedidos(pedido['id'],sku,nombre_prod,cantidad,valor_unitario,subtotal,subtotal_impuestos)
        
        # Tabla actualizaciones
        self.guardar_fecha_actualizaciones()

    def generar_reporte_general(self):
        actual = dtime.datetime.utcnow() #Fecha actual
        fecha_limite = actual - dtime.timedelta(days=30) #Fecha actual - 30 días
        actual = str(actual.strftime("%Y-%m-%dT%H:%M:%S"))
        fecha_limite = str(fecha_limite.strftime("%Y-%m-%dT%H:%M:%S"))

        num_clientes = Pedido.objects.filter(
        fecha_pedido__gte=str(fecha_limite), 
        fecha_pedido__lte=str(actual)).values("id_consumidor_id").distinct().count()
        
        total_ventas = Pedido.objects.filter(
        fecha_pedido__gte=str(fecha_limite), 
        fecha_pedido__lte=str(actual)).aggregate(Sum('valor_total'))
        
        transacciones = Pedido.objects.filter(
        fecha_pedido__gte=str(fecha_limite), 
        fecha_pedido__lte=str(actual)).count()

        consumo_promedio = Pedido.objects.filter(
        fecha_pedido__gte=str(fecha_limite), 
        fecha_pedido__lte=str(actual)).aggregate(Avg("valor_total"))
        
        total_impuestos= Pedido.objects.filter(
        fecha_pedido__gte=str(fecha_limite), 
        fecha_pedido__lte=str(actual)).aggregate(Sum('total_impuestos'))
               
        top_pedidos = Detalle_pedido.objects.annotate(pedidos=Count('nombre_prod')).order_by('-pedidos')[:3]
        return num_clientes, total_ventas , transacciones,consumo_promedio,total_impuestos,top_pedidos


class Actualizacion_pedido:
    
    def obtener_pedidos_noCompletado(self):
        pedidos_noC=[]
        for pedido in Pedido.objects.exclude(estado_pedido = 'completed').exclude(estado_pedido ='cancelled'): 
            pedidos_noC.append(pedido.num_pedido)
        return pedidos_noC

    def modificar_estado_pedido(self,us_id,pedidos_noC):
        wc= Woocommerce(us_id)
        sincro = Sincronizacion()
        for pedido in pedidos_noC:
            datos_pedidos = wc.get_pedido(pedido)
            consulta=Pedido.objects.get(num_pedido = pedido)
            if (consulta.estado_pedido != datos_pedidos['status']):
                consulta.estado_pedido =datos_pedidos['status']
                consulta.save()
        sincro.guardar_fecha_actualizaciones()
        return


