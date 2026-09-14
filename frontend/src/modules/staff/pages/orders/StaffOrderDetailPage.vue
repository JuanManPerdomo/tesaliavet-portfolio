<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import api from '../../../../lib/api'
import { useOrdersStore } from '../../../../stores/orders'
import { useReturnsStore } from '../../../../stores/returns'
import { useToastStore } from '../../../../stores/toast'
import { useCashRegisterStore } from '../../../../stores/cashRegister'
import { useAuthStore } from '../../../../stores/auth'
import { returnableItems as computeReturnableItems, isOrderReturnable } from '../../../../lib/returnEligibility'

const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Pagado: 'bg-sky-50 text-sky-700',
  Entregado: 'bg-emerald-50 text-emerald-700',
  Cancelado: 'bg-red-50 text-red-600',
}

const route = useRoute()
const ordersStore = useOrdersStore()
const returnsStore = useReturnsStore()
const toastStore = useToastStore()
const cashRegisterStore = useCashRegisterStore()
const authStore = useAuthStore()
// Bodeguero puede vender/registrar pagos cuando queda a cargo, pero
// Devoluciones se dejó fuera a proposito (decision Bodeguero ampliada,
// 2026-09-02, mas sensible que una venta nueva) - el backend ya la
// rechaza (403), esto evita mostrarle un formulario que siempre va a
// fallar.
const canRegisterReturn = computed(() => authStore.hasRole('admin'))

const orderId = computed(() => Number(route.params.id))
const order = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const submitting = ref(false)
const downloadingInvoice = ref(false)

async function handleDownloadInvoice() {
  downloadingInvoice.value = true
  try {
    await ordersStore.downloadInvoicePdf(orderId.value, order.value.payment.invoiceNumber)
  } catch {
    toastStore.error('No se pudo descargar el recibo.')
  } finally {
    downloadingInvoice.value = false
  }
}

// Anular pedido (RF25 en la matriz de trazabilidad): exige motivo
// obligatorio, mismo patron de revelar el formulario que ya usa la
// devolucion mas abajo en este archivo.
const showCancelForm = ref(false)
const cancelReason = ref('')

// Registrar pago (decision 28 en CLAUDE.md): solo aplica mientras el
// pedido sigue Pendiente - una vez pagado, el pago no se edita aca.
const paymentAmount = ref('')
const paymentReference = ref('')
const registeringPayment = ref(false)
const paymentError = ref('')

// Registrar devolucion: solo aplica sobre un pedido Entregado, dentro del
// plazo (decision del roadmap del panel) - un mapa item.id -> cantidad a
// devolver, topado por lo que queda disponible de cada linea.
const returnQuantities = reactive({})
const returnReason = ref('')
const refundMethod = ref('Efectivo')
const refundReference = ref('')
const registeringReturn = ref(false)
const returnError = ref('')

const returnableItems = computed(() => computeReturnableItems(order.value))

const canReturn = computed(() => isOrderReturnable(order.value))

function imageUrl(item) {
  return item.productImage ? `${api.defaults.baseURL}${item.productImage}` : null
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function load() {
  try {
    order.value = await ordersStore.fetchOrder(orderId.value)
    paymentAmount.value = order.value.total
    if (order.value.paymentMethod !== 'Tarjeta') refundMethod.value = order.value.paymentMethod
  } catch {
    errorMessage.value = 'No se pudo cargar el pedido.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  cashRegisterStore.fetchCurrent()
})

async function handleRegisterPayment() {
  paymentError.value = ''
  registeringPayment.value = true
  try {
    order.value = await ordersStore.registerPayment(orderId.value, {
      amount: paymentAmount.value,
      reference: paymentReference.value.trim() || undefined,
    })
    toastStore.success('Pago registrado. El pedido pasó a Pagado.')
  } catch (err) {
    paymentError.value = err.response?.data?.message || 'No se pudo registrar el pago.'
  } finally {
    registeringPayment.value = false
  }
}

async function handleRegisterReturn() {
  returnError.value = ''

  const items = Object.entries(returnQuantities)
    .map(([salesOrderItemId, quantity]) => ({ salesOrderItemId: Number(salesOrderItemId), quantity: Number(quantity) }))
    .filter((i) => i.quantity > 0)

  if (!items.length) {
    returnError.value = 'Indica al menos una cantidad a devolver.'
    return
  }
  if (!returnReason.value.trim()) {
    returnError.value = 'El motivo es requerido.'
    return
  }

  registeringReturn.value = true
  try {
    order.value = await returnsStore.createReturn(orderId.value, {
      reason: returnReason.value.trim(),
      refundMethod: refundMethod.value,
      refundReference: refundReference.value.trim() || undefined,
      items,
    })
    Object.keys(returnQuantities).forEach((key) => delete returnQuantities[key])
    returnReason.value = ''
    refundReference.value = ''
    toastStore.success('Devolución registrada.')
  } catch (err) {
    returnError.value = err.response?.data?.message || 'No se pudo registrar la devolución.'
  } finally {
    registeringReturn.value = false
  }
}

async function markStatus(status) {
  submitting.value = true
  errorMessage.value = ''
  try {
    order.value = await ordersStore.updateOrderStatus(orderId.value, status)
    toastStore.success('Estado del pedido actualizado.')
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo actualizar el estado.'
  } finally {
    submitting.value = false
  }
}

async function handleCancelOrder() {
  if (!cancelReason.value.trim()) {
    errorMessage.value = 'La anulación requiere un motivo.'
    return
  }
  submitting.value = true
  errorMessage.value = ''
  try {
    order.value = await ordersStore.updateOrderStatus(orderId.value, 'Cancelado', {
      cancelReason: cancelReason.value.trim(),
    })
    toastStore.success('Pedido anulado.')
    showCancelForm.value = false
    cancelReason.value = ''
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo anular el pedido.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl">
    <RouterLink
      :to="{ name: 'staff-orders' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a Pedidos
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="!order" class="text-sm text-red-600">{{ errorMessage }}</div>

    <template v-else>
      <div class="flex items-start justify-between mb-5">
        <div>
          <h1 class="text-xl font-extrabold text-slate-900">Pedido #{{ order.id }}</h1>
          <p class="text-xs text-slate-500 mt-1">{{ formatDate(order.createdAt) }}</p>
        </div>
        <span
          class="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full"
          :class="STATUS_BADGE[order.status]"
        >
          {{ order.status }}
        </span>
      </div>

      <p
        v-if="order.status === 'Cancelado' && order.cancelReason"
        class="text-sm text-red-700 bg-red-50 rounded-xl px-4 py-3 mb-5"
      >
        <span class="font-semibold">Motivo de la anulación:</span> {{ order.cancelReason }}
      </p>

      <!-- Cliente -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="user" :size="16" class="text-emerald-700" />
          Cliente
        </h3>
        <p class="text-sm text-slate-700">
          <strong class="text-slate-900">{{ order.customerName }}</strong> — {{ order.customerEmail }}
        </p>
      </div>

      <!-- Facturación -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="truck" :size="16" class="text-emerald-700" />
          Facturación
        </h3>
        <div class="space-y-1.5 text-sm text-slate-600">
          <p><strong class="text-slate-900">{{ order.shippingName }}</strong></p>
          <p v-if="order.shippingPhone">{{ order.shippingPhone }}</p>
          <p>{{ order.shippingAddress }}, {{ order.shippingCity }}</p>
          <p class="text-xs text-slate-400 pt-1">Método de pago: {{ order.paymentMethod }}</p>
          <p v-if="order.notes" class="pt-2 text-slate-500 italic">"{{ order.notes }}"</p>
        </div>
      </div>

      <!-- Producto -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="shopping-bag" :size="16" class="text-emerald-700" />
          Producto
        </h3>

        <div
          v-for="item in order.items"
          :key="item.id"
          class="flex items-center gap-4 py-3 border-b border-slate-50 last:border-0"
        >
          <div class="w-12 h-12 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0">
            <img
              v-if="imageUrl(item)"
              :src="imageUrl(item)"
              :alt="item.productName"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-slate-300">
              <AppIcon name="paw" :size="18" />
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-slate-900 truncate">{{ item.productName }}</p>
            <p class="text-xs text-slate-500">{{ item.quantity }} × $ {{ item.unitPrice.toLocaleString() }}</p>
          </div>
          <p class="text-sm font-bold text-slate-900">$ {{ item.total?.toLocaleString() }}</p>
        </div>

        <div class="pt-4 mt-2 border-t border-slate-100 flex justify-between text-base font-bold text-slate-900">
          <span>Total</span>
          <span>$ {{ order.total.toLocaleString() }}</span>
        </div>
      </div>

      <!-- Pago ya registrado -->
      <div v-if="order.payment" class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="cash" :size="16" class="text-emerald-700" />
          Pago
        </h3>
        <div class="space-y-1.5 text-sm text-slate-600">
          <p>Recibo <strong class="text-slate-900">{{ order.payment.invoiceNumber }}</strong></p>
          <p>Monto: <strong class="text-slate-900">$ {{ order.payment.amount.toLocaleString() }}</strong></p>
          <p v-if="order.payment.reference">Referencia: {{ order.payment.reference }}</p>
          <p class="text-xs text-slate-400">
            Confirmado el {{ formatDate(order.payment.paidAt) }}
            <template v-if="order.payment.registeredByName">por {{ order.payment.registeredByName }}</template>
          </p>
        </div>
        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:underline disabled:opacity-50"
          :disabled="downloadingInvoice"
          @click="handleDownloadInvoice"
        >
          <AppIcon name="download" :size="14" />
          {{ downloadingInvoice ? 'Descargando...' : 'Descargar recibo (PDF)' }}
        </button>
      </div>

      <!-- Registrar pago -->
      <div v-else-if="order.status === 'Pendiente'" class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="cash" :size="16" class="text-emerald-700" />
          Registrar pago
        </h3>

        <div v-if="!cashRegisterStore.current" class="flex items-start gap-2 text-sm text-amber-700 bg-amber-50 rounded-lg px-3 py-3">
          <AppIcon name="alert-triangle" :size="16" class="shrink-0 mt-0.5" />
          <span>
            No hay una caja abierta — no se pueden registrar pagos.
            <RouterLink :to="{ name: 'staff-cash-register' }" class="font-semibold underline">Ir a Caja</RouterLink>
          </span>
        </div>

        <template v-else>
          <div class="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Monto recibido</label>
              <input
                v-model="paymentAmount"
                type="number"
                step="0.01"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">
                Referencia (si fue transferencia)
              </label>
              <input
                v-model="paymentReference"
                type="text"
                placeholder="Número de comprobante"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              />
            </div>
          </div>
          <p v-if="paymentError" class="text-sm text-red-600 mb-3">{{ paymentError }}</p>
          <PrimaryButton :loading="registeringPayment" class="gap-2" @click="handleRegisterPayment">
            <AppIcon name="check" :size="14" />
            Confirmar pago recibido
          </PrimaryButton>
        </template>
      </div>

      <!-- Devoluciones ya registradas -->
      <div v-if="order.returns.length" class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="arrow-back-up" :size="16" class="text-emerald-700" />
          Devoluciones
        </h3>
        <div
          v-for="ret in order.returns"
          :key="ret.id"
          class="py-3 border-b border-slate-50 last:border-0 text-sm text-slate-600 space-y-1"
        >
          <p v-for="item in ret.items" :key="item.id">
            {{ item.quantity }} × {{ item.productName }} — $ {{ item.amount.toLocaleString() }}
          </p>
          <p class="text-xs text-slate-400">
            "{{ ret.reason }}" · reembolso {{ ret.refundMethod }}
            <template v-if="ret.refundReference">({{ ret.refundReference }})</template>
            · {{ formatDate(ret.createdAt) }}
            <template v-if="ret.registeredByName">por {{ ret.registeredByName }}</template>
          </p>
        </div>
      </div>

      <!-- Registrar devolución -->
      <div v-if="canReturn && canRegisterReturn" class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="arrow-back-up" :size="16" class="text-emerald-700" />
          Registrar devolución
        </h3>

        <div v-if="!cashRegisterStore.current" class="flex items-start gap-2 text-sm text-amber-700 bg-amber-50 rounded-lg px-3 py-3">
          <AppIcon name="alert-triangle" :size="16" class="shrink-0 mt-0.5" />
          <span>
            No hay una caja abierta — no se pueden registrar devoluciones.
            <RouterLink :to="{ name: 'staff-cash-register' }" class="font-semibold underline">Ir a Caja</RouterLink>
          </span>
        </div>

        <template v-else>
          <div class="space-y-3 mb-4">
            <div
              v-for="item in returnableItems.filter((i) => i.remaining > 0)"
              :key="item.id"
              class="flex items-center justify-between gap-4"
            >
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-800 truncate">{{ item.productName }}</p>
                <p class="text-xs text-slate-400">Disponible para devolver: {{ item.remaining }}</p>
              </div>
              <input
                v-model="returnQuantities[item.id]"
                type="number"
                min="0"
                :max="item.remaining"
                step="0.01"
                placeholder="0"
                class="w-24 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              />
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-xs font-semibold text-slate-500 mb-1">Motivo</label>
            <textarea
              v-model="returnReason"
              rows="2"
              placeholder="Ej. producto defectuoso, cliente cambió de opinión..."
              class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 resize-none focus:outline-none focus:border-emerald-700"
            ></textarea>
          </div>

          <div class="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Reembolso vía</label>
              <select
                v-model="refundMethod"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              >
                <option value="Efectivo">Efectivo</option>
                <option value="Transferencia">Transferencia</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">
                Referencia (si fue transferencia)
              </label>
              <input
                v-model="refundReference"
                type="text"
                placeholder="Número de comprobante"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              />
            </div>
          </div>

          <p v-if="returnError" class="text-sm text-red-600 mb-3">{{ returnError }}</p>
          <PrimaryButton :loading="registeringReturn" class="gap-2" @click="handleRegisterReturn">
            <AppIcon name="arrow-back-up" :size="14" />
            Confirmar devolución
          </PrimaryButton>
        </template>
      </div>

      <!-- Cambiar estado -->
      <div v-if="order.status === 'Pagado' || order.status === 'Pendiente'" class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-4">Actualizar estado</h3>

        <div class="flex items-center gap-3 flex-wrap">
          <PrimaryButton
            v-if="order.status === 'Pagado'"
            :loading="submitting"
            class="gap-2"
            @click="markStatus('Entregado')"
          >
            <AppIcon name="check" :size="14" />
            Marcar Entregado
          </PrimaryButton>

          <button
            v-if="!showCancelForm"
            type="button"
            class="px-4 py-2 border border-red-200 text-red-600 text-sm font-semibold rounded-lg hover:bg-red-50 transition"
            :disabled="submitting"
            @click="showCancelForm = true"
          >
            Cancelar pedido
          </button>
        </div>

        <div v-if="showCancelForm" class="mt-4 pt-4 border-t border-slate-100">
          <label class="block text-xs font-semibold text-slate-500 mb-1">Motivo de la anulación *</label>
          <textarea
            v-model="cancelReason"
            rows="2"
            placeholder="Ej. el cliente se equivocó de producto, pedido duplicado..."
            class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 resize-none focus:outline-none focus:border-emerald-700"
          ></textarea>
          <div class="flex items-center gap-3 mt-3">
            <button
              type="button"
              class="px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition disabled:opacity-50"
              :disabled="submitting"
              @click="handleCancelOrder"
            >
              Confirmar anulación
            </button>
            <button
              type="button"
              class="px-4 py-2 text-slate-500 text-sm font-semibold hover:text-slate-700 transition"
              :disabled="submitting"
              @click="showCancelForm = false; cancelReason = ''"
            >
              Cancelar
            </button>
          </div>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600 mt-4">{{ errorMessage }}</p>
      </div>
    </template>
  </div>
</template>
