import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useAppointmentsStore = defineStore('appointments', () => {
  const appointments = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchAppointments() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/appointments')
      appointments.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar tus citas.'
    } finally {
      loading.value = false
    }
  }

  async function fetchAppointment(id) {
    const { data } = await api.get(`/appointments/${id}`)
    return data
  }

  async function fetchAvailability(dateStr) {
    const { data } = await api.get('/appointments/availability', { params: { date: dateStr } })
    return data
  }

  async function fetchAvailabilitySummary(monthStr) {
    const { data } = await api.get('/appointments/availability-summary', {
      params: { month: monthStr },
    })
    return data
  }

  async function createAppointment(payload) {
    const { data } = await api.post('/appointments', payload)
    return data
  }

  async function cancelAppointment(id, cancelReason) {
    const { data } = await api.put(`/appointments/${id}/cancel`, { cancelReason })
    return data
  }

  const staffAppointments = ref([])
  const staffLoading = ref(false)
  const staffError = ref('')

  async function fetchStaffAppointments(status, assignedToMe, ownerId, petId) {
    staffLoading.value = true
    staffError.value = ''
    try {
      const params = {}
      if (status) params.status = status
      if (assignedToMe) params.assigned_to_me = 'true'
      if (ownerId) params.owner_id = ownerId
      if (petId) params.pet_id = petId
      const { data } = await api.get('/appointments/staff', { params })
      staffAppointments.value = data
    } catch (err) {
      staffError.value = err.response?.data?.message || 'No se pudieron cargar las citas.'
    } finally {
      staffLoading.value = false
    }
  }

  async function updateAppointmentStaff(id, payload) {
    const { data } = await api.put(`/appointments/${id}`, payload)
    return data
  }

  return {
    appointments,
    loading,
    error,
    fetchAppointments,
    fetchAppointment,
    fetchAvailability,
    fetchAvailabilitySummary,
    createAppointment,
    cancelAppointment,
    staffAppointments,
    staffLoading,
    staffError,
    fetchStaffAppointments,
    updateAppointmentStaff,
  }
})
