<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useCashRegisterStore } from '../../../../stores/cashRegister'
import { formatCOP } from '../../../../lib/pricing'

const route = useRoute()
const cashRegisterStore = useCashRegisterStore()

const sessionId = computed(() => Number(route.params.id))
const session = ref(null)
const loading = ref(true)
const errorMessage = ref('')

async function load() {
  loading.value = true
  try {
    session.value = await cashRegisterStore.fetchSessionDetail(sessionId.value)
  } catch {
    errorMessage.value = 'No se pudo cargar el reporte de esta sesión.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

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
</script>

<template>
  <div class="max-w-3xl">
    <RouterLink
      :to="{ name: 'staff-cash-register-history' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a reportes
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="!session" class="text-sm text-red-600">{{ errorMessage }}</div>

    <template v-else>
      <div class="flex items-start justify-between mb-5">
        <div>
          <h1 class="text-xl font-extrabold text-slate-900">Sesión de caja #{{ session.id }}</h1>
          <p class="text-xs text-slate-500 mt-1">
            Responsable: {{ session.responsibleUserName || '—' }}
          </p>
        </div>
        <span
          class="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full"
          :class="session.status === 'Abierta' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
        >
          {{ session.status }}
        </span>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4">Datos del turno</h3>
        <dl class="grid sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
          <div>
            <dt class="text-xs text-slate-400">Abierta</dt>
            <dd class="text-slate-800 font-medium">{{ formatDateTime(session.openedAt) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Cerrada</dt>
            <dd class="text-slate-800 font-medium">{{ formatDateTime(session.closedAt) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Fondo base</dt>
            <dd class="text-slate-800 font-medium">{{ formatCOP(session.openingAmount) }}</dd>
          </div>
          <div v-if="session.openingNotes">
            <dt class="text-xs text-slate-400">Observaciones de apertura</dt>
            <dd class="text-slate-800 font-medium">{{ session.openingNotes }}</dd>
          </div>
        </dl>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4">Resumen de ingresos/egresos</h3>
        <dl class="space-y-1.5 text-sm">
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
        <div class="mt-3 pt-3 border-t border-slate-100 flex justify-between text-base font-bold text-slate-900">
          <span>Total recaudado</span>
          <span>{{ formatCOP(session.totals.totalRecaudado) }}</span>
        </div>
      </div>

      <div v-if="session.status === 'Cerrada'" class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4">Cuadre de cierre</h3>
        <dl class="grid sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
          <div>
            <dt class="text-xs text-slate-400">Efectivo esperado</dt>
            <dd class="text-slate-800 font-medium">{{ formatCOP(session.expectedCash) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Efectivo contado</dt>
            <dd class="text-slate-800 font-medium">{{ formatCOP(session.countedCash) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Diferencia de cuadre</dt>
            <dd class="font-bold" :class="session.cashDifference === 0 ? 'text-emerald-700' : 'text-red-600'">
              {{ formatCOP(session.cashDifference) }}
            </dd>
          </div>
          <div v-if="session.differenceJustification" class="sm:col-span-2">
            <dt class="text-xs text-slate-400">Justificación</dt>
            <dd class="text-slate-800 font-medium">{{ session.differenceJustification }}</dd>
          </div>
        </dl>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-4">Movimientos de la sesión</h3>
        <div v-if="!session.movements.length" class="text-sm text-slate-500 text-center py-6">
          Sin movimientos en esta sesión.
        </div>
        <RouterLink
          v-for="m in session.movements"
          :key="`${m.kind}-${m.id}`"
          :to="{ name: 'staff-order-detail', params: { id: m.orderId } }"
          class="flex items-center gap-4 py-3 border-b border-slate-50 last:border-0 hover:bg-slate-50 -mx-2 px-2 rounded-lg transition"
        >
          <div
            class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
            :class="m.kind === 'in' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
          >
            <AppIcon :name="m.kind === 'in' ? 'cash' : 'arrow-back-up'" :size="16" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-slate-800">
              Pedido #{{ m.orderId }} — {{ m.kind === 'in' ? m.invoiceNumber : m.reason }}
            </p>
            <p class="text-xs text-slate-400">{{ m.method }} · {{ formatDateTime(m.time) }}</p>
          </div>
          <p class="text-sm font-bold shrink-0" :class="m.kind === 'in' ? 'text-emerald-700' : 'text-red-600'">
            {{ m.kind === 'in' ? '+' : '−' }}{{ formatCOP(m.amount) }}
          </p>
        </RouterLink>
      </div>
    </template>
  </div>
</template>
