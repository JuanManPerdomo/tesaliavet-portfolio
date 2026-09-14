<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { useOrdersStore } from '../../../../stores/orders'

const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Pagado: 'bg-sky-50 text-sky-700',
  Entregado: 'bg-emerald-50 text-emerald-700',
  Cancelado: 'bg-red-50 text-red-600',
}

const FILTERS = [
  { value: '', label: 'Todos' },
  { value: 'Pendiente', label: 'Pendientes' },
  { value: 'Pagado', label: 'Pagados' },
  { value: 'Entregado', label: 'Entregados' },
  { value: 'Cancelado', label: 'Cancelados' },
]

const route = useRoute()
const ordersStore = useOrdersStore()
const activeFilter = ref('')
const search = ref('')

const ownerId = computed(() => route.query.ownerId || undefined)
const ownerName = computed(() => route.query.ownerName || '')

function load() {
  ordersStore.fetchStaffOrders({
    status: activeFilter.value || undefined,
    search: search.value || undefined,
    ownerId: ownerId.value,
  })
}

onMounted(load)

function handleSearch() {
  load()
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function firstItem(order) {
  return order.items?.[0]
}
</script>

<template>
  <div>
    <RouterLink
      v-if="ownerId"
      :to="{ name: 'staff-client-detail', params: { id: ownerId } }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver al cliente
    </RouterLink>

    <div class="flex items-start justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 mb-1">
          {{ ownerId ? `Pedidos de ${ownerName}` : 'Pedidos' }}
        </h1>
        <p class="text-sm text-slate-500">
          {{ ownerId ? 'Historial de pedidos de este cliente.' : 'Productos apartados por los clientes.' }}
        </p>
      </div>
      <PrimaryButton v-if="!ownerId" class="gap-2 shrink-0" :to="{ name: 'staff-new-sale' }">
        <AppIcon name="plus" :size="16" />
        Nueva venta
      </PrimaryButton>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por cliente, producto o # de pedido..."
        class="flex-1 min-w-[220px] border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @keyup.enter="handleSearch"
      />
      <button
        class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
        @click="handleSearch"
      >
        Buscar
      </button>
    </div>

    <div class="flex gap-2 mb-5">
      <button
        v-for="f in FILTERS"
        :key="f.value"
        class="px-3.5 py-1.5 rounded-full text-xs font-semibold border transition"
        :class="
          activeFilter === f.value
            ? 'bg-emerald-700 text-white border-emerald-700'
            : 'border-slate-200 text-slate-600 hover:border-emerald-700 hover:text-emerald-700'
        "
        @click="activeFilter = f.value; load()"
      >
        {{ f.label }}
      </button>
    </div>

    <div v-if="ordersStore.staffLoading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="ordersStore.staffError" class="text-sm text-red-600">{{ ordersStore.staffError }}</div>
    <div
      v-else-if="!ordersStore.staffOrders.length"
      class="bg-white rounded-2xl border border-slate-200 p-10 text-center text-sm text-slate-500"
    >
      No hay pedidos en este filtro.
    </div>

    <div v-else class="space-y-3">
      <RouterLink
        v-for="order in ordersStore.staffOrders"
        :key="order.id"
        :to="{ name: 'staff-order-detail', params: { id: order.id } }"
        class="flex items-center gap-4 bg-white rounded-2xl border border-slate-200 p-5 hover:border-emerald-300 transition"
      >
        <div class="w-10 h-10 rounded-xl bg-slate-50 text-slate-500 flex items-center justify-center shrink-0">
          <AppIcon name="shopping-bag" :size="18" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-bold text-slate-900 truncate">
              Pedido #{{ order.id }} — {{ firstItem(order)?.productName }}
            </h3>
            <span v-if="order.items.length > 1" class="text-[10px] font-bold text-slate-400 shrink-0">
              +{{ order.items.length - 1 }}
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">
            {{ order.customerName }} — {{ formatDate(order.createdAt) }}
          </p>
        </div>
        <p class="text-sm font-bold text-slate-900 shrink-0">$ {{ order.total.toLocaleString() }}</p>
        <span
          class="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full shrink-0"
          :class="STATUS_BADGE[order.status]"
        >
          {{ order.status }}
        </span>
        <AppIcon name="chevron-right" :size="16" class="text-slate-300 shrink-0" />
      </RouterLink>
    </div>
  </div>
</template>
