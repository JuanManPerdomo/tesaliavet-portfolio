import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useReturnsStore = defineStore('returns', () => {
  const returns = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchStaffReturns({ search } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = {}
      if (search) params.search = search
      const { data } = await api.get('/orders/staff/returns', { params })
      returns.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las devoluciones.'
    } finally {
      loading.value = false
    }
  }

  async function createReturn(orderId, payload) {
    const { data } = await api.post(`/orders/staff/${orderId}/returns`, payload)
    return data
  }

  return { returns, loading, error, fetchStaffReturns, createReturn }
})
