from django.http import request
from Facturacion.models import Contribuyente,Detalle_pedido, Pedido, Consumidor,Actualizaciones, Valores
from woocommerce import API
import time
import locale

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
        for datos in Contribuyente.objects.filter(usuario_id= us_id): #Recibir el correo de quien inicie sesion
            cred1=datos.consumer_key
            cred2=datos.consumer_secret
            url = datos.url_tienda
        return cred1,cred2,url

    def get_pedidos(self, after):
        url = 'orders/?per_page=100&after={}'.format(after)
        pedidos = self.wcapi.get(url).json()
        return pedidos 
    
    def get_pedido(self, id_pedido):
        url = 'orders/' + str(id_pedido)
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
            id_contribuyente = Contribuyente.objects.get(usuario_id =us_id)
        )
    ## ---------------------------------- Tabla Detalle Pedido ----------------------------------
    def guardar_detalle_pedidos(self,id_pedido,nombre_prod,cant,unitario,subtotal,sub_impuestos):
        Detalle_pedido.objects.create(
            id_pedido=Pedido.objects.get(num_pedido=id_pedido),
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
                cedula_consumidor = '9999999999'

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
                subtotal = det['subtotal']
                if (det['total_tax']=="0.00"):
                    subtotal_impuestos = 0
                else:
                    subtotal_impuestos = det['taxes'][0]['total']
                self.guardar_detalle_pedidos(pedido['id'],nombre_prod,cantidad,valor_unitario,subtotal,subtotal_impuestos)
        
        # Tabla actualizaciones
        self.guardar_fecha_actualizaciones()


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
            print("---------------------------------"+pedido)
            datos_pedidos = wc.get_pedido(pedido)
            print(datos_pedidos['status'])
            consulta=Pedido.objects.get(num_pedido = pedido)
            print(consulta.estado_pedido)    
            
            if (consulta.estado_pedido != datos_pedidos['status']):
                print("Son diferentes - toca actualizar")
                consulta.estado_pedido =datos_pedidos['status']
                consulta.save()
            else:
                print("Suerte - No ha cambiado nada")
        sincro.guardar_fecha_actualizaciones()
        return