from django import template
from django.utils import timezone
from ..traducciones import TRADUCCIONES

register = template.Library()

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


@register.filter
def traducir(texto, idioma):
    return TRADUCCIONES.get(idioma, TRADUCCIONES["es"]).get(texto, texto)


@register.filter
def obtener(diccionario, llave):
    return diccionario.get(llave)


@register.filter
def algun_hecho(habitos_dict):
    return any(habitos_dict.values())


EN_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
EN_MESES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

@register.filter
def es_dia_activo(dias_semana, weekday):
    if not dias_semana:
        return True
    return str(weekday) in dias_semana.split(",")


@register.filter
def dias_labels(dias_semana, idioma):
    if not dias_semana:
        return ""
    nums = [int(d) for d in dias_semana.split(",") if d]
    if idioma == "es":
        return ", ".join(DIAS_SEMANA[n] for n in nums)
    return ", ".join(EN_DIAS[n] for n in nums)


@register.filter
def formatear_fecha(fecha, idioma):
    if idioma == "es":
        dia_semana = DIAS_SEMANA[fecha.weekday()]
        mes = MESES[fecha.month - 1]
        return f"{dia_semana}, {fecha.day} de {mes}, {fecha.year}"
    dia_semana = EN_DIAS[fecha.weekday()]
    mes = EN_MESES[fecha.month - 1]
    return f"{dia_semana}, {mes} {fecha.day}, {fecha.year}"
