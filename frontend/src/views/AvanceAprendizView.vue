<template>
  <div v-if="loading" class="empty-state">
    <div class="loading-spinner"></div>
  </div>
  <div v-else-if="error" class="alert alert-error">
    {{ error }}
  </div>
  <div v-else>
    <div class="flex-between mb-24">
      <div class="page-title" style="margin:0">
        <RouterLink to="/dashboard" class="btn btn-secondary btn-sm mb-8">← Volver al Dashboard</RouterLink>
        <h1>Avance: {{ data.aprendiz.nombre }} {{ data.aprendiz.apellidos }}</h1>
        <p>Documento: {{ data.aprendiz.numero_documento }} | Estado: {{ data.aprendiz.estado }}</p>
      </div>
    </div>

    <!-- KPIs del Aprendiz -->
    <div class="kpi-grid">
      <KpiCard label="Total Juicios" :value="data.resumen.total" icon="📋" color="var(--accent)" />
      <KpiCard label="Aprobados" :value="data.resumen.aprobados" icon="✅" color="var(--sena-green)" />
      <KpiCard label="Pendientes" :value="data.resumen.pendientes" icon="⏳" color="var(--warning)" />
      <KpiCard
        label="% Avance Total"
        :value="data.resumen.porcentaje + '%'"
        icon="🎯"
        color="var(--sena-green)"
        :progress="data.resumen.porcentaje"
      />
    </div>

    <!-- Gráficas de Avance -->
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Avance por Competencia</div>
        <BarChart
          v-if="competenciaLabels.length"
          :labels="competenciaLabels"
          :datasets="competenciaDatasets"
          :horizontal="true"
        />
        <div v-else class="empty-state">Sin datos de competencias</div>
      </div>
      <div class="card">
        <div class="card-title">Avance por Resultado de Aprendizaje</div>
        <BarChart
          v-if="resultadoLabels.length"
          :labels="resultadoLabels"
          :datasets="resultadoDatasets"
          :horizontal="true"
        />
        <div v-else class="empty-state">Sin datos de resultados</div>
      </div>
    </div>

    <!-- Detalle de Juicios -->
    <div class="card mt-24">
      <div class="card-title">Detalle de Juicios Evaluativos</div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Competencia</th>
              <th>Resultado de Aprendizaje</th>
              <th>Juicio</th>
              <th>Fecha/Hora</th>
              <th>Funcionario</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="j in juicios" :key="j.id">
              <td>{{ j.competencia }}</td>
              <td>{{ j.resultado_aprendizaje }}</td>
              <td>
                <span class="badge" :class="j.juicio_evaluacion?.toLowerCase().includes('aprobado') ? 'badge-success' : 'badge-warning'">
                  {{ j.juicio_evaluacion }}
                </span>
              </td>
              <td>{{ formatDate(j.fecha_hora_juicio) }}</td>
              <td>{{ j.funcionario }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import api from '../api/index.js'
import KpiCard from '../components/KpiCard.vue'
import BarChart from '../components/BarChart.vue'

const route = useRoute()
const loading = ref(true)
const error = ref(null)
const data = ref(null)
const juicios = ref([])

async function cargarDatos() {
  loading.value = true
  try {
    const id = route.params.id
    const res = await api.getAvanceAprendiz(id)
    data.value = res.data

    // Cargar también la lista completa de juicios para la tabla
    const resJuicios = await api.getJuicios({ documento: res.data.aprendiz.numero_documento })
    juicios.value = resJuicios.data
  } catch (err) {
    error.value = "Error al cargar el avance del aprendiz."
  } finally {
    loading.value = false
  }
}

onMounted(cargarDatos)

const competenciaLabels = computed(() => data.value?.por_competencia.map(c => c.competencia.slice(0, 30)) || [])
const competenciaDatasets = computed(() => [
  {
    label: '% Aprobación',
    data: data.value?.por_competencia.map(c => c.porcentaje) || [],
    backgroundColor: 'rgba(57,169,0,0.7)',
    borderRadius: 4
  }
])

const resultadoLabels = computed(() => data.value?.por_resultado.map(r => r.resultado.slice(0, 30)) || [])
const resultadoDatasets = computed(() => [
  {
    label: '% Aprobación',
    data: data.value?.por_resultado.map(r => r.porcentaje) || [],
    backgroundColor: 'rgba(59,130,246,0.7)',
    borderRadius: 4
  }
])

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString()
}
</script>
