import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useAuditStore = defineStore('audit', () => {
  const logs = ref([])
  const users = ref([])
  const loading = ref(false)
  const error = ref('')
  const pagination = ref({ total: 0, page: 1, pages: 1, perPage: 20 })

  async function fetchLogs({ userId, module, action, dateFrom, dateTo, page = 1, perPage = 20 } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = new URLSearchParams()
      params.append('page', page)
      params.append('perPage', perPage)
      if (userId) params.append('userId', userId)
      if (module) params.append('module', module)
      if (action) params.append('action', action)
      if (dateFrom) params.append('dateFrom', dateFrom)
      if (dateTo) params.append('dateTo', dateTo)
      const { data } = await api.get('/audit', { params })
      logs.value = data.items
      pagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.perPage }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el registro de auditoría.'
    } finally {
      loading.value = false
    }
  }

  async function fetchUsers() {
    const { data } = await api.get('/audit/users')
    users.value = data
  }

  return {
    logs,
    users,
    loading,
    error,
    pagination,
    fetchLogs,
    fetchUsers,
  }
})
