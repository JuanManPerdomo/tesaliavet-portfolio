import { defineStore } from 'pinia'
import { ref } from 'vue'

let nextId = 1

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])

  function remove(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  function push(message, type = 'success', duration = 4000) {
    const id = nextId++
    toasts.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => remove(id), duration)
    }
    return id
  }

  function success(message, duration) {
    return push(message, 'success', duration)
  }

  function error(message, duration) {
    return push(message, 'error', duration)
  }

  function info(message, duration) {
    return push(message, 'info', duration)
  }

  return { toasts, push, remove, success, error, info }
})
