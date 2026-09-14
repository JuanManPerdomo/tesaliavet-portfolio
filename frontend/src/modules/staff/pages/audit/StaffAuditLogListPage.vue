<script setup>
import { ref, onMounted } from 'vue'
import AdminPagination from '../../components/AdminPagination.vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import AuditDetailModal from './AuditDetailModal.vue'
import { useAuditStore } from '../../../../stores/audit'

const MODULE_OPTIONS = [
  'Inventario',
  'Proveedores',
  'Ventas',
  'Citas',
  'Usuarios',
  'Mascotas',
  'PQRS',
  'Caja',
  'Sesión',
]

const ACTION_LABELS = {
  create: 'Creó',
  update: 'Editó',
  delete: 'Eliminó',
  activate: 'Activó',
  deactivate: 'Desactivó',
  login: 'Inició sesión',
  logout: 'Cerró sesión',
  role_change: 'Cambió roles',
  status_change: 'Cambió estado',
  cancel: 'Canceló',
  register_payment: 'Registró pago',
  register_return: 'Registró devolución',
  pos_sale: 'Registró venta de mostrador',
  respond: 'Respondió',
  reopen: 'Reabrió',
  associate_product: 'Asoció producto',
  add_medical_record: 'Agregó historial médico',
  add_vaccination: 'Aplicó vacuna',
  open_session: 'Abrió caja',
  close_session: 'Cerró caja',
}

const auditStore = useAuditStore()

const userIdFilter = ref('')
const moduleFilter = ref('')
const actionFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const perPage = ref(20)

function load(page = 1) {
  auditStore.fetchLogs({
    userId: userIdFilter.value || undefined,
    module: moduleFilter.value || undefined,
    action: actionFilter.value || undefined,
    dateFrom: dateFrom.value || undefined,
    dateTo: dateTo.value || undefined,
    page,
    perPage: perPage.value,
  })
}

onMounted(() => {
  auditStore.fetchUsers()
  load()
})

function handleFilter() {
  load(1)
}

function handleClearFilters() {
  userIdFilter.value = ''
  moduleFilter.value = ''
  actionFilter.value = ''
  dateFrom.value = ''
  dateTo.value = ''
  load(1)
}

function handlePageChange(page) {
  load(page)
}

function handlePageSizeChange(size) {
  perPage.value = size
  load(1)
}

function actionLabel(action) {
  return ACTION_LABELS[action] || action
}

const detailLog = ref(null)

function showDetail(log) {
  detailLog.value = log
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
    <div class="mb-6">
      <h1 class="text-2xl font-extrabold text-slate-900">Auditoría</h1>
      <p class="text-sm text-slate-500 mt-1">
        Registro de acciones realizadas en el sistema — creaciones, ediciones, eliminaciones,
        inicios/cierres de sesión y más, por usuario y módulo.
      </p>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <select
        v-model="userIdFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleFilter"
      >
        <option value="">Todos los usuarios</option>
        <option v-for="u in auditStore.users" :key="u.id" :value="u.id">{{ u.name || u.email }}</option>
      </select>

      <select
        v-model="moduleFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleFilter"
      >
        <option value="">Todos los módulos</option>
        <option v-for="m in MODULE_OPTIONS" :key="m" :value="m">{{ m }}</option>
      </select>

      <input
        v-model="dateFrom"
        type="date"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleFilter"
      />
      <input
        v-model="dateTo"
        type="date"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleFilter"
      />

      <button
        class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
        @click="handleClearFilters"
      >
        Limpiar filtros
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="auditStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="auditStore.error" class="p-8 text-sm text-red-600">{{ auditStore.error }}</div>
      <div v-else-if="!auditStore.logs.length" class="p-8 text-sm text-slate-500 text-center">
        No hay registros con estos filtros.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="log in auditStore.logs" :key="log.id" class="p-4">
          <div class="flex items-start justify-between gap-2">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700">
              {{ log.module }}
            </span>
            <span class="text-xs text-slate-400 whitespace-nowrap">{{ formatDateTime(log.createdAt) }}</span>
          </div>
          <p class="text-sm text-slate-800 font-semibold mt-2">
            {{ log.userName || 'Cuenta eliminada' }} · {{ actionLabel(log.action) }}
          </p>
          <p class="text-xs text-slate-600 mt-1">{{ log.description }}</p>
          <button
            v-if="log.changes?.length"
            type="button"
            class="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 hover:underline"
            @click="showDetail(log)"
          >
            <AppIcon name="eye" :size="14" />
            Ver detalle
          </button>
        </div>
      </div>

      <table v-if="auditStore.logs.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Fecha</th>
            <th class="px-5 py-3">Usuario</th>
            <th class="px-5 py-3">Módulo</th>
            <th class="px-5 py-3">Acción</th>
            <th class="px-5 py-3">Descripción</th>
            <th class="px-5 py-3">Detalle</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="log in auditStore.logs"
            :key="log.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3 text-slate-500 whitespace-nowrap">{{ formatDateTime(log.createdAt) }}</td>
            <td class="px-5 py-3 text-slate-700">{{ log.userName || 'Cuenta eliminada' }}</td>
            <td class="px-5 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700">
                {{ log.module }}
              </span>
            </td>
            <td class="px-5 py-3 text-slate-500">{{ actionLabel(log.action) }}</td>
            <td class="px-5 py-3 text-slate-700">{{ log.description }}</td>
            <td class="px-5 py-3">
              <button
                v-if="log.changes?.length"
                type="button"
                class="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 hover:underline"
                @click="showDetail(log)"
              >
                <AppIcon name="eye" :size="14" />
                Ver
              </button>
              <span v-else class="text-slate-300">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminPagination
      :pagination="auditStore.pagination"
      item-label="registros"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />

    <AuditDetailModal
      :open="!!detailLog"
      :log="detailLog"
      :action-label="actionLabel"
      :format-date-time="formatDateTime"
      @close="detailLog = null"
    />
  </div>
</template>
