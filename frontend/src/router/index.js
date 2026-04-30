import { createRouter, createWebHistory } from 'vue-router'
import ImportarView from '../views/ImportarView.vue'
import DashboardView from '../views/DashboardView.vue'
import AvanceAprendizView from '../views/AvanceAprendizView.vue'
import ProyectoFormativoView from '../views/ProyectoFormativoView.vue'
import DashboardFasesView from '../views/DashboardFasesView.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/importar', name: 'importar', component: ImportarView },
  { path: '/dashboard', name: 'dashboard', component: DashboardView },
  { path: '/avance/:id', name: 'avance-aprendiz', component: AvanceAprendizView, props: true },
  { path: '/proyecto-formativo', name: 'proyecto-formativo', component: ProyectoFormativoView },
  { path: '/dashboard-fases', name: 'dashboard-fases', component: DashboardFasesView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
