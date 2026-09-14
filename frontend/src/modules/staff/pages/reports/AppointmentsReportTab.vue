<script setup>
import { ref, computed, onMounted } from 'vue'
import KpiTile from '../../components/KpiTile.vue'
import ReportDateFilter from '../../components/ReportDateFilter.vue'
import ReportExportButton from '../../components/ReportExportButton.vue'
import { useReportsStore } from '../../../../stores/reports'
import { getPresetRange } from '../../../../lib/reportDatePresets'

const store = useReportsStore()

const defaultRange = getPresetRange('mes')
const dateFrom = ref(defaultRange.dateFrom)
const dateTo = ref(defaultRange.dateTo)

function load() {
  store.fetchAppointments({ dateFrom: dateFrom.value, dateTo: dateTo.value })
}

onMounted(load)

function handleFilterChange() {
  load()
}

function handleExport(format) {
  store.exportReport('appointments', format, { dateFrom: dateFrom.value, dateTo: dateTo.value }, 'reporte_citas')
}

const STATUS_COLORS = {
  Completada: '#047857',
  Confirmada: '#0ea5e9',
  Pendiente: '#f59e0b',
  Cancelada: '#ef4444',
}

const statusDonut = computed(() => {
  const counts = store.appointments?.statusCounts || {}
  const total = Object.values(counts).reduce((sum, v) => sum + v, 0)
  const circumference = 2 * Math.PI * 50
  let cumulative = 0
  return Object.entries(counts).map(([label, count]) => {
    const length = total > 0 ? (count / total) * circumference : 0
    const segment = {
      label, count, color: STATUS_COLORS[label],
      length, offset: -cumulative, circumference,
    }
    cumulative += length
    return segment
  })
})

const totalAppointments = computed(() =>
  Object.values(store.appointments?.statusCounts || {}).reduce((sum, v) => sum + v, 0)
)
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

    <div v-if="store.loading && !store.appointments" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="store.error" class="text-sm text-red-600">{{ store.error }}</div>

    <template v-else-if="store.appointments">
      <div class="grid sm:grid-cols-2 gap-5">
        <KpiTile
          icon="calendar"
          label="Citas del Período"
          :value="store.appointments.kpis.totalAppointments"
          icon-bg-class="bg-emerald-50"
          icon-color-class="text-emerald-700"
        />
        <KpiTile
          icon="check"
          label="Tasa de Asistencia"
          :value="store.appointments.kpis.attendanceRate !== null ? `${store.appointments.kpis.attendanceRate}%` : 'Sin datos'"
          icon-bg-class="bg-sky-50"
          icon-color-class="text-sky-700"
        />
      </div>

      <div class="grid lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h3 class="text-sm font-bold text-slate-900 mb-4">Estado de Citas</h3>
          <div v-if="!totalAppointments" class="text-sm text-slate-400 text-center py-8">Sin citas en el rango.</div>
          <div v-else class="flex flex-col items-center">
            <svg viewBox="0 0 120 120" class="w-28 h-28">
              <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="14" />
              <circle
                v-for="seg in statusDonut" :key="seg.label" cx="60" cy="60" r="50" fill="none"
                :stroke="seg.color" stroke-width="14"
                :stroke-dasharray="`${seg.length} ${seg.circumference}`" :stroke-dashoffset="seg.offset"
                transform="rotate(-90 60 60)"
              />
              <text x="60" y="56" text-anchor="middle" class="fill-slate-900 font-extrabold" style="font-size: 20px">
                {{ totalAppointments }}
              </text>
              <text x="60" y="74" text-anchor="middle" class="fill-slate-400" style="font-size: 10px">Total</text>
            </svg>
            <div class="flex flex-col gap-1 mt-3 text-xs">
              <span v-for="seg in statusDonut" :key="seg.label" class="flex items-center gap-1.5 text-slate-600">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: seg.color }"></span>
                {{ seg.label }} ({{ seg.count }})
              </span>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <h3 class="text-sm font-bold text-slate-900 px-6 pt-6 pb-4">Rendimiento por Veterinario</h3>
          <div v-if="!store.appointments.byVeterinarian.length" class="p-8 text-sm text-slate-500 text-center">
            Sin citas asignadas a un veterinario en este rango.
          </div>
          <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
          <div v-else class="md:hidden divide-y divide-slate-100">
            <div v-for="v in store.appointments.byVeterinarian" :key="v.name" class="p-4">
              <div class="flex items-start justify-between gap-2">
                <p class="font-semibold text-slate-800">{{ v.name }}</p>
                <span
                  v-if="v.effectiveness !== null"
                  class="shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700"
                >
                  {{ v.effectiveness }}% efectividad
                </span>
              </div>
              <p class="text-xs text-slate-500 mt-1">
                {{ v.total }} citas totales ·
                <span class="text-emerald-700">{{ v.completadas }} completadas</span> ·
                <span class="text-red-500">{{ v.canceladas }} canceladas</span>
              </p>
            </div>
          </div>

          <table v-if="store.appointments.byVeterinarian.length" class="hidden md:table w-full text-sm">
            <thead>
              <tr class="bg-slate-50 border-y border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                <th class="px-5 py-3">Veterinario</th>
                <th class="px-5 py-3">Total Citas</th>
                <th class="px-5 py-3">Completadas</th>
                <th class="px-5 py-3">Canceladas</th>
                <th class="px-5 py-3">Efectividad</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="v in store.appointments.byVeterinarian"
                :key="v.name"
                class="border-b border-slate-100 last:border-0"
              >
                <td class="px-5 py-3 font-semibold text-slate-800">{{ v.name }}</td>
                <td class="px-5 py-3 text-slate-700">{{ v.total }}</td>
                <td class="px-5 py-3 text-emerald-700">{{ v.completadas }}</td>
                <td class="px-5 py-3 text-red-500">{{ v.canceladas }}</td>
                <td class="px-5 py-3">
                  <span
                    v-if="v.effectiveness !== null"
                    class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700"
                  >
                    {{ v.effectiveness }}%
                  </span>
                  <span v-else class="text-slate-400">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
