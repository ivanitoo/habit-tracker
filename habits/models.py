from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Habito(models.Model):
    DIARIO = "daily"
    SEMANAL = "weekly"

    FRECUENCIAS = [
        (DIARIO, "Diario"),
        (SEMANAL, "Semanal"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habitos")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    frecuencia = models.CharField(
        max_length=10, choices=FRECUENCIAS, default=DIARIO, verbose_name="Frecuencia"
    )
    color = models.CharField(max_length=7, default="#6366f1", verbose_name="Color")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Hábito"
        verbose_name_plural = "Hábitos"

    def __str__(self):
        return self.nombre

    def racha_actual(self):
        registros = (
            self.registros.order_by("-fecha")
            .values_list("fecha", flat=True)
            .distinct()
        )
        if not registros:
            return 0

        hoy = timezone.localdate()
        racha = 0
        dia = hoy

        for fecha in registros:
            if fecha == dia:
                racha += 1
                dia -= timezone.timedelta(days=1)
            elif fecha < dia and racha == 0:
                return 0
            else:
                break
        return racha

    def total_completados(self):
        return self.registros.count()

    def tasa_30d(self):
        hoy = timezone.localdate()
        hace_30 = hoy - timezone.timedelta(days=30)
        total = self.registros.filter(fecha__gte=hace_30).count()
        return round((total / 30) * 100, 1)


class RegistroHabito(models.Model):
    habito = models.ForeignKey(
        Habito, on_delete=models.CASCADE, related_name="registros"
    )
    fecha = models.DateField(verbose_name="Fecha")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["habito", "fecha"]
        ordering = ["-fecha"]
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

    def __str__(self):
        return f"{self.habito.nombre} - {self.fecha}"
