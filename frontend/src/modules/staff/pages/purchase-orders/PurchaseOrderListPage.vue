<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import { usePurchaseOrdersStore } from '../../../../stores/purchaseOrders'
import { useToastStore } from '../../../../stores/toast'
import { formatCOP } from '../../../../lib/pricing'

const STATUS_OPTIONS = [
  { value: 'all', label: 'Todas' },
  { value: 'Borrador', label: 'Borrador' },
  { value: 'Enviada', label: 'Enviada' },
  { value: 'Recibida', label: 'Recibida' },
  { value: 'Cancelada', label: 'Cancelada' },
]

const STATUS_BADGE = {
  Borrador: 'bg-slate-100 text-slate-600',
  Enviada: 'bg-amber-50 text-amber-700',
  Recibida: 'bg-emerald-50 text-emerald-700',
  Cancelada: 'bg-red-50 text-red-600',
}

const route = useRoute()
const purchaseOrdersStore = usePurchaseOrdersStore()
const toastStore = useToastStore()

const search = ref('')
const statusFilter = ref('all')
const perPage = ref(10)

const supplierId = computed(() => route.query.supplierId || undefined)
const supplierName = computed(() => route.query.supplierName || '')

const deletingId = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

function load(page = 1) {
  purchaseOrdersStore.fetchPurchaseOrders({
    search: search.value,
    status: statusFilter.value,
    supplierId: supplierId.value,
    page,
    perPage: perPage.value,
  })
}

onMounted(() => load())

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

function formatDate(isoDate) {
  if (!isoDate) return '—'
  return new Date(isoDate).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function askDelete(id) {
  deletingId.value = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await purchaseOrdersStore.deletePurchaseOrder(deletingId.value)
    toastStore.success('Orden de compra eliminada.')
    showDeleteConfirm.value = false
    load(1)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar la orden.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <RouterLink
      v-if="supplierId"
      :to="{ name: 'staff-supplier-detail', params: { id: supplierId } }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver al proveedor
    </RouterLink>

    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900">
          {{ supplierId ? `Órdenes de compra de ${supplierName}` : 'Órdenes de compra' }}
        </h1>
        <p class="text-sm text-slate-500 mt-1">
          {{ supplierId ? 'Historial de órdenes con este proveedor.' : 'Pedidos de reabastecimiento a proveedores.' }}
        </p>
      </div>
      <PrimaryButton class="gap-2" :to="{ name: 'staff-purchase-order-new' }">
        <AppIcon name="plus" :size="16" />
        Nueva orden
      </PrimaryButton>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por proveedor o # de orden..."
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

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="purchaseOrdersStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="purchaseOrdersStore.error" class="p-8 text-sm text-red-600">{{ purchaseOrdersStore.error }}</div>
      <div v-else-if="!purchaseOrdersStore.purchaseOrders.length" class="p-8 text-sm text-slate-500 text-center">
        No hay órdenes de compra con estos filtros.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="order in purchaseOrdersStore.purchaseOrders" :key="order.id" class="p-4">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="font-semibold text-slate-800">#{{ order.id }} — {{ order.supplierName }}</p>
              <p class="text-xs text-slate-400">
                {{ formatDate(order.orderDate) }} · Entrega: {{ formatDate(order.expectedDeliveryDate) }}
              </p>
            </div>
            <span class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold" :class="STATUS_BADGE[order.status]">
              {{ order.status }}
            </span>
          </div>
          <p class="text-sm font-semibold text-slate-800 mt-2">{{ formatCOP(order.totalAmount) }}</p>

          <div class="flex gap-2 mt-3">
            <RouterLink
              :to="{ name: 'staff-purchase-order-detail', params: { id: order.id } }"
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
              title="Ver detalle"
            >
              <AppIcon name="eye" :size="14" />
            </RouterLink>

            <template v-if="order.status === 'Borrador'">
              <RouterLink
                :to="{ name: 'staff-purchase-order-edit', params: { id: order.id } }"
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                title="Editar"
              >
                <AppIcon name="edit" :size="14" />
              </RouterLink>
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                title="Eliminar"
                @click="askDelete(order.id)"
              >
                <AppIcon name="x" :size="14" />
              </button>
            </template>
          </div>
        </div>
      </div>

      <table v-if="purchaseOrdersStore.purchaseOrders.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">#</th>
            <th class="px-5 py-3">Proveedor</th>
            <th class="px-5 py-3">Fecha</th>
            <th class="px-5 py-3">Entrega esperada</th>
            <th class="px-5 py-3">Total</th>
            <th class="px-5 py-3">Estado</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="order in purchaseOrdersStore.purchaseOrders"
            :key="order.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3 font-semibold text-slate-800">#{{ order.id }}</td>
            <td class="px-5 py-3 text-slate-700">{{ order.supplierName }}</td>
            <td class="px-5 py-3 text-slate-500">{{ formatDate(order.orderDate) }}</td>
            <td class="px-5 py-3 text-slate-500">{{ formatDate(order.expectedDeliveryDate) }}</td>
            <td class="px-5 py-3 font-semibold text-slate-800">
              {{ formatCOP(order.totalAmount) }}
            </td>
            <td class="px-5 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="STATUS_BADGE[order.status]">
                {{ order.status }}
              </span>
            </td>
            <td class="px-5 py-3">
              <div class="flex justify-end gap-2">
                <RouterLink
                  :to="{ name: 'staff-purchase-order-detail', params: { id: order.id } }"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Ver detalle"
                >
                  <AppIcon name="eye" :size="14" />
                </RouterLink>

                <template v-if="order.status === 'Borrador'">
                  <RouterLink
                    :to="{ name: 'staff-purchase-order-edit', params: { id: order.id } }"
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                    title="Editar"
                  >
                    <AppIcon name="edit" :size="14" />
                  </RouterLink>
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                    title="Eliminar"
                    @click="askDelete(order.id)"
                  >
                    <AppIcon name="x" :size="14" />
                  </button>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminPagination
      :pagination="purchaseOrdersStore.pagination"
      item-label="órdenes"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar orden de compra"
      message="Esta acción no se puede deshacer. Solo se pueden eliminar órdenes en estado Borrador (nunca enviadas al proveedor)."
      confirm-label="Sí, eliminar"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
