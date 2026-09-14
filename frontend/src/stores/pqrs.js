import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const usePqrsStore = defineStore('pqrs', () => {
  const items = ref([])
  const pagination = ref({ total: 0, page: 1, perPage: 10, pages: 0 })
  const loading = ref(false)
  const error = ref('')

  async function fetchAll({ status, search, page = 1, perPage = 10 } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = { page, perPage }
      if (status) params.status = status
      if (search) params.search = search
      const { data } = await api.get('/pqrs', { params })
      items.value = data.items
      pagination.value = { total: data.total, page: data.page, perPage: data.perPage, pages: data.pages }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las solicitudes PQRS.'
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    const { data } = await api.get(`/pqrs/${id}`)
    return data
  }

  async function fetchMine() {
    const { data } = await api.get('/pqrs/mine')
    return data
  }

  async function respond(id, payload) {
    const { data } = await api.put(`/pqrs/${id}/respond`, payload)
    return data
  }

  async function reopen(id) {
    const { data } = await api.put(`/pqrs/${id}/reopen`)
    return data
  }

  return { items, pagination, loading, error, fetchAll, fetchOne, fetchMine, respond, reopen }
})
