from django import forms
from .models import Habito


class FormularioHabito(forms.ModelForm):
    class Meta:
        model = Habito
        fields = ["nombre", "descripcion", "frecuencia", "dia_semana", "color"]
        widgets = {
            "color": forms.TextInput(attrs={"type": "color"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "dia_semana": forms.Select(choices=[("", "Selecciona un día")] + Habito.DIAS_SEMANA_CHOICES),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "frecuencia": "Frecuencia",
            "dia_semana": "Día de la semana",
            "color": "Color",
        }
