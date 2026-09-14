<script setup>
import { ref } from 'vue'
import AppIcon from '../../../components/ui/AppIcon.vue'

defineProps({
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['export'])

const open = ref(false)

function handleExport(format) {
  open.value = false
  emit('export', format)
}
</script>

<template>
  <div class="relative">
    <button
      type="button"
      class="flex items-center gap-2 px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-50"
      :disabled="loading"
      @click="open = !open"
    >
      <AppIcon name="download" :size="16" />
      {{ loading ? 'Exportando...' : 'Exportar' }}
      <AppIcon name="chevron-down" :size="14" />
    </button>

    <template v-if="open">
      <div class="fixed inset-0 z-10" @click="open = false"></div>
      <div class="absolute right-0 mt-2 w-40 bg-white border border-slate-200 rounded-xl shadow-lg py-2 z-20">
        <button
          type="button"
          class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-emerald-50"
          @click="handleExport('csv')"
        >
          Exportar CSV
        </button>
        <button
          type="button"
          class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-emerald-50"
          @click="handleExport('pdf')"
        >
          Exportar PDF
        </button>
      </div>
    </template>
  </div>
</template>
