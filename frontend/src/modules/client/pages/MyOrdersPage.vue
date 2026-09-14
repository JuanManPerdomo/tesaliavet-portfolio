<script setup>
import { ref, computed, onMounted } from 'vue'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import api from '../../../lib/api'
import { useOrdersStore } from '../../../stores/orders'

const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Pagado: 'bg-sky-50 text-sky-700',
  Entregado: 'bg-emerald-50 text-emerald-700',
  Cancelado: 'bg-red-50 text-red-600',
}

const FILTERS = [
  { value: 'all', label: 'Todos' },
  { value: 'Pendiente', label: 'Pendientes' },
  { value: 'Pagado', label: 'Pagados' },
  { value: 'Entregado', label: 'Entregados' },
  { value: 'Cancelado', label: 'Cancelados' },
]

const ordersStore = useOrdersStore()
const activeFilter = ref('all')

const filteredOrders = computed(() => {
  if (activeFilter.value === 'all') return ordersStore.orders
  return ordersStore.orders.filter((o) => o.status === activeFilter.value)
})

function firstItem(order) {
  return order.items?.[0]
}

function imageUrl(item) {
  return item?.productImage ? `${api.defaults.baseURL}${item.productImage}` : null
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(() => {
  ordersStore.fetchOrders()
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-5xl mx-auto px-6 py-12 w-full">
      <div class="mb-8">
        <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Mis Pedidos</h1>
        <p class="text-sm text-slate-500">
          Revisa el estado de los productos que has apartado.
        </p>
      </div>

      <div class="flex overflow-x-auto gap-6 border-b border-slate-200 mb-6">
        <button
          v-for="filter in FILTERS"
          :key="filter.value"
          type="button"
          class="pb-3 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="
            activeFilter === filter.value
              ? 'text-emerald-700 border-emerald-700'
              : 'text-slate-500 border-transparent hover:text-emerald-700'
          "
          @click="activeFilter = filter.value"
        >
          {{ filter.label }}
        </button>
      </div>

      <p v-if="ordersStore.error" class="text-sm text-red-600 mb-6">{{ ordersStore.error }}</p>

      <div v-if="ordersStore.loading" class="text-sm text-slate-500">Cargando...</div>

      <div
        v-else-if="filteredOrders.length === 0"
        class="bg-white border border-slate-200 rounded-2xl p-12 text-center"
      >
        <AppIcon name="shopping-bag" :size="28" class="text-slate-300 mx-auto mb-3" />
        <p class="text-sm text-slate-500 mb-4">No tienes pedidos en esta categoría.</p>
        <RouterLink
          to="/productos"
          class="inline-flex items-center gap-2 text-emerald-700 font-semibold hover:underline"
        >
          Ver catálogo
        </RouterLink>
      </div>

      <div v-else class="flex flex-col gap-3">
        <RouterLink
          v-for="order in filteredOrders"
          :key="order.id"
          :to="{ name: 'order-detail', params: { id: order.id } }"
          class="bg-white rounded-2xl border border-slate-200 p-5 flex flex-col md:flex-row md:items-center gap-4 hover:border-emerald-300 transition"
        >
          <div class="w-12 h-12 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0">
            <img
              v-if="imageUrl(firstItem(order))"
              :src="imageUrl(firstItem(order))"
              :alt="firstItem(order)?.productName"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-slate-300">
              <AppIcon name="paw" :size="20" />
            </div>
          </div>

          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-slate-900 truncate">
              {{ firstItem(order)?.productName }}
              <span v-if="order.items.length > 1" class="text-slate-400 font-normal">
                +{{ order.items.length - 1 }} más
              </span>
            </p>
            <p class="text-xs text-slate-500">Pedido #{{ order.id }} · {{ formatDate(order.createdAt) }}</p>
          </div>

          <div class="w-full md:w-32 flex-shrink-0">
            <p class="text-xs text-slate-400">Total</p>
            <p class="text-sm font-bold text-slate-900">$ {{ order.total.toLocaleString() }}</p>
          </div>

          <div class="flex-shrink-0">
            <span
              class="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide"
              :class="STATUS_BADGE[order.status]"
            >
              {{ order.status }}
            </span>
          </div>

          <AppIcon name="chevron-right" :size="18" class="text-slate-300 flex-shrink-0 md:ml-2" />
        </RouterLink>
      </div>
    </main>

    <Footer />
  </div>
</template>
