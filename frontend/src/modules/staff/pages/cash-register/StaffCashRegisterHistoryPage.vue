<script setup>
import { onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import { useCashRegisterStore } from '../../../../stores/cashRegister'
import { formatCOP } from '../../../../lib/pricing'

const cashRegisterStore = useCashRegisterStore()

function load(page = 1) {
  cashRegisterStore.fetchSessions({ page, perPage: cashRegisterStore.sessionsPagination.perPage })
}

onMounted(() => load())

function handlePageChange(page) {
  load(page)
}

function handlePageSizeChange(size) {
  cashRegisterStore.sessionsPagination.perPage = size
  load(1)
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
    <RouterLink
      :to="{ name: 'staff-cash-register' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a Caja
    </RouterLink>

    <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Reportes de caja</h1>
    <p class="text-sm text-slate-500 mb-6">Historial de sesiones de caja, abiertas y cerradas.</p>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="cashRegisterStore.sessionsLoading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="!cashRegisterStore.sessions.length" class="p-8 text-sm text-slate-500 text-center">
        No hay sesiones de caja registradas todavía.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <RouterLink
          v-for="session in cashRegisterStore.sessions"
          :key="session.id"
          :to="{ name: 'staff-cash-register-detail', params: { id: session.id } }"
          class="block p-4 hover:bg-slate-50/50"
        >
          <div class="flex items-start justify-between gap-2">
            <p class="font-semibold text-slate-800">Sesión #{{ session.id }}</p>
            <span
              class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold"
              :class="session.status === 'Abierta' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            >
              {{ session.status }}
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-1">{{ session.responsibleUserName || '—' }}</p>
          <p class="text-xs text-slate-400 mt-1">
            {{ formatDateTime(session.openedAt) }}<span v-if="session.closedAt"> → {{ formatDateTime(session.closedAt) }}</span>
          </p>
          <div class="flex items-center justify-between mt-2 text-sm">
            <span class="font-semibold text-slate-800">{{ formatCOP(session.totals.totalRecaudado) }}</span>
            <span v-if="session.cashDifference === null" class="text-slate-400 text-xs">Sin cerrar</span>
            <span
              v-else
              class="text-xs font-semibold"
              :class="session.cashDifference === 0 ? 'text-emerald-700' : 'text-red-600'"
            >
              Diferencia: {{ formatCOP(session.cashDifference) }}
            </span>
          </div>
        </RouterLink>
      </div>

      <table v-if="cashRegisterStore.sessions.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Sesión</th>
            <th class="px-5 py-3">Responsable</th>
            <th class="px-5 py-3">Abierta</th>
            <th class="px-5 py-3">Cerrada</th>
            <th class="px-5 py-3 text-right">Total recaudado</th>
            <th class="px-5 py-3 text-right">Diferencia</th>
            <th class="px-5 py-3">Estado</th>
          </tr>
        </thead>
        <tbody>
          <RouterLink
            v-for="session in cashRegisterStore.sessions"
            :key="session.id"
            v-slot="{ navigate }"
            :to="{ name: 'staff-cash-register-detail', params: { id: session.id } }"
            custom
          >
            <tr
              class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50 cursor-pointer"
              @click="navigate"
            >
              <td class="px-5 py-3 font-semibold text-slate-800">#{{ session.id }}</td>
              <td class="px-5 py-3 text-slate-500">{{ session.responsibleUserName || '—' }}</td>
              <td class="px-5 py-3 text-slate-500">{{ formatDateTime(session.openedAt) }}</td>
              <td class="px-5 py-3 text-slate-500">{{ formatDateTime(session.closedAt) }}</td>
              <td class="px-5 py-3 text-right font-semibold text-slate-800">{{ formatCOP(session.totals.totalRecaudado) }}</td>
              <td class="px-5 py-3 text-right">
                <span v-if="session.cashDifference === null" class="text-slate-400">—</span>
                <span v-else :class="session.cashDifference === 0 ? 'text-emerald-700' : 'text-red-600'" class="font-semibold">
                  {{ formatCOP(session.cashDifference) }}
                </span>
              </td>
              <td class="px-5 py-3">
                <span
                  class="px-2 py-0.5 rounded-full text-xs font-bold"
                  :class="session.status === 'Abierta' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                >
                  {{ session.status }}
                </span>
              </td>
            </tr>
          </RouterLink>
        </tbody>
      </table>
    </div>

    <AdminPagination
      :pagination="cashRegisterStore.sessionsPagination"
      item-label="sesiones"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />
  </div>
</template>
