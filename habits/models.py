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
    dias_semana = models.CharField(
        max_length=20, blank=True, default="", verbose_name="Días de la semana"
    )
    color = models.CharField(max_length=7, default="#6366f1", verbose_name="Color")
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Hábito"
        verbose_name_plural = "Hábitos"

    def __str__(self):
        return self.nombre

    def get_dias_semana_list(self):
        if not self.dias_semana:
            return []
        return [int(d) for d in self.dias_semana.split(",") if d]

    def es_dia_activo(self, dia):
        return dia in self.get_dias_semana_list()

    def proximo_dia_activo(self, desde=None):
        dias = self.get_dias_semana_list()
        if not dias:
            return None
        if desde is None:
            desde = timezone.localdate()
        for i in range(8):
            d = desde + timezone.timedelta(days=i)
            if d.weekday() in dias:
                return d
        return None

    def racha_actual(self):
        if self.frecuencia == self.SEMANAL and self.dias_semana:
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

        dias_activos = self.get_dias_semana_list()
        if not dias_activos:
            return 0

        hoy = timezone.localdate()
        dia = hoy
        racha = 0

        for _ in range(365):
            if dia.weekday() in dias_activos:
                if dia in registros:
                    racha += 1
                else:
                    break
            dia -= timezone.timedelta(days=1)
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
