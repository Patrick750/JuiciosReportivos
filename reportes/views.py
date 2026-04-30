import io

import pandas as pd
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Actividad, Aprendiz, CentroFormacion,
    Ficha, FaseProyecto, JuicioEvaluativo, Regional,
)
from .serializers import (
    ActividadSerializer,
    AprendizSerializer,
    AvanceAprendizSerializer,
    DashboardFasesSerializer,
    FichaSerializer,
    FaseProyectoSerializer,
    ImportarReporteSerializer,
    JuicioEvaluativoSerializer,
)


# ---------------------------------------------------------------------------
# Helpers de importación
# ---------------------------------------------------------------------------

def _clean(value) -> str:
    if value is None:
        return ""
    texto = str(value).strip()
    return "" if texto.lower() in ("nan", "-", "none") else texto


def _parse_fecha(value):
    if not value:
        return None
    try:
        result = pd.to_datetime(str(value), dayfirst=True, errors="coerce")
        return None if pd.isna(result) else result.date()
    except Exception:
        return None


def _parse_datetime(value):
    if not value:
        return None
    try:
        result = pd.to_datetime(str(value), dayfirst=True, errors="coerce")
        return None if pd.isna(result) else result
    except Exception:
        return None


METADATA_MAP = {
    "Fecha del Reporte:": "fecha_reporte",
    "Ficha de Caracterización:": "ficha_caracterizacion",
    "Cógigo:": "codigo",
    "Versión:": "version",
    "Denominación:": "denominacion",
    "Estado de la Ficha de Caracterización:": "estado_ficha",
    "Fecha Inicio:": "fecha_inicio",
    "Fecha Fin:": "fecha_fin",
    "Modalidad de Formación:": "modalidad",
    "Regional:": "regional",
    "Centro de Formación:": "centro_formacion",
}

COLUMNAS_ESPERADAS = [
    "Tipo de Documento",
    "Número de Documento",
    "Nombre",
    "Apellidos",
    "Estado",
    "Competencia",
    "Resultado de Aprendizaje",
    "Juicio de Evaluación",
    "Fecha y Hora del Juicio Evaluativo",
    "Funcionario que registro el juicio evaluativo",
]


def _extraer_metadatos(archivo_bytes: bytes) -> dict:
    df_meta = pd.read_excel(
        io.BytesIO(archivo_bytes), header=None, nrows=11
    )
    meta = {}
    for _, fila in df_meta.iterrows():
        etiqueta = _clean(fila.iloc[0])
        valor = _clean(fila.iloc[2]) if len(fila) > 2 else ""
        if etiqueta in METADATA_MAP:
            meta[METADATA_MAP[etiqueta]] = valor
    return meta


def _get_or_create_ficha(meta: dict) -> Ficha:
    regional = None
    if meta.get("regional"):
        regional, _ = Regional.objects.get_or_create(nombre=meta["regional"])

    centro = None
    if meta.get("centro_formacion"):
        centro, _ = CentroFormacion.objects.get_or_create(
            nombre=meta["centro_formacion"],
            defaults={"regional": regional},
        )

    ficha, _ = Ficha.objects.get_or_create(
        ficha_caracterizacion=meta.get("ficha_caracterizacion", ""),
        codigo=meta.get("codigo", ""),
        defaults={
            "fecha_reporte": _parse_fecha(meta.get("fecha_reporte")),
            "version": meta.get("version", ""),
            "denominacion": meta.get("denominacion", ""),
            "estado_ficha": meta.get("estado_ficha", ""),
            "fecha_inicio": _parse_fecha(meta.get("fecha_inicio")),
            "fecha_fin": _parse_fecha(meta.get("fecha_fin")),
            "modalidad": meta.get("modalidad", ""),
            "regional": regional,
            "centro_formacion": centro,
        },
    )
    return ficha


def _calcular_avance(juicios_qs):
    """Retorna dict con avance por competencia y por resultado."""
    por_competencia = {}
    por_resultado = {}

    for j in juicios_qs:
        comp = j.competencia or "Sin competencia"
        res = j.resultado_aprendizaje or "Sin resultado"
        aprobado = (j.juicio_evaluacion or "").strip().lower() == "aprobado"

        if comp not in por_competencia:
            por_competencia[comp] = {"total": 0, "aprobados": 0}
        por_competencia[comp]["total"] += 1
        if aprobado:
            por_competencia[comp]["aprobados"] += 1

        if res not in por_resultado:
            por_resultado[res] = {"total": 0, "aprobados": 0}
        por_resultado[res]["total"] += 1
        if aprobado:
            por_resultado[res]["aprobados"] += 1

    def _to_list(d):
        result = []
        for key, val in d.items():
            total = val["total"]
            aprobados = val["aprobados"]
            result.append({
                "competencia" if "competencia" in d else "resultado": key,
                "total": total,
                "aprobados": aprobados,
                "pendientes": total - aprobados,
                "porcentaje": round(aprobados / total * 100, 1) if total else 0,
            })
        return result

    comp_list = []
    for key, val in por_competencia.items():
        total = val["total"]
        aprobados = val["aprobados"]
        comp_list.append({
            "competencia": key,
            "total": total,
            "aprobados": aprobados,
            "pendientes": total - aprobados,
            "porcentaje": round(aprobados / total * 100, 1) if total else 0,
        })

    res_list = []
    for key, val in por_resultado.items():
        total = val["total"]
        aprobados = val["aprobados"]
        res_list.append({
            "resultado": key,
            "total": total,
            "aprobados": aprobados,
            "pendientes": total - aprobados,
            "porcentaje": round(aprobados / total * 100, 1) if total else 0,
        })

    return comp_list, res_list


# ---------------------------------------------------------------------------
# Importar Reporte XLS
# ---------------------------------------------------------------------------

class ImportarReporteView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = ImportarReporteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        archivo_bytes = serializer.validated_data["archivo"].read()
        resumen = {"aprendices_nuevos": 0, "juicios_creados": 0, "filas_con_error": []}

        try:
            with transaction.atomic():
                meta = _extraer_metadatos(archivo_bytes)
                ficha = _get_or_create_ficha(meta)

                # 1. Cargar el archivo completo primero para buscar la cabecera
                df_full = pd.read_excel(io.BytesIO(archivo_bytes))
                
                # 2. Buscar la fila que contiene las columnas
                header_row_idx = None
                for idx, row in df_full.iterrows():
                    row_values = [str(v).strip() for v in row.values if v is not None]
                    if "Tipo de Documento" in row_values and "Número de Documento" in row_values:
                        header_row_idx = idx
                        break
                
                if header_row_idx is None:
                    # Si no la encuentra, intentamos con el comportamiento por defecto (fila 11)
                    df = pd.read_excel(io.BytesIO(archivo_bytes), skiprows=11)
                else:
                    # Recargar desde la fila encontrada
                    df = pd.read_excel(io.BytesIO(archivo_bytes), skiprows=header_row_idx + 1)
                    # El read_excel con skiprows usa la siguiente fila como data, 
                    # pero queremos que la fila encontrada sean los nombres de las columnas.
                    df.columns = [str(c).strip() for c in df_full.iloc[header_row_idx]]

                # Limpiar nombres de columnas (quitar espacios, etc)
                df.columns = [str(c).strip() for c in df.columns]

                # Validar columnas
                faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
                if faltantes:
                    return Response(
                        {"error": "Formato inesperado.", "columnas_faltantes": faltantes},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )

                for idx, fila in df.iterrows():
                    numero_doc = _clean(fila.get("Número de Documento", ""))
                    if not numero_doc:
                        continue
                    try:
                        aprendiz, creado = Aprendiz.objects.get_or_create(
                            numero_documento=numero_doc,
                            defaults={
                                "tipo_documento": _clean(fila.get("Tipo de Documento")),
                                "nombre": _clean(fila.get("Nombre")),
                                "apellidos": _clean(fila.get("Apellidos")),
                                "estado": _clean(fila.get("Estado")),
                            },
                        )
                        if creado:
                            resumen["aprendices_nuevos"] += 1

                        JuicioEvaluativo.objects.create(
                            ficha=ficha,
                            aprendiz=aprendiz,
                            competencia=_clean(fila.get("Competencia")),
                            resultado_aprendizaje=_clean(fila.get("Resultado de Aprendizaje")),
                            juicio_evaluacion=_clean(fila.get("Juicio de Evaluación")),
                            fecha_hora_juicio=_parse_datetime(fila.get("Fecha y Hora del Juicio Evaluativo")),
                            funcionario=_clean(fila.get("Funcionario que registro el juicio evaluativo")),
                        )
                        resumen["juicios_creados"] += 1
                    except Exception as exc:
                        resumen["filas_con_error"].append({"fila": int(idx) + 13, "error": str(exc)})

        except Exception as exc:
            return Response(
                {"error": f"Error crítico: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"mensaje": "Archivo importado.", "ficha": FichaSerializer(ficha).data, "resumen": resumen},
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Fichas
# ---------------------------------------------------------------------------

class FichasListView(APIView):
    def get(self, request):
        qs = Ficha.objects.select_related("regional", "centro_formacion").all()
        return Response(FichaSerializer(qs, many=True).data)


# ---------------------------------------------------------------------------
# Aprendices (con filtros avanzados)
# ---------------------------------------------------------------------------

class AprendicesListView(APIView):
    def get(self, request):
        qs = Aprendiz.objects.all()
        q = request.query_params

        if q.get("nombre"):
            qs = qs.filter(
                Q(nombre__icontains=q["nombre"]) | Q(apellidos__icontains=q["nombre"])
            )
        if q.get("documento"):
            qs = qs.filter(numero_documento__icontains=q["documento"])
        if q.get("estado"):
            qs = qs.filter(estado__iexact=q["estado"])
        if q.get("ficha"):
            qs = qs.filter(juicios__ficha_id=q["ficha"]).distinct()
        if q.get("competencia"):
            qs = qs.filter(juicios__competencia__icontains=q["competencia"]).distinct()
        if q.get("resultado"):
            qs = qs.filter(juicios__resultado_aprendizaje__icontains=q["resultado"]).distinct()

        return Response(AprendizSerializer(qs, many=True).data)


# ---------------------------------------------------------------------------
# Avance por Aprendiz
# ---------------------------------------------------------------------------

class AvanceAprendizView(APIView):
    def get(self, request, aprendiz_id):
        try:
            aprendiz = Aprendiz.objects.get(pk=aprendiz_id)
        except Aprendiz.DoesNotExist:
            return Response({"error": "Aprendiz no encontrado."}, status=404)

        ficha_id = request.query_params.get("ficha")
        juicios = JuicioEvaluativo.objects.filter(aprendiz=aprendiz)
        if ficha_id:
            juicios = juicios.filter(ficha_id=ficha_id)

        juicios = list(juicios)
        total = len(juicios)
        aprobados = sum(1 for j in juicios if (j.juicio_evaluacion or "").strip().lower() == "aprobado")
        por_competencia, por_resultado = _calcular_avance(juicios)

        data = {
            "aprendiz": AprendizSerializer(aprendiz).data,
            "por_competencia": por_competencia,
            "por_resultado": por_resultado,
            "resumen": {
                "total": total,
                "aprobados": aprobados,
                "pendientes": total - aprobados,
                "porcentaje": round(aprobados / total * 100, 1) if total else 0,
            },
        }
        return Response(data)


# ---------------------------------------------------------------------------
# Dashboard Principal
# ---------------------------------------------------------------------------

class DashboardView(APIView):
    def get(self, request):
        ficha_id = request.query_params.get("ficha")

        juicios_qs = JuicioEvaluativo.objects.select_related("aprendiz", "ficha")
        if ficha_id:
            juicios_qs = juicios_qs.filter(ficha_id=ficha_id)

        juicios = list(juicios_qs)
        total_juicios = len(juicios)
        aprobados_total = sum(1 for j in juicios if (j.juicio_evaluacion or "").strip().lower() == "aprobado")
        pendientes_total = total_juicios - aprobados_total

        # Aprendices únicos
        aprendices_ids = {j.aprendiz_id for j in juicios}
        total_aprendices = len(aprendices_ids)

        # KPI por aprendiz
        aprendiz_map = {}
        for j in juicios:
            aid = j.aprendiz_id
            if aid not in aprendiz_map:
                aprendiz_map[aid] = {
                    "aprendiz_id": aid,
                    "nombre": j.aprendiz.nombre,
                    "apellidos": j.aprendiz.apellidos,
                    "numero_documento": j.aprendiz.numero_documento,
                    "estado": j.aprendiz.estado,
                    "ficha_numero": j.ficha.ficha_caracterizacion,
                    "formacion": j.ficha.denominacion,
                    "total_juicios": 0,
                    "aprobados": 0,
                    "competencias": set(),
                    "resultados": set(),
                }
            aprendiz_map[aid]["total_juicios"] += 1
            if j.competencia:
                aprendiz_map[aid]["competencias"].add(j.competencia)
            if j.resultado_aprendizaje:
                aprendiz_map[aid]["resultados"].add(j.resultado_aprendizaje)
            if (j.juicio_evaluacion or "").strip().lower() == "aprobado":
                aprendiz_map[aid]["aprobados"] += 1

        kpi_aprendices = []
        for v in aprendiz_map.values():
            v["pendientes"] = v["total_juicios"] - v["aprobados"]
            v["porcentaje_avance"] = round(
                v["aprobados"] / v["total_juicios"] * 100, 1
            ) if v["total_juicios"] else 0
            # Convertir sets a listas para JSON
            v["competencias"] = list(v["competencias"])
            v["resultados"] = list(v["resultados"])
            kpi_aprendices.append(v)

        # % aprobación por competencia y resultado
        por_competencia, por_resultado = _calcular_avance(juicios)

        return Response({
            "total_aprendices": total_aprendices,
            "total_juicios": total_juicios,
            "aprobados_total": aprobados_total,
            "pendientes_total": pendientes_total,
            "porcentaje_aprobacion": round(aprobados_total / total_juicios * 100, 1) if total_juicios else 0,
            "kpi_aprendices": kpi_aprendices,
            "por_competencia": por_competencia,
            "por_resultado": por_resultado,
        })


# ---------------------------------------------------------------------------
# Juicios con filtros avanzados
# ---------------------------------------------------------------------------

class JuiciosListView(APIView):
    def get(self, request):
        qs = JuicioEvaluativo.objects.select_related("aprendiz", "ficha").all()
        q = request.query_params

        if q.get("ficha"):
            qs = qs.filter(ficha_id=q["ficha"])
        if q.get("aprendiz"):
            qs = qs.filter(
                Q(aprendiz__nombre__icontains=q["aprendiz"])
                | Q(aprendiz__apellidos__icontains=q["aprendiz"])
            )
        if q.get("documento"):
            qs = qs.filter(aprendiz__numero_documento__icontains=q["documento"])
        if q.get("estado"):
            qs = qs.filter(aprendiz__estado__iexact=q["estado"])
        if q.get("competencia"):
            qs = qs.filter(competencia__icontains=q["competencia"])
        if q.get("resultado"):
            qs = qs.filter(resultado_aprendizaje__icontains=q["resultado"])
        if q.get("juicio"):
            qs = qs.filter(juicio_evaluacion__icontains=q["juicio"])

        return Response(JuicioEvaluativoSerializer(qs, many=True).data)


# ---------------------------------------------------------------------------
# Fases del Proyecto Formativo (CRUD)
# ---------------------------------------------------------------------------

class FaseProyectoViewSet(viewsets.ModelViewSet):
    queryset = FaseProyecto.objects.prefetch_related("actividades").all()
    serializer_class = FaseProyectoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        ficha_id = self.request.query_params.get("ficha")
        if ficha_id:
            qs = qs.filter(ficha_id=ficha_id)
        return qs


class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.select_related("fase").all()
    serializer_class = ActividadSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        fase_id = self.request.query_params.get("fase")
        if fase_id:
            qs = qs.filter(fase_id=fase_id)
        return qs


# ---------------------------------------------------------------------------
# Dashboard de Fases
# ---------------------------------------------------------------------------

class DashboardFasesView(APIView):
    def get(self, request):
        ficha_id = request.query_params.get("ficha")
        if not ficha_id:
            return Response({"error": "Se requiere el parámetro 'ficha'."}, status=400)

        fases = FaseProyecto.objects.prefetch_related("actividades").filter(ficha_id=ficha_id)
        resultado = []

        for fase in fases:
            # Recopilar todas las competencias y resultados de esta fase
            competencias_fase = set()
            resultados_fase = set()
            for act in fase.actividades.all():
                for c in act.competencias:
                    competencias_fase.add(c)
                for r in act.resultados:
                    resultados_fase.add(r)

            # Juicios relacionados a esta fase
            juicios_qs = JuicioEvaluativo.objects.filter(ficha_id=ficha_id)
            if competencias_fase:
                q_comp = Q()
                for c in competencias_fase:
                    q_comp |= Q(competencia__icontains=c)
                juicios_qs = juicios_qs.filter(q_comp)
            else:
                juicios_qs = juicios_qs.none()

            juicios = list(juicios_qs.select_related("aprendiz"))
            total = len(juicios)
            aprobados = sum(1 for j in juicios if (j.juicio_evaluacion or "").strip().lower() == "aprobado")

            # Aprendices aprobados en la fase (todos sus juicios de la fase aprobados)
            aprendiz_juicios = {}
            for j in juicios:
                aid = j.aprendiz_id
                if aid not in aprendiz_juicios:
                    aprendiz_juicios[aid] = {"total": 0, "aprobados": 0}
                aprendiz_juicios[aid]["total"] += 1
                if (j.juicio_evaluacion or "").strip().lower() == "aprobado":
                    aprendiz_juicios[aid]["aprobados"] += 1

            aprendices_aprobados = sum(
                1 for v in aprendiz_juicios.values()
                if v["total"] > 0 and v["aprobados"] == v["total"]
            )
            aprendices_pendientes = len(aprendiz_juicios) - aprendices_aprobados

            resultado.append({
                "fase_id": fase.id,
                "fase_nombre": fase.nombre,
                "orden": fase.orden,
                "total_juicios": total,
                "aprobados": aprobados,
                "pendientes": total - aprobados,
                "porcentaje_cumplimiento": round(aprobados / total * 100, 1) if total else 0,
                "aprendices_aprobados": aprendices_aprobados,
                "aprendices_pendientes": aprendices_pendientes,
            })

        return Response(resultado)
