from Facturacion.models import Contribuyente, Detalle_pedido, Pedido, Consumidor,Actualizaciones
from woocommerce import API
from datetime import datetime

class Woocommerce:
    def __init__(self):
        cred1,cred2 = self.obtener_credenciales()
        self.wcapi = API(
            url="https://avelectronics.cc/", 
            consumer_key = cred1,
            consumer_secret = cred2,
            wp_api=True, 
            version="wc/v3" 
        )
        
    def obtener_credenciales(self):
        for datos in Contribuyente.objects.filter(correo= 'karla.vanessa@outlook.es'): #Recibir el correo de quien inicie sesion
            cred1=datos.consumer_key
            cred2=datos.consumer_secret
        return cred1,cred2

    def get_pedidos(self, after):
        url = 'orders/?per_page=100&after={}'.format(after)
        pedidos = self.wcapi.get(url).json()
        return pedidos 
    
    def get_pedido(self, id_pedido):
        url = 'orders/' + str(id_pedido)
        pedido = self.wcapi.get(url).json()
        return pedido

class Sincronizacion:
    ## --------------------------------------- Tabla Consumidor ----------------------------------
    def guardar_consumidor(self,identif,nombre, correo, direccion,tlf):
        Consumidor.objects.create(
            identificacion = identif,
            nombre = nombre,
            correo = correo,
            direccion = direccion,
            telefono = tlf
        )
    ## --------------------------------------- Tabla Pedido ----------------------------------
    def guardar_pedidos(self,pedido,cedula,fecha,estado,href,total,t_imp):
        Pedido.objects.create(
            num_pedido = pedido,
            id_consumidor = Consumidor.objects.get(identificacion=cedula),
            fecha_pedido = fecha,
            estado_pedido = estado,
            href_pedido = href,
            ## pedido_completo = str(json_completo), agregar como parametro
            valor_total = float(total),
            total_impuestos = float(t_imp)
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
    def Actualizar (self,fecha,var):
        Actualizaciones.objects.create(
            fecha_actualizacion= fecha,
            ultima_fecha_pedido=var.fecha_pedido,
            ultimo_num_pedido = var.num_pedido
        )
    ## --------------------------------------- Todo ----------------------------------
    def guardar_todo(self,fecha):
        datos_json = Woocommerce()
        pedidos = datos_json.get_pedidos(fecha) 
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
                self.guardar_pedidos(pedido['id'],cedula_consumidor,pedido['date_created'],pedido['status'],pedido['_links']['self'][0]['href'],pedido['total'],pedido['total_tax'])
            else:
                if (pedido['billing']['first_name']==''): ## Cuando es consumidor final
                    self.guardar_consumidor(cedula_consumidor,'CONSUMIDOR FINAL', '', '','')   
                else: 
                    self.guardar_consumidor(cedula_consumidor,pedido['billing']['first_name']+' '+pedido['billing']['last_name'], pedido['billing']['email'],pedido['billing']['address_1'],pedido['billing']['phone'])
                self.guardar_pedidos(pedido['id'],cedula_consumidor,pedido['date_created'],pedido['status'],pedido['_links']['self'][0]['href'],pedido['total'],pedido['total_tax'])
            
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
        var = Pedido.objects.order_by('fecha_pedido').last() 
        actual = datetime.now()
        fecha = str(actual.year)+'-'+str(actual.month)+'-'+str(actual.day)
        hora = str(actual.hour)+':'+str(actual.minute)+':'+str(actual.second)
        fecha_actual=fecha+'T'+hora
        self.Actualizar(fecha_actual,var)
        