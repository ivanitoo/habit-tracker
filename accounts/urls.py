from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path(
        "iniciar-sesion/",
        auth_views.LoginView.as_view(
            template_name="accounts/iniciar_sesion.html",
            redirect_authenticated_user=True,
        ),
        name="iniciar_sesion",
    ),
    path("cerrar-sesion/", auth_views.LogoutView.as_view(), name="cerrar_sesion"),
]
