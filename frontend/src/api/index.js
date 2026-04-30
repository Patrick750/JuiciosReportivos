import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export default {
  // Fichas
  getFichas: () => api.get('/api/reportes/fichas/'),

  // Importar
  importarReporte: (formData) =>
    api.post('/api/reportes/importar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  // Aprendices
  getAprendices: (params = {}) => api.get('/api/reportes/aprendices/', { params }),

  // Juicios
  getJuicios: (params = {}) => api.get('/api/reportes/juicios/', { params }),

  // Avance aprendiz
  getAvanceAprendiz: (id, params = {}) =>
    api.get(`/api/reportes/avance/${id}/`, { params }),

  // Dashboard principal
  getDashboard: (params = {}) => api.get('/api/reportes/dashboard/', { params }),

  // Fases
  getFases: (params = {}) => api.get('/api/reportes/fases/', { params }),
  createFase: (data) => api.post('/api/reportes/fases/', data),
  updateFase: (id, data) => api.put(`/api/reportes/fases/${id}/`, data),
  deleteFase: (id) => api.delete(`/api/reportes/fases/${id}/`),

  // Actividades
  getActividades: (params = {}) => api.get('/api/reportes/actividades/', { params }),
  createActividad: (data) => api.post('/api/reportes/actividades/', data),
  updateActividad: (id, data) => api.put(`/api/reportes/actividades/${id}/`, data),
  deleteActividad: (id) => api.delete(`/api/reportes/actividades/${id}/`),

  // Dashboard fases
  getDashboardFases: (fichaId) =>
    api.get('/api/reportes/dashboard-fases/', { params: { ficha: fichaId } }),
}
