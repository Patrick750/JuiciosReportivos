from rest_framework import serializers
from .models import (
    Regional, CentroFormacion, Ficha,
    Aprendiz, JuicioEvaluativo,
    FaseProyecto, Actividad,
)


# ---------------------------------------------------------------------------
# Base serializers
# ---------------------------------------------------------------------------

class RegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regional
        fields = ["id", "nombre"]


class CentroFormacionSerializer(serializers.ModelSerializer):
    regional = RegionalSerializer(read_only=True)

    class Meta:
        model = CentroFormacion
        fields = ["id", "nombre", "regional"]


class FichaSerializer(serializers.ModelSerializer):
    regional = RegionalSerializer(read_only=True)
    centro_formacion = CentroFormacionSerializer(read_only=True)

    class Meta:
        model = Ficha
        fields = [
            "id", "fecha_reporte", "ficha_caracterizacion", "codigo",
            "version", "denominacion", "estado_ficha",
            "fecha_inicio", "fecha_fin", "modalidad",
            "regional", "centro_formacion", "creado_en",
        ]


class AprendizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aprendiz
        fields = [
            "id", "tipo_documento", "numero_documento",
            "nombre", "apellidos", "estado",
        ]


class JuicioEvaluativoSerializer(serializers.ModelSerializer):
    aprendiz = AprendizSerializer(read_only=True)

    class Meta:
        model = JuicioEvaluativo
        fields = [
            "id", "ficha", "aprendiz", "competencia",
            "resultado_aprendizaje", "juicio_evaluacion",
            "fecha_hora_juicio", "funcionario", "creado_en",
        ]


# ---------------------------------------------------------------------------
# Importación
# ---------------------------------------------------------------------------

class ImportarReporteSerializer(serializers.Serializer):
    archivo = serializers.FileField()

    def validate_archivo(self, value):
        nombre = value.name.lower()
        if not (nombre.endswith(".xls") or nombre.endswith(".xlsx")):
            raise serializers.ValidationError(
                "Solo se aceptan archivos en formato .xls o .xlsx."
            )
        return value


# ---------------------------------------------------------------------------
# Proyecto Formativo
# ---------------------------------------------------------------------------

class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = [
            "id", "fase", "nombre", "descripcion",
            "competencias", "resultados",
        ]


class ActividadDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = ["id", "nombre", "descripcion", "competencias", "resultados"]


class FaseProyectoSerializer(serializers.ModelSerializer):
    actividades = ActividadDetalleSerializer(many=True, read_only=True)

    class Meta:
        model = FaseProyecto
        fields = ["id", "ficha", "nombre", "descripcion", "orden", "actividades"]


# ---------------------------------------------------------------------------
# Dashboard KPIs
# ---------------------------------------------------------------------------

class KpiAprendizSerializer(serializers.Serializer):
    """Resumen de juicios de un aprendiz."""
    aprendiz_id = serializers.IntegerField()
    nombre = serializers.CharField()
    apellidos = serializers.CharField()
    numero_documento = serializers.CharField()
    estado = serializers.CharField()
    total_juicios = serializers.IntegerField()
    aprobados = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    porcentaje_avance = serializers.FloatField()


class AvanceCompetenciaSerializer(serializers.Serializer):
    competencia = serializers.CharField()
    total = serializers.IntegerField()
    aprobados = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    porcentaje = serializers.FloatField()


class AvanceResultadoSerializer(serializers.Serializer):
    resultado = serializers.CharField()
    total = serializers.IntegerField()
    aprobados = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    porcentaje = serializers.FloatField()


class AvanceAprendizSerializer(serializers.Serializer):
    aprendiz = AprendizSerializer()
    por_competencia = AvanceCompetenciaSerializer(many=True)
    por_resultado = AvanceResultadoSerializer(many=True)
    resumen = serializers.DictField()


class DashboardFasesSerializer(serializers.Serializer):
    fase_id = serializers.IntegerField()
    fase_nombre = serializers.CharField()
    orden = serializers.IntegerField()
    total_juicios = serializers.IntegerField()
    aprobados = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    porcentaje_cumplimiento = serializers.FloatField()
    aprendices_aprobados = serializers.IntegerField()
    aprendices_pendientes = serializers.IntegerField()
