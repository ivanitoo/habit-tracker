from django.urls import path
from django.contrib.auth import views as auth_views
from django_ratelimit.decorators import ratelimit
from . import views
from .forms import FormularioLogin

login_view = ratelimit(key="ip", rate="5/m", method="POST", block=True)(
    auth_views.LoginView.as_view(
        template_name="accounts/iniciar_sesion.html",
        redirect_authenticated_user=True,
        authentication_form=FormularioLogin,
    )
)

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("iniciar-sesion/", login_view, name="iniciar_sesion"),
    path("cerrar-sesion/", auth_views.LogoutView.as_view(), name="cerrar_sesion"),
]
