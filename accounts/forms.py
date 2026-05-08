from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class FormularioLogin(AuthenticationForm):
    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos",
        "inactive": "Esta cuenta está inactiva.",
    }


class FormularioRegistro(UserCreationForm):
    email = forms.EmailField(
        max_length=254, required=True, label="Correo electrónico"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password1"].help_text = (
            "Mínimo 8 caracteres. No puede ser solo números."
        )
        self.fields["password2"].help_text = (
            "Repite la contraseña para confirmar."
        )
