from email.mime import base
from lxml import etree
import subprocess
from xml.dom.minidom import parse, parseString
from Facturacion.sri import Service as SRIService

import codecs
import base64

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')

class Factura:
    def _get_tax_element(self):
        
        infoTributaria = etree.Element('infoTributaria')
        etree.SubElement(infoTributaria, 'ambiente').text = "1"
        etree.SubElement(infoTributaria, 'tipoEmision').text = "1"
        etree.SubElement(infoTributaria, 'razonSocial').text = "MOYON RIVERA KARLA VANESSA"
        etree.SubElement(infoTributaria, 'ruc').text = "1724997950001"
        etree.SubElement(infoTributaria, 'claveAcceso').text = "3101202201172499795000110010020000000015362683516"
        etree.SubElement(infoTributaria, 'codDoc').text = "01"
        etree.SubElement(infoTributaria, 'estab').text = "001"
        etree.SubElement(infoTributaria, 'ptoEmi').text = "002"
        etree.SubElement(infoTributaria, 'secuencial').text = "000000001"
        etree.SubElement(infoTributaria, 'dirMatriz').text = "QUITO, PEDRO CAPIRO OE5-15 AV. TENIENTE HUGO ORTIZ, FRENTE AL CUERPO DE BOMBEROS, NUEVO SUR"
        return infoTributaria

    def _get_invoice_element(self):
        infoFactura = etree.Element('infoFactura')
        etree.SubElement(infoFactura, 'fechaEmision').text = "31012022"
        etree.SubElement(infoFactura, 'dirEstablecimiento').text = "QUITO, PEDRO CAPIRO OE5-15 AV. TENIENTE HUGO ORTIZ, FRENTE AL CUERPO DE BOMBEROS, NUEVO SUR"
        etree.SubElement(infoFactura, 'obligadoContabilidad').text = 'NO'
        etree.SubElement(infoFactura, 'tipoIdentificacionComprador').text = "05"
        etree.SubElement(infoFactura, 'razonSocialComprador').text = "Xavier Chasi"
        etree.SubElement(infoFactura, 'identificacionComprador').text = "1753244324"
        etree.SubElement(infoFactura, 'direccionComprador').text = "El Condado"
        etree.SubElement(infoFactura, 'totalSinImpuestos').text = "40.0"
        etree.SubElement(infoFactura, 'totalDescuento').text = "0.00"
        
        #totalConImpuestos
        totalConImpuestos = etree.Element('totalConImpuestos')
        totalImpuesto = etree.Element('totalImpuesto')
        etree.SubElement(totalImpuesto, 'codigo').text = "2"
        etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = "2"
        etree.SubElement(totalImpuesto, 'descuentoAdicional').text = "0.00"
        etree.SubElement(totalImpuesto, 'baseImponible').text = "40.00"
        etree.SubElement(totalImpuesto, 'valor').text = "4.80"
        totalConImpuestos.append(totalImpuesto)
        infoFactura.append(totalConImpuestos)
        
        etree.SubElement(infoFactura, 'propina').text = '0.00'
        etree.SubElement(infoFactura, 'importeTotal').text = "44.80"
        etree.SubElement(infoFactura, 'moneda').text = 'DOLAR'
        
        #Pagos 
        pagos = etree.Element('pagos')
        pago = etree.Element('pago')
        etree.SubElement(pago, 'formaPago').text = "20"
        etree.SubElement(pago, 'total').text = "44.80"
        pagos.append(pago)
        infoFactura.append(pagos)

        return infoFactura

    def _get_detail_element(self):
        detalles = etree.Element('detalles')
        detalle = etree.Element('detalle')
        etree.SubElement(detalle, 'codigoPrincipal').text = "AS024"
        etree.SubElement(detalle, 'descripcion').text = "YUN Shield V1.1.6"
        etree.SubElement(detalle, 'cantidad').text = "1"
        etree.SubElement(detalle, 'precioUnitario').text = "40.00"
        etree.SubElement(detalle, 'descuento').text = "0.00"
        etree.SubElement(detalle, 'precioTotalSinImpuesto').text = "40.00"
        impuestos = etree.Element('impuestos')
        
        impuesto = etree.Element('impuesto')
        etree.SubElement(impuesto, 'codigo').text = "2"
        etree.SubElement(impuesto, 'codigoPorcentaje').text = "2"
        etree.SubElement(impuesto, 'tarifa').text = "12"
        etree.SubElement(impuesto, 'baseImponible').text = "40.00"
        etree.SubElement(impuesto, 'valor').text = "4.80"
        impuestos.append(impuesto)
        detalle.append(impuestos)
        detalles.append(detalle)
        return detalles
    
    def _generate_xml_invoice(self):
        factura = etree.Element('factura')
        factura.set("id", "comprobante")
        factura.set("version", "1.1.0")
        
        # generar infoTributaria
        infoTributaria = self._get_tax_element()
        factura.append(infoTributaria)
        
        # generar infoFactura
        infoFactura = self._get_invoice_element()
        factura.append(infoFactura)
        
        #generar detalles
        detalles = self._get_detail_element()
        
        factura.append(detalles)
        return factura
    
    def ejecutar(self):
        path = "Facturacion/XMLs/probando.xml"
        factura = self._generate_xml_invoice()
        
        tree = etree.ElementTree(factura)
        tree.write(path, xml_declaration=True, encoding='utf-8', method="xml")
        
        a = subprocess.check_output('java -jar '+ r'.\Facturacion\privada\firmador.jar '+ 
        r'.\Facturacion\privada\FIRMA.p12 '+
        'KVmr210897 '+
        r'.\Facturacion\XMLs\probando.xml '+
        r'.\Facturacion\XMLs ' +
       'probando.xml',shell=True)
       
    def send_receipt(self):
        name = "Facturacion/XMLs/probando.xml"
        cadena = open(name, mode='rb').read()
        document = parseString(cadena.strip())
        xml = base64.b64encode(document.toxml('UTF-8'))
        
        #xml = codecs.encode(document.toxml('UTF-8'),'base64')
        print (xml)
        client = Client(SRIService.get_ws_test()[0])
        print(client)
        
        result =  client.service.validarComprobante(cadena)
        print(result)
        mensaje_error = ""
        
        if (result[0] == 'DEVUELTA'):
            comprobante = result[1].comprobante
            mensaje_error += 'Clave de Acceso: ' + comprobante[0].claveAcceso
            mensajes = comprobante[0].mensajes
            i = 0
            mensaje_error += "\nErrores:\n"
            while i < len(mensajes):
                mensaje = mensajes[i]
                mensaje_error += 'Identificador: ' + mensaje[i].identificador + '\nMensaje: ' + mensaje[i].mensaje + '\nInformacion Adicional: ' + mensaje[i].informacionAdicional + '\nTipo: ' + mensaje[i].tipo + "\n"
                i += 1
            print('Error SRI', mensaje_error)
        
        return True
    
    def request_authorization(self,access_key):
        try:
            client_auto = Client(SRIService.get_ws_test()[1])
            result_auto =  client_auto.service.autorizacionComprobante(access_key)
                
            if result_auto[2] == '':
                print('Error SRI', 'No existe comprobante')
            else:
                autorizaciones = result_auto[2].autorizacion
                i = 0
                autorizado = False
                while i < len(autorizaciones):
                    autorizacion = autorizaciones[i]
                    estado = autorizacion.estado
                    fecha_autorizacion = autorizacion.fechaAutorizacion
                    mensaje_error = ''
                    if (estado == 'NO AUTORIZADO'):
                        #comprobante no autorizado
                        mensajes = autorizacion.mensajes
                        j = 0
                        mensaje_error += "\nErrores:\n"
                        while j < len(mensajes):
                            mensaje = mensajes[j]
                            mensaje_error += 'Identificador: ' + mensaje[j].identificador + '\nMensaje: ' + mensaje[j].mensaje + '\nTipo: ' + mensaje[j].tipo + '\n'
                            j += 1
                    else:
                        autorizado = True
                        numero_autorizacion = autorizacion.numeroAutorizacion
                    i += 1    
                if autorizado == True:
                    print("AUTORIZADO")
                    """
                    self.write(cr, uid, obj.id, {'autorizado_sri': True, 'numero_autorizacion': numero_autorizacion, 'fecha_autorizacion': fecha_autorizacion})
                    autorizacion_xml = etree.Element('autorizacion')
                    etree.SubElement(autorizacion_xml, 'estado').text = estado
                    etree.SubElement(autorizacion_xml, 'numeroAutorizacion').text = numero_autorizacion
                    etree.SubElement(autorizacion_xml, 'fechaAutorizacion').text = str(fecha_autorizacion.strftime("%d/%m/%Y %H:%M:%S"))
                    etree.SubElement(autorizacion_xml, 'comprobante').text = etree.CDATA(autorizacion.comprobante)
                    
                    tree = etree.ElementTree(autorizacion_xml)
                    name = '%s%s.xml' %('/opt/facturas/', access_key)
                    fichero = tree.write(name,pretty_print=True,xml_declaration=True,encoding='utf-8',method="xml")
                    """
                else:
                    print('Error SRI', mensaje_error)
        except TransportError as e:
            print(('Warning!'), (str(e)))

        return 