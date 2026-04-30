<template>
  <div class="chart-container">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import {
  Chart,
  BarElement, BarController,
  CategoryScale, LinearScale,
  Tooltip, Legend
} from 'chart.js'

Chart.register(BarElement, BarController, CategoryScale, LinearScale, Tooltip, Legend)

const props = defineProps({
  labels:   { type: Array, required: true },
  datasets: { type: Array, required: true },
  title:    { type: String, default: '' },
  horizontal: { type: Boolean, default: false },
})

const canvas = ref(null)
let chartInstance = null

function buildChart() {
  if (chartInstance) { chartInstance.destroy(); chartInstance = null }
  if (!canvas.value) return

  chartInstance = new Chart(canvas.value, {
    type: 'bar',
    data: { labels: props.labels, datasets: props.datasets },
    options: {
      indexAxis: props.horizontal ? 'y' : 'x',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#8892a4', font: { family: 'Inter', size: 12 }, boxWidth: 12 },
        },
        tooltip: {
          backgroundColor: '#1a1d27',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          titleColor: '#e8eaf0',
          bodyColor: '#8892a4',
        },
      },
      scales: {
        x: {
          ticks: { color: '#8892a4', font: { size: 11, family: 'Inter' } },
          grid:  { color: 'rgba(255,255,255,0.04)' },
        },
        y: {
          ticks: { color: '#8892a4', font: { size: 11, family: 'Inter' } },
          grid:  { color: 'rgba(255,255,255,0.04)' },
          beginAtZero: true,
        },
      },
    },
  })
}

onMounted(buildChart)
onBeforeUnmount(() => { if (chartInstance) chartInstance.destroy() })
watch(() => [props.labels, props.datasets], buildChart, { deep: true })
</script>

<style scoped>
.chart-container { position: relative; width: 100%; height: 300px; }
</style>
