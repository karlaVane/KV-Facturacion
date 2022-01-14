from django.shortcuts import render
from Facturacion.models import Contribuyente,Tipo_comprobante
from django.http import HttpResponse

# Create your views here.
"""
def cred_WooCommerce(request):
    for datos in Contribuyente.objects.filter(correo= 'karla.vanessa@outlook.es'):
        cred1=datos.consumer_key
        cred2=datos.consumer_secret
    print (cred1,"\n",cred2)
    return HttpResponse(cred1)
"""

