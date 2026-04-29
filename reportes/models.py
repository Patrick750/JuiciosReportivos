from django.db import models

# Abstract base classes
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Core models
class Formacion(models.Model):
    ficha = models.CharField(max_length=255, blank=True, null=True)
    codigo = models.CharField(max_length=255, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    denominacion = models.CharField(max_length=255, blank=True, null=True)
    estado_ficha = models.CharField(max_length=255, blank=True, null=True)
    fecha_inicio = models.TimeField(blank=True, null=True)
    fecha_fin = models.TimeField(blank=True, null=True)
    modalidad = models.CharField(max_length=255, blank=True, null=True)
    id_centro_formacion = models.ForeignKey('CentroFormacion', on_delete=models.PROTECT, related_name='formaciones', blank=True, null=True)

    def __str__(self):
        return f"{self.denominacion} ({self.codigo})"

class Regional(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre or "Regional"

class CentroFormacion(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    regional = models.ForeignKey(Regional, on_delete=models.PROTECT, related_name='centros')


    def __str__(self):
        return self.nombre or "CentroFormacion"

class Usuario(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ("DNI", "DNI"),
        ("PAS", "Pasaporte"),
    ]
    tipo_documento = models.CharField(max_length=255, blank=True, null=True, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    apellidos = models.CharField(max_length=255, blank=True, null=True)
    formacion = models.ForeignKey(Formacion, on_delete=models.PROTECT, related_name='usuarios', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}".strip()

class Aprendiz(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='aprendiz')
    estado = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.usuario)

class Instructor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='instructor')

    def __str__(self):
        return str(self.usuario)

class Competencia(models.Model):
    competencia = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.competencia or "Competencia"

class Resultado(models.Model):
    competencia = models.ForeignKey(Competencia, on_delete=models.PROTECT, related_name='resultados')

    def __str__(self):
        return f"Resultado de {self.competencia}"

class AsignacionCompetencia(models.Model):
    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE, related_name='asignaciones')
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, related_name='asignaciones')

    def __str__(self):
        return f"{self.aprendiz} - {self.competencia}"

class JuicioEvaluativo(models.Model):
    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE, related_name='juicios')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='juicios')
    resultado = models.ForeignKey(Resultado, on_delete=models.CASCADE, related_name='juicios')
    fecha_hora = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Juicio {self.id}"
