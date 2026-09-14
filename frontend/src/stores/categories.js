import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useCategoriesStore = defineStore('categoriesAdmin', () => {
  const categories = ref([])
  const loading = ref(false)
  const error = ref('')

  // Siempre trae TODO (activas e inactivas) - el filtro de estado se aplica
  // en el frontend (CategoryListPage.vue), no acá. Filtrar en el backend
  // rompia el arbol: una subcategoria inactiva quedaba huerfana si su
  // categoria padre (casi siempre activa) no venia en la misma respuesta.
  async function fetchCategories() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/categories', { params: { status: 'all' } })
      categories.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las categorías.'
    } finally {
      loading.value = false
    }
  }

  function topLevel() {
    return categories.value.filter((c) => !c.parentId)
  }

  function childrenOf(parentId) {
    return categories.value.filter((c) => c.parentId === parentId)
  }

  async function createCategory(payload) {
    const { data } = await api.post('/categories', payload)
    return data
  }

  async function updateCategory(id, payload) {
    const { data } = await api.put(`/categories/${id}`, payload)
    return data
  }

  async function deleteCategory(id) {
    await api.delete(`/categories/${id}`)
  }

  async function deactivateCategory(id) {
    const { data } = await api.put(`/categories/${id}`, { isActive: false })
    return data
  }

  async function reactivateCategory(id) {
    const { data } = await api.put(`/categories/${id}`, { isActive: true })
    return data
  }

  return {
    categories,
    loading,
    error,
    fetchCategories,
    topLevel,
    childrenOf,
    createCategory,
    updateCategory,
    deleteCategory,
    deactivateCategory,
    reactivateCategory,
  }
})
