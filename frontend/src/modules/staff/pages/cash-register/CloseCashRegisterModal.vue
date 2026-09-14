<script setup>
import { ref, computed, watch } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { formatCOP } from '../../../../lib/pricing'

const props = defineProps({
  open: { type: Boolean, default: false },
  session: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  serverError: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])

const countedCash = ref('')
const justification = ref('')

const difference = computed(() => {
  if (!props.session || countedCash.value === '') return null
  return Number(countedCash.value) - props.session.totals.expectedCashLive
})

const differenceRequiresJustification = computed(() => difference.value !== null && difference.value !== 0)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      countedCash.value = ''
      justification.value = ''
    }
  }
)

function formatDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function handleSubmit() {
  if (countedCash.value === '') return
  if (differenceRequiresJustification.value && !justification.value.trim()) return

  emit('submit', {
    countedCash: countedCash.value,
    justification: justification.value.trim() || undefined,
  })
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open && session" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('close')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          class="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="16" />
        </button>

        <h3 class="text-lg font-bold text-slate-900 mb-5">Cierre de Caja</h3>

        <div class="grid sm:grid-cols-2 gap-5">
          <!-- Resumen de turno -->
          <div>
            <h4 class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">Resumen del turno</h4>
            <p class="text-sm text-slate-700 mb-3">
              Responsable: <strong>{{ session.responsibleUserName }}</strong><br />
              <span class="text-xs text-slate-400">Abierta el {{ formatDateTime(session.openedAt) }}</span>
            </p>
            <dl class="space-y-1.5 text-sm">
              <div class="flex justify-between">
                <dt class="text-slate-500">Fondo base</dt>
                <dd class="font-semibold text-slate-800">{{ formatCOP(session.openingAmount) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-slate-500">Ventas en efectivo</dt>
                <dd class="font-semibold text-slate-800">{{ formatCOP(session.totals.paymentsEfectivo) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-slate-500">Ventas por transferencia</dt>
                <dd class="font-semibold text-slate-800">{{ formatCOP(session.totals.paymentsTransferencia) }}</dd>
              </div>
              <div class="flex justify-between text-red-600">
                <dt>Devoluciones (efectivo)</dt>
                <dd class="font-semibold">− {{ formatCOP(session.totals.returnsEfectivo) }}</dd>
              </div>
              <div class="flex justify-between text-red-600">
                <dt>Devoluciones (transferencia)</dt>
                <dd class="font-semibold">− {{ formatCOP(session.totals.returnsTransferencia) }}</dd>
              </div>
            </dl>
            <div class="mt-3 pt-3 border-t border-slate-100 flex justify-between text-sm font-bold text-slate-900">
              <span>Total recaudado</span>
              <span>{{ formatCOP(session.totals.totalRecaudado) }}</span>
            </div>

            <div class="mt-4 bg-slate-50 rounded-lg p-3 text-xs text-slate-600 space-y-1">
              <p class="font-bold text-slate-500 uppercase tracking-wide mb-1">Desglose de efectivo esperado</p>
              <div class="flex justify-between"><span>Fondo base inicial</span><span>{{ formatCOP(session.openingAmount) }}</span></div>
              <div class="flex justify-between"><span>Ingresos en efectivo netos</span><span>{{ formatCOP(session.totals.netEfectivo) }}</span></div>
              <div class="flex justify-between font-bold text-slate-800 pt-1 border-t border-slate-200">
                <span>Total efectivo esperado</span><span>{{ formatCOP(session.totals.expectedCashLive) }}</span>
              </div>
            </div>
          </div>

          <!-- Conteo fisico -->
          <form class="space-y-4" @submit.prevent="handleSubmit">
            <p v-if="serverError" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ serverError }}</p>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Efectivo total contado *</label>
              <input
                v-model="countedCash"
                type="number"
                min="0"
                step="0.01"
                required
                placeholder="0"
                class="w-full border border-slate-200 rounded-lg px-3 py-3 text-xl font-bold text-slate-900 focus:outline-none focus:border-emerald-700"
              />
            </div>

            <div
              v-if="difference !== null"
              class="rounded-lg px-3 py-2 text-sm font-semibold"
              :class="difference === 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
            >
              <template v-if="difference === 0">Cuadre perfecto — sin diferencia.</template>
              <template v-else-if="difference > 0">Sobante de {{ formatCOP(difference) }} respecto al efectivo esperado.</template>
              <template v-else>Faltante de {{ formatCOP(Math.abs(difference)) }} respecto al efectivo esperado.</template>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">
                Justificación {{ differenceRequiresJustification ? '(requerida por la diferencia)' : '(opcional)' }}
              </label>
              <textarea
                v-model="justification"
                rows="3"
                :required="differenceRequiresJustification"
                placeholder="Ej. vuelto entregado incorrectamente en factura #..."
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 resize-none focus:outline-none focus:border-emerald-700"
              ></textarea>
            </div>

            <p class="flex items-start gap-2 text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-2">
              <AppIcon name="alert-triangle" :size="14" class="shrink-0 mt-0.5" />
              El cierre quedará registrado en la bitácora de auditoría.
            </p>

            <div class="flex justify-end gap-3 pt-1">
              <button
                type="button"
                class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
                @click="emit('close')"
              >
                Cancelar
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-2xl font-semibold transition inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none"
              >
                <svg v-if="saving" class="animate-spin h-4 w-4 flex-shrink-0" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V4C7.373 4 4 7.373 4 12z"></path>
                </svg>
                Cerrar caja y generar reporte
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>
