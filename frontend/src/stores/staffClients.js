import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStaffClientsStore = defineStore('staffClients', () => {
  const clients = ref([])
  const loading = ref(false)
  const error = ref('')
  const pagination = ref({ total: 0, page: 1, pages: 1, perPage: 10 })

  const stats = ref(null)
  const statsLoading = ref(false)

  async function fetchClients({ search, status, city, page = 1, perPage = 10 } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = new URLSearchParams()
      params.append('per_page', perPage)
      params.append('page', page)
      if (search) params.append('search', search)
      if (city) params.append('city', city)
      params.append('status', status || 'active')
      const { data } = await api.get('/staff/clients', { params })
      clients.value = data.clients
      pagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.per_page }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar los clientes.'
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    statsLoading.value = true
    try {
      const { data } = await api.get('/staff/clients/stats')
      stats.value = data
    } finally {
      statsLoading.value = false
    }
  }

  async function fetchClient(id) {
    const { data } = await api.get(`/staff/clients/${id}`)
    return data
  }

  async function fetchClientPets(id) {
    const { data } = await api.get(`/staff/clients/${id}/pets`)
    return data
  }

  async function updateClient(id, payload) {
    const { data } = await api.put(`/staff/clients/${id}`, payload)
    return data
  }

  async function deactivateClient(id) {
    const { data } = await api.put(`/staff/clients/${id}`, { isActive: false })
    return data
  }

  async function reactivateClient(id) {
    const { data } = await api.put(`/staff/clients/${id}`, { isActive: true })
    return data
  }

  return {
    clients,
    loading,
    error,
    pagination,
    stats,
    statsLoading,
    fetchClients,
    fetchStats,
    fetchClient,
    fetchClientPets,
    updateClient,
    deactivateClient,
    reactivateClient,
  }
})
