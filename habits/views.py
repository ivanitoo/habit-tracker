import json
import os
from datetime import date, timedelta
from collections import defaultdict

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count

from .models import Habito, RegistroHabito
from .forms import FormularioHabito


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

    heatmap_semanas = []
    inicio_heatmap = hoy - timedelta(days=364)
    semana = []
    for i in range(365):
        d = inicio_heatmap + timedelta(days=i)
        semana.append(d)
        if d.weekday() == 6 or i == 364:
            heatmap_semanas.append(semana)
            semana = []

    calendario_dias = []
    dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    for i in range(29, -1, -1):
        d = hoy - timedelta(days=i)
        dia_info = {
            "fecha": d,
            "fecha_str": str(d),
            "num": d.day,
            "dia_semana": dias_semana[d.weekday()],
            "mes": d.strftime("%b"),
            "habitos": {},
        }
        for h in habitos:
            dia_info["habitos"][h.id] = (
                str(d) in heatmap_data[h.id]["registros"]
            )
        calendario_dias.append(dia_info)

    today_str = str(hoy)
    checked_hoy = {}
    for h in habitos:
        checked_hoy[h.id] = today_str in heatmap_data[h.id]["registros"]

    ctx = {
        "habitos": habitos,
        "stats": stats,
        "heatmap_data": heatmap_data,
        "heatmap_semanas": heatmap_semanas,
        "calendario_dias": calendario_dias,
        "dias_semana": dias_semana,
        "hoy": hoy,
        "today_str": today_str,
        "checked_hoy": checked_hoy,
        "primer_habito_id": habitos.first().id if habitos else None,
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
