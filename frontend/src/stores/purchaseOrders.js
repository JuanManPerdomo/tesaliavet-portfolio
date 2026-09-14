import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const usePurchaseOrdersStore = defineStore('purchaseOrders', () => {
  const purchaseOrders = ref([])
  const loading = ref(false)
  const error = ref('')
  const pagination = ref({ total: 0, page: 1, pages: 1, perPage: 10 })

  async function fetchPurchaseOrders({ search, status, supplierId, page = 1, perPage = 10 } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = new URLSearchParams()
      params.append('per_page', perPage)
      params.append('page', page)
      if (search) params.append('search', search)
      if (supplierId) params.append('supplier_id', supplierId)
      params.append('status', status || 'all')
      const { data } = await api.get('/purchase-orders', { params })
      purchaseOrders.value = data.purchaseOrders
      pagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.per_page }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar las órdenes de compra.'
    } finally {
      loading.value = false
    }
  }

  async function fetchPurchaseOrderDetail(id) {
    const { data } = await api.get(`/purchase-orders/${id}`)
    return data
  }

  async function createPurchaseOrder(payload) {
    const { data } = await api.post('/purchase-orders', payload)
    return data
  }

  async function updatePurchaseOrder(id, payload) {
    const { data } = await api.put(`/purchase-orders/${id}`, payload)
    return data
  }

  async function updateStatus(id, status) {
    const { data } = await api.put(`/purchase-orders/${id}/status`, { status })
    return data
  }

  async function deletePurchaseOrder(id) {
    await api.delete(`/purchase-orders/${id}`)
  }

  async function uploadInvoice(id, file) {
    const formData = new FormData()
    formData.append('invoice', file)
    const { data } = await api.post(`/purchase-orders/${id}/invoice`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  }

  async function removeInvoice(id) {
    const { data } = await api.delete(`/purchase-orders/${id}/invoice`)
    return data
  }

  return {
    purchaseOrders,
    loading,
    error,
    pagination,
    fetchPurchaseOrders,
    fetchPurchaseOrderDetail,
    createPurchaseOrder,
    updatePurchaseOrder,
    updateStatus,
    deletePurchaseOrder,
    uploadInvoice,
    removeInvoice,
  }
})
