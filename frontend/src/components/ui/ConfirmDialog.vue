<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, required: true },
  message: { type: String, required: true },
  confirmLabel: { type: String, default: 'Confirmar' },
  cancelLabel: { type: String, default: 'Cancelar' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('cancel')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-sm w-full p-6">
        <div class="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center mb-4">
          <AppIcon name="alert-triangle" :size="22" />
        </div>

        <h3 class="text-lg font-bold text-slate-900 mb-2">{{ title }}</h3>
        <p class="text-sm text-slate-500 mb-6">{{ message }}</p>

        <div class="flex justify-end gap-3">
          <button
            type="button"
            class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
            @click="emit('cancel')"
          >
            {{ cancelLabel }}
          </button>
          <button
            type="button"
            :disabled="loading"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded-lg transition disabled:opacity-50 disabled:pointer-events-none"
            @click="emit('confirm')"
          >
            {{ loading ? 'Eliminando...' : confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
