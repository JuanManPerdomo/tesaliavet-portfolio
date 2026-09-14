<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import KpiTile from '../../components/KpiTile.vue'
import ReportExportButton from '../../components/ReportExportButton.vue'
import { useReportsStore } from '../../../../stores/reports'
import { formatCOP } from '../../../../lib/pricing'

const store = useReportsStore()

const sessionId = ref('')

function load() {
  store.fetchCash({ sessionId: sessionId.value })
}

onMounted(load)

function handleSessionChange() {
  load()
}

function handleExport(format) {
  store.exportReport('cash', format, { sessionId: sessionId.value }, 'reporte_caja')
}

const session = computed(() => store.cash?.session)
const totals = computed(() => session.value?.totals)

function formatTime(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <select
        v-model="sessionId"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-emerald-700"
        @change="handleSessionChange"
      >
        <option value="">Sesión actual / última cerrada</option>
        <option v-for="s in store.cash?.recentSessions || []" :key="s.id" :value="s.id">
          Caja #{{ s.id }} — {{ s.status }} ({{ new Date(s.openedAt).toLocaleDateString('es-CO') }})
        </option>
      </select>
      <div class="flex items-center gap-2">
        <RouterLink
          v-if="session?.status === 'Abierta'"
          :to="{ name: 'staff-cash-register' }"
          class="px-4 py-2.5 rounded-lg text-sm font-semibold bg-emerald-700 text-white hover:bg-emerald-800 flex items-center gap-2"
        >
          <AppIcon name="cash" :size="16" />
          Ir a Caja
        </RouterLink>
        <ReportExportButton :loading="store.exporting" @export="handleExport" />
      </div>
    </div>

    <div v-if="store.loading && !store.cash" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="store.error" class="text-sm text-red-600">{{ store.error }}</div>
    <div v-else-if="!session" class="bg-white rounded-2xl border border-slate-200 p-10 text-center text-sm text-slate-500">
      Todavía no hay ninguna sesión de caja registrada.
    </div>

    <template v-else>
      <div class="grid sm:grid-cols-2 gap-5">
        <KpiTile
          icon="cash"
          label="Total Recaudado"
          :value="formatCOP(totals.totalRecaudado)"
          :sub="session.status === 'Abierta' ? 'Turno en curso' : `Turno cerrado ${formatTime(session.closedAt)}`"
          icon-bg-class="bg-emerald-50"
          icon-color-class="text-emerald-700"
        />
        <KpiTile
          v-if="session.cashDifference !== null"
          icon="alert-triangle"
          label="Discrepancia de Caja"
          :value="formatCOP(session.cashDifference)"
          :sub="
            session.cashDifference === 0
              ? 'Cuadre exacto'
              : session.differenceJustification
                ? `Justificado: ${session.differenceJustification}`
                : 'Sin justificar'
          "
          :icon-bg-class="session.cashDifference === 0 ? 'bg-emerald-50' : 'bg-red-50'"
          :icon-color-class="session.cashDifference === 0 ? 'text-emerald-700' : 'text-red-600'"
        />
        <KpiTile
          v-else
          icon="cash"
          label="Efectivo Esperado en Caja"
          :value="formatCOP(totals.expectedCashLive)"
          icon-bg-class="bg-sky-50"
          icon-color-class="text-sky-700"
        />
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Desglose por Medio de Pago</h3>
          <div class="space-y-3">
            <div>
              <div class="flex justify-between text-xs text-slate-600 mb-1">
                <span class="font-semibold">Efectivo</span>
                <span>{{ formatCOP(totals.netEfectivo) }}</span>
              </div>
              <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-emerald-600 rounded-full"
                  :style="{ width: `${totals.totalRecaudado ? (totals.netEfectivo / totals.totalRecaudado) * 100 : 0}%` }"
                ></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs text-slate-600 mb-1">
                <span class="font-semibold">Transferencia</span>
                <span>{{ formatCOP(totals.netTransferencia) }}</span>
              </div>
              <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-sky-500 rounded-full"
                  :style="{ width: `${totals.totalRecaudado ? (totals.netTransferencia / totals.totalRecaudado) * 100 : 0}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <h3 class="text-sm font-bold text-slate-900 px-6 pt-6 pb-4">Resumen de Movimientos</h3>
          <div v-if="!session.movements?.length" class="p-8 text-sm text-slate-500 text-center">
            Sin movimientos registrados en este turno.
          </div>
          <div v-else class="max-h-80 overflow-y-auto divide-y divide-slate-100">
            <div
              v-for="m in session.movements"
              :key="`${m.kind}-${m.id}`"
              class="flex items-center justify-between gap-3 px-6 py-2.5"
            >
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-800 truncate">
                  {{ m.kind === 'in' ? (m.invoiceNumber || 'Pago') : (m.reason || 'Devolución') }}
                </p>
                <p class="text-xs text-slate-400">{{ formatTime(m.time) }} · {{ m.method }}</p>
              </div>
              <p
                class="text-sm font-bold shrink-0"
                :class="m.kind === 'in' ? 'text-emerald-700' : 'text-red-500'"
              >
                {{ m.kind === 'in' ? '+' : '-' }}{{ formatCOP(m.amount) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
