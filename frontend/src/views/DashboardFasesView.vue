<template>
  <div>
    <div class="flex-between mb-24">
      <div class="page-title" style="margin:0">
        <h1>🏁 Dashboard de Fases</h1>
        <p>Seguimiento del cumplimiento por fases del proyecto formativo.</p>
      </div>
      <select class="form-control" style="width:260px" v-model="fichaId" @change="cargar">
        <option value="">— Selecciona una ficha —</option>
        <option v-for="f in fichas" :key="f.id" :value="f.id">
          {{ f.ficha_caracterizacion }} · {{ f.denominacion?.slice(0,35) }}
        </option>
      </select>
    </div>

    <div v-if="!fichaId" class="empty-state">
      <div class="icon">🔍</div>
      <p>Selecciona una ficha para ver los indicadores por fase.</p>
    </div>

    <div v-else-if="loading" class="empty-state">
      <div class="loading-spinner"></div>
    </div>

    <template v-else>
      <!-- Resumen de Fases (Gráfica) -->
      <div class="card mb-24">
        <div class="card-title">Progreso de Cumplimiento por Fase</div>
        <BarChart
          v-if="fasesData.length"
          :labels="faseLabels"
          :datasets="faseDatasets"
        />
        <div v-else class="empty-state">No hay fases configuradas para esta ficha.</div>
      </div>

      <!-- Detalle por Fase -->
      <div class="grid-2">
        <div v-for="fase in fasesData" :key="fase.fase_id" class="card">
          <div class="flex-between mb-16">
            <h3>{{ fase.fase_nombre }}</h3>
            <span class="badge badge-info">Fase {{ fase.orden }}</span>
          </div>

          <div class="kpi-grid" style="grid-template-columns: 1fr 1fr; margin-bottom: 16px;">
            <div class="kpi-item">
              <div class="kpi-label">Aprendices Aprobados</div>
              <div class="kpi-value" style="font-size: 1.5rem; color: var(--success)">{{ fase.aprendices_aprobados }}</div>
            </div>
            <div class="kpi-item">
              <div class="kpi-label">Aprendices Pendientes</div>
              <div class="kpi-value" style="font-size: 1.5rem; color: var(--warning)">{{ fase.aprendices_pendientes }}</div>
            </div>
          </div>

          <div class="mt-8">
            <div class="flex-between mb-4">
              <span class="kpi-label">Cumplimiento General</span>
              <span class="kpi-value" style="font-size: 1rem; margin:0">{{ fase.porcentaje_cumplimiento }}%</span>
            </div>
            <div class="progress-bar-wrap">
              <div class="progress-bar-fill" :style="{ width: fase.porcentaje_cumplimiento + '%' }"></div>
            </div>
          </div>

          <div class="mt-16 text-muted" style="font-size: 0.8rem">
            Total juicios en esta fase: <strong>{{ fase.total_juicios }}</strong> ({{ fase.aprobados }} aprobados)
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api/index.js'
import BarChart from '../components/BarChart.vue'

const fichaId = ref('')
const fichas = ref([])
const loading = ref(false)
const fasesData = ref([])

async function cargarFichas() {
  const res = await api.getFichas()
  fichas.value = res.data
}

async function cargar() {
  if (!fichaId.value) return
  loading.value = true
  try {
    const res = await api.getDashboardFases(fichaId.value)
    fasesData.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(cargarFichas)

const faseLabels = computed(() => fasesData.value.map(f => f.fase_nombre))
const faseDatasets = computed(() => [
  {
    label: '% Cumplimiento',
    data: fasesData.value.map(f => f.porcentaje_cumplimiento),
    backgroundColor: 'rgba(57,169,0,0.7)',
    borderRadius: 4
  }
])
</script>

<style scoped>
.kpi-item {
  background: var(--bg-card2);
  padding: 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}
</style>
