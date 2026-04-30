<template>
  <div class="kpi-card" :style="{ '--kpi-color': color }">
    <div class="kpi-icon">{{ icon }}</div>
    <div class="kpi-label">{{ label }}</div>
    <div class="kpi-value">{{ formattedValue }}</div>
    <div v-if="sub" class="kpi-sub">{{ sub }}</div>
    <div v-if="progress !== null" class="mt-8">
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill" :style="{ width: progress + '%', background: color }"></div>
      </div>
      <div class="kpi-sub mt-4">{{ progress }}%</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label:    { type: String, required: true },
  value:    { type: [Number, String], default: 0 },
  icon:     { type: String, default: '📈' },
  color:    { type: String, default: 'var(--sena-green)' },
  sub:      { type: String, default: '' },
  progress: { type: Number, default: null },
})

const formattedValue = computed(() =>
  typeof props.value === 'number' ? props.value.toLocaleString('es-CO') : props.value
)
</script>
