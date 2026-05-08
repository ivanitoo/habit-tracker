from django import template
from django.utils import timezone
from ..traducciones import TRADUCCIONES

register = template.Library()


@register.filter
def traducir(texto, idioma):
    return TRADUCCIONES.get(idioma, TRADUCCIONES["es"]).get(texto, texto)


@register.filter
def obtener(diccionario, llave):
    return diccionario.get(llave)


@register.filter
def algun_hecho(habitos_dict):
    return any(habitos_dict.values())
