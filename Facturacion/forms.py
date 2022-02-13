
from django import forms
from Facturacion.models import Consumidor

class FormularioConsumidor(forms.ModelForm):
    class Meta:
        model = Consumidor
        fields = '__all__'