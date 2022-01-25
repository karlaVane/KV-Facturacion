from dataclasses import fields
from pydoc import classname
from django import forms
from Facturacion.models import Consumidor

class FormularioConsumidor(forms.ModelForm):
    class Meta:
        model = Consumidor
        fields = '__all__'