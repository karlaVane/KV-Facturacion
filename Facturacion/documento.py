import xml.etree.cElementTree as ET 
import random 

class DocumentoXML:
    def generar_XML(self,ambiente,emision,razonSocial,nombreComercial,ruc,clave,codDoc,estab,ptoEmi,secuencial,dirMatriz):
        factura = ET.Element("factura", id="comprobante", version="1.0.0")
        ## Información tributaria
        infoTributaria = ET.SubElement(factura, "infoTributaria")
        ET.SubElement(infoTributaria, "ambiente").text = ambiente
        ET.SubElement(infoTributaria, "tipoEmision").text = emision
        ET.SubElement(infoTributaria, "razonSocial").text = razonSocial
        ET.SubElement(infoTributaria, "nombreComercial").text = nombreComercial
        ET.SubElement(infoTributaria, "ruc").text = ruc
        ET.SubElement(infoTributaria, "claveAcceso").text = clave
        ET.SubElement(infoTributaria, "codDoc").text = codDoc
        ET.SubElement(infoTributaria, "estab").text = estab
        ET.SubElement(infoTributaria, "ptoEmi").text = ptoEmi
        ET.SubElement(infoTributaria, "secuencial").text = secuencial
        ET.SubElement(infoTributaria, "dirMatriz").text = dirMatriz

        ## Información factura
        infoFactura = ET.SubElement(factura, "infoFactura")
        ET.SubElement(infoFactura, "fechaEmision").text = "fecha"
        ET.SubElement(infoFactura, "dirEstablecimiento").text = "dirEstablecimiento"
        ET.SubElement(infoFactura, "obligadoContabilidad").text = "obligadoContabilidad"
        ET.SubElement(infoFactura, "tipoIdentificacionComprador").text = "tipoIdentificacionComprador"
        ET.SubElement(infoFactura, "razonSocialComprador").text = "razonSocialComprador"
        ET.SubElement(infoFactura, "identificacionComprador").text = "identificacionComprador"
        ET.SubElement(infoFactura, "direccionComprador").text = "direccionComprador"
        ET.SubElement(infoFactura, "totalSinImpuestos").text = "totalSinImpuestos"
        ET.SubElement(infoFactura, "totalDescuento").text = "totalDescuento"
        
        ####  Total con Impuestos
        ###### Total impuesto
        totalConImpuestos = ET.SubElement(infoFactura, "totalConImpuestos")
        totalImpuesto = ET.SubElement(totalConImpuestos, "totalImpuesto")
        ######
        ET.SubElement(totalImpuesto, "codigo").text = "codigo"
        ET.SubElement(totalImpuesto, "codigoPorcentaje").text = "codigoPorcentaje"
        ET.SubElement(totalImpuesto, "baseImponible").text = "baseImponible"
        ET.SubElement(totalImpuesto, "valor").text = "valor"
        ## Información factura
        ET.SubElement(infoFactura, "propina").text = "propina"
        ET.SubElement(infoFactura, "importeTotal").text = "importeTotal"
        ET.SubElement(infoFactura, "moneda").text = "moneda"
        
        pagos = ET.SubElement(infoFactura, "pagos")
        pago = ET.SubElement(pagos, "pago")
        ET.SubElement(pago, "formaPago").text = "formapago"
        ET.SubElement(pago, "total").text = "total"
        ET.SubElement(pago, "plazo").text = "plazo" #Cuando corresponda
        ET.SubElement(pago, "unidadTiempo").text = "dias" #cuando corresponda

        ## Detalles
        #### Detalle
        detalles = ET.SubElement(factura, "detalles")
        detalle = ET.SubElement(detalles,"detalle")
        ET.SubElement(detalle, "codigoPrincipal").text = "codigoPrincipal"
        ET.SubElement(detalle, "descripcion").text = "descripcion"
        ET.SubElement(detalle, "cantidad").text = "cantidad"
        ET.SubElement(detalle, "precioUnitario").text = "precioUnitario"
        ET.SubElement(detalle, "descuento").text = "descuento"
        ET.SubElement(detalle, "precioTotalSinImpuesto").text = "precioTotalSinImpuesto"

        impuestos = ET.SubElement(detalle,"impuestos")
        impuesto = ET.SubElement(impuestos,"impuesto")
        ET.SubElement(impuesto, "codigo").text = "codigo"
        ET.SubElement(impuesto, "codigoPorcentaje").text = "codigoPorcentaje"
        ET.SubElement(impuesto, "tarifa").text = "tarifa"
        ET.SubElement(impuesto, "baseImponible").text = "baseImponible"
        ET.SubElement(impuesto, "valor").text = "valor"

        ## Campos adicionales
        campoAdicional= ET.SubElement(factura, "campoAdicional", nombre="riempe").text = "Popular o Emprendedor"
        
        
        #arbol = ET.ElementTree(comienzo)
        arbol = ET.ElementTree(factura)
        #ET.ElementTree.parse(arbol,source="Facturacion/XMLs/prueba.xml")
        arbol.write("Facturacion/XMLs/prueba.xml",encoding="UTF-8",xml_declaration=True)
        
        
        
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
