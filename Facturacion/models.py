from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def nombre(self):
        return self.last_name + " " + self.first_name

class Contribuyente(models.Model):
    usuario = models.OneToOneField(Usuario,on_delete=models.CASCADE)
    RUC = models.CharField(primary_key=True,max_length=15)
    razon_social = models.CharField(max_length=40, verbose_name="Razón social")
    nombre_comercial = models.CharField(max_length=300, verbose_name="Nombre Comercial", blank=True)
    url_tienda = models.CharField(max_length=300, verbose_name="URL Tienda")
    consumer_key = models.CharField(max_length=100)
    consumer_secret = models.CharField(max_length=100)
    direccion = models.CharField(max_length=900,verbose_name="Dirección")
    contabilidad = models.BooleanField()
    telefono = models.CharField(max_length=10,verbose_name="Teléfono")
    firma_electronica = models.FileField()
    fecha_caducidad = models.DateField()

    def __str__(self):
        return self.razon_social


class Tipo_comprobante(models.Model):
    cod_comprobante = models.CharField(primary_key=True,max_length=2,verbose_name="Código comprobante")
    nombre_comprobante = models.CharField(max_length=50,verbose_name="Nombre comprobante")
    
    def __str__(self):
        return self.nombre_comprobante
    

class Establecimiento(models.Model):
    num_establecimiento = models.CharField(primary_key= True,max_length=3)
    id_usuario = models.ForeignKey(Contribuyente,on_delete=models.CASCADE, null=True)
    nombre_establecimiento= models.CharField(max_length=50)

    def __str__(self):
        return self.nombre_establecimiento

class Punto_emision(models.Model):
    num_punto_emision = models.CharField(primary_key= True,max_length=3,verbose_name="Num. Punto de emisión")
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE,null=True)
    nombre_punto_emision = models.CharField(max_length=30,verbose_name="Nombre Punto de emisión")

    def __str__(self):
        return self.nombre_punto_emision
    
class Consumidor(models.Model):
    identificacion = models.CharField(primary_key=True,max_length=15)
    nombre = models.CharField(max_length=500)
    correo = models.CharField(max_length=100)
    direccion = models.CharField(max_length=300)
    telefono = models.CharField(max_length=15)
    def __str__(self):
        return self.nombre

class Pedido (models.Model): 
    num_pedido = models.CharField(primary_key=True,max_length=50)
    id_consumidor = models.ForeignKey(Consumidor,on_delete=models.CASCADE,null=True)
    fecha_pedido = models.CharField(max_length=50)
    estado_pedido = models.CharField(max_length=20)
    envio = models.BooleanField(default=False)
    href_pedido = models.URLField()
    ##pedido_completo = models.JSONField() 
    valor_total = models.DecimalField(max_digits=9, decimal_places=4,default=0)
    total_impuestos = models.DecimalField(max_digits=9, decimal_places=4,default=0)
    valor_transporte = models.DecimalField(max_digits=9, decimal_places=4,default=0)
    total_compra = models.DecimalField(max_digits=9, decimal_places=4,default=0)
    id_contribuyente = models.ForeignKey(Contribuyente,on_delete=models.CASCADE,null=True)
    esta_facturado= models.CharField(default="Sin facturar", max_length=100)

class Detalle_pedido(models.Model):
    id_pedido = models.ForeignKey(Pedido,on_delete=models.CASCADE,null=False)
    sku = models.CharField(max_length=10)
    nombre_prod = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=9,decimal_places=4, default=0)
    subtotal = models.DecimalField(max_digits=9,decimal_places=4,default=0 )
    subtotal_impuestos = models.DecimalField(max_digits=9,decimal_places=4,default=0 )

class Documento(models.Model):
    num_comprobante = models.CharField(primary_key=True,max_length=9)
    id_pedido = models.OneToOneField(Pedido,on_delete=models.CASCADE) ###
    tipo_ambiente = models.CharField(max_length=2)
    tipo_emision = models.IntegerField(default=1) #Emisión normal
    id_usuario = models.ForeignKey(Contribuyente,on_delete=models.CASCADE, null=True)
    clave_acceso = models.CharField(max_length=49)
    tipo_comprobante = models.ForeignKey(Tipo_comprobante,on_delete=models.CASCADE, null=True)
    serie = models.CharField(max_length=6) #establecimiento + punto emision
    fecha_emision = models.DateTimeField(auto_now_add=True)
    #num_gr = models.CharField(max_length=30) NO APLICA
    documento = models.FileField()

class Valores(models.Model): 
    id_documento = models.ForeignKey(Documento,on_delete=models.CASCADE,null=True)
    nombre_valor = models.CharField(max_length=30)
    valor = models.DecimalField(max_digits=9,decimal_places=4,default=0)

class Actualizaciones(models.Model):
    fecha_actualizacion = models.CharField(max_length=50)
    ultima_fecha_pedido = models.CharField(max_length=50)
    ultimo_num_pedido = models.CharField(max_length=10)