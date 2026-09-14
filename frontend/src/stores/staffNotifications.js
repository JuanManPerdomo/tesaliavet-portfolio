import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStaffNotificationsStore = defineStore('staffNotifications', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref('')
  const pagination = ref({ total: 0, page: 1, pages: 1, perPage: 10 })
  const summary = ref(null)

  async function fetchNotifications({ type, read, search, dateFrom, dateTo, page = 1, perPage = 10 } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = new URLSearchParams()
      params.append('page', page)
      params.append('perPage', perPage)
      if (type) params.append('type', type)
      if (read) params.append('read', read)
      if (search) params.append('search', search)
      if (dateFrom) params.append('dateFrom', dateFrom)
      if (dateTo) params.append('dateTo', dateTo)
      const { data } = await api.get('/staff/notifications', { params })
      items.value = data.items
      pagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.perPage }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las notificaciones.'
    } finally {
      loading.value = false
    }
  }

  async function fetchSummary() {
    const { data } = await api.get('/staff/notifications/summary')
    summary.value = data
  }

  async function markAsRead(key) {
    const { data } = await api.post('/staff/notifications/read', { key })
    summary.value = data
    const item = items.value.find((i) => i.key === key)
    if (item) item.read = true
  }

  return {
    items,
    loading,
    error,
    pagination,
    summary,
    fetchNotifications,
    fetchSummary,
    markAsRead,
  }
})
