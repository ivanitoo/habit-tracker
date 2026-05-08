from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import FormularioRegistro


def registro(request):
    if request.user.is_authenticated:
        return redirect("panel")
    if request.method == "POST":
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("panel")
    else:
        form = FormularioRegistro()
    return render(request, "accounts/registro.html", {"form": form})
