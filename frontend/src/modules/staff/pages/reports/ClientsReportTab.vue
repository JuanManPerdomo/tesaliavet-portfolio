<script setup>
import { ref, computed, onMounted } from 'vue'
import KpiTile from '../../components/KpiTile.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import ReportDateFilter from '../../components/ReportDateFilter.vue'
import ReportExportButton from '../../components/ReportExportButton.vue'
import { useReportsStore } from '../../../../stores/reports'
import { getPresetRange } from '../../../../lib/reportDatePresets'
import { formatCOP } from '../../../../lib/pricing'

const MONTH_LABELS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

const store = useReportsStore()

const defaultRange = getPresetRange('mes')
const dateFrom = ref(defaultRange.dateFrom)
const dateTo = ref(defaultRange.dateTo)
const search = ref('')
const status = ref('')
const city = ref('')
const page = ref(1)
const perPage = ref(10)

function load() {
  store.fetchClients({
    dateFrom: dateFrom.value,
    dateTo: dateTo.value,
    search: search.value,
    status: status.value,
    city: city.value,
    page: page.value,
    perPage: perPage.value,
  })
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
  store.exportReport('clients', format, { dateFrom: dateFrom.value, dateTo: dateTo.value }, 'reporte_clientes')
}

const byMonthSeries = computed(() => {
  const rows = store.clients?.byMonth || []
  return rows.slice(-12).map((r) => ({ label: `${MONTH_LABELS[r.month - 1]}`, count: r.count }))
})
const maxMonthCount = computed(() => Math.max(...byMonthSeries.value.map((m) => m.count), 1))

const cityDonut = computed(() => {
  const rows = store.clients?.byCity || []
  const total = rows.reduce((sum, r) => sum + r.count, 0)
  const colors = ['#047857', '#0ea5e9', '#f59e0b', '#8b5cf6', '#ef4444']
  const circumference = 2 * Math.PI * 50
  let cumulative = 0
  return rows.slice(0, 5).map((r, i) => {
    const length = total > 0 ? (r.count / total) * circumference : 0
    const segment = {
      label: r.city, count: r.count, color: colors[i % colors.length],
      length, offset: -cumulative, circumference,
    }
    cumulative += length
    return segment
  })
})

function formatDate(iso) {
  if (!iso) return 'Sin compras'
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

const maxFrequentOrders = computed(() => {
  const list = store.clients?.frequentClients || []
  return Math.max(...list.map((c) => c.ordersCount), 1)
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

    <div v-if="store.loading && !store.clients" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="store.error" class="text-sm text-red-600">{{ store.error }}</div>

    <template v-else-if="store.clients">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiTile
          icon="users"
          label="Clientes Totales"
          :value="store.clients.kpis.total"
          icon-bg-class="bg-emerald-50"
          icon-color-class="text-emerald-700"
        />
        <KpiTile
          icon="user-check"
          label="Activos"
          :value="store.clients.kpis.active"
          :sub="`${store.clients.kpis.activePercent}% del total`"
          icon-bg-class="bg-sky-50"
          icon-color-class="text-sky-700"
        />
        <KpiTile
          icon="plus"
          label="Nuevos en el Período"
          :value="store.clients.kpis.newInPeriod"
          icon-bg-class="bg-cyan-50"
          icon-color-class="text-cyan-700"
        />
        <KpiTile
          icon="archive"
          label="Clientes Inactivos"
          :value="store.clients.kpis.inactive"
          icon-bg-class="bg-amber-50"
          icon-color-class="text-amber-700"
        />
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Clientes registrados por mes</h3>
          <div v-if="!byMonthSeries.length" class="text-sm text-slate-400 text-center py-8">Sin registros.</div>
          <div v-else class="flex items-end gap-2 h-36">
            <div v-for="m in byMonthSeries" :key="m.label" class="flex-1 flex flex-col items-center gap-1">
              <div
                class="w-full bg-emerald-500 rounded-t transition-all"
                :style="{ height: `${(m.count / maxMonthCount) * 100}%`, minHeight: m.count ? '4px' : '0' }"
              ></div>
              <span class="text-[10px] text-slate-400">{{ m.label }}</span>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Distribución por ciudad</h3>
          <div v-if="!cityDonut.length" class="text-sm text-slate-400 text-center py-8">Sin datos de ciudad.</div>
          <div v-else class="flex flex-col items-center">
            <svg viewBox="0 0 120 120" class="w-24 h-24">
              <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="14" />
              <circle
                v-for="seg in cityDonut" :key="seg.label" cx="60" cy="60" r="50" fill="none"
                :stroke="seg.color" stroke-width="14"
                :stroke-dasharray="`${seg.length} ${seg.circumference}`" :stroke-dashoffset="seg.offset"
                transform="rotate(-90 60 60)"
              />
            </svg>
            <div class="flex flex-wrap justify-center gap-2 mt-3 text-[11px]">
              <span v-for="seg in cityDonut" :key="seg.label" class="flex items-center gap-1 text-slate-600">
                <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: seg.color }"></span>
                {{ seg.label }} ({{ seg.count }})
              </span>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Activos vs. Inactivos</h3>
          <div class="flex flex-col items-center justify-center h-full pb-6">
            <svg viewBox="0 0 120 120" class="w-24 h-24">
              <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="14" />
              <circle
                cx="60" cy="60" r="50" fill="none" stroke="#047857" stroke-width="14"
                :stroke-dasharray="`${store.clients.kpis.total ? (store.clients.kpis.active / store.clients.kpis.total) * 2 * Math.PI * 50 : 0} ${2 * Math.PI * 50}`"
                transform="rotate(-90 60 60)"
              />
              <text x="60" y="65" text-anchor="middle" class="fill-slate-900 font-extrabold" style="font-size: 18px">
                {{ store.clients.kpis.activePercent }}%
              </text>
            </svg>
            <div class="flex gap-3 mt-3 text-[11px] text-slate-600">
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-emerald-700"></span> Activos</span>
              <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-slate-200"></span> Inactivos</span>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-1">Clientes frecuentes</h3>
        <p class="text-xs text-slate-400 mb-4">Top 5 por cantidad de pedidos pagados, sobre todo el historial.</p>
        <div v-if="!store.clients.frequentClients.length" class="text-sm text-slate-400 text-center py-8">
          Todavía no hay pedidos pagados registrados.
        </div>
        <div v-else class="space-y-3">
          <div v-for="c in store.clients.frequentClients" :key="c.id">
            <div class="flex justify-between text-xs text-slate-600 mb-1">
              <span class="font-semibold">{{ c.name }}</span>
              <span>{{ c.ordersCount }} {{ c.ordersCount === 1 ? 'pedido' : 'pedidos' }} · {{ formatCOP(c.totalSpent) }}</span>
            </div>
            <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-emerald-600 rounded-full"
                :style="{ width: `${(c.ordersCount / maxFrequentOrders) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <div class="flex flex-wrap gap-2 p-6 pb-4">
          <input
            v-model="search"
            type="text"
            placeholder="Buscar por nombre o correo..."
            class="flex-1 min-w-[180px] border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-700"
            @keyup.enter="handleFilterChange"
          />
          <select
            v-model="status"
            class="border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-700"
            @change="handleFilterChange"
          >
            <option value="">Todos los estados</option>
            <option value="active">Activos</option>
            <option value="inactive">Inactivos</option>
          </select>
          <select
            v-model="city"
            class="border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-700"
            @change="handleFilterChange"
          >
            <option value="">Todas las ciudades</option>
            <option v-for="c in store.clients.byCity" :key="c.city" :value="c.city">{{ c.city }}</option>
          </select>
        </div>

        <div v-if="!store.clients.clients.items.length" class="p-8 text-sm text-slate-500 text-center">
          No hay clientes con estos filtros.
        </div>
        <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
        <div v-else class="md:hidden divide-y divide-slate-100">
          <div v-for="c in store.clients.clients.items" :key="c.id" class="p-4">
            <div class="flex items-start justify-between gap-2">
              <p class="font-semibold text-slate-800 truncate">{{ c.name }}</p>
              <span
                class="shrink-0 text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
                :class="c.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ c.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-1 truncate">{{ c.email }}</p>
            <p class="text-xs text-slate-500">{{ c.phone || '—' }} · {{ c.ciudad || '—' }}</p>
            <p class="text-xs text-slate-400 mt-1">Última compra: {{ formatDate(c.lastPurchaseAt) }}</p>
          </div>
        </div>

        <table v-if="store.clients.clients.items.length" class="hidden md:table w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-y border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
              <th class="px-5 py-3">Cliente</th>
              <th class="px-5 py-3">Correo</th>
              <th class="px-5 py-3">Teléfono</th>
              <th class="px-5 py-3">Ciudad</th>
              <th class="px-5 py-3">Estado</th>
              <th class="px-5 py-3">Última compra</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in store.clients.clients.items"
              :key="c.id"
              class="border-b border-slate-100 last:border-0"
            >
              <td class="px-5 py-3 font-semibold text-slate-800">{{ c.name }}</td>
              <td class="px-5 py-3 text-slate-500">{{ c.email }}</td>
              <td class="px-5 py-3 text-slate-500">{{ c.phone || '—' }}</td>
              <td class="px-5 py-3 text-slate-500">{{ c.ciudad || '—' }}</td>
              <td class="px-5 py-3">
                <span
                  class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
                  :class="c.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                >
                  {{ c.isActive ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-5 py-3 text-slate-500">{{ formatDate(c.lastPurchaseAt) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="px-6">
          <AdminPagination
            :pagination="store.clients.clients"
            item-label="clientes"
            @page-change="handlePageChange"
            @page-size-change="handlePageSizeChange"
          />
        </div>
      </div>
    </template>
  </div>
</template>
