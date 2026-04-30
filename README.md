# JuiciosReportivos

Sistema integral de gestión y visualización de **Juicios Evaluativos** para el seguimiento académico de aprendices. El proyecto permite procesar reportes masivos de Excel, gestionar fases de proyectos formativos y visualizar el avance mediante dashboards interactivos.

## 🚀 Tecnologías

### Backend
- **Django 6.0.2**: Framework principal.
- **Django REST Framework**: Para la construcción de la API.
- **Pandas & Openpyxl**: Procesamiento eficiente de archivos Excel.
- **SQLite**: Base de datos predeterminada (fácil de portar a PostgreSQL).
- **SimpleJWT**: Autenticación segura mediante tokens.

### Frontend
- **Vue.js 3**: Framework reactivo para la interfaz.
- **Vite**: Herramienta de construcción ultra rápida.
- **Chart.js**: Visualización de datos y métricas.
- **Axios**: Comunicación fluida con la API.

---

## ✨ Características Principales

1.  **Carga Masiva**: Importación de reportes de Juicios Evaluativos directamente desde archivos `.xlsx` generados por SofíaPlus.
2.  **Dashboard de Avance**: Gráficos interactivos que muestran el porcentaje de aprobación por competencia y resultado de aprendizaje.
3.  **Seguimiento por Fases**: Organización del proyecto formativo en fases (Análisis, Planeación, Ejecución, Evaluación) con sus respectivas actividades.
4.  **Filtros Avanzados**: Búsqueda por ficha, aprendiz, regional o centro de formación.
5.  **Gestión Institucional**: Catálogos de Regionales y Centros de Formación.

---

## 📂 Estructura del Proyecto

```bash
JuiciosReportivos/
├── autenticacion/     # Gestión de usuarios y permisos
├── reportes/          # Lógica de negocio, modelos y API de juicios
├── frontend/          # Proyecto Vue.js 3 + Vite
├── db.sqlite3         # Base de datos local
├── manage.py          # Script de gestión de Django
└── requirements.txt   # Dependencias de Python
```

---

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd JuiciosReportivos
```

### 2. Configurar el Backend
```bash
# Crear entorno virtual
python -m venv venv
source venv/Scripts/activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

### 3. Configurar el Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

---

## 📌 Sistema de Versionado

El proyecto sigue el estándar de versionado semántico bajo el siguiente formato:

> Formato: `MAYOR.MENOR.PARCHE` (`high.low.patch`)
>
> - **MAYOR** — cambio funcional significativo o rediseño arquitectónico.
> - **MENOR** — nueva funcionalidad añadida.
> - **PARCHE** — correcciones, ajustes menores o refactorizaciones.

### Historial de Versiones

| Versión | Tipo | Descripción |
| :--- | :--- | :--- |
| **1.2.0** | MENOR | Implementación de Dashboard de Fases y gestión de Proyecto Formativo. |
| **1.1.0** | MENOR | Módulo de importación masiva de Excel y procesamiento de metadatos de ficha. |
| **1.0.1** | PARCHE | Corrección de errores de codificación (UTF-8) en nombres de competencias. |
| **1.0.0** | MAYOR | Versión inicial: Estructura base, modelos de Aprendiz y Juicios, y Dashboard general. |

---

## 📄 Licencia
Este proyecto es de uso institucional. Todos los derechos reservados.
