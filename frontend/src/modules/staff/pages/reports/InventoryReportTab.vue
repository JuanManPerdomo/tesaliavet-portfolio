<script setup>
import { ref, computed, onMounted } from 'vue'
import KpiTile from '../../components/KpiTile.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import ReportExportButton from '../../components/ReportExportButton.vue'
import { useReportsStore } from '../../../../stores/reports'
import { formatCOP } from '../../../../lib/pricing'

const store = useReportsStore()

const page = ref(1)
const perPage = ref(10)

function load() {
  store.fetchInventory({ page: page.value, perPage: perPage.value })
}

onMounted(load)

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
  store.exportReport('inventory', format, {}, 'reporte_inventario')
}

const maxUnitsSold = computed(() => {
  const list = store.inventory?.topProducts || []
  return Math.max(...list.map((p) => p.unitsSold), 1)
})

const categoryDonut = computed(() => {
  const rows = store.inventory?.byCategory || []
  const total = rows.reduce((sum, r) => sum + r.count, 0)
  const colors = ['#047857', '#0ea5e9', '#f59e0b', '#8b5cf6', '#ef4444']
  const circumference = 2 * Math.PI * 50
  let cumulative = 0
  return rows.map((r, i) => {
    const length = total > 0 ? (r.count / total) * circumference : 0
    const segment = {
      label: r.category,
      count: r.count,
      color: colors[i % colors.length],
      length,
      offset: -cumulative,
      circumference,
    }
    cumulative += length
    return segment
  })
})

const statusClass = {
  'Sin stock': 'bg-red-50 text-red-600',
  Bajo: 'bg-amber-50 text-amber-700',
  Óptimo: 'bg-emerald-50 text-emerald-700',
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-end">
      <ReportExportButton :loading="store.exporting" @export="handleExport" />
    </div>

    <div v-if="store.loading && !store.inventory" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="store.error" class="text-sm text-red-600">{{ store.error }}</div>

    <template v-else-if="store.inventory">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiTile
          icon="package"
          label="Productos Activos"
          :value="store.inventory.kpis.activeProducts"
          :sub="`${store.inventory.kpis.inactiveProducts} inactivos`"
          icon-bg-class="bg-emerald-50"
          icon-color-class="text-emerald-700"
        />
        <KpiTile
          icon="cash"
          label="Valor del Inventario"
          :value="formatCOP(store.inventory.kpis.inventoryValue)"
          sub="Costo total estimado"
          icon-bg-class="bg-sky-50"
          icon-color-class="text-sky-700"
        />
        <KpiTile
          icon="alert-triangle"
          label="Sin Stock"
          :value="store.inventory.kpis.outOfStock"
          sub="Bajo stock mínimo"
          icon-bg-class="bg-red-50"
          icon-color-class="text-red-600"
        />
        <KpiTile
          icon="chart-bar"
          label="Alta Rotación"
          :value="store.inventory.kpis.topProduct || '—'"
          icon-bg-class="bg-cyan-50"
          icon-color-class="text-cyan-700"
        />
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Productos más vendidos</h3>
          <div v-if="!store.inventory.topProducts.length" class="text-sm text-slate-400 text-center py-8">
            Todavía no hay ventas registradas.
          </div>
          <div v-else class="space-y-3">
            <div v-for="p in store.inventory.topProducts" :key="p.name">
              <div class="flex justify-between text-xs text-slate-600 mb-1">
                <span class="font-semibold">{{ p.name }}</span>
                <span>{{ p.unitsSold }} vendidos</span>
              </div>
              <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-emerald-600 rounded-full"
                  :style="{ width: `${(p.unitsSold / maxUnitsSold) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Stock por Categoría</h3>
          <div v-if="!categoryDonut.length" class="text-sm text-slate-400 text-center py-8">Sin productos activos.</div>
          <div v-else class="flex flex-col items-center">
            <svg viewBox="0 0 120 120" class="w-28 h-28">
              <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="14" />
              <circle
                v-for="seg in categoryDonut"
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
              <text x="60" y="56" text-anchor="middle" class="fill-slate-900 font-extrabold" style="font-size: 20px">
                {{ store.inventory.kpis.activeProducts }}
              </text>
              <text x="60" y="74" text-anchor="middle" class="fill-slate-400" style="font-size: 10px">Total</text>
            </svg>
            <div class="flex flex-wrap justify-center gap-3 mt-3 text-xs">
              <span v-for="seg in categoryDonut" :key="seg.label" class="flex items-center gap-1.5 text-slate-600">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: seg.color }"></span>
                {{ seg.label }} ({{ seg.count }})
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <h3 class="text-sm font-bold text-slate-900 px-6 pt-6 pb-4">Detalle de Existencias</h3>
        <div v-if="!store.inventory.products.items.length" class="p-8 text-sm text-slate-500 text-center">
          Sin productos activos.
        </div>
        <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
        <div v-else class="md:hidden divide-y divide-slate-100">
          <div v-for="p in store.inventory.products.items" :key="p.id" class="p-4">
            <div class="flex items-start justify-between gap-2">
              <p class="font-semibold text-slate-800 truncate">{{ p.name }}</p>
              <span class="shrink-0 text-[10px] font-bold uppercase px-2 py-0.5 rounded-full" :class="statusClass[p.status]">
                {{ p.status }}
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-1">{{ p.category?.name || '—' }}</p>
            <p class="text-sm text-slate-700 mt-1.5">
              Stock: {{ p.stock }} {{ p.unitLabel }} (mín. {{ p.minStock }}) · {{ formatCOP(p.stock * p.purchasePrice) }}
            </p>
          </div>
        </div>

        <table v-if="store.inventory.products.items.length" class="hidden md:table w-full text-sm">
          <thead>
            <tr class="bg-slate-50 border-y border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
              <th class="px-5 py-3">Producto</th>
              <th class="px-5 py-3">Categoría</th>
              <th class="px-5 py-3">Stock</th>
              <th class="px-5 py-3">Mínimo</th>
              <th class="px-5 py-3">Valor</th>
              <th class="px-5 py-3">Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in store.inventory.products.items"
              :key="p.id"
              class="border-b border-slate-100 last:border-0"
            >
              <td class="px-5 py-3 font-semibold text-slate-800">{{ p.name }}</td>
              <td class="px-5 py-3 text-slate-500">{{ p.category?.name || '—' }}</td>
              <td class="px-5 py-3 text-slate-700">{{ p.stock }} {{ p.unitLabel }}</td>
              <td class="px-5 py-3 text-slate-500">{{ p.minStock }}</td>
              <td class="px-5 py-3 text-slate-700">{{ formatCOP(p.stock * p.purchasePrice) }}</td>
              <td class="px-5 py-3">
                <span
                  class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
                  :class="statusClass[p.status]"
                >
                  {{ p.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <AdminPagination
          :pagination="store.inventory.products"
          item-label="productos"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        />
      </div>
    </template>
  </div>
</template>
