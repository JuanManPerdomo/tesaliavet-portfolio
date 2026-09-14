import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

const TOKEN_KEY = 'tesaliavet_token'
const REFRESH_TOKEN_KEY = 'tesaliavet_refresh_token'
const USER_KEY = 'tesaliavet_user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const refreshToken = ref(localStorage.getItem(REFRESH_TOKEN_KEY) || '')
  const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  function persist(data) {
    token.value = data.token
    refreshToken.value = data.refreshToken
    user.value = data.user
    localStorage.setItem(TOKEN_KEY, data.token)
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
  }

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    persist(data)
  }

  async function register(payload) {
    const { data } = await api.post('/auth/register', payload)
    persist(data)
  }

  async function fetchMe() {
    const { data } = await api.get('/auth/me')
    user.value = data
    localStorage.setItem(USER_KEY, JSON.stringify(data))
    return data
  }

  async function updateProfile(payload) {
    const { data } = await api.put('/auth/me', payload)
    user.value = data
    localStorage.setItem(USER_KEY, JSON.stringify(data))
    return data
  }

  async function changePassword(payload) {
    const { data } = await api.put('/auth/password', payload)
    return data
  }

  async function forgotPassword(email) {
    const { data } = await api.post('/auth/forgot-password', { email })
    return data
  }

  async function verifyResetCode(email, code) {
    const { data } = await api.post('/auth/verify-reset-code', { email, code })
    return data
  }

  async function resetPassword(email, code, newPassword) {
    const { data } = await api.post('/auth/reset-password', { email, code, newPassword })
    return data
  }

  async function uploadPhoto(file) {
    const formData = new FormData()
    formData.append('photo', file)
    const { data } = await api.put('/auth/me/photo', formData)
    user.value = data
    localStorage.setItem(USER_KEY, JSON.stringify(data))
    return data
  }

  async function removePhoto() {
    const { data } = await api.delete('/auth/me/photo')
    user.value = data
    localStorage.setItem(USER_KEY, JSON.stringify(data))
    return data
  }

  async function logout() {
    // Deja el registro de auditoria (decision 44) antes de borrar el token -
    // best-effort, si falla (red caida, token ya vencido) el cierre de
    // sesion del lado del cliente sigue adelante igual (decision 8: sin
    // invalidacion server-side todavia).
    try {
      await api.post('/auth/logout')
    } catch {
      // ignorado a proposito
    }
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  function hasRole(...roles) {
    return roles.some((role) => user.value?.roles?.includes(role))
  }

  return {
    token,
    refreshToken,
    user,
    login,
    register,
    logout,
    hasRole,
    fetchMe,
    updateProfile,
    changePassword,
    uploadPhoto,
    removePhoto,
    forgotPassword,
    verifyResetCode,
    resetPassword,
  }
})
