<script setup>
import { ref, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import { usePqrsStore } from '../../../../stores/pqrs'

const STATUS_BADGE = {
  Abierto: 'bg-amber-50 text-amber-700',
  'En Proceso': 'bg-sky-50 text-sky-700',
  Resuelto: 'bg-emerald-50 text-emerald-700',
  Cerrado: 'bg-slate-100 text-slate-600',
}

const FILTERS = [
  { value: '', label: 'Todas' },
  { value: 'Abierto', label: 'Abiertas' },
  { value: 'En Proceso', label: 'En proceso' },
  { value: 'Resuelto', label: 'Resueltas' },
  { value: 'Cerrado', label: 'Cerradas' },
]

const pqrsStore = usePqrsStore()
const activeFilter = ref('')
const search = ref('')
const perPage = ref(10)

function load(page = 1) {
  pqrsStore.fetchAll({
    status: activeFilter.value || undefined,
    search: search.value || undefined,
    page,
    perPage: perPage.value,
  })
}

onMounted(() => load())

function handleFilterChange(value) {
  activeFilter.value = value
  load()
}

function handleSearch() {
  load()
}

function handlePageChange(page) {
  load(page)
}

function handlePageSizeChange(size) {
  perPage.value = size
  load()
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-extrabold text-slate-900 mb-1">PQRS</h1>
    <p class="text-sm text-slate-500 mb-6">Peticiones, quejas, reclamos y sugerencias recibidas.</p>

    <div class="flex flex-wrap items-center gap-3 mb-5">
      <div class="flex gap-2">
        <button
          v-for="f in FILTERS"
          :key="f.value"
          class="px-3.5 py-1.5 rounded-full text-xs font-semibold border transition"
          :class="
            activeFilter === f.value
              ? 'bg-emerald-700 text-white border-emerald-700'
              : 'border-slate-200 text-slate-600 hover:border-emerald-700 hover:text-emerald-700'
          "
          @click="handleFilterChange(f.value)"
        >
          {{ f.label }}
        </button>
      </div>
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por asunto, nombre o correo..."
        class="flex-1 min-w-[200px] border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-700"
        @keyup.enter="handleSearch"
      />
    </div>

    <div v-if="pqrsStore.loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="pqrsStore.error" class="text-sm text-red-600">{{ pqrsStore.error }}</div>
    <div
      v-else-if="!pqrsStore.items.length"
      class="bg-white rounded-2xl border border-slate-200 p-10 text-center text-sm text-slate-500"
    >
      No hay solicitudes en este filtro.
    </div>

    <div v-else class="space-y-3">
      <RouterLink
        v-for="item in pqrsStore.items"
        :key="item.id"
        :to="{ name: 'staff-pqrs-detail', params: { id: item.id } }"
        class="flex items-center gap-4 bg-white rounded-2xl border border-slate-200 p-5 hover:border-emerald-300 transition"
      >
        <div class="w-10 h-10 rounded-xl bg-slate-50 text-slate-500 flex items-center justify-center shrink-0">
          <AppIcon name="message-circle" :size="18" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-bold text-slate-900 truncate">{{ item.subject }}</h3>
            <span class="text-[10px] font-bold text-slate-400 uppercase shrink-0">{{ item.type }}</span>
            <AppIcon
              v-if="item.attachmentUrl"
              name="file-text"
              :size="13"
              class="text-slate-400 shrink-0"
              title="Tiene adjunto"
            />
          </div>
          <p class="text-xs text-slate-500 mt-0.5">{{ item.senderName }} — {{ formatDate(item.createdAt) }}</p>
        </div>
        <span class="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full shrink-0" :class="STATUS_BADGE[item.status]">
          {{ item.status }}
        </span>
        <AppIcon name="chevron-right" :size="16" class="text-slate-300 shrink-0" />
      </RouterLink>

      <AdminPagination
        :pagination="pqrsStore.pagination"
        item-label="solicitudes"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
      />
    </div>
  </div>
</template>
