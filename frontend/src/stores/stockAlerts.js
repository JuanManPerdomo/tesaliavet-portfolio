import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStockAlertsStore = defineStore('stockAlerts', () => {
  const alerts = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchAlerts(status = 'Activa') {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/stock-alerts', { params: { status } })
      alerts.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las alertas de stock.'
    } finally {
      loading.value = false
    }
  }

  return {
    alerts,
    loading,
    error,
    fetchAlerts,
  }
})
