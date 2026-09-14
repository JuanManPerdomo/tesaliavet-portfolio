import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStaffStore = defineStore('staff', () => {
  const profile = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function fetchProfile() {
    loading.value = true
    error.value = ''
    try {
      const { data } = await api.get('/staff/me')
      profile.value = data
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudo cargar el panel.'
    } finally {
      loading.value = false
    }
  }

  return { profile, loading, error, fetchProfile }
})
