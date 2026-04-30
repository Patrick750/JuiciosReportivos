<template>
  <div>
    <div class="page-title">
      <h1>📥 Importar Reporte XLS</h1>
      <p>Sube el archivo "Reporte de Juicios Evaluativos" en formato .xls para registrar los datos.</p>
    </div>

    <div class="card">
      <!-- Drop Zone -->
      <div
        class="drop-zone"
        :class="{ dragging, 'has-file': archivo }"
        @dragover.prevent="dragging = true"
        @dragleave="dragging = false"
        @drop.prevent="onDrop"
        @click="fileInput.click()"
      >
        <input ref="fileInput" type="file" accept=".xls,.xlsx" class="hidden-input" @change="onFileSelect" />
        <div v-if="!archivo" class="dz-content">
          <div class="dz-icon">📂</div>
          <div class="dz-title">Arrastra el archivo aquí</div>
          <div class="dz-sub">o haz clic para seleccionarlo</div>
          <div class="dz-hint">Solo archivos <strong>.xls / .xlsx</strong></div>
        </div>
        <div v-else class="dz-content dz-selected">
          <div class="dz-icon">📄</div>
          <div class="dz-title">{{ archivo.name }}</div>
          <div class="dz-sub">{{ (archivo.size / 1024).toFixed(1) }} KB · Listo para importar</div>
          <button class="btn btn-secondary btn-sm mt-8" @click.stop="clearFile">Cambiar archivo</button>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="error" class="alert alert-error mt-16">⚠️ {{ error }}</div>
      <div v-if="resultado" class="alert alert-success mt-16">
        ✅ Importación exitosa — <strong>{{ resultado.resumen.juicios_creados }}</strong> juicios y
        <strong>{{ resultado.resumen.aprendices_nuevos }}</strong> aprendices nuevos registrados.
      </div>

      <!-- Ficha Info -->
      <div v-if="resultado" class="ficha-info mt-16">
        <div class="card-title">Ficha importada</div>
        <div class="info-grid">
          <div class="info-item"><span class="info-label">Ficha</span><span>{{ resultado.ficha.ficha_caracterizacion }}</span></div>
          <div class="info-item"><span class="info-label">Denominación</span><span>{{ resultado.ficha.denominacion }}</span></div>
          <div class="info-item"><span class="info-label">Código</span><span>{{ resultado.ficha.codigo }}</span></div>
          <div class="info-item"><span class="info-label">Versión</span><span>{{ resultado.ficha.version }}</span></div>
          <div class="info-item"><span class="info-label">Estado</span><span>{{ resultado.ficha.estado_ficha }}</span></div>
          <div class="info-item"><span class="info-label">Modalidad</span><span>{{ resultado.ficha.modalidad }}</span></div>
          <div class="info-item"><span class="info-label">Regional</span><span>{{ resultado.ficha.regional?.nombre }}</span></div>
          <div class="info-item"><span class="info-label">Centro</span><span>{{ resultado.ficha.centro_formacion?.nombre }}</span></div>
        </div>
      </div>

      <!-- Errores de fila -->
      <div v-if="resultado?.resumen?.filas_con_error?.length" class="mt-16">
        <div class="card-title">⚠️ Filas con errores ({{ resultado.resumen.filas_con_error.length }})</div>
        <div class="table-wrapper">
          <table>
            <thead><tr><th>Fila</th><th>Error</th></tr></thead>
            <tbody>
              <tr v-for="e in resultado.resumen.filas_con_error" :key="e.fila">
                <td>{{ e.fila }}</td>
                <td><code>{{ e.error }}</code></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex-between mt-24">
        <button class="btn btn-secondary" :disabled="loading" @click="clearAll">Limpiar</button>
        <button class="btn btn-primary" :disabled="!archivo || loading" @click="importar">
          <span v-if="loading" class="loading-spinner"></span>
          <span>{{ loading ? 'Importando…' : '🚀 Importar Archivo' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/index.js'

const fileInput = ref(null)
const archivo   = ref(null)
const dragging  = ref(false)
const loading   = ref(false)
const error     = ref('')
const resultado = ref(null)

function onDrop(e) {
  dragging.value = false
  const f = e.dataTransfer.files[0]
  if (f) setFile(f)
}
function onFileSelect(e) {
  const f = e.target.files[0]
  if (f) setFile(f)
}
function setFile(f) {
  const name = f.name.toLowerCase()
  if (!name.endsWith('.xls') && !name.endsWith('.xlsx')) {
    error.value = 'Solo se aceptan archivos .xls o .xlsx.'
    return
  }
  archivo.value = f
  error.value = ''
  resultado.value = null
}
function clearFile() { archivo.value = null; if (fileInput.value) fileInput.value.value = '' }
function clearAll()  { clearFile(); error.value = ''; resultado.value = null }

async function importar() {
  if (!archivo.value) return
  loading.value = true
  error.value = ''
  resultado.value = null
  try {
    const fd = new FormData()
    fd.append('archivo', archivo.value)
    const res = await api.importarReporte(fd)
    resultado.value = res.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Error al importar el archivo.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition);
}
.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--sena-green);
  background: rgba(57,169,0,0.05);
}
.drop-zone.has-file { border-color: var(--sena-green); background: rgba(57,169,0,0.07); }
.hidden-input { display: none; }
.dz-icon  { font-size: 3rem; margin-bottom: 12px; }
.dz-title { font-size: 1.1rem; font-weight: 700; color: var(--text); }
.dz-sub   { color: var(--text-muted); font-size: 0.875rem; margin-top: 4px; }
.dz-hint  { font-size: 0.78rem; color: var(--text-muted); margin-top: 12px;
            background: rgba(255,255,255,0.04); display: inline-block;
            padding: 4px 12px; border-radius: 99px; }
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}
.info-item {
  background: var(--bg-card2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.info-label { font-size: 0.7rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.6px; }
code { font-size: 0.78rem; color: var(--danger); background: rgba(239,68,68,0.08); padding: 2px 6px; border-radius: 4px; }
</style>
