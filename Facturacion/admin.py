from django.contrib import admin
from Facturacion.models import Tipo_comprobante, Contribuyente,Establecimiento,Punto_emision
# Register your models here.

class ComprobanteAdmin (admin.ModelAdmin):
    list_display = ("cod_comprobante","nombre_comprobante")
    search_fields = ("cod_comprobante","nombre_comprobante")

class ContribuyenteAdmin(admin.ModelAdmin):
    list_display = ("RUC","razon_social","contabilidad","correo","direccion","telefono")
    search_fields = ("RUC","razon_social")

class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ("num_establecimiento","nombre_establecimiento")
    search_fields = ("num_establecimiento","nombre_establecimiento")

class EmisionAdmin(admin.ModelAdmin):
    list_display = ("num_punto_emision","nombre_punto_emision")
    search_fields = ("num_punto_emision","nombre_punto_emision")

admin.site.register(Tipo_comprobante,ComprobanteAdmin)
admin.site.register(Contribuyente,ContribuyenteAdmin)
admin.site.register(Establecimiento,EstablecimientoAdmin)
admin.site.register(Punto_emision,EmisionAdmin)