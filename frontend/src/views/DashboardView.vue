<template>
  <div>
    <!-- Header -->
    <div class="flex-between mb-24">
      <div class="page-title" style="margin:0">
        <h1>📊 Dashboard General</h1>
        <p>Indicadores globales de seguimiento y evaluación por aprendiz.</p>
      </div>
      <select class="form-control" style="width:260px" v-model="fichaId" @change="cargar">
        <option value="">— Todas las fichas —</option>
        <option v-for="f in fichas" :key="f.id" :value="f.id">
          {{ f.ficha_caracterizacion }} · {{ f.denominacion?.slice(0,35) }}
        </option>
      </select>
    </div>

    <!-- KPIs -->
    <div v-if="loading" class="empty-state"><div class="loading-spinner"></div></div>
    <template v-else>
      <div class="kpi-grid">
        <KpiCard label="Total Aprendices" :value="data.total_aprendices" icon="👤" color="var(--info)" />
        <KpiCard label="Total Juicios" :value="data.total_juicios" icon="📋" color="var(--accent)" />
        <KpiCard label="Juicios Aprobados" :value="data.aprobados_total" icon="✅" color="var(--sena-green)" />
        <KpiCard label="Juicios Pendientes" :value="data.pendientes_total" icon="⏳" color="var(--warning)" />
        <KpiCard
          label="% Aprobación Global"
          :value="data.porcentaje_aprobacion + '%'"
          icon="🎯"
          color="var(--sena-green)"
          :progress="data.porcentaje_aprobacion"
        />
      </div>

      <!-- Filtros avanzados -->
      <div class="card mb-16">
        <div class="card-title">🔍 Filtros Avanzados</div>
        <div class="grid-3" style="gap:12px">
          <div class="form-group" style="margin:0">
            <label class="form-label">Aprendiz</label>
            <input v-model="filtros.nombre" class="form-control" placeholder="Nombre o apellido…" @input="filtrarAprendices" />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Documento</label>
            <input v-model="filtros.documento" class="form-control" placeholder="Número…" @input="filtrarAprendices" />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Estado</label>
            <select v-model="filtros.estado" class="form-control" @change="filtrarAprendices">
              <option value="">Todos los estados</option>
              <option v-for="e in uniqueEstados" :key="e" :value="e">{{ e }}</option>
            </select>
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Competencia</label>
            <SearchableSelect 
              v-model="filtros.competencia" 
              :options="uniqueCompetencias" 
              placeholder="Buscar competencia..."
              @change="filtrarAprendices"
            />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Resultado de Aprendizaje</label>
            <SearchableSelect 
              v-model="filtros.resultado" 
              :options="uniqueResultados" 
              placeholder="Buscar resultado..."
              @change="filtrarAprendices"
            />
          </div>
          <div class="form-group" style="margin:0">
            <label class="form-label">Ficha</label>
            <select v-model="filtros.ficha" class="form-control" @change="filtrarAprendices">
              <option value="">Todas las fichas</option>
              <option v-for="f in uniqueFichas" :key="f" :value="f">{{ f }}</option>
            </select>
          </div>
          <div class="flex" style="align-items:flex-end">
            <button class="btn btn-secondary" style="width:100%" @click="limpiarFiltros">Limpiar filtros</button>
          </div>
        </div>
      </div>

      <!-- Gráfica por Competencia -->
      <div class="grid-2" style="margin-bottom:20px">
        <div class="card">
          <div class="card-title">📚 % Aprobación por Competencia</div>
          <BarChart
            v-if="competenciaLabels.length"
            :labels="competenciaLabels"
            :datasets="competenciaDatasets"
            :horizontal="true"
          />
          <div v-else class="empty-state"><div class="icon">📭</div><p>Sin datos</p></div>
        </div>
        <div class="card">
          <div class="card-title">📊 Aprobados vs Pendientes por Aprendiz</div>
          <BarChart
            v-if="aprendizLabels.length"
            :labels="aprendizLabels"
            :datasets="aprendizDatasets"
          />
          <div v-else class="empty-state"><div class="icon">📭</div><p>Sin datos</p></div>
        </div>
      </div>

      <!-- Tabla de Aprendices -->
      <div class="card">
        <div class="flex-between mb-16">
          <div class="card-title" style="margin:0">👥 Seguimiento por Aprendiz ({{ aprendicesFiltrados.length }})</div>
        </div>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Aprendiz</th>
                <th>Documento</th>
                <th>Formación</th>
                <th>Estado</th>
                <th>Total</th>
                <th>Aprobados</th>
                <th>Pendientes</th>
                <th>Avance</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in aprendicesFiltrados" :key="a.aprendiz_id">
                <td><strong>{{ a.apellidos }}, {{ a.nombre }}</strong></td>
                <td>{{ a.numero_documento }}</td>
                <td :title="a.formacion">
                  {{ a.formacion ? a.formacion.slice(0, 40) + (a.formacion.length > 40 ? '...' : '') : '—' }}
                </td>
                <td><span class="badge" :class="estadoBadge(a.estado)">{{ a.estado || '—' }}</span></td>
                <td>{{ a.total_juicios }}</td>
                <td><span class="badge badge-success">{{ a.aprobados }}</span></td>
                <td><span class="badge badge-warning">{{ a.pendientes }}</span></td>
                <td style="min-width:120px">
                  <div class="progress-bar-wrap">
                    <div class="progress-bar-fill" :style="{ width: a.porcentaje_avance + '%' }"></div>
                  </div>
                  <div class="kpi-sub mt-4">{{ a.porcentaje_avance }}%</div>
                </td>
                <td>
                  <RouterLink :to="`/avance/${a.aprendiz_id}`" class="btn btn-secondary btn-sm">Ver avance</RouterLink>
                </td>
              </tr>
              <tr v-if="!aprendicesFiltrados.length">
                <td colspan="8" class="empty-state" style="padding:32px">Sin resultados</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../api/index.js'
import KpiCard from '../components/KpiCard.vue'
import BarChart from '../components/BarChart.vue'
import SearchableSelect from '../components/SearchableSelect.vue'

const fichaId = ref('')
const fichas  = ref([])
const loading = ref(false)
const data    = ref({
  total_aprendices: 0, total_juicios: 0,
  aprobados_total: 0, pendientes_total: 0,
  porcentaje_aprobacion: 0, kpi_aprendices: [], 
  por_competencia: [], por_resultado: [],
})

const uniqueEstados = computed(() => {
  const s = new Set(data.value.kpi_aprendices.map(a => a.estado).filter(Boolean))
  return Array.from(s).sort()
})
const uniqueCompetencias = computed(() => {
  return data.value.por_competencia.map(c => c.competencia).sort()
})
const uniqueResultados = computed(() => {
  return (data.value.por_resultado || []).map(r => r.resultado).sort()
})
const uniqueFichas = computed(() => {
  const s = new Set(data.value.kpi_aprendices.map(a => a.ficha_numero).filter(Boolean))
  return Array.from(s).sort()
})

const filtros = ref({ nombre: '', documento: '', estado: '', competencia: '', resultado: '', ficha: '' })
const aprendicesFiltrados = ref([])

function filtrarAprendices() {
  const { nombre, documento, estado, ficha, competencia, resultado } = filtros.value
  aprendicesFiltrados.value = data.value.kpi_aprendices.filter(a => {
    const fullName = `${a.nombre} ${a.apellidos}`.toLowerCase()
    if (nombre && !fullName.includes(nombre.toLowerCase())) return false
    if (documento && !a.numero_documento.includes(documento)) return false
    if (estado && a.estado !== estado) return false
    if (ficha && a.ficha_numero !== ficha) return false
    if (competencia && !a.competencias.includes(competencia)) return false
    if (resultado && !a.resultados.includes(resultado)) return false
    return true
  })
}
function limpiarFiltros() {
  filtros.value = { nombre: '', documento: '', estado: '', competencia: '', resultado: '', ficha: '' }
  aprendicesFiltrados.value = [...data.value.kpi_aprendices]
}

async function cargar() {
  loading.value = true
  try {
    const params = fichaId.value ? { ficha: fichaId.value } : {}
    const res = await api.getDashboard(params)
    data.value = res.data
    aprendicesFiltrados.value = [...res.data.kpi_aprendices]
  } catch { /* silencioso */ } finally { loading.value = false }
}

onMounted(async () => {
  const res = await api.getFichas()
  fichas.value = res.data
  await cargar()
})

// Chart data
const competenciaLabels = computed(() => data.value.por_competencia.map(c => c.competencia.slice(0, 40)))
const competenciaDatasets = computed(() => [
  {
    label: 'Aprobados',
    data: data.value.por_competencia.map(c => c.aprobados),
    backgroundColor: 'rgba(57,169,0,0.7)',
    borderRadius: 4,
  },
  {
    label: 'Pendientes',
    data: data.value.por_competencia.map(c => c.pendientes),
    backgroundColor: 'rgba(245,158,11,0.5)',
    borderRadius: 4,
  },
])

const aprendizLabels = computed(() =>
  aprendicesFiltrados.value.slice(0, 15).map(a => `${a.apellidos} ${a.nombre}`.slice(0, 20))
)
const aprendizDatasets = computed(() => [
  {
    label: 'Aprobados',
    data: aprendicesFiltrados.value.slice(0, 15).map(a => a.aprobados),
    backgroundColor: 'rgba(57,169,0,0.7)',
    borderRadius: 4,
  },
  {
    label: 'Pendientes',
    data: aprendicesFiltrados.value.slice(0, 15).map(a => a.pendientes),
    backgroundColor: 'rgba(239,68,68,0.5)',
    borderRadius: 4,
  },
])

function estadoBadge(estado) {
  const s = (estado || '').toLowerCase()
  if (s.includes('activ')) return 'badge-success'
  if (s.includes('retir')) return 'badge-danger'
  if (s.includes('trasl')) return 'badge-warning'
  return 'badge-gray'
}
</script>
