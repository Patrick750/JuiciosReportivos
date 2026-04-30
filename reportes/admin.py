from django.contrib import admin
from .models import (
    Regional, CentroFormacion, Ficha,
    Aprendiz, JuicioEvaluativo,
    FaseProyecto, Actividad,
)


@admin.register(Regional)
class RegionalAdmin(admin.ModelAdmin):
    list_display = ["nombre", "creado_en"]
    search_fields = ["nombre"]


@admin.register(CentroFormacion)
class CentroFormacionAdmin(admin.ModelAdmin):
    list_display = ["nombre", "regional", "creado_en"]
    list_filter = ["regional"]
    search_fields = ["nombre"]


@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display = [
        "ficha_caracterizacion", "denominacion", "codigo",
        "estado_ficha", "fecha_reporte", "centro_formacion",
    ]
    list_filter = ["estado_ficha", "modalidad", "centro_formacion"]
    search_fields = ["ficha_caracterizacion", "denominacion", "codigo"]


@admin.register(Aprendiz)
class AprendizAdmin(admin.ModelAdmin):
    list_display = ["nombre", "apellidos", "numero_documento", "tipo_documento", "estado"]
    list_filter = ["estado", "tipo_documento"]
    search_fields = ["nombre", "apellidos", "numero_documento"]


@admin.register(JuicioEvaluativo)
class JuicioEvaluativoAdmin(admin.ModelAdmin):
    list_display = [
        "aprendiz", "ficha", "competencia",
        "juicio_evaluacion", "fecha_hora_juicio", "funcionario",
    ]
    list_filter = ["juicio_evaluacion", "ficha"]
    search_fields = [
        "aprendiz__nombre", "aprendiz__apellidos",
        "competencia", "resultado_aprendizaje",
    ]


@admin.register(FaseProyecto)
class FaseProyectoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "orden", "ficha"]
    list_filter = ["ficha"]
    search_fields = ["nombre"]


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ["nombre", "fase"]
    list_filter = ["fase__ficha"]
    search_fields = ["nombre"]
