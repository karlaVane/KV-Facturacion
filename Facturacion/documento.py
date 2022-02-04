import xml.etree.cElementTree as ET 
import random 
import subprocess

class DocumentoXML:
    def generar_XML(self,ambiente,emision,clave,codDoc,estab,ptoEmi,secuencial,
    fecha, emisor, consumidor, pedido,detalle_pedido):
        factura = ET.Element("factura", id="comprobante", version="1.0.0")
        ## Información tributaria
        infoTributaria = ET.SubElement(factura, "infoTributaria")
        ET.SubElement(infoTributaria, "ambiente").text = ambiente
        ET.SubElement(infoTributaria, "tipoEmision").text = emision
        ET.SubElement(infoTributaria, "razonSocial").text = emisor.razon_social
        if emisor.nombre_comercial != '':
            ET.SubElement(infoTributaria, "nombreComercial").text = emisor.nombre_comercial
        ET.SubElement(infoTributaria, "ruc").text = emisor.RUC
        ET.SubElement(infoTributaria, "claveAcceso").text = clave
        ET.SubElement(infoTributaria, "codDoc").text = codDoc
        ET.SubElement(infoTributaria, "estab").text = estab
        ET.SubElement(infoTributaria, "ptoEmi").text = ptoEmi
        ET.SubElement(infoTributaria, "secuencial").text = secuencial
        ET.SubElement(infoTributaria, "dirMatriz").text = emisor.direccion

        ## Información factura
        infoFactura = ET.SubElement(factura, "infoFactura")
        ET.SubElement(infoFactura, "fechaEmision").text = fecha
        #ET.SubElement(infoFactura, "dirEstablecimiento").text = "dirEstablecimiento"
        if emisor.contabilidad:
            ET.SubElement(infoFactura, "obligadoContabilidad").text = "SI"
        else:
            ET.SubElement(infoFactura, "obligadoContabilidad").text = "NO"
        if consumidor.identificacion == '9999999999999':
            ET.SubElement(infoFactura, "tipoIdentificacionComprador").text = "07"
        else:
            if len(consumidor.identificacion)==10:
                ET.SubElement(infoFactura, "tipoIdentificacionComprador").text = "05"
            elif len(consumidor.identificacion)==13:
                ET.SubElement(infoFactura, "tipoIdentificacionComprador").text = "04"

        ET.SubElement(infoFactura, "razonSocialComprador").text = consumidor.nombre
        ET.SubElement(infoFactura, "identificacionComprador").text = consumidor.identificacion
        ET.SubElement(infoFactura, "direccionComprador").text = consumidor.direccion
        ET.SubElement(infoFactura, "totalSinImpuestos").text = str(round(float(pedido.valor_total)-float(pedido.total_impuestos),2))
        ET.SubElement(infoFactura, "totalDescuento").text = "0.00"
        
        ####  Total con Impuestos
        ###### Total impuesto
        totalConImpuestos = ET.SubElement(infoFactura, "totalConImpuestos")
        totalImpuesto = ET.SubElement(totalConImpuestos, "totalImpuesto")
        ######
        ET.SubElement(totalImpuesto, "codigo").text = "2"
        if pedido.total_impuestos != 0.0000:
            ET.SubElement(totalImpuesto, "codigoPorcentaje").text ="2"
        else:
            ET.SubElement(totalImpuesto, "codigoPorcentaje").text ="0"

        ET.SubElement(totalImpuesto, "descuentoAdicional").text = "0.00"
        ET.SubElement(totalImpuesto, "baseImponible").text = str(round(float(pedido.valor_total)-float(pedido.total_impuestos),2))
        ET.SubElement(totalImpuesto, "valor").text = str(round(float(pedido.total_impuestos),2))
        ## Información factura
        ET.SubElement(infoFactura, "propina").text = "0.00"
        ET.SubElement(infoFactura, "importeTotal").text = str(round(pedido.valor_total,2))
        ET.SubElement(infoFactura, "moneda").text = "DOLAR"
        
        pagos = ET.SubElement(infoFactura, "pagos")
        pago = ET.SubElement(pagos, "pago")
        ET.SubElement(pago, "formaPago").text = "20"
        ET.SubElement(pago, "total").text = str(round(pedido.valor_total,2))
        #ET.SubElement(pago, "plazo").text = "plazo" #Cuando corresponda
        #ET.SubElement(pago, "unidadTiempo").text = "dias" #cuando corresponda

        ## Detalles
        #### Detalle
        detalles = ET.SubElement(factura, "detalles")
        for det in detalle_pedido:

            detalle = ET.SubElement(detalles,"detalle")
            ET.SubElement(detalle, "codigoPrincipal").text = det.sku
            ET.SubElement(detalle, "descripcion").text = det.nombre_prod
            ET.SubElement(detalle, "cantidad").text = str(det.cantidad)
            ET.SubElement(detalle, "precioUnitario").text = str(round(det.valor_unitario,2))
            ET.SubElement(detalle, "descuento").text = "0.00"
            ET.SubElement(detalle, "precioTotalSinImpuesto").text = str(round(det.subtotal,2))

            impuestos = ET.SubElement(detalle,"impuestos")
            impuesto = ET.SubElement(impuestos,"impuesto")
            ET.SubElement(impuesto, "codigo").text = "2"

            if det.subtotal_impuestos != 0.0000:
                ET.SubElement(impuesto, "codigoPorcentaje").text = "2"
                ET.SubElement(impuesto, "tarifa").text = "12"
            else:    
                ET.SubElement(impuesto, "codigoPorcentaje").text = "0"
                ET.SubElement(impuesto, "tarifa").text = "0"
            
            ET.SubElement(impuesto, "baseImponible").text = str(round(det.subtotal,2))
            ET.SubElement(impuesto, "valor").text = str(round(det.subtotal_impuestos,2))

        ## Campos adicionales
        #campoAdicional= ET.SubElement(factura, "campoAdicional", nombre="riempe").text = "Popular o Emprendedor"
        print (factura)
        arbol = ET.ElementTree(factura)
        arbol.write("Facturacion/XMLs/"+pedido.num_pedido+".xml",encoding="UTF-8",xml_declaration=True)
        
        
        
    def generar_cod_numerico(self):
        num = 8
        cod=''
        for e in range(num):
            cod+=str(random.randint(1, 9))
        return cod # devuelve en string
    
    def digito_verificador(self,codigo):
        ban=2
        sum= 0
        codigo =  codigo[len(codigo)::-1] # invierto
        for cod in codigo:
            cod= int(cod)
            if (ban == 8):
                ban=2
            sum += cod*ban 
            ban += 1
        digito = 11 - (sum%11)
        if digito == 11:
            digito = 0
        elif digito == 10:
            digito = 1
        return str(digito) #devuelve en int

    def subproceso(self,contra,num_pedido):        
        #return subprocess.check_output('java -jar C:\\Users\\HP\\Documents\\Karla\\01.TESIS\\KV-Facturacion\\KVFacturacion\\Facturacion\\privada\\firmador.jar C:\\Users\\HP\\Documents\\Karla\\01.TESIS\\KV-Facturacion\\KVFacturacion\\Facturacion\\privada\\FIRMA.p12 KVmr210897 C:\\Users\\HP\\Documents\\Karla\\01.TESIS\\KV-Facturacion\\KVFacturacion\\Facturacion\\XMLs\\1753244324.xml C:\\Users\\HP\\Documents\\Karla\\01.TESIS\\KV-Facturacion\\KVFacturacion\\Facturacion\\XMLs 1753244324F.xml',shell=True)
        a = subprocess.check_output('java -jar '+ r'.\Facturacion\privada\firmador.jar '+ 
        r'.\Facturacion\privada\FIRMA.p12 '+
        contra+' '+
        '.\\Facturacion\\XMLs\\'+str(num_pedido)+".xml "+
        r'.\Facturacion\XMLs ' +
        str(num_pedido)+'.xml',shell=True)
        
        return a
        
        