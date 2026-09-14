import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../lib/api'

export const useCartStore = defineStore('cart', () => {
  const cart = ref(null)
  const loading = ref(false)
  const error = ref('')

  const itemCount = computed(() => cart.value?.items?.length || 0)

  async function fetchCart() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/cart')
      cart.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el carrito.'
    } finally {
      loading.value = false
    }
  }

  async function addItem(productId, quantity = 1) {
    const { data } = await api.post('/cart/items', { productId, quantity })
    cart.value = data
    return data
  }

  async function updateItem(itemId, quantity) {
    const { data } = await api.put(`/cart/items/${itemId}`, { quantity })
    cart.value = data
    return data
  }

  async function removeItem(itemId) {
    const { data } = await api.delete(`/cart/items/${itemId}`)
    cart.value = data
    return data
  }

  async function checkout(payload) {
    const { data } = await api.post('/cart/checkout', payload)
    cart.value = null // el backend abre un carrito nuevo vacío; se recarga con fetchCart
    return data
  }

  return {
    cart,
    loading,
    error,
    itemCount,
    fetchCart,
    addItem,
    updateItem,
    removeItem,
    checkout,
  }
})
