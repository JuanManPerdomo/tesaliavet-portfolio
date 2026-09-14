import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStaffVaccinesStore = defineStore('staffVaccines', () => {
  const vaccines = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchVaccines() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/vaccines')
      vaccines.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las vacunas.'
    } finally {
      loading.value = false
    }
  }

  async function createVaccine(payload) {
    const { data } = await api.post('/vaccines', payload)
    return data
  }

  async function updateVaccine(id, payload) {
    const { data } = await api.put(`/vaccines/${id}`, payload)
    return data
  }

  async function deleteVaccine(id) {
    await api.delete(`/vaccines/${id}`)
  }

  return {
    vaccines,
    loading,
    error,
    fetchVaccines,
    createVaccine,
    updateVaccine,
    deleteVaccine,
  }
})
