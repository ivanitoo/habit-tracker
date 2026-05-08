from django import forms
from .models import Habito


class FormularioHabito(forms.ModelForm):
    dias_semana = forms.MultipleChoiceField(
        choices=Habito.DIAS_SEMANA_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "dias-semana-checkboxes"}),
        required=False,
        label="Días de la semana",
    )

    class Meta:
        model = Habito
        fields = ["nombre", "descripcion", "frecuencia", "dias_semana", "color"]
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.dias_semana:
            self.initial["dias_semana"] = [
                str(d) for d in self.instance.get_dias_semana_list()
            ]

    def clean_dias_semana(self):
        data = self.cleaned_data["dias_semana"]
        if not data:
            return ""
        return ",".join(data)