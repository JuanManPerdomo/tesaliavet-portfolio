<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import KpiTile from '../../components/KpiTile.vue'
import IncomeChart from '../../components/IncomeChart.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import ReportDateFilter from '../../components/ReportDateFilter.vue'
import ReportExportButton from '../../components/ReportExportButton.vue'
import { useReportsStore } from '../../../../stores/reports'
import { formatCOP } from '../../../../lib/pricing'
import { getPresetRange } from '../../../../lib/reportDatePresets'

const store = useReportsStore()

const defaultRange = getPresetRange('mes')
const dateFrom = ref(defaultRange.dateFrom)
const dateTo = ref(defaultRange.dateTo)
const page = ref(1)
const perPage = ref(5)

function load() {
  store.fetchFinancial({ dateFrom: dateFrom.value, dateTo: dateTo.value, page: page.value, perPage: perPage.value })
}

onMounted(load)

function handleFilterChange() {
  page.value = 1
  load()
}

function handlePageChange(p) {
  page.value = p
  load()
}

function handlePageSizeChange(size) {
  perPage.value = size
  page.value = 1
  load()
}

function handleExport(format) {
  store.exportReport('financial', format, { dateFrom: dateFrom.value, dateTo: dateTo.value }, 'reporte_financiero')
}

const paymentDonut = computed(() => {
  const methods = store.financial?.paymentMethods || {}
  // El % del donut es por monto (dinero recaudado) - un pago grande pesa mas
  // que varios chicos, por eso se muestra tambien la cantidad de pagos
  // aparte, para no confundir "cuanta plata entro" con "cuantas ventas hubo".
  const total = Object.values(methods).reduce((sum, m) => sum + m.amount, 0)
  const colors = { Efectivo: '#047857', Transferencia: '#0ea5e9' }
  const circumference = 2 * Math.PI * 50
  let cumulative = 0
  return Object.entries(methods).map(([label, m]) => {
    const length = total > 0 ? (m.amount / total) * circumference : 0
    const segment = {
      label,
      amount: m.amount,
      count: m.count,
      percent: total > 0 ? Math.round((m.amount / total) * 100) : 0,
      color: colors[label] || '#94a3b8',
      length,
      offset: -cumulative,
      circumference,
    }
    cumulative += length
    return segment
  })
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <ReportDateFilter
        v-model:date-from="dateFrom"
        v-model:date-to="dateTo"
        @change="handleFilterChange"
      />
      <ReportExportButton :loading="store.exporting" @export="handleExport" />
    </div>

    <div v-if="store.loading && !store.financial" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="store.error" class="text-sm text-red-600">{{ store.error }}</div>

    <template v-else-if="store.financial">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiTile
          icon="cash"
          label="Ingresos Netos"
          :value="formatCOP(store.financial.kpis.incomeTotal)"
          sub="Ventas menos devoluciones"
          icon-bg-class="bg-emerald-50"
          icon-color-class="text-emerald-700"
        />
        <KpiTile
          icon="file-invoice"
          label="Facturas Emitidas"
          :value="store.financial.kpis.invoicesEmitted"
          :sub="`${store.financial.kpis.invoicesVoided} anuladas`"
          icon-bg-class="bg-sky-50"
          icon-color-class="text-sky-700"
        />
        <KpiTile
          icon="tag"
          label="Ticket Promedio"
          :value="formatCOP(store.financial.kpis.averageTicket)"
          icon-bg-class="bg-cyan-50"
          icon-color-class="text-cyan-700"
        />
        <KpiTile
          icon="arrow-back-up"
          label="Devoluciones"
          :value="formatCOP(store.financial.kpis.returnsTotal)"
          :sub="`${store.financial.kpis.returnsCount} procesadas`"
          icon-bg-class="bg-amber-50"
          icon-color-class="text-amber-700"
        />
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2 mb-4">
            <AppIcon name="chart-bar" :size="16" class="text-emerald-700" />
            Evolución de Ingresos
          </h3>
          <IncomeChart :series="store.financial.chart" :loading="store.loading" />
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Métodos de Pago</h3>
          <div v-if="!paymentDonut.length" class="text-sm text-slate-400 text-center py-8">Sin pagos en el rango.</div>
          <div v-else class="flex flex-col items-center">
            <svg viewBox="0 0 120 120" class="w-28 h-28">
              <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="14" />
              <circle
                v-for="seg in paymentDonut"
                :key="seg.label"
                cx="60"
                cy="60"
                r="50"
                fill="none"
                :stroke="seg.color"
                stroke-width="14"
                :stroke-dasharray="`${seg.length} ${seg.circumference}`"
                :stroke-dashoffset="seg.offset"
                transform="rotate(-90 60 60)"
              />
            </svg>
            <div class="w-full mt-3 space-y-1.5">
              <div v-for="seg in paymentDonut" :key="seg.label" class="flex items-center justify-between text-xs">
                <span class="flex items-center gap-1.5 text-slate-600">
                  <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: seg.color }"></span>
                  {{ seg.label }}
                </span>
                <span class="text-slate-500 text-right">
                  {{ seg.count }} {{ seg.count === 1 ? 'pago' : 'pagos' }} ·
                  <span class="font-semibold text-slate-800">{{ formatCOP(seg.amount) }}</span>
                  ({{ seg.percent }}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <h3 class="text-sm font-bold text-slate-900 px-6 pt-6 pb-4">Facturas Recientes</h3>
        <div v-if="!store.financial.invoices.items.length" class="p-8 text-sm text-slate-500 text-center">
          No hay facturas en este rango.
        </div>
        <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
        <div v-else class="md:hidden divide-y divide-slate-100">
          <div v-for="inv in store.financial.invoices.items" :key="inv.invoiceNumber" class="p-4">
            <div class="flex items-start justify-between gap-2">
              <p class="font-semibold text-slate-800">{{ inv.invoiceNumber }}</p>
              <span
                class="shrink-0 text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
                :class="inv.status === 'Emitida' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
              >
                {{ inv.status }}
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-1">{{ inv.clientName }}</p>
            <p class="text-xs text-slate-400">
              {{ new Date(inv.issueDate).toLocaleDateString('es-CO') }} · {{ inv.method || '—' }}
            </p>
            <p class="text-sm font-semibold text-slate-800 mt-1">{{ formatCOP(inv.total) }}</p>
          </div>
        </div>

        <table v-if="store.financial.invoices.items.length" class="hidden md:table w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-y border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
              <th class="px-5 py-3">N° Factura</th>
              <th class="px-5 py-3">Cliente</th>
              <th class="px-5 py-3">Fecha</th>
              <th class="px-5 py-3">Método</th>
              <th class="px-5 py-3">Total</th>
              <th class="px-5 py-3">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="inv in store.financial.invoices.items"
              :key="inv.invoiceNumber"
              class="border-b border-slate-100 last:border-0"
            >
              <td class="px-5 py-3 font-semibold text-slate-800">{{ inv.invoiceNumber }}</td>
              <td class="px-5 py-3 text-slate-700">{{ inv.clientName }}</td>
              <td class="px-5 py-3 text-slate-500">{{ new Date(inv.issueDate).toLocaleDateString('es-CO') }}</td>
              <td class="px-5 py-3 text-slate-500">{{ inv.method || '—' }}</td>
              <td class="px-5 py-3 font-semibold text-slate-800">{{ formatCOP(inv.total) }}</td>
              <td class="px-5 py-3">
                <span
                  class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
                  :class="inv.status === 'Emitida' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
                >
                  {{ inv.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <AdminPagination
          :pagination="store.financial.invoices"
          item-label="facturas"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        />
      </div>
    </template>
  </div>
</template>
