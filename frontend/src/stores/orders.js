import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchOrders() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/orders')
      orders.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar tus pedidos.'
    } finally {
      loading.value = false
    }
  }

  async function fetchOrder(id) {
    const { data } = await api.get(`/orders/${id}`)
    return data
  }

  // Recibo interno en PDF (decision 28: sin cufe/DIAN) - mismo patron de
  // descarga por blob autenticado que ya usa stores/reports.js.
  async function downloadInvoicePdf(id, filename) {
    const response = await api.get(`/orders/${id}/invoice/pdf`, { responseType: 'blob' })
    const blobUrl = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `${filename || `recibo-${id}`}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(blobUrl)
  }

  const staffOrders = ref([])
  const staffLoading = ref(false)
  const staffError = ref('')

  async function fetchStaffOrders({ status, search, ownerId } = {}) {
    staffLoading.value = true
    staffError.value = ''
    try {
      const params = {}
      if (status) params.status = status
      if (search) params.search = search
      if (ownerId) params.owner_id = ownerId
      const { data } = await api.get('/orders/staff', { params })
      staffOrders.value = data
    } catch (err) {
      staffError.value = err.response?.data?.message || 'No se pudieron cargar los pedidos.'
    } finally {
      staffLoading.value = false
    }
  }

  async function updateOrderStatus(id, status, extra = {}) {
    const { data } = await api.put(`/orders/staff/${id}`, { status, ...extra })
    return data
  }

  async function registerPayment(id, payload) {
    const { data } = await api.post(`/orders/staff/${id}/payment`, payload)
    return data
  }

  // Punto de venta (decision 81): registra una venta presencial completa
  // (pedido + pago) en una sola accion.
  async function registerWalkinSale(payload) {
    const { data } = await api.post('/orders/staff', payload)
    return data
  }

  // Dashboard de Inicio (decision 47) - KPIs, grafico y actividad reciente.
  const dashboardKpis = ref(null)
  const incomeChart = ref(null)
  const recentPayments = ref([])
  const dashboardLoading = ref(false)

  async function fetchDashboardKpis() {
    const { data } = await api.get('/orders/staff/kpis')
    dashboardKpis.value = data
    return data
  }

  async function fetchIncomeChart(range) {
    dashboardLoading.value = true
    try {
      const { data } = await api.get('/orders/staff/income-chart', { params: { range } })
      incomeChart.value = data
      return data
    } finally {
      dashboardLoading.value = false
    }
  }

  async function fetchRecentPayments(limit = 6) {
    const { data } = await api.get('/orders/staff/recent-payments', { params: { limit } })
    recentPayments.value = data
    return data
  }

  return {
    orders,
    loading,
    error,
    fetchOrders,
    fetchOrder,
    downloadInvoicePdf,
    staffOrders,
    staffLoading,
    staffError,
    fetchStaffOrders,
    updateOrderStatus,
    registerPayment,
    registerWalkinSale,
    dashboardKpis,
    incomeChart,
    recentPayments,
    dashboardLoading,
    fetchDashboardKpis,
    fetchIncomeChart,
    fetchRecentPayments,
  }
})
