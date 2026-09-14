import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const usePetsStore = defineStore('pets', () => {
  const pets = ref([])
  const loading = ref(false)
  const error = ref('')

  const species = ref([])
  const breeds = ref([])

  async function fetchPets() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/pets')
      pets.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar tus mascotas.'
    } finally {
      loading.value = false
    }
  }

  async function fetchPet(id) {
    const { data } = await api.get(`/pets/${id}`)
    return data
  }

  async function fetchMedicalRecords(id) {
    const { data } = await api.get(`/pets/${id}/medical-records`)
    return data
  }

  async function fetchVaccinations(id) {
    const { data } = await api.get(`/pets/${id}/vaccinations`)
    return data
  }

  async function fetchSpecies() {
    // Solo especies de mascotas (Perro, Gato...): desde que existe la
    // categoria padre "Ganaderia" (ver decision 19/20 en CLAUDE.md), el
    // catalogo de especies tambien incluye Bovino/Porcino/etc, que no
    // aplican para el registro de una mascota de cliente.
    const { data: categories } = await api.get('/catalog/categories')
    const petsCategory = categories.find((c) => c.name === 'Mascotas' && !c.parentId)
    const { data } = await api.get('/catalog/species', {
      params: petsCategory ? { category_id: petsCategory.id } : {},
    })
    species.value = data
  }

  async function fetchBreeds(speciesId) {
    if (!speciesId) {
      breeds.value = []
      return
    }
    const { data } = await api.get('/catalog/breeds', { params: { species_id: speciesId } })
    breeds.value = data
  }

  async function createPet(formData) {
    const { data } = await api.post('/pets', formData)
    return data
  }

  async function updatePet(id, formData) {
    const { data } = await api.put(`/pets/${id}`, formData)
    return data
  }

  async function deletePet(id) {
    await api.delete(`/pets/${id}`)
  }

  const vaccines = ref([])

  async function fetchVaccines() {
    const { data } = await api.get('/catalog/vaccines')
    vaccines.value = data
  }

  async function createMedicalRecord(petId, payload) {
    const { data } = await api.post(`/pets/${petId}/medical-records`, payload)
    return data
  }

  async function createVaccination(petId, payload) {
    const { data } = await api.post(`/pets/${petId}/vaccinations`, payload)
    return data
  }

  return {
    pets,
    loading,
    error,
    species,
    breeds,
    vaccines,
    fetchPets,
    fetchPet,
    fetchMedicalRecords,
    fetchVaccinations,
    fetchSpecies,
    fetchBreeds,
    fetchVaccines,
    createPet,
    updatePet,
    deletePet,
    createMedicalRecord,
    createVaccination,
  }
})
