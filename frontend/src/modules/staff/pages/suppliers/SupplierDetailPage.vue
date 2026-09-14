<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import SupplierFormModal from './SupplierFormModal.vue'
import AssociateProductModal from './AssociateProductModal.vue'
import { useSuppliersStore } from '../../../../stores/suppliers'
import { useProductsStore } from '../../../../stores/products'
import { useToastStore } from '../../../../stores/toast'
import { formatCOP } from '../../../../lib/pricing'

const route = useRoute()
const suppliersStore = useSuppliersStore()
const productsStore = useProductsStore()
const toastStore = useToastStore()

const supplierId = computed(() => Number(route.params.id))
const supplier = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const showEditForm = ref(false)
const editSaving = ref(false)
const editError = ref('')

const showDeactivateConfirm = ref(false)
const deactivating = ref(false)

const showAssociateForm = ref(false)
const associateSaving = ref(false)
const associateError = ref('')

function formatDate(isoDate) {
  if (!isoDate) return '—'
  return new Date(isoDate).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function load() {
  loading.value = true
  try {
    supplier.value = await suppliersStore.fetchSupplierDetail(supplierId.value)
  } catch {
    errorMessage.value = 'No se pudo cargar el proveedor.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await Promise.all([load(), productsStore.fetchAdminProducts({ status: 'active', perPage: 100 })])
})

async function handleEditSubmit(payload) {
  editSaving.value = true
  editError.value = ''
  try {
    supplier.value = await suppliersStore.updateSupplier(supplierId.value, payload)
    toastStore.success('Proveedor actualizado.')
    showEditForm.value = false
  } catch (err) {
    editError.value = err.response?.data?.message || 'No se pudo guardar el proveedor.'
  } finally {
    editSaving.value = false
  }
}

async function confirmDeactivate() {
  deactivating.value = true
  try {
    await suppliersStore.deactivateSupplier(supplierId.value)
    toastStore.success('Proveedor desactivado.')
    showDeactivateConfirm.value = false
    await load()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo desactivar el proveedor.')
  } finally {
    deactivating.value = false
  }
}

async function handleActivate() {
  try {
    await suppliersStore.reactivateSupplier(supplierId.value)
    toastStore.success('Proveedor activado.')
    await load()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo activar el proveedor.')
  }
}

async function handleAssociateSubmit(form) {
  associateSaving.value = true
  associateError.value = ''
  try {
    supplier.value = await suppliersStore.associateProduct(supplierId.value, form)
    toastStore.success('Producto asociado.')
    showAssociateForm.value = false
  } catch (err) {
    associateError.value = err.response?.data?.message || 'No se pudo asociar el producto.'
  } finally {
    associateSaving.value = false
  }
}
</script>

<template>
  <div class="max-w-6xl">
    <RouterLink
      :to="{ name: 'staff-suppliers' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a proveedores
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="!supplier" class="text-sm text-red-600">{{ errorMessage }}</div>

    <template v-else>
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center flex-shrink-0">
            <AppIcon name="truck" :size="20" />
          </div>
          <h1 class="text-2xl font-extrabold text-slate-900">{{ supplier.name }}</h1>
        </div>
        <span
          class="text-[11px] font-bold uppercase px-3 py-1 rounded-full"
          :class="supplier.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
        >
          {{ supplier.isActive ? 'Activo' : 'Inactivo' }}
        </span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 class="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wide mb-5">
              <AppIcon name="file-text" :size="14" />
              Información de la empresa
            </h2>
            <dl class="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
              <div>
                <dt class="text-xs text-slate-400">Tipo / Nº documento</dt>
                <dd class="text-slate-800 font-medium">
                  {{ supplier.documentNumber ? `${supplier.documentType || ''} ${supplier.documentNumber}` : '—' }}
                </dd>
              </div>
              <div>
                <dt class="text-xs text-slate-400">Nombre del contacto</dt>
                <dd class="text-slate-800 font-medium">{{ supplier.contactName || '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-400">Teléfono</dt>
                <dd class="text-slate-800 font-medium">{{ supplier.contactPhone || '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-400">Correo</dt>
                <dd class="text-slate-800 font-medium">{{ supplier.contactEmail || '—' }}</dd>
              </div>
              <div class="col-span-2">
                <dt class="text-xs text-slate-400">Dirección</dt>
                <dd class="text-slate-800 font-medium">
                  {{ [supplier.address, supplier.city].filter(Boolean).join(', ') || '—' }}
                </dd>
              </div>
              <div v-if="supplier.notes" class="col-span-2">
                <dt class="text-xs text-slate-400">Notas</dt>
                <dd class="text-slate-700">{{ supplier.notes }}</dd>
              </div>
            </dl>
          </div>

          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <div class="flex items-center justify-between mb-5">
              <h2 class="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wide">
                <AppIcon name="package" :size="14" />
                Productos asociados ({{ supplier.productsCount }})
              </h2>
              <button
                type="button"
                class="px-3.5 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50 flex items-center gap-1.5"
                @click="showAssociateForm = true"
              >
                <AppIcon name="plus" :size="14" />
                Asociar producto
              </button>
            </div>

            <p v-if="!supplier.products.length" class="text-sm text-slate-500 text-center py-6">
              Sin productos asociados aún.
            </p>
            <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
            <div v-else class="sm:hidden divide-y divide-slate-100">
              <div v-for="row in supplier.products" :key="row.productId" class="py-3">
                <p class="font-medium text-slate-800">{{ row.productName }}</p>
                <p class="text-xs text-slate-500 mt-1">SKU proveedor: {{ row.supplierSku || '—' }}</p>
                <p class="text-xs text-slate-500">
                  {{ row.purchasePrice !== null ? formatCOP(row.purchasePrice) : 'Sin precio' }} ·
                  {{ row.leadTimeDays !== null ? `${row.leadTimeDays} días de entrega` : 'Sin entrega estimada' }}
                </p>
              </div>
            </div>

            <table v-if="supplier.products.length" class="hidden sm:table w-full text-sm">
              <thead>
                <tr class="border-b border-slate-100 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                  <th class="py-2 pr-3">Producto</th>
                  <th class="py-2 px-3">SKU proveedor</th>
                  <th class="py-2 px-3 text-right">P. compra</th>
                  <th class="py-2 pl-3">Entrega</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in supplier.products" :key="row.productId" class="border-b border-slate-50 last:border-0">
                  <td class="py-2.5 pr-3 font-medium text-slate-800">{{ row.productName }}</td>
                  <td class="py-2.5 px-3 text-slate-500">{{ row.supplierSku || '—' }}</td>
                  <td class="py-2.5 px-3 text-right text-slate-600">
                    {{ row.purchasePrice !== null ? formatCOP(row.purchasePrice) : '—' }}
                  </td>
                  <td class="py-2.5 pl-3 text-slate-500">
                    {{ row.leadTimeDays !== null ? `${row.leadTimeDays} días` : '—' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="space-y-4">
          <RouterLink
            :to="{ name: 'staff-purchase-orders', query: { supplierId: supplier.id, supplierName: supplier.name } }"
            class="bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2.5 rounded-lg font-semibold text-sm transition flex items-center justify-center gap-2"
          >
            <AppIcon name="file-invoice" :size="16" />
            Ver órdenes de compra
          </RouterLink>

          <button
            type="button"
            class="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-2"
            @click="showEditForm = true"
          >
            <AppIcon name="edit" :size="16" />
            Editar proveedor
          </button>

          <button
            v-if="supplier.isActive"
            type="button"
            class="w-full px-4 py-2.5 border border-red-200 rounded-lg text-sm font-semibold text-red-600 hover:bg-red-50 flex items-center justify-center gap-2"
            @click="showDeactivateConfirm = true"
          >
            <AppIcon name="archive" :size="16" />
            Desactivar
          </button>
          <button
            v-else
            type="button"
            class="w-full px-4 py-2.5 border border-emerald-200 rounded-lg text-sm font-semibold text-emerald-700 hover:bg-emerald-50 flex items-center justify-center gap-2"
            @click="handleActivate"
          >
            <AppIcon name="refresh" :size="16" />
            Activar
          </button>

          <div class="bg-emerald-50 rounded-2xl p-5">
            <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">Resumen</h3>
            <dl class="space-y-2 text-sm">
              <div class="flex items-center justify-between">
                <dt class="text-slate-500">Órdenes totales</dt>
                <dd class="font-semibold text-slate-800">{{ supplier.purchaseOrdersCount }}</dd>
              </div>
              <div class="flex items-center justify-between">
                <dt class="text-slate-500">Última orden</dt>
                <dd class="font-semibold text-slate-800">{{ formatDate(supplier.lastPurchaseOrderDate) }}</dd>
              </div>
              <div class="flex items-center justify-between">
                <dt class="text-slate-500">Productos asociados</dt>
                <dd class="font-semibold text-slate-800">{{ supplier.productsCount }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <SupplierFormModal
        :open="showEditForm"
        :supplier="supplier"
        :saving="editSaving"
        :server-error="editError"
        @close="showEditForm = false"
        @submit="handleEditSubmit"
      />

      <AssociateProductModal
        :open="showAssociateForm"
        :products="productsStore.adminProducts"
        :saving="associateSaving"
        :server-error="associateError"
        @close="showAssociateForm = false"
        @submit="handleAssociateSubmit"
      />

      <ConfirmDialog
        :open="showDeactivateConfirm"
        title="Desactivar proveedor"
        message="El proveedor dejará de aparecer como opción al asignarlo a productos. Podrás reactivarlo cuando quieras."
        confirm-label="Sí, desactivar"
        :loading="deactivating"
        @cancel="showDeactivateConfirm = false"
        @confirm="confirmDeactivate"
      />
    </template>
  </div>
</template>
