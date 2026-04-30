from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImportarReporteView,
    FichasListView,
    AprendicesListView,
    AvanceAprendizView,
    DashboardView,
    JuiciosListView,
    FaseProyectoViewSet,
    ActividadViewSet,
    DashboardFasesView,
)

router = DefaultRouter()
router.register(r"fases", FaseProyectoViewSet, basename="fases")
router.register(r"actividades", ActividadViewSet, basename="actividades")

urlpatterns = [
    # Importación
    path("api/reportes/importar/", ImportarReporteView.as_view(), name="importar-reporte"),

    # Consultas
    path("api/reportes/fichas/", FichasListView.as_view(), name="fichas-list"),
    path("api/reportes/aprendices/", AprendicesListView.as_view(), name="aprendices-list"),
    path("api/reportes/juicios/", JuiciosListView.as_view(), name="juicios-list"),
    path("api/reportes/avance/<int:aprendiz_id>/", AvanceAprendizView.as_view(), name="avance-aprendiz"),

    # Dashboards
    path("api/reportes/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("api/reportes/dashboard-fases/", DashboardFasesView.as_view(), name="dashboard-fases"),

    # Proyecto Formativo (CRUD via router)
    path("api/reportes/", include(router.urls)),
]