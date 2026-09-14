import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../lib/api'

export const useStaffUsersStore = defineStore('staffUsers', () => {
  const users = ref([])
  const roles = ref([])
  const loading = ref(false)
  const error = ref('')
  const pagination = ref({ total: 0, page: 1, pages: 1, perPage: 10 })

  async function fetchUsers({ role, search, page = 1, perPage = 10 } = {}) {
    loading.value = true
    error.value = ''
    try {
      const params = { page, per_page: perPage }
      if (role) params.role = role
      if (search) params.search = search
      const { data } = await api.get('/staff/users', { params })
      users.value = data.users
      pagination.value = { total: data.total, page: data.page, pages: data.pages, perPage: data.per_page }
    } catch (err) {
      error.value = err.response?.data?.message || 'No se pudieron cargar los usuarios.'
    } finally {
      loading.value = false
    }
  }

  async function fetchRoles() {
    const { data } = await api.get('/staff/roles')
    roles.value = data
  }

  async function updateRoles(userId, roleNames) {
    const { data } = await api.put(`/staff/users/${userId}/roles`, { roles: roleNames })
    return data
  }

  async function updateUser(userId, payload) {
    const { data } = await api.put(`/staff/users/${userId}`, payload)
    return data
  }

  async function createUser(payload) {
    const { data } = await api.post('/staff/users', payload)
    return data
  }

  async function updateStatus(userId, isActive) {
    const { data } = await api.put(`/staff/users/${userId}/status`, { isActive })
    return data
  }

  async function deleteUser(userId) {
    await api.delete(`/staff/users/${userId}`)
  }

  return {
    users,
    roles,
    loading,
    error,
    pagination,
    fetchUsers,
    fetchRoles,
    updateRoles,
    updateUser,
    createUser,
    updateStatus,
    deleteUser,
  }
})
