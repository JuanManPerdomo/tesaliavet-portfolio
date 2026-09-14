<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import KpiTile from '../../components/KpiTile.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import { useStaffNotificationsStore } from '../../../../stores/staffNotifications'
import { NOTIFICATION_TYPE_META as TYPE_META } from '../../../../lib/notificationTypes'

const TABS = [
  { value: '', label: 'Todas' },
  { value: 'stock', label: 'Stock' },
  { value: 'pqrs', label: 'PQRS' },
  { value: 'cita', label: 'Cita' },
  { value: 'compra', label: 'Compra' },
  { value: 'entrega', label: 'Entrega' },
  { value: 'vacuna', label: 'Vacuna' },
]

const store = useStaffNotificationsStore()

const activeTab = ref('')
const search = ref('')
const readFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const perPage = ref(10)

function load(page = 1) {
  store.fetchNotifications({
    type: activeTab.value || undefined,
    read: readFilter.value || undefined,
    search: search.value || undefined,
    dateFrom: dateFrom.value || undefined,
    dateTo: dateTo.value || undefined,
    page,
    perPage: perPage.value,
  })
}

onMounted(() => {
  store.fetchSummary()
  load()
})

function handleTab(value) {
  activeTab.value = value
  load(1)
}

function handleFilter() {
  load(1)
}

function handleClearFilters() {
  search.value = ''
  readFilter.value = ''
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

function handleMarkRead(key) {
  store.markAsRead(key)
}

function formatTime(iso) {
  if (!iso) return ''
  const date = new Date(iso)
  const now = new Date()
  const diffMin = Math.floor((now - date) / 60000)
  if (diffMin < 1) return 'Justo ahora'
  if (diffMin < 60) return `Hace ${diffMin} min`
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
  }
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return `Ayer, ${date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}`
  }
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function dateGroupLabel(iso) {
  const date = new Date(iso)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) return 'Hoy'
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) return 'Ayer'
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'long', year: 'numeric' })
}

const groupedItems = computed(() => {
  const groups = []
  let currentLabel = null
  for (const item of store.items) {
    const label = dateGroupLabel(item.createdAt)
    if (label !== currentLabel) {
      groups.push({ label, items: [] })
      currentLabel = label
    }
    groups[groups.length - 1].items.push(item)
  }
  return groups
})
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-extrabold text-slate-900">Centro de Notificaciones</h1>
      <p class="text-sm text-slate-500 mt-1">
        Todo lo que requiere tu atención: stock crítico, PQRS sin responder, citas pendientes de
        confirmar, pedidos pendientes de pago y pedidos pagados pendientes de entrega.
      </p>
    </div>

    <div v-if="store.summary" class="grid sm:grid-cols-3 gap-5 mb-6">
      <KpiTile icon="bell" label="Todas" :value="store.summary.total" icon-bg-class="bg-slate-100" icon-color-class="text-slate-600" />
      <KpiTile icon="mail" label="No Leídas" :value="store.summary.unread" icon-bg-class="bg-emerald-50" icon-color-class="text-emerald-700" />
      <KpiTile icon="calendar" label="Recibidas Hoy" :value="store.summary.receivedToday" icon-bg-class="bg-sky-50" icon-color-class="text-sky-700" />
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div class="flex overflow-x-auto gap-6 border-b border-slate-200 px-5 pt-2">
        <button
          v-for="tab in TABS"
          :key="tab.value"
          type="button"
          class="pb-3 pt-2 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="
            activeTab === tab.value
              ? 'text-emerald-700 border-emerald-700'
              : 'text-slate-500 border-transparent hover:text-emerald-700'
          "
          @click="handleTab(tab.value)"
        >
          {{ tab.label }}
          <span
            v-if="store.summary && (tab.value ? store.summary.byType[tab.value] : store.summary.total)"
            class="ml-1 text-[11px] font-bold px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500"
          >
            {{ tab.value ? store.summary.byType[tab.value] : store.summary.total }}
          </span>
        </button>
      </div>

      <div class="flex flex-wrap gap-2 px-5 py-4 border-b border-slate-100">
        <input
          v-model="search"
          type="text"
          placeholder="Buscar notificaciones..."
          class="flex-1 min-w-[200px] border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
          @keyup.enter="handleFilter"
        />
        <select
          v-model="readFilter"
          class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
          @change="handleFilter"
        >
          <option value="">Todos los estados</option>
          <option value="unread">No leídas</option>
          <option value="read">Leídas</option>
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
          type="button"
          class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
          @click="handleClearFilters"
        >
          Limpiar filtros
        </button>
      </div>

      <div v-if="store.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="store.error" class="p-8 text-sm text-red-600">{{ store.error }}</div>
      <div v-else-if="!store.items.length" class="p-8 text-sm text-slate-500 text-center">
        No hay notificaciones con estos filtros.
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div v-for="group in groupedItems" :key="group.label">
          <div class="px-5 py-2 bg-slate-50 text-xs font-bold text-slate-500 flex items-center gap-1.5">
            <AppIcon name="calendar" :size="12" />
            {{ group.label }}
          </div>

          <div
            v-for="item in group.items"
            :key="item.key"
            class="px-5 py-4 flex items-start gap-3 border-l-4 transition"
            :class="[
              item.read ? 'opacity-60 border-transparent' : 'border-emerald-600',
            ]"
          >
            <div
              class="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
              :class="[TYPE_META[item.type].iconBgClass, TYPE_META[item.type].iconColorClass]"
            >
              <AppIcon :name="TYPE_META[item.type].icon" :size="16" />
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span
                  class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
                  :class="TYPE_META[item.type].badgeClass"
                >
                  {{ TYPE_META[item.type].badge }}
                </span>
                <p class="text-sm font-bold text-slate-900">{{ item.title }}</p>
              </div>
              <p class="text-sm text-slate-600 mt-0.5">{{ item.description }}</p>

              <div class="flex items-center gap-2 mt-3">
                <RouterLink
                  :to="item.action.to"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-700 text-white hover:bg-emerald-800"
                >
                  {{ item.action.label }}
                </RouterLink>
                <button
                  v-if="!item.read"
                  type="button"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold border border-slate-200 text-slate-600 hover:bg-slate-50 flex items-center gap-1"
                  @click="handleMarkRead(item.key)"
                >
                  <AppIcon name="check" :size="12" />
                  Marcar como leído
                </button>
              </div>
            </div>

            <span class="text-xs text-slate-400 shrink-0 whitespace-nowrap">{{ formatTime(item.createdAt) }}</span>
          </div>
        </div>
      </div>
    </div>

    <AdminPagination
      :pagination="store.pagination"
      item-label="notificaciones"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />
  </div>
</template>
