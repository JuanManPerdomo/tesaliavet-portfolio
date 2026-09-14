<script setup>
import { ref, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useStockAlertsStore } from '../../../../stores/stockAlerts'

const STATUS_OPTIONS = [
  { value: 'Activa', label: 'Activas' },
  { value: 'Resuelta', label: 'Resueltas' },
  { value: 'all', label: 'Todas' },
]

const stockAlertsStore = useStockAlertsStore()
const statusFilter = ref('Activa')

function load() {
  stockAlertsStore.fetchAlerts(statusFilter.value)
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
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-extrabold text-slate-900">Alertas de stock</h1>
      <p class="text-sm text-slate-500 mt-1">
        Productos activos cuyo stock llegó a su mínimo configurado. Se generan y se
        resuelven solas cuando el stock cambia — sin acción manual.
      </p>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <select
        v-model="statusFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="load"
      >
        <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="stockAlertsStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="stockAlertsStore.error" class="p-8 text-sm text-red-600">{{ stockAlertsStore.error }}</div>
      <div v-else-if="!stockAlertsStore.alerts.length" class="p-10 text-center">
        <AppIcon name="check" :size="28" class="text-emerald-300 mx-auto mb-3" />
        <p class="text-sm text-slate-500">No hay alertas {{ statusFilter === 'Activa' ? 'activas' : '' }} en este filtro.</p>
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="alert in stockAlertsStore.alerts" :key="alert.id" class="p-4">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="font-semibold text-slate-800 truncate">{{ alert.productName }}</p>
              <p class="text-xs text-slate-400">{{ alert.sku }}</p>
            </div>
            <span
              class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold"
              :class="alert.status === 'Activa' ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-700'"
            >
              {{ alert.status }}
            </span>
          </div>
          <p class="text-sm mt-1.5">
            <span class="font-bold" :class="alert.currentStock <= 0 ? 'text-red-600' : 'text-amber-600'">
              {{ alert.currentStock }} {{ alert.unitLabel }}
            </span>
            <span class="text-slate-400"> / mínimo {{ alert.minStock }} {{ alert.unitLabel }}</span>
          </p>
          <p class="text-xs text-slate-500 mt-1">Generada: {{ formatDateTime(alert.createdAt) }}</p>
          <p v-if="alert.resolvedAt" class="text-xs text-slate-500">
            Resuelta: {{ formatDateTime(alert.resolvedAt) }}<span v-if="alert.resolvedBy"> · {{ alert.resolvedBy }}</span>
          </p>

          <div class="flex gap-2 mt-3">
            <RouterLink
              :to="{ name: 'staff-product-edit', params: { id: alert.productId } }"
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
              title="Ver producto"
            >
              <AppIcon name="eye" :size="14" />
            </RouterLink>
          </div>
        </div>
      </div>

      <table v-if="stockAlertsStore.alerts.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Producto</th>
            <th class="px-5 py-3 text-right">Stock actual</th>
            <th class="px-5 py-3 text-right">Mínimo</th>
            <th class="px-5 py-3">Estado</th>
            <th class="px-5 py-3">Generada</th>
            <th class="px-5 py-3">Resuelta</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="alert in stockAlertsStore.alerts"
            :key="alert.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3">
              <p class="font-semibold text-slate-800">{{ alert.productName }}</p>
              <p class="text-xs text-slate-400">{{ alert.sku }}</p>
            </td>
            <td class="px-5 py-3 text-right">
              <span class="font-bold" :class="alert.currentStock <= 0 ? 'text-red-600' : 'text-amber-600'">
                {{ alert.currentStock }} {{ alert.unitLabel }}
              </span>
            </td>
            <td class="px-5 py-3 text-right text-slate-500">{{ alert.minStock }} {{ alert.unitLabel }}</td>
            <td class="px-5 py-3">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-bold"
                :class="alert.status === 'Activa' ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-700'"
              >
                {{ alert.status }}
              </span>
            </td>
            <td class="px-5 py-3 text-slate-500">{{ formatDateTime(alert.createdAt) }}</td>
            <td class="px-5 py-3 text-slate-500">
              <span v-if="alert.resolvedAt">{{ formatDateTime(alert.resolvedAt) }}<span v-if="alert.resolvedBy"> · {{ alert.resolvedBy }}</span></span>
              <span v-else>—</span>
            </td>
            <td class="px-5 py-3">
              <div class="flex justify-end">
                <RouterLink
                  :to="{ name: 'staff-product-edit', params: { id: alert.productId } }"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Ver producto"
                >
                  <AppIcon name="eye" :size="14" />
                </RouterLink>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
