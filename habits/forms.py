from django import forms
from .models import Habito


class FormularioHabito(forms.ModelForm):
    class Meta:
        model = Habito
        fields = ["nombre", "descripcion", "frecuencia", "color"]
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "frecuencia": "Frecuencia",
            "color": "Color",
        }
