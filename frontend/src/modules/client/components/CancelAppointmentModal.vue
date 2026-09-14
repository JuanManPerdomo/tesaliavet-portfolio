<script setup>
import { ref, watch } from 'vue'
import AppIcon from '../../../components/ui/AppIcon.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  appointment: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['cancel', 'confirm'])

const reason = ref('')

watch(
  () => props.open,
  (open) => {
    if (open) reason.value = ''
  }
)

function formatDateTime(isoDateTime) {
  if (!isoDateTime) return '—'
  const dt = new Date(isoDateTime)
  const label = dt.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
  const time = dt.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
  return `${label}, ${time}`
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open && appointment" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('cancel')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-lg w-full overflow-hidden">
        <div class="p-6 md:p-8 bg-red-50/60 border-b border-slate-100 flex flex-col items-center text-center">
          <div class="w-14 h-14 rounded-full bg-red-100 text-red-600 flex items-center justify-center mb-4">
            <AppIcon name="alert-triangle" :size="26" />
          </div>
          <h3 class="text-xl font-bold text-slate-900 mb-2">¿Cancelar esta cita?</h3>
          <p class="text-sm text-slate-500 max-w-sm">
            Esta acción no se puede deshacer. Revisa los detalles antes de confirmar.
          </p>
        </div>

        <div class="p-6 md:p-8 flex flex-col gap-5">
          <div class="bg-slate-50 rounded-lg p-4 border border-slate-100">
            <h4 class="text-sm font-bold text-slate-800 mb-3">Resumen de la cita</h4>
            <ul class="flex flex-col gap-2.5 text-sm">
              <li class="flex items-center justify-between gap-3">
                <span class="flex items-center gap-2 text-slate-500">
                  <AppIcon name="calendar" :size="16" class="text-emerald-700" /> Fecha y hora
                </span>
                <span class="font-medium text-slate-800 text-right">
                  {{ formatDateTime(appointment.appointmentDatetime) }}
                </span>
              </li>
              <li class="flex items-center justify-between gap-3">
                <span class="flex items-center gap-2 text-slate-500">
                  <AppIcon name="stethoscope" :size="16" class="text-emerald-700" /> Motivo
                </span>
                <span class="font-medium text-slate-800 text-right">{{ appointment.reason }}</span>
              </li>
              <li class="flex items-center justify-between gap-3">
                <span class="flex items-center gap-2 text-slate-500">
                  <AppIcon name="paw" :size="16" class="text-emerald-700" /> Paciente
                </span>
                <span class="font-medium text-slate-800 text-right">
                  {{ appointment.pet?.name }}
                </span>
              </li>
            </ul>
          </div>

          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-2" for="cancel-reason">
              Motivo de cancelación
            </label>
            <textarea
              id="cancel-reason"
              v-model="reason"
              rows="3"
              placeholder="Ej. Problemas personales, cambio de horario..."
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            ></textarea>
          </div>

          <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        </div>

        <div class="p-6 md:p-8 pt-0 flex flex-col sm:flex-row gap-3 justify-end">
          <button
            type="button"
            class="w-full sm:w-auto px-6 py-2.5 rounded-lg border border-emerald-700 text-emerald-700 text-sm font-semibold hover:bg-emerald-50 transition"
            @click="emit('cancel')"
          >
            No, mantener cita
          </button>
          <button
            type="button"
            :disabled="loading"
            class="w-full sm:w-auto px-6 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-semibold transition disabled:opacity-50 disabled:pointer-events-none"
            @click="emit('confirm', reason)"
          >
            {{ loading ? 'Cancelando...' : 'Sí, cancelar cita' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
