import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useCashRegisterStore = defineStore('cashRegister', () => {
  const current = ref(null) // sesion abierta (con movimientos) o null
  const loading = ref(false)
  const error = ref('')

  const sessions = ref([])
  const sessionsPagination = ref({ total: 0, page: 1, pages: 1, perPage: 5 })
  const sessionsLoading = ref(false)

  async function fetchCurrent() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/cash-register/current')
      current.value = data.session
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el estado de la caja.'
    } finally {
      loading.value = false
    }
  }

  async function openSession(payload) {
    const { data } = await api.post('/cash-register/open', payload)
    current.value = data
    return data
  }

  async function closeSession(id, payload) {
    const { data } = await api.put(`/cash-register/${id}/close`, payload)
    current.value = null
    return data
  }

  async function fetchSessions({ page = 1, perPage = 5 } = {}) {
    sessionsLoading.value = true
    try {
      const { data } = await api.get('/cash-register/sessions', { params: { page, per_page: perPage } })
      sessions.value = data.sessions
      sessionsPagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.per_page }
    } finally {
      sessionsLoading.value = false
    }
  }

  async function fetchSessionDetail(id) {
    const { data } = await api.get(`/cash-register/sessions/${id}`)
    return data
  }

  // Independiente de fetchSessions/sessionsPagination a proposito: la tarjeta
  // "Ultimo cierre" de Apertura de Caja solo necesita 1 sesion, y no debe
  // pisar el estado de paginacion que usa la pagina de Reportes de caja.
  async function fetchLastClosedSession() {
    const { data } = await api.get('/cash-register/sessions', { params: { page: 1, per_page: 1 } })
    return data.sessions.find((s) => s.status === 'Cerrada') || null
  }

  return {
    current,
    loading,
    error,
    sessions,
    sessionsPagination,
    sessionsLoading,
    fetchCurrent,
    openSession,
    closeSession,
    fetchSessions,
    fetchSessionDetail,
    fetchLastClosedSession,
  }
})
