<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import ClientAvatar from './ClientAvatar.vue'
import { useStaffClientsStore } from '../../../../stores/staffClients'
import { useToastStore } from '../../../../stores/toast'

const STATUS_OPTIONS = [
  { value: 'active', label: 'Activos' },
  { value: 'inactive', label: 'Inactivos' },
  { value: 'all', label: 'Todos' },
]

const MONTH_LABELS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

const clientsStore = useStaffClientsStore()
const toastStore = useToastStore()

const search = ref('')
const statusFilter = ref('active')
const cityFilter = ref('')
const perPage = ref(10)

const deactivatingId = ref(null)
const showDeactivateConfirm = ref(false)
const deactivating = ref(false)
const activatingId = ref(null)

function load(page = 1) {
  clientsStore.fetchClients({
    search: search.value,
    status: statusFilter.value,
    city: cityFilter.value || undefined,
    page,
    perPage: perPage.value,
  })
}

onMounted(() => {
  load()
  clientsStore.fetchStats()
})

function handleSearch() {
  load(1)
}

function handlePageChange(page) {
  load(page)
}

function handlePageSizeChange(size) {
  perPage.value = size
  load(1)
}

function askDeactivate(id) {
  deactivatingId.value = id
  showDeactivateConfirm.value = true
}

async function confirmDeactivate() {
  deactivating.value = true
  try {
    await clientsStore.deactivateClient(deactivatingId.value)
    toastStore.success('Cliente desactivado.')
    showDeactivateConfirm.value = false
    load(clientsStore.pagination.page)
    clientsStore.fetchStats()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo desactivar el cliente.')
  } finally {
    deactivating.value = false
  }
}

async function handleActivate(id) {
  activatingId.value = id
  try {
    await clientsStore.reactivateClient(id)
    toastStore.success('Cliente activado.')
    load(clientsStore.pagination.page)
    clientsStore.fetchStats()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo activar el cliente.')
  } finally {
    activatingId.value = null
  }
}

const monthSeries = computed(() => {
  const stats = clientsStore.stats
  const now = new Date()
  const months = []
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const year = d.getFullYear()
    const month = d.getMonth() + 1
    const found = stats?.byMonth.find((m) => m.year === year && m.month === month)
    months.push({ label: MONTH_LABELS[month - 1], count: found?.count || 0 })
  }
  return months
})

const monthMax = computed(() => Math.max(1, ...monthSeries.value.map((m) => m.count)))

const cityMax = computed(() => Math.max(1, ...(clientsStore.stats?.byCity.map((c) => c.count) || [1])))

const activeInactive = computed(() => {
  const stats = clientsStore.stats
  const active = stats?.active || 0
  const inactive = stats?.inactive || 0
  const total = active + inactive
  const circumference = 2 * Math.PI * 50
  const activeLength = total > 0 ? (active / total) * circumference : 0
  return { active, inactive, total, circumference, activeLength }
})
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-extrabold text-slate-900">Clientes</h1>
      <p class="text-sm text-slate-500 mt-1">Cuentas de clientes registradas en la plataforma.</p>
    </div>

    <div v-if="clientsStore.stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center mb-3">
          <AppIcon name="users" :size="16" />
        </div>
        <p class="text-xs text-slate-500 mb-1">Total clientes</p>
        <p class="text-2xl font-extrabold text-slate-900">{{ clientsStore.stats.total }}</p>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center mb-3">
          <AppIcon name="user-check" :size="16" />
        </div>
        <p class="text-xs text-slate-500 mb-1">Clientes activos</p>
        <p class="text-2xl font-extrabold text-slate-900">{{ clientsStore.stats.active }}</p>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="w-9 h-9 rounded-lg bg-sky-50 text-sky-700 flex items-center justify-center mb-3">
          <AppIcon name="plus" :size="16" />
        </div>
        <p class="text-xs text-slate-500 mb-1">Nuevos este mes</p>
        <p class="text-2xl font-extrabold text-slate-900">{{ clientsStore.stats.newThisMonth }}</p>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 p-4">
        <div class="w-9 h-9 rounded-lg bg-slate-100 text-slate-500 flex items-center justify-center mb-3">
          <AppIcon name="archive" :size="16" />
        </div>
        <p class="text-xs text-slate-500 mb-1">Clientes inactivos</p>
        <p class="text-2xl font-extrabold text-slate-900">{{ clientsStore.stats.inactive }}</p>
      </div>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nombre o email..."
        class="flex-1 min-w-[220px] border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @keyup.enter="handleSearch"
      />
      <select
        v-model="statusFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleSearch"
      >
        <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <button
        class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
        @click="handleSearch"
      >
        Buscar
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden mb-6">
      <div v-if="clientsStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="clientsStore.error" class="p-8 text-sm text-red-600">{{ clientsStore.error }}</div>
      <div v-else-if="!clientsStore.clients.length" class="p-8 text-sm text-slate-500 text-center">
        No hay clientes con estos filtros.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="client in clientsStore.clients" :key="client.id" class="p-4 flex gap-3">
          <ClientAvatar :first-name="client.firstName" :last-name="client.lastName" :size="40" />
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="font-semibold text-slate-800 truncate">{{ client.firstName }} {{ client.lastName }}</p>
                <p class="text-xs text-slate-400">ID #{{ client.id }}</p>
              </div>
              <span
                class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold"
                :class="client.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ client.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-1 truncate">{{ client.email }}</p>
            <p class="text-xs text-slate-500">{{ client.phone || '—' }} · {{ client.ciudad || '—' }}</p>

            <div class="flex gap-2 mt-3">
              <RouterLink
                :to="{ name: 'staff-client-detail', params: { id: client.id } }"
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                title="Ver detalle"
              >
                <AppIcon name="eye" :size="14" />
              </RouterLink>
              <button
                v-if="client.isActive"
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                title="Desactivar"
                @click="askDeactivate(client.id)"
              >
                <AppIcon name="archive" :size="14" />
              </button>
              <button
                v-else
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                title="Activar"
                :disabled="activatingId === client.id"
                @click="handleActivate(client.id)"
              >
                <AppIcon name="refresh" :size="14" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <table v-if="clientsStore.clients.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Cliente</th>
            <th class="px-5 py-3">Email</th>
            <th class="px-5 py-3">Teléfono</th>
            <th class="px-5 py-3">Ciudad</th>
            <th class="px-5 py-3">Estado</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="client in clientsStore.clients"
            :key="client.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3">
              <div class="flex items-center gap-3">
                <ClientAvatar :first-name="client.firstName" :last-name="client.lastName" :size="36" />
                <div>
                  <p class="font-semibold text-slate-800">{{ client.firstName }} {{ client.lastName }}</p>
                  <p class="text-xs text-slate-400">ID #{{ client.id }}</p>
                </div>
              </div>
            </td>
            <td class="px-5 py-3 text-slate-500">{{ client.email }}</td>
            <td class="px-5 py-3 text-slate-500">{{ client.phone || '—' }}</td>
            <td class="px-5 py-3 text-slate-500">{{ client.ciudad || '—' }}</td>
            <td class="px-5 py-3">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-bold"
                :class="client.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ client.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3">
              <div class="flex justify-end gap-2">
                <RouterLink
                  :to="{ name: 'staff-client-detail', params: { id: client.id } }"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Ver detalle"
                >
                  <AppIcon name="eye" :size="14" />
                </RouterLink>
                <button
                  v-if="client.isActive"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                  title="Desactivar"
                  @click="askDeactivate(client.id)"
                >
                  <AppIcon name="archive" :size="14" />
                </button>
                <button
                  v-else
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                  title="Activar"
                  :disabled="activatingId === client.id"
                  @click="handleActivate(client.id)"
                >
                  <AppIcon name="refresh" :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminPagination
      :pagination="clientsStore.pagination"
      item-label="clientes"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />

    <div v-if="clientsStore.stats" class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">Clientes registrados por mes</h3>
        <div class="flex items-end justify-between gap-2 h-32">
          <div v-for="m in monthSeries" :key="m.label" class="flex-1 flex flex-col items-center gap-1.5">
            <span class="text-[11px] font-semibold text-slate-600">{{ m.count }}</span>
            <div
              class="w-full rounded-t"
              :class="m.count === 0 ? 'bg-slate-100' : 'bg-emerald-600'"
              :style="{ height: `${Math.max((m.count / monthMax) * 88, m.count > 0 ? 6 : 2)}px` }"
            ></div>
            <span class="text-[11px] text-slate-400">{{ m.label }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">Distribución por ciudad</h3>
        <div v-if="!clientsStore.stats.byCity.length" class="text-sm text-slate-400 text-center py-8">
          Ningún cliente tiene ciudad registrada todavía.
        </div>
        <div v-else class="space-y-3">
          <div v-for="c in clientsStore.stats.byCity" :key="c.city" class="text-sm">
            <div class="flex justify-between mb-1">
              <span class="text-slate-600">{{ c.city }}</span>
              <span class="font-semibold text-slate-800">{{ c.count }}</span>
            </div>
            <div class="h-2 rounded-full bg-slate-100 overflow-hidden">
              <div class="h-full bg-emerald-600 rounded-full" :style="{ width: `${(c.count / cityMax) * 100}%` }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-5">
        <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">Activos vs inactivos</h3>
        <div class="flex flex-col items-center">
          <svg viewBox="0 0 120 120" class="w-28 h-28">
            <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="14" />
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="#047857"
              stroke-width="14"
              stroke-linecap="round"
              :stroke-dasharray="`${activeInactive.activeLength} ${activeInactive.circumference}`"
              transform="rotate(-90 60 60)"
            />
            <text x="60" y="56" text-anchor="middle" class="fill-slate-900 font-extrabold" style="font-size: 22px">
              {{ activeInactive.total }}
            </text>
            <text x="60" y="74" text-anchor="middle" class="fill-slate-400" style="font-size: 10px">clientes</text>
          </svg>
          <div class="flex gap-4 mt-3 text-xs">
            <span class="flex items-center gap-1.5 text-slate-600">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-700"></span>
              Activos ({{ activeInactive.active }})
            </span>
            <span class="flex items-center gap-1.5 text-slate-600">
              <span class="w-2.5 h-2.5 rounded-full bg-slate-200"></span>
              Inactivos ({{ activeInactive.inactive }})
            </span>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :open="showDeactivateConfirm"
      title="Desactivar cliente"
      message="El cliente no podrá iniciar sesión mientras la cuenta esté desactivada. Podrás reactivarla cuando quieras."
      confirm-label="Sí, desactivar"
      :loading="deactivating"
      @cancel="showDeactivateConfirm = false"
      @confirm="confirmDeactivate"
    />
  </div>
</template>
