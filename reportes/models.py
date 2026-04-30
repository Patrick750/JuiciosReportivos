from django.db import models


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class TimestampMixin(models.Model):
    """Agrega campos de auditoría a cualquier modelo que lo herede."""
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Catálogos geográficos / institucionales
# ---------------------------------------------------------------------------

class Regional(TimestampMixin):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Regional"
        verbose_name_plural = "Regionales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class CentroFormacion(TimestampMixin):
    nombre = models.CharField(max_length=255)
    regional = models.ForeignKey(
        Regional,
        on_delete=models.PROTECT,
        related_name="centros_formacion",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Centro de Formación"
        verbose_name_plural = "Centros de Formación"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ---------------------------------------------------------------------------
# Ficha de caracterización  (metadatos del Excel, filas 0-10)
# ---------------------------------------------------------------------------

class Ficha(TimestampMixin):
    """Almacena los metadatos extraídos de la cabecera del reporte XLS."""

    fecha_reporte = models.DateField(null=True, blank=True)
    ficha_caracterizacion = models.CharField(max_length=255, blank=True, null=True)
    codigo = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=100, blank=True, null=True)
    denominacion = models.TextField(blank=True, null=True)
    estado_ficha = models.CharField(max_length=255, blank=True, null=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    modalidad = models.CharField(max_length=255, blank=True, null=True)
    regional = models.ForeignKey(
        Regional,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="fichas",
    )
    centro_formacion = models.ForeignKey(
        CentroFormacion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="fichas",
    )

    class Meta:
        verbose_name = "Ficha de Caracterización"
        verbose_name_plural = "Fichas de Caracterización"
        ordering = ["-fecha_reporte"]

    def __str__(self):
        return f"Ficha {self.ficha_caracterizacion} – {self.denominacion}"


# ---------------------------------------------------------------------------
# Aprendiz  (documento como identificador natural)
# ---------------------------------------------------------------------------

class Aprendiz(TimestampMixin):
    """Un aprendiz se identifica de forma única por su número de documento."""

    tipo_documento = models.CharField(max_length=50, blank=True, null=True)
    numero_documento = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    apellidos = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Aprendiz"
        verbose_name_plural = "Aprendices"
        ordering = ["apellidos", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.numero_documento})"


# ---------------------------------------------------------------------------
# Juicio Evaluativo  (fila de datos del Excel)
# ---------------------------------------------------------------------------

class JuicioEvaluativo(TimestampMixin):
    """Registra cada línea del reporte de juicios evaluativos."""

    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.CASCADE,
        related_name="juicios",
    )
    aprendiz = models.ForeignKey(
        Aprendiz,
        on_delete=models.PROTECT,
        related_name="juicios",
    )
    competencia = models.TextField(blank=True, null=True)
    resultado_aprendizaje = models.TextField(blank=True, null=True)
    juicio_evaluacion = models.CharField(max_length=100, blank=True, null=True)
    fecha_hora_juicio = models.DateTimeField(null=True, blank=True)
    funcionario = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Juicio Evaluativo"
        verbose_name_plural = "Juicios Evaluativos"
        ordering = ["-fecha_hora_juicio"]

    def __str__(self):
        return f"Juicio #{self.pk} – {self.aprendiz} – {self.juicio_evaluacion}"

    @property
    def aprobado(self):
        return (self.juicio_evaluacion or "").strip().lower() == "aprobado"


# ---------------------------------------------------------------------------
# Proyecto Formativo – Fases y Actividades
# ---------------------------------------------------------------------------

class FaseProyecto(TimestampMixin):
    """Fase del proyecto formativo asociada a una ficha."""

    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.CASCADE,
        related_name="fases",
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "Fase del Proyecto"
        verbose_name_plural = "Fases del Proyecto"
        ordering = ["ficha", "orden"]
        unique_together = [("ficha", "orden")]

    def __str__(self):
        return f"Fase {self.orden}: {self.nombre}"


class Actividad(TimestampMixin):
    """Actividad dentro de una fase; vincula competencias y resultados."""

    fase = models.ForeignKey(
        FaseProyecto,
        on_delete=models.CASCADE,
        related_name="actividades",
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    # Textos libres que mapean con las columnas del Excel
    competencias = models.JSONField(
        default=list,
        help_text="Lista de textos de competencias relacionadas",
    )
    resultados = models.JSONField(
        default=list,
        help_text="Lista de textos de resultados de aprendizaje relacionados",
    )

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ["fase", "nombre"]

    def __str__(self):
        return f"{self.fase} → {self.nombre}"
