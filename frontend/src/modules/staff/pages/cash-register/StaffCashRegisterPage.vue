<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import KpiTile from '../../components/KpiTile.vue'
import CloseCashRegisterModal from './CloseCashRegisterModal.vue'
import { useCashRegisterStore } from '../../../../stores/cashRegister'
import { useAuthStore } from '../../../../stores/auth'
import { useToastStore } from '../../../../stores/toast'
import { formatCOP } from '../../../../lib/pricing'

const cashRegisterStore = useCashRegisterStore()
const authStore = useAuthStore()
const toastStore = useToastStore()

const lastClosed = ref(null)

const openingAmount = ref('')
const openingNotes = ref('')
const opening = ref(false)
const openError = ref('')

const showCloseModal = ref(false)
const closing = ref(false)
const closeError = ref('')

const movements = computed(() => cashRegisterStore.current?.movements || [])

// Solo quien abrio la caja o un admin puede cerrarla (gap real señalado por
// Juan Manuel, 2026-09-02) - se oculta el boton en vez de dejar que
// cualquiera lo intente y se tope con el 403 del backend.
const canCloseSession = computed(
  () =>
    authStore.hasRole('admin') ||
    cashRegisterStore.current?.responsibleUserId === authStore.user?.id
)

async function load() {
  await cashRegisterStore.fetchCurrent()
  if (!cashRegisterStore.current) {
    await loadLastClosed()
  }
}

async function loadLastClosed() {
  lastClosed.value = await cashRegisterStore.fetchLastClosedSession()
}

onMounted(load)

async function handleOpen() {
  openError.value = ''
  opening.value = true
  try {
    await cashRegisterStore.openSession({
      openingAmount: openingAmount.value,
      notes: openingNotes.value.trim() || undefined,
    })
    toastStore.success('Caja abierta.')
    openingAmount.value = ''
    openingNotes.value = ''
    await cashRegisterStore.fetchCurrent()
  } catch (err) {
    openError.value = err.response?.data?.message || 'No se pudo abrir la caja.'
  } finally {
    opening.value = false
  }
}

function openCloseModal() {
  closeError.value = ''
  showCloseModal.value = true
}

async function handleClose(payload) {
  closing.value = true
  closeError.value = ''
  try {
    await cashRegisterStore.closeSession(cashRegisterStore.current.id, payload)
    toastStore.success('Caja cerrada.')
    showCloseModal.value = false
    load()
  } catch (err) {
    closeError.value = err.response?.data?.message || 'No se pudo cerrar la caja.'
  } finally {
    closing.value = false
  }
}

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
  <div>
    <div v-if="cashRegisterStore.loading" class="text-sm text-slate-500">Cargando...</div>

    <!-- Sin sesion abierta: Apertura de Caja -->
    <template v-else-if="!cashRegisterStore.current">
      <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Apertura de Caja</h1>
      <p class="text-sm text-slate-500 mb-6">
        Inicia una nueva sesión de caja para procesar pagos y devoluciones.
      </p>

      <div class="grid lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6">
          <div class="mb-4">
            <label class="block text-xs font-semibold text-slate-500 mb-1">Monto base inicial *</label>
            <input
              v-model="openingAmount"
              type="number"
              min="0"
              step="0.01"
              placeholder="0"
              class="w-full border border-slate-200 rounded-lg px-4 py-3 text-2xl font-bold text-slate-900 focus:outline-none focus:border-emerald-700"
            />
            <p class="text-xs text-slate-400 mt-1">Efectivo disponible en caja al momento de abrir.</p>
          </div>

          <div class="mb-4">
            <label class="block text-xs font-semibold text-slate-500 mb-1">Usuario responsable</label>
            <div class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-500 bg-slate-50">
              {{ authStore.user?.firstName }} {{ authStore.user?.lastName }}
            </div>
            <p class="text-xs text-slate-400 mt-1">
              El responsable siempre es quien abre la caja — no se puede asignar a otra persona.
            </p>
          </div>

          <div class="mb-4">
            <label class="block text-xs font-semibold text-slate-500 mb-1">Observaciones (opcional)</label>
            <textarea
              v-model="openingNotes"
              rows="2"
              placeholder="Ingresa cualquier nota relevante sobre la apertura..."
              class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 resize-none focus:outline-none focus:border-emerald-700"
            ></textarea>
          </div>

          <p v-if="openError" class="text-sm text-red-600 mb-3">{{ openError }}</p>
          <PrimaryButton :loading="opening" class="gap-2" @click="handleOpen">
            <AppIcon name="shield-check" :size="14" />
            Abrir nueva caja
          </PrimaryButton>
        </div>

        <div class="space-y-4">
          <div v-if="lastClosed" class="bg-white rounded-2xl border border-slate-200 p-5">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-bold text-slate-900">Último cierre</h3>
              <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                Cerrada
              </span>
            </div>
            <dl class="space-y-2 text-sm">
              <div class="flex justify-between">
                <dt class="text-slate-500">ID de sesión</dt>
                <dd class="font-semibold text-slate-800">#{{ lastClosed.id }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-slate-500">Fecha de cierre</dt>
                <dd class="font-semibold text-slate-800">{{ formatDateTime(lastClosed.closedAt) }}</dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-slate-500">Total recaudado</dt>
                <dd class="font-semibold text-slate-800">{{ formatCOP(lastClosed.totals.totalRecaudado) }}</dd>
              </div>
            </dl>
            <div
              class="mt-3 rounded-lg px-3 py-2 text-xs font-semibold"
              :class="lastClosed.cashDifference === 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'"
            >
              <template v-if="lastClosed.cashDifference === 0">Cuadre perfecto — sin diferencia.</template>
              <template v-else>Diferencia de {{ formatCOP(lastClosed.cashDifference) }} detectada.</template>
            </div>
          </div>

          <RouterLink
            :to="{ name: 'staff-cash-register-history' }"
            class="w-full px-4 py-3 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center justify-between"
          >
            Ver reportes anteriores
            <AppIcon name="chevron-right" :size="16" />
          </RouterLink>
        </div>
      </div>
    </template>

    <!-- Sesion abierta: Estado de Caja -->
    <template v-else>
      <div class="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Estado de Caja</h1>
          <p class="text-sm text-slate-500">
            Sesión #{{ cashRegisterStore.current.id }} — abierta {{ formatDateTime(cashRegisterStore.current.openedAt) }}
          </p>
        </div>
        <button
          v-if="canCloseSession"
          type="button"
          class="px-4 py-2.5 bg-red-50 text-red-600 border border-red-200 rounded-lg text-sm font-semibold hover:bg-red-100 flex items-center gap-2"
          @click="openCloseModal"
        >
          <AppIcon name="shield-check" :size="14" />
          Cerrar caja
        </button>
      </div>

      <div class="bg-emerald-50 border border-emerald-100 rounded-2xl p-4 mb-6 flex items-center justify-between flex-wrap gap-2">
        <div>
          <p class="text-xs font-bold text-emerald-700 uppercase tracking-wide">Sesión activa · Caja abierta</p>
          <p class="text-sm text-slate-700 mt-1">
            Responsable: <strong>{{ cashRegisterStore.current.responsibleUserName }}</strong>
          </p>
          <p v-if="!canCloseSession" class="text-xs text-slate-500 mt-1">
            Solo {{ cashRegisterStore.current.responsibleUserName }} o un administrador puede cerrar esta caja.
          </p>
        </div>
      </div>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <KpiTile
          icon="cash"
          label="Efectivo esperado en caja"
          :value="formatCOP(cashRegisterStore.current.totals.expectedCashLive)"
          :sub="`Incluye base de ${formatCOP(cashRegisterStore.current.openingAmount)}`"
        />
        <KpiTile
          icon="cash"
          label="Efectivo"
          :value="formatCOP(cashRegisterStore.current.totals.netEfectivo)"
          :sub="`${cashRegisterStore.current.totals.paymentsCount} pago(s)`"
          icon-bg-class="bg-sky-50"
          icon-color-class="text-sky-700"
        />
        <KpiTile
          icon="arrow-back-up"
          label="Transferencias"
          :value="formatCOP(cashRegisterStore.current.totals.netTransferencia)"
          icon-bg-class="bg-violet-50"
          icon-color-class="text-violet-700"
        />
        <KpiTile
          icon="chart-bar"
          label="Total recaudado"
          :value="formatCOP(cashRegisterStore.current.totals.totalRecaudado)"
          sub="Efectivo + Transferencias"
          icon-bg-class="bg-emerald-50"
          icon-color-class="text-emerald-700"
        />
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-4">Movimientos de la sesión</h3>

        <div v-if="!movements.length" class="text-sm text-slate-500 text-center py-6">
          Sin movimientos todavía en esta sesión.
        </div>

        <RouterLink
          v-for="m in movements"
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

    <CloseCashRegisterModal
      :open="showCloseModal"
      :session="cashRegisterStore.current"
      :saving="closing"
      :server-error="closeError"
      @close="showCloseModal = false"
      @submit="handleClose"
    />
  </div>
</template>
