import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStaffSpeciesStore = defineStore('staffSpecies', () => {
  const species = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchSpecies() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/species')
      species.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las especies.'
    } finally {
      loading.value = false
    }
  }

  async function createSpecies(payload) {
    const { data } = await api.post('/species', payload)
    return data
  }

  async function updateSpecies(id, payload) {
    const { data } = await api.put(`/species/${id}`, payload)
    return data
  }

  async function deleteSpecies(id) {
    await api.delete(`/species/${id}`)
  }

  return {
    species,
    loading,
    error,
    fetchSpecies,
    createSpecies,
    updateSpecies,
    deleteSpecies,
  }
})
