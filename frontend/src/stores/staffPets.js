import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStaffPetsStore = defineStore('staffPets', () => {
  const pets = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchPets(search) {
    loading.value = true
    error.value = ''
    try {
      const params = search ? { search } : {}
      const { data } = await api.get('/pets/staff', { params })
      pets.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las mascotas.'
    } finally {
      loading.value = false
    }
  }

  async function fetchPet(id) {
    const { data } = await api.get(`/pets/staff/${id}`)
    return data
  }

  async function updatePet(id, formData) {
    const { data } = await api.put(`/pets/staff/${id}`, formData)
    return data
  }

  async function deletePet(id) {
    await api.delete(`/pets/staff/${id}`)
  }

  async function fetchMedicalRecords(id) {
    const { data } = await api.get(`/pets/staff/${id}/medical-records`)
    return data
  }

  async function fetchVaccinations(id) {
    const { data } = await api.get(`/pets/staff/${id}/vaccinations`)
    return data
  }

  // Para el dashboard del veterinario (panel muy vacío, decision "Panel del
  // veterinario", 2026-09-02) - admin ve lo mismo pero de todo el personal.
  async function fetchRecentPatients(limit = 6) {
    const { data } = await api.get('/pets/staff/recent-patients', { params: { limit } })
    return data
  }

  async function fetchUpcomingVaccines(limit = 6) {
    const { data } = await api.get('/pets/staff/upcoming-vaccines', { params: { limit } })
    return data
  }

  return {
    pets,
    loading,
    error,
    fetchPets,
    fetchPet,
    updatePet,
    deletePet,
    fetchMedicalRecords,
    fetchVaccinations,
    fetchRecentPatients,
    fetchUpcomingVaccines,
  }
})
