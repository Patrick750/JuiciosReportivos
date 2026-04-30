<template>
  <div>
    <div class="page-title">
      <h1>🗂️ Proyecto Formativo</h1>
      <p>Administra las fases y actividades del proyecto y selecciónalas para cada competencia.</p>
    </div>

    <div class="flex gap-12 mb-16">
      <select class="form-control" style="max-width:300px" v-model="fichaSeleccionada" @change="cargarFases">
        <option value="">Selecciona una ficha...</option>
        <option v-for="f in fichas" :key="f.id" :value="f.id">
          {{ f.ficha_caracterizacion }} - {{ f.denominacion }}
        </option>
      </select>
      <button class="btn btn-primary" :disabled="!fichaSeleccionada" @click="mostrarModalFase = true">
        + Nueva Fase
      </button>
    </div>

    <div v-if="!fichaSeleccionada" class="empty-state">
      <div class="icon">🔍</div>
      <p>Selecciona una ficha para ver su proyecto formativo.</p>
    </div>

    <div v-else-if="loading" class="empty-state">
      <div class="loading-spinner"></div>
    </div>

    <div v-else class="fases-container">
      <div v-for="fase in fases" :key="fase.id" class="card mb-16">
        <div class="flex-between mb-16">
          <div>
            <h3>Fase {{ fase.orden }}: {{ fase.nombre }}</h3>
            <p class="text-muted">{{ fase.descripcion }}</p>
          </div>
          <div class="flex gap-8">
            <button class="btn btn-secondary btn-sm" @click="editarFase(fase)">Editar</button>
            <button class="btn btn-danger btn-sm" @click="eliminarFase(fase.id)">Eliminar</button>
            <button class="btn btn-primary btn-sm" @click="nuevaActividad(fase.id)">+ Actividad</button>
          </div>
        </div>

        <div v-if="fase.actividades?.length" class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Actividad</th>
                <th>Competencias</th>
                <th>Resultados</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="act in fase.actividades" :key="act.id">
                <td>
                  <strong>{{ act.nombre }}</strong>
                  <div class="text-muted">{{ act.descripcion }}</div>
                </td>
                <td>
                  <div v-for="c in act.competencias" :key="c" class="badge badge-info mb-4" style="display:block; width:fit-content">
                    {{ c.slice(0, 50) }}...
                  </div>
                </td>
                <td>
                  <div v-for="r in act.resultados" :key="r" class="badge badge-gray mb-4" style="display:block; width:fit-content">
                    {{ r.slice(0, 50) }}...
                  </div>
                </td>
                <td>
                  <div class="flex gap-8">
                    <button class="btn btn-icon btn-secondary" @click="editarActividad(act)">✏️</button>
                    <button class="btn btn-icon btn-secondary" @click="eliminarActividad(act.id)">🗑️</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-muted text-center p-16">No hay actividades registradas en esta fase.</div>
      </div>
    </div>

    <!-- Modal Fase -->
    <div v-if="mostrarModalFase" class="modal-overlay">
      <div class="card modal-content">
        <div class="card-title">{{ formFase.id ? 'Editar Fase' : 'Nueva Fase' }}</div>
        <div class="form-group">
          <label class="form-label">Nombre de la Fase</label>
          <input v-model="formFase.nombre" class="form-control" placeholder="Ej: Fase de Análisis" />
        </div>
        <div class="form-group">
          <label class="form-label">Descripción</label>
          <textarea v-model="formFase.descripcion" class="form-control" rows="3"></textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Orden</label>
          <input v-model.number="formFase.orden" type="number" class="form-control" />
        </div>
        <div class="flex-between mt-16">
          <button class="btn btn-secondary" @click="cerrarModalFase">Cancelar</button>
          <button class="btn btn-primary" @click="guardarFase">Guardar</button>
        </div>
      </div>
    </div>

    <!-- Modal Actividad -->
    <div v-if="mostrarModalActividad" class="modal-overlay">
      <div class="card modal-content" style="max-width:600px">
        <div class="card-title">{{ formActividad.id ? 'Editar Actividad' : 'Nueva Actividad' }}</div>
        <div class="form-group">
          <label class="form-label">Nombre de la Actividad</label>
          <input v-model="formActividad.nombre" class="form-control" placeholder="Ej: Recolección de requisitos" />
        </div>
        <div class="form-group">
          <label class="form-label">Descripción</label>
          <textarea v-model="formActividad.descripcion" class="form-control" rows="2"></textarea>
        </div>
        
        <div class="form-group">
          <label class="form-label">Competencias Relacionadas</label>
          <div class="flex gap-8 mb-8">
            <SearchableSelect 
              v-model="tempCompetencia" 
              :options="listadoCompetencias" 
              placeholder="Buscar competencia..."
            />
            <button class="btn btn-secondary" @click="agregarComp">Agregar</button>
          </div>
          <div class="flex wrap gap-8">
            <span v-for="(c, i) in formActividad.competencias" :key="i" class="badge badge-info">
              {{ c.slice(0, 30) }}... <span class="cursor-pointer" @click="formActividad.competencias.splice(i, 1)">x</span>
            </span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Resultados Relacionados</label>
          <div class="flex gap-8 mb-8">
            <SearchableSelect 
              v-model="tempResultado" 
              :options="resultadosFiltrados" 
              placeholder="Buscar resultado..."
            />
            <button class="btn btn-secondary" @click="agregarRes">Agregar</button>
          </div>
          <div class="flex wrap gap-8">
            <span v-for="(r, i) in formActividad.resultados" :key="i" class="badge badge-gray">
              {{ r.slice(0, 30) }}... <span class="cursor-pointer" @click="formActividad.resultados.splice(i, 1)">x</span>
            </span>
          </div>
        </div>

        <div class="flex-between mt-16">
          <button class="btn btn-secondary" @click="cerrarModalActividad">Cancelar</button>
          <button class="btn btn-primary" @click="guardarActividad">Guardar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api/index.js'
import SearchableSelect from '../components/SearchableSelect.vue'

const fichas = ref([])
const fichaSeleccionada = ref('')
const fases = ref([])
const loading = ref(false)

// Listados para selección
const listadoCompetencias = ref([])
const listadoResultados = ref([])
const juiciosRaw = ref([])

const resultadosFiltrados = computed(() => {
  if (!tempCompetencia.value) return listadoResultados.value
  const resSet = new Set(
    juiciosRaw.value
      .filter(j => j.competencia === tempCompetencia.value)
      .map(j => j.resultado_aprendizaje)
  )
  return Array.from(resSet).filter(Boolean)
})

// Modal Fase
const mostrarModalFase = ref(false)
const formFase = ref({ id: null, nombre: '', descripcion: '', orden: 1 })

// Modal Actividad
const mostrarModalActividad = ref(false)
const formActividad = ref({ id: null, fase: null, nombre: '', descripcion: '', competencias: [], resultados: [] })
const tempCompetencia = ref('')
const tempResultado = ref('')

async function cargarFichas() {
  const res = await api.getFichas()
  fichas.value = res.data
}

async function cargarFases() {
  if (!fichaSeleccionada.value) return
  loading.value = true
  try {
    const res = await api.getFases({ ficha: fichaSeleccionada.value })
    fases.value = res.data

    // Cargar competencias y resultados únicos de la ficha para los selectores
    const resAvance = await api.getDashboard({ ficha: fichaSeleccionada.value })
    listadoCompetencias.value = resAvance.data.por_competencia.map(c => c.competencia)
    
    // Para resultados, necesitamos consultar los juicios o el dashboard extendido
    const resJuicios = await api.getJuicios({ ficha: fichaSeleccionada.value })
    juiciosRaw.value = resJuicios.data
    const resSet = new Set(resJuicios.data.map(j => j.resultado_aprendizaje))
    listadoResultados.value = Array.from(resSet).filter(Boolean)
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

function editarFase(fase) {
  formFase.value = { ...fase }
  mostrarModalFase.value = true
}

function cerrarModalFase() {
  mostrarModalFase.value = false
  formFase.value = { id: null, nombre: '', descripcion: '', orden: fases.value.length + 1 }
}

async function guardarFase() {
  try {
    const data = { ...formFase.value, ficha: fichaSeleccionada.value }
    if (data.id) {
      await api.updateFase(data.id, data)
    } else {
      await api.createFase(data)
    }
    cerrarModalFase()
    cargarFases()
  } catch (err) { alert("Error al guardar fase") }
}

async function eliminarFase(id) {
  if (!confirm("¿Eliminar esta fase y todas sus actividades?")) return
  await api.deleteFase(id)
  cargarFases()
}

function nuevaActividad(faseId) {
  formActividad.value = { id: null, fase: faseId, nombre: '', descripcion: '', competencias: [], resultados: [] }
  mostrarModalActividad.value = true
}

function editarActividad(act) {
  formActividad.value = { ...act }
  mostrarModalActividad.value = true
}

function cerrarModalActividad() {
  mostrarModalActividad.value = false
  tempCompetencia.value = ''
  tempResultado.value = ''
}

function agregarComp() {
  if (tempCompetencia.value && !formActividad.value.competencias.includes(tempCompetencia.value)) {
    formActividad.value.competencias.push(tempCompetencia.value)
    tempCompetencia.value = ''
  }
}

function agregarRes() {
  if (tempResultado.value && !formActividad.value.resultados.includes(tempResultado.value)) {
    formActividad.value.resultados.push(tempResultado.value)
    tempResultado.value = ''
  }
}

async function guardarActividad() {
  try {
    if (formActividad.value.id) {
      await api.updateActividad(formActividad.value.id, formActividad.value)
    } else {
      await api.createActividad(formActividad.value)
    }
    cerrarModalActividad()
    cargarFases()
  } catch (err) { alert("Error al guardar actividad") }
}

async function eliminarActividad(id) {
  if (!confirm("¿Eliminar actividad?")) return
  await api.deleteActividad(id)
  cargarFases()
}

onMounted(cargarFichas)
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 20px;
}
.modal-content { max-width: 500px; width: 100%; }
.wrap { flex-wrap: wrap; }
.cursor-pointer { cursor: pointer; }
</style>
