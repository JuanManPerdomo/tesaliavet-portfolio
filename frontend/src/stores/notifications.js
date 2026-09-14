import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

// Contador real de "novedades" para el cliente (PQRS respondidas, pedidos
// pagados/entregados/cancelados, citas confirmadas/completadas/canceladas
// desde su ultima visita a /notificaciones) - equivalente simple del
// sistema que ya tiene el panel de personal (staffNotifications.js,
// decision 51), pero sin tabla de items marcados uno por uno: el cliente
// solo necesita saber si hay algo nuevo, no cual item especifico.
export const useNotificationsStore = defineStore('notifications', () => {
  const unreadCount = ref(0)

  async function fetchSummary() {
    const { data } = await api.get('/notifications/summary')
    unreadCount.value = data.unread
  }

  async function markAsRead() {
    const { data } = await api.post('/notifications/read')
    unreadCount.value = data.unread
  }

  return {
    unreadCount,
    fetchSummary,
    markAsRead,
  }
})
