<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'

defineProps({
  open: { type: Boolean, default: false },
  log: { type: Object, default: null },
  actionLabel: { type: Function, required: true },
  formatDateTime: { type: Function, required: true },
})

const emit = defineEmits(['close'])

function formatValue(value) {
  if (value === null || value === undefined || value === '') return '(vacío)'
  if (typeof value === 'boolean') return value ? 'Sí' : 'No'
  return value
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open && log" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('close')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          class="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="16" />
        </button>

        <div class="mb-4">
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700">
              {{ log.module }}
            </span>
            <span class="text-xs text-slate-400">{{ formatDateTime(log.createdAt) }}</span>
          </div>
          <h3 class="text-lg font-bold text-slate-900 mt-2">
            {{ log.userName || 'Cuenta eliminada' }} · {{ actionLabel(log.action) }}
          </h3>
          <p class="text-sm text-slate-600 mt-1">{{ log.description }}</p>
        </div>

        <div v-if="log.changes?.length" class="border-t border-slate-100 pt-4">
          <p class="text-xs font-bold uppercase tracking-wide text-slate-400 mb-3">Detalle del movimiento</p>
          <dl class="space-y-3">
            <div v-for="c in log.changes" :key="c.field">
              <dt class="text-xs text-slate-500">{{ c.label }}</dt>
              <dd class="text-sm text-slate-800 font-medium font-mono">
                {{ formatValue(c.old) }} <span class="text-slate-400">→</span> {{ formatValue(c.new) }}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </Teleport>
</template>
