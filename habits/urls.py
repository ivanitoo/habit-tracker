from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("panel/", views.panel, name="panel"),
    path("habitos/", views.lista_habitos, name="lista_habitos"),
    path("habitos/nuevo/", views.crear_habito, name="crear_habito"),
    path("habitos/<int:pk>/editar/", views.editar_habito, name="editar_habito"),
    path(
        "habitos/<int:pk>/eliminar/",
        views.eliminar_habito,
        name="eliminar_habito",
    ),
    path("alternar-registro/", views.alternar_registro, name="alternar_registro"),
    path("datos-estadisticas/", views.datos_estadisticas, name="datos_estadisticas"),
]
