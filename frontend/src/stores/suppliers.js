import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useSuppliersStore = defineStore('suppliers', () => {
  const suppliers = ref([])
  const loading = ref(false)
  const error = ref('')
  const pagination = ref({ total: 0, page: 1, pages: 1, perPage: 10 })

  async function fetchSuppliers({ search, status, page = 1, perPage = 10 } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = new URLSearchParams()
      params.append('per_page', perPage)
      params.append('page', page)
      if (search) params.append('search', search)
      params.append('status', status || 'active')
      const { data } = await api.get('/suppliers', { params })
      suppliers.value = data.suppliers
      pagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.per_page }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar los proveedores.'
    } finally {
      loading.value = false
    }
  }

  async function fetchSupplierDetail(id) {
    const { data } = await api.get(`/suppliers/${id}`)
    return data
  }

  async function associateProduct(id, payload) {
    const { data } = await api.post(`/suppliers/${id}/products`, payload)
    return data
  }

  async function createSupplier(payload) {
    const { data } = await api.post('/suppliers', payload)
    return data
  }

  async function updateSupplier(id, payload) {
    const { data } = await api.put(`/suppliers/${id}`, payload)
    return data
  }

  async function deleteSupplier(id) {
    await api.delete(`/suppliers/${id}`)
  }

  async function deactivateSupplier(id) {
    const { data } = await api.put(`/suppliers/${id}`, { isActive: false })
    return data
  }

  async function reactivateSupplier(id) {
    const { data } = await api.put(`/suppliers/${id}`, { isActive: true })
    return data
  }

  return {
    suppliers,
    loading,
    error,
    pagination,
    fetchSuppliers,
    fetchSupplierDetail,
    associateProduct,
    createSupplier,
    updateSupplier,
    deleteSupplier,
    deactivateSupplier,
    reactivateSupplier,
  }
})
