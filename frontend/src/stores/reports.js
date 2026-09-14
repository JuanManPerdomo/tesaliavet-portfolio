import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

function buildParams(filters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') params.append(key, value)
  })
  return params
}

export const useReportsStore = defineStore('reports', () => {
  const financial = ref(null)
  const inventory = ref(null)
  const clients = ref(null)
  const appointments = ref(null)
  const cash = ref(null)
  const loading = ref(false)
  const error = ref('')
  const exporting = ref(false)

  async function fetchFinancial(filters) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/reports/financial', { params: buildParams(filters) })
      financial.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el reporte financiero.'
    } finally {
      loading.value = false
    }
  }

  async function fetchInventory(filters) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/reports/inventory', { params: buildParams(filters) })
      inventory.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el reporte de inventario.'
    } finally {
      loading.value = false
    }
  }

  async function fetchClients(filters) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/reports/clients', { params: buildParams(filters) })
      clients.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el reporte de clientes.'
    } finally {
      loading.value = false
    }
  }

  async function fetchAppointments(filters) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/reports/appointments', { params: buildParams(filters) })
      appointments.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el resumen de citas.'
    } finally {
      loading.value = false
    }
  }

  async function fetchCash(filters) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/reports/cash', { params: buildParams(filters) })
      cash.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el reporte de caja.'
    } finally {
      loading.value = false
    }
  }

  async function exportReport(type, format, filters, filename) {
    exporting.value = true
    try {
      const response = await api.get(`/reports/${type}/export`, {
        params: buildParams({ ...filters, format }),
        responseType: 'blob',
      })
      const blobUrl = URL.createObjectURL(response.data)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `${filename}.${format}`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(blobUrl)
    } finally {
      exporting.value = false
    }
  }

  return {
    financial,
    inventory,
    clients,
    appointments,
    cash,
    loading,
    error,
    exporting,
    fetchFinancial,
    fetchInventory,
    fetchClients,
    fetchAppointments,
    fetchCash,
    exportReport,
  }
})
