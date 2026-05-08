from django.contrib import admin
from .models import Habito, RegistroHabito


@admin.register(Habito)
class HabitoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "usuario", "frecuencia", "creado"]
    list_filter = ["frecuencia", "creado"]
    search_fields = ["nombre", "usuario__username"]


@admin.register(RegistroHabito)
class RegistroHabitoAdmin(admin.ModelAdmin):
    list_display = ["habito", "fecha", "creado"]
    list_filter = ["fecha"]
