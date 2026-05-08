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

    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6

    DIAS_SEMANA_CHOICES = [
        (LUNES, "Lunes"),
        (MARTES, "Martes"),
        (MIERCOLES, "Miércoles"),
        (JUEVES, "Jueves"),
        (VIERNES, "Viernes"),
        (SABADO, "Sábado"),
        (DOMINGO, "Domingo"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habitos")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    frecuencia = models.CharField(
        max_length=10, choices=FRECUENCIAS, default=DIARIO, verbose_name="Frecuencia"
    )
    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA_CHOICES, null=True, blank=True, verbose_name="Día de la semana"
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
        if self.frecuencia == self.SEMANAL and self.dia_semana is not None:
            return self._racha_semanal()
        return self._racha_diaria()

    def _racha_diaria(self):
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

    def _racha_semanal(self):
        registros = set(
            self.registros.values_list("fecha", flat=True)
        )
        if not registros:
            return 0

        hoy = timezone.localdate()
        diff = (hoy.weekday() - self.dia_semana) % 7
        ultimo_dia_objetivo = hoy - timezone.timedelta(days=diff)

        if ultimo_dia_objetivo > hoy:
            ultimo_dia_objetivo -= timezone.timedelta(days=7)

        racha = 0
        dia = ultimo_dia_objetivo

        while dia in registros:
            racha += 1
            dia -= timezone.timedelta(days=7)
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
