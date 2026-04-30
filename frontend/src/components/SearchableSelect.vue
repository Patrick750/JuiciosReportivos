<template>
  <div class="searchable-select" ref="container">
    <div class="input-wrapper">
      <input
        type="text"
        class="form-control"
        :placeholder="placeholder"
        v-model="searchTerm"
        @focus="onFocus"
        @input="onInput"
      />
      <div class="chevron" :class="{ 'is-open': isOpen }" @click="toggleDropdown">▼</div>
    </div>
    
    <div v-if="isOpen" class="dropdown-list shadow-lg">
      <div 
        v-if="filteredOptions.length === 0" 
        class="no-results"
      >
        No se encontraron resultados
      </div>
      <div
        v-for="option in filteredOptions"
        :key="option"
        class="dropdown-item"
        :class="{ 'is-selected': option === modelValue }"
        @click="selectOption(option)"
        :title="option"
      >
        {{ option }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  modelValue: String,
  options: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: 'Seleccionar...'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchTerm = ref('')
const container = ref(null)

// Sincronizar el término de búsqueda con el valor seleccionado
watch(() => props.modelValue, (newVal) => {
  if (!isOpen.value) {
    searchTerm.value = newVal || ''
  }
}, { immediate: true })

const filteredOptions = computed(() => {
  const term = searchTerm.value.toLowerCase().trim()
  if (!term || (props.modelValue && term === props.modelValue.toLowerCase().trim())) {
    return props.options
  }
  return props.options.filter(opt => 
    opt.toLowerCase().includes(term)
  )
})

function onFocus() {
  isOpen.value = true
}

function onInput() {
  isOpen.value = true
  // Si el usuario borra todo, emitimos vacío
  if (!searchTerm.value) {
    emit('update:modelValue', '')
    emit('change', '')
  }
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function selectOption(option) {
  searchTerm.value = option
  isOpen.value = false
  emit('update:modelValue', option)
  emit('change', option)
}

function handleClickOutside(event) {
  if (container.value && !container.value.contains(event.target)) {
    isOpen.value = false
    // Al salir, si no hay match exacto o está vacío, restaurar o limpiar
    if (searchTerm.value !== props.modelValue) {
       searchTerm.value = props.modelValue || ''
    }
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>

<style scoped>
.searchable-select {
  position: relative;
  width: 100%;
}

.input-wrapper {
  position: relative;
}

.form-control {
  padding-right: 30px !important;
  text-overflow: ellipsis;
}

.chevron {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.6rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: transform 0.2s ease;
  padding: 4px;
}

.chevron.is-open {
  transform: translateY(-50%) rotate(180deg);
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 6px;
  background: var(--bg-card2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 10px 40px rgba(0,0,0,0.6);
}

.dropdown-item {
  padding: 10px 14px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: rgba(57,169,0,0.15);
  color: var(--sena-green);
  padding-left: 18px;
}

.dropdown-item.is-selected {
  background: var(--sena-green);
  color: white;
}

.no-results {
  padding: 16px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
  font-style: italic;
}

/* Scrollbar */
.dropdown-list::-webkit-scrollbar { width: 5px; }
.dropdown-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
.dropdown-list::-webkit-scrollbar-thumb:hover { background: var(--sena-green); }
</style>
