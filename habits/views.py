import calendar
import os
from datetime import date, timedelta

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count

from .models import Habito, RegistroHabito
from .forms import FormularioHabito


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
DIAS_SEMANA = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def inicio(request):
    if request.user.is_authenticated:
        return redirect("panel")
    return render(request, "home.html")


@login_required
def panel(request):
    habitos = (
        Habito.objects.filter(usuario=request.user)
        .annotate(total_registros=Count("registros"))
        .order_by("-creado")
    )

    hoy = timezone.localdate()
    hace_30 = hoy - timedelta(days=30)

    stats = {
        "total_habitos": habitos.count(),
        "total_completados": RegistroHabito.objects.filter(
            habito__usuario=request.user, fecha__gte=hace_30
        ).count(),
        "mejor_racha": 0,
        "hechos_hoy": 0,
    }

    heatmap_data = {}
    for h in habitos:
        registros = set(
            h.registros.filter(fecha__gte=hoy - timedelta(days=364)).values_list(
                "fecha", flat=True
            )
        )
        heatmap_data[h.id] = {
            "nombre": h.nombre,
            "color": h.color,
            "registros": {str(d): True for d in registros},
        }
        stats["mejor_racha"] = max(stats["mejor_racha"], h.racha_actual())
        if hoy in registros:
            stats["hechos_hoy"] += 1

    selected_year = int(request.GET.get("ano", hoy.year))
    selected_month = int(request.GET.get("mes", hoy.month))
    _, num_days = calendar.monthrange(selected_year, selected_month)

    calendario_dias = []
    for day in range(1, num_days + 1):
        d = date(selected_year, selected_month, day)
        dia_info = {
            "fecha": d,
            "fecha_str": str(d),
            "num": d.day,
            "dia_semana": DIAS_SEMANA[d.weekday()],
            "habitos": {},
        }
        for h in habitos:
            dia_info["habitos"][h.id] = str(d) in heatmap_data[h.id]["registros"]
        calendario_dias.append(dia_info)

    meses_disponibles = []
    for m in range(1, 13):
        meses_disponibles.append({
            "numero": m,
            "nombre": MESES[m - 1],
            "actual": m == selected_month,
        })

    today_str = str(hoy)
    checked_hoy = {}
    total_mes = {}
    completados_mes = {}
    for h in habitos:
        checked_hoy[h.id] = today_str in heatmap_data[h.id]["registros"]
        completados = sum(
            1 for d in calendario_dias
            if d["habitos"].get(h.id)
        )
        completados_mes[h.id] = completados
        total_mes[h.id] = num_days

    ctx = {
        "habitos": habitos,
        "stats": stats,
        "heatmap_data": heatmap_data,
        "calendario_dias": calendario_dias,
        "dias_semana": DIAS_SEMANA,
        "hoy": hoy,
        "today_str": today_str,
        "checked_hoy": checked_hoy,
        "primer_habito_id": habitos.first().id if habitos else None,
        "selected_month": selected_month,
        "selected_year": selected_year,
        "meses_disponibles": meses_disponibles,
        "mes_actual": MESES[selected_month - 1],
        "completados_mes": completados_mes,
        "total_mes": total_mes,
        "num_days": num_days,
    }
    return render(request, "habits/panel.html", ctx)


@login_required
def lista_habitos(request):
    habitos = Habito.objects.filter(usuario=request.user).annotate(
        total=Count("registros")
    )
    return render(request, "habits/lista.html", {"habitos": habitos})


@login_required
def crear_habito(request):
    if request.method == "POST":
        form = FormularioHabito(request.POST)
        if form.is_valid():
            h = form.save(commit=False)
            h.usuario = request.user
            h.save()
            return redirect("panel")
    else:
        form = FormularioHabito()
    return render(
        request, "habits/formulario.html", {"form": form, "titulo": "Nuevo Hábito"}
    )


@login_required
def editar_habito(request, pk):
    h = get_object_or_404(Habito, pk=pk, usuario=request.user)
    if request.method == "POST":
        form = FormularioHabito(request.POST, instance=h)
        if form.is_valid():
            form.save()
            return redirect("panel")
    else:
        form = FormularioHabito(instance=h)
    return render(
        request,
        "habits/formulario.html",
        {"form": form, "titulo": "Editar Hábito"},
    )


@login_required
def eliminar_habito(request, pk):
    h = get_object_or_404(Habito, pk=pk, usuario=request.user)
    if request.method == "POST":
        h.delete()
        return redirect("panel")
    return render(
        request, "habits/confirmar_eliminar.html", {"habito": h}
    )


@login_required
def alternar_registro(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    habito_id = request.POST.get("habito_id")
    fecha = request.POST.get("fecha", str(timezone.localdate()))

    h = get_object_or_404(Habito, pk=habito_id, usuario=request.user)
    registro, creado = RegistroHabito.objects.get_or_create(
        habito=h, fecha=fecha
    )

    if not creado:
        registro.delete()
        return JsonResponse({"status": "unchecked"})

    return JsonResponse({"status": "checked"})


@login_required
def datos_estadisticas(request):
    habito_id = request.GET.get("habito_id")
    if not habito_id:
        return JsonResponse({"error": "habito_id required"}, status=400)

    h = get_object_or_404(Habito, pk=habito_id, usuario=request.user)
    hoy = timezone.localdate()

    registros = set(
        h.registros.filter(fecha__gte=hoy - timedelta(days=364)).values_list(
            "fecha", flat=True
        )
    )

    labels = []
    data = []
    for i in range(89, -1, -1):
        d = hoy - timedelta(days=i)
        labels.append(d.strftime("%b %d"))
        data.append(1 if d in registros else 0)

    return JsonResponse(
        {"labels": labels, "data": data, "racha": h.racha_actual()}
    )


def setup_admin(request):
    token = request.GET.get("token", "")
    expected = os.environ.get("SETUP_TOKEN", "")
    if not expected or token != expected:
        return HttpResponse("Token inválido", status=403)
    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse("El admin ya existe")
    User.objects.create_superuser("admin", "ivanvenegasvallejo@gmail.com", "admin123")
    return HttpResponse("Admin creado: usuario=admin, clave=admin123")
