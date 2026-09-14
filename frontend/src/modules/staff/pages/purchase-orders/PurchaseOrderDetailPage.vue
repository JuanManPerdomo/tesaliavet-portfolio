<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import { usePurchaseOrdersStore } from '../../../../stores/purchaseOrders'
import { useToastStore } from '../../../../stores/toast'
import { formatCOP, formatQuantity } from '../../../../lib/pricing'
import api from '../../../../lib/api'

const ALLOWED_INVOICE_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
const MAX_INVOICE_SIZE = 5 * 1024 * 1024

const STATUS_BADGE = {
  Borrador: 'bg-slate-100 text-slate-600',
  Enviada: 'bg-amber-50 text-amber-700',
  Recibida: 'bg-emerald-50 text-emerald-700',
  Cancelada: 'bg-red-50 text-red-600',
}

const route = useRoute()
const purchaseOrdersStore = usePurchaseOrdersStore()
const toastStore = useToastStore()

const orderId = computed(() => Number(route.params.id))
const order = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const updating = ref(false)

const invoiceInput = ref(null)
const uploadingInvoice = ref(false)

const confirmAction = ref(null) // 'Recibida' | 'Cancelada' | null
const showConfirm = computed(() => confirmAction.value !== null)

const CONFIRM_COPY = {
  Recibida: {
    title: 'Marcar orden como recibida',
    message:
      'Esto suma la cantidad pedida de cada producto al stock del inventario. Esta acción no se puede deshacer.',
    confirmLabel: 'Sí, marcar como recibida',
  },
  Cancelada: {
    title: 'Cancelar orden de compra',
    message: 'La orden quedará cerrada y no se podrá reactivar. Esta acción no se puede deshacer.',
    confirmLabel: 'Sí, cancelar orden',
  },
}

async function load() {
  loading.value = true
  try {
    order.value = await purchaseOrdersStore.fetchPurchaseOrderDetail(orderId.value)
  } catch {
    errorMessage.value = 'No se pudo cargar la orden de compra.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

function formatDate(isoDate) {
  if (!isoDate) return '—'
  return new Date(isoDate).toLocaleDateString('es-CO', { day: '2-digit', month: 'long', year: 'numeric' })
}

async function sendOrder() {
  updating.value = true
  try {
    order.value = await purchaseOrdersStore.updateStatus(orderId.value, 'Enviada')
    toastStore.success('Orden marcada como enviada al proveedor.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo actualizar la orden.')
  } finally {
    updating.value = false
  }
}

function askConfirm(status) {
  confirmAction.value = status
}

async function confirmStatusChange() {
  const status = confirmAction.value
  updating.value = true
  try {
    order.value = await purchaseOrdersStore.updateStatus(orderId.value, status)
    toastStore.success(status === 'Recibida' ? 'Orden recibida: stock actualizado.' : 'Orden cancelada.')
    confirmAction.value = null
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo actualizar la orden.')
  } finally {
    updating.value = false
  }
}

function triggerInvoiceInput() {
  invoiceInput.value?.click()
}

async function handleInvoiceSelected(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  if (!ALLOWED_INVOICE_TYPES.includes(file.type)) {
    toastStore.error('Formato inválido. Solo se aceptan PDF, JPG o PNG.')
    return
  }
  if (file.size > MAX_INVOICE_SIZE) {
    toastStore.error('El archivo supera el tamaño máximo de 5MB.')
    return
  }

  uploadingInvoice.value = true
  try {
    order.value = await purchaseOrdersStore.uploadInvoice(orderId.value, file)
    toastStore.success('Factura adjuntada.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo adjuntar la factura.')
  } finally {
    uploadingInvoice.value = false
  }
}

async function openInvoice() {
  try {
    const { data } = await api.get(order.value.invoiceUrl, { responseType: 'blob' })
    window.open(URL.createObjectURL(data), '_blank')
  } catch {
    toastStore.error('No se pudo abrir la factura.')
  }
}

async function handleRemoveInvoice() {
  uploadingInvoice.value = true
  try {
    order.value = await purchaseOrdersStore.removeInvoice(orderId.value)
    toastStore.success('Factura eliminada.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo quitar la factura.')
  } finally {
    uploadingInvoice.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl">
    <RouterLink
      :to="{ name: 'staff-purchase-orders' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a órdenes de compra
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="!order" class="text-sm text-red-600">{{ errorMessage }}</div>

    <template v-else>
      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <div class="flex items-start justify-between mb-5">
          <div>
            <h1 class="text-xl font-extrabold text-slate-900">Orden de compra #{{ order.id }}</h1>
            <p class="text-sm text-slate-500 mt-1">{{ order.supplierName }}</p>
            <div
              v-if="order.supplierContactPhone || order.supplierContactEmail"
              class="flex flex-wrap items-center gap-3 mt-1.5 text-xs"
            >
              <a
                v-if="order.supplierContactPhone"
                :href="`tel:${order.supplierContactPhone}`"
                class="inline-flex items-center gap-1 text-emerald-700 hover:underline"
              >
                <AppIcon name="phone" :size="12" />
                {{ order.supplierContactPhone }}
              </a>
              <a
                v-if="order.supplierContactEmail"
                :href="`mailto:${order.supplierContactEmail}`"
                class="inline-flex items-center gap-1 text-emerald-700 hover:underline"
              >
                <AppIcon name="mail" :size="12" />
                {{ order.supplierContactEmail }}
              </a>
            </div>
          </div>
          <span class="text-[11px] font-bold uppercase px-3 py-1 rounded-full" :class="STATUS_BADGE[order.status]">
            {{ order.status }}
          </span>
        </div>

        <div class="grid grid-cols-3 gap-4 text-sm border-t border-slate-100 pt-5">
          <div>
            <p class="text-xs text-slate-400 mb-1">Fecha de creación</p>
            <p class="font-semibold text-slate-800">{{ formatDate(order.orderDate) }}</p>
          </div>
          <div>
            <p class="text-xs text-slate-400 mb-1">Entrega esperada</p>
            <p class="font-semibold text-slate-800">{{ formatDate(order.expectedDeliveryDate) }}</p>
          </div>
          <div>
            <p class="text-xs text-slate-400 mb-1">Recibida el</p>
            <p class="font-semibold text-slate-800">{{ formatDate(order.receivedAt) }}</p>
          </div>
          <div v-if="order.createdByName" class="col-span-3">
            <p class="text-xs text-slate-400 mb-1">Creada por</p>
            <p class="text-slate-700">{{ order.createdByName }}</p>
          </div>
          <div v-if="order.notes" class="col-span-3">
            <p class="text-xs text-slate-400 mb-1">Notas</p>
            <p class="text-slate-700">{{ order.notes }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h2 class="font-bold text-slate-900 mb-4">Productos</h2>

        <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
        <div class="sm:hidden divide-y divide-slate-100">
          <div v-for="item in order.items" :key="item.id" class="py-3">
            <div class="flex items-start justify-between gap-2">
              <p class="font-medium text-slate-800">{{ item.productName }}</p>
              <p class="font-semibold text-slate-800 shrink-0">{{ formatCOP(item.subtotal) }}</p>
            </div>
            <p class="text-xs text-slate-500 mt-1">
              {{ item.sku }} · {{ formatQuantity(item.quantityOrdered, item.unitLabel, item.unitWeightKg) }} ·
              {{ formatCOP(item.unitCost) }} c/u
            </p>
          </div>
        </div>

        <table class="hidden sm:table w-full text-sm">
          <thead>
            <tr class="text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-100">
              <th class="pb-2 pr-3">Producto</th>
              <th class="pb-2 pr-3">SKU</th>
              <th class="pb-2 pr-3 text-right">Cantidad</th>
              <th class="pb-2 pr-3 text-right">Costo unit.</th>
              <th class="pb-2 text-right">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in order.items" :key="item.id" class="border-b border-slate-50 last:border-0">
              <td class="py-2.5 pr-3 font-medium text-slate-800">{{ item.productName }}</td>
              <td class="py-2.5 pr-3 text-slate-500">{{ item.sku }}</td>
              <td class="py-2.5 pr-3 text-right text-slate-700">
                {{ formatQuantity(item.quantityOrdered, item.unitLabel, item.unitWeightKg) }}
              </td>
              <td class="py-2.5 pr-3 text-right text-slate-700">{{ formatCOP(item.unitCost) }}</td>
              <td class="py-2.5 text-right font-semibold text-slate-800">
                {{ formatCOP(item.subtotal) }}
              </td>
            </tr>
          </tbody>
        </table>

        <div class="flex flex-col items-end gap-0.5 text-sm text-slate-500 border-t border-slate-100 mt-4 pt-4">
          <p>Subtotal productos: {{ formatCOP(order.itemsSubtotal) }}</p>
          <p v-if="order.shippingCost > 0">Transporte: {{ formatCOP(order.shippingCost) }}</p>
          <p v-if="order.taxAmount > 0">Impuestos: {{ formatCOP(order.taxAmount) }}</p>
          <p class="text-right mt-1">
            <span class="text-xs text-slate-400 block">Total de la orden</span>
            <span class="text-xl font-extrabold text-slate-900">{{ formatCOP(order.totalAmount) }}</span>
          </p>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h2 class="font-bold text-slate-900 mb-1">Factura del proveedor</h2>
        <p class="text-xs text-slate-500 mb-4">
          Adjunta el documento real que te entregó el proveedor (PDF, JPG o PNG, máx. 5MB) como respaldo de la compra.
        </p>

        <div class="flex flex-wrap items-center gap-3">
          <button
            v-if="order.invoiceUrl"
            type="button"
            class="inline-flex items-center gap-1.5 text-emerald-700 text-sm font-semibold hover:underline"
            @click="openInvoice"
          >
            <AppIcon name="file-text" :size="14" /> Ver factura adjunta
          </button>
          <span v-else class="text-sm text-slate-400">Todavía no se ha adjuntado ninguna factura.</span>

          <button
            type="button"
            class="px-3.5 py-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50 flex items-center gap-1.5 disabled:opacity-50"
            :disabled="uploadingInvoice"
            @click="triggerInvoiceInput"
          >
            <AppIcon name="cloud" :size="14" />
            {{ uploadingInvoice ? 'Subiendo...' : order.invoiceUrl ? 'Reemplazar factura' : 'Adjuntar factura' }}
          </button>
          <button
            v-if="order.invoiceUrl"
            type="button"
            class="px-3.5 py-2 border border-red-200 rounded-lg text-xs font-semibold text-red-600 hover:bg-red-50 flex items-center gap-1.5 disabled:opacity-50"
            :disabled="uploadingInvoice"
            @click="handleRemoveInvoice"
          >
            <AppIcon name="x" :size="14" />
            Quitar factura
          </button>
          <input
            ref="invoiceInput"
            type="file"
            accept="application/pdf,image/jpeg,image/png"
            class="hidden"
            @change="handleInvoiceSelected"
          />
        </div>
      </div>

      <p v-if="errorMessage" class="text-sm text-red-600 mb-4">{{ errorMessage }}</p>

      <p v-if="order.status === 'Borrador'" class="text-xs text-slate-500 mb-3">
        "Marcar como enviada" no le manda ningún mensaje al proveedor — el sistema no tiene esa
        integración. Contáctalo tú mismo (teléfono/correo arriba) por WhatsApp, llamada o correo,
        y usa este botón solo para dejar el registro en el sistema.
      </p>

      <div class="flex flex-wrap gap-3">
        <RouterLink
          v-if="order.status === 'Borrador'"
          :to="{ name: 'staff-purchase-order-edit', params: { id: order.id } }"
          class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center gap-2"
        >
          <AppIcon name="edit" :size="16" />
          Editar
        </RouterLink>

        <PrimaryButton v-if="order.status === 'Borrador'" :loading="updating" class="gap-2" @click="sendOrder">
          <AppIcon name="send" :size="16" />
          Marcar como enviada
        </PrimaryButton>

        <PrimaryButton
          v-if="order.status === 'Enviada'"
          :loading="updating"
          class="gap-2"
          @click="askConfirm('Recibida')"
        >
          <AppIcon name="check" :size="16" />
          Marcar como recibida
        </PrimaryButton>

        <button
          v-if="order.status === 'Borrador' || order.status === 'Enviada'"
          type="button"
          class="px-4 py-2.5 border border-red-200 rounded-lg text-sm font-semibold text-red-600 hover:bg-red-50 flex items-center gap-2"
          @click="askConfirm('Cancelada')"
        >
          <AppIcon name="x" :size="16" />
          Cancelar orden
        </button>
      </div>
    </template>

    <ConfirmDialog
      v-if="confirmAction"
      :open="showConfirm"
      :title="CONFIRM_COPY[confirmAction].title"
      :message="CONFIRM_COPY[confirmAction].message"
      :confirm-label="CONFIRM_COPY[confirmAction].confirmLabel"
      :loading="updating"
      @cancel="confirmAction = null"
      @confirm="confirmStatusChange"
    />
  </div>
</template>
