<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import api from '../../../lib/api'
import { useOrdersStore } from '../../../stores/orders'
import { useToastStore } from '../../../stores/toast'

const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Pagado: 'bg-sky-50 text-sky-700',
  Entregado: 'bg-emerald-50 text-emerald-700',
  Cancelado: 'bg-red-50 text-red-600',
}

const STATUS_ICON = {
  Pendiente: 'clock',
  Pagado: 'cash',
  Entregado: 'check',
  Cancelado: 'x',
}

const STEPS = ['Pendiente', 'Pagado', 'Entregado']

const route = useRoute()
const ordersStore = useOrdersStore()
const toastStore = useToastStore()

const orderId = computed(() => Number(route.params.id))
const order = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const downloadingInvoice = ref(false)

const currentStepIndex = computed(() => STEPS.indexOf(order.value?.status))

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

onMounted(async () => {
  try {
    order.value = await ordersStore.fetchOrder(orderId.value)
  } catch {
    errorMessage.value = 'No se pudo cargar el pedido.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-3xl mx-auto px-6 py-12 w-full">
      <RouterLink
        :to="{ name: 'my-orders' }"
        class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-6"
      >
        <AppIcon name="arrow-left" :size="16" />
        Volver a mis pedidos
      </RouterLink>

      <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
      <div
        v-else-if="!order"
        class="bg-white border border-red-100 rounded-2xl p-10 text-center text-sm text-red-600"
      >
        {{ errorMessage }}
      </div>

      <template v-else>
        <div class="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <h1 class="text-2xl font-extrabold text-slate-900">Pedido #{{ order.id }}</h1>
            <p class="text-sm text-slate-500 mt-1">{{ formatDate(order.createdAt) }}</p>
          </div>
          <span
            class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide"
            :class="STATUS_BADGE[order.status]"
          >
            <AppIcon :name="STATUS_ICON[order.status]" :size="13" />
            {{ order.status }}
          </span>
        </div>

        <!-- Progreso -->
        <div v-if="order.status !== 'Cancelado'" class="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
          <div class="flex items-center">
            <template v-for="(step, index) in STEPS" :key="step">
              <div class="flex flex-col items-center flex-1">
                <div
                  class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors"
                  :class="
                    index <= currentStepIndex
                      ? 'bg-emerald-700 border-emerald-700 text-white'
                      : 'bg-white border-slate-200 text-slate-400'
                  "
                >
                  <AppIcon v-if="index < currentStepIndex" name="check" :size="14" />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <span
                  class="mt-2 text-[11px] font-semibold text-center"
                  :class="index <= currentStepIndex ? 'text-emerald-700' : 'text-slate-400'"
                >
                  {{ step }}
                </span>
              </div>
              <div
                v-if="index < STEPS.length - 1"
                class="h-0.5 flex-1 -mt-5"
                :class="index < currentStepIndex ? 'bg-emerald-700' : 'bg-slate-200'"
              ></div>
            </template>
          </div>
        </div>
        <div v-else class="bg-red-50 border border-red-100 rounded-2xl p-5 mb-6 text-sm text-red-700">
          Este pedido fue cancelado. Si tienes dudas, escríbenos por WhatsApp o PQRS.
        </div>

        <!-- Pago -->
        <div v-if="order.payment" class="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
          <h2 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
            <AppIcon name="cash" :size="16" class="text-emerald-700" />
            Pago confirmado
          </h2>
          <div class="space-y-1.5 text-sm text-slate-600">
            <p>Recibo <strong class="text-slate-900">{{ order.payment.invoiceNumber }}</strong></p>
            <p>Monto: <strong class="text-slate-900">$ {{ order.payment.amount.toLocaleString() }}</strong></p>
            <p v-if="order.payment.reference">Referencia: {{ order.payment.reference }}</p>
            <p class="text-xs text-slate-400">Confirmado el {{ formatDate(order.payment.paidAt) }}</p>
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

        <!-- Devoluciones -->
        <div v-if="order.returns?.length" class="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
          <h2 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
            <AppIcon name="arrow-back-up" :size="16" class="text-emerald-700" />
            Devoluciones
          </h2>
          <div
            v-for="ret in order.returns"
            :key="ret.id"
            class="py-3 border-b border-slate-50 last:border-0 text-sm text-slate-600 space-y-1"
          >
            <p v-for="item in ret.items" :key="item.id">
              {{ item.quantity }} × {{ item.productName }} — $ {{ item.amount.toLocaleString() }}
            </p>
            <p class="text-xs text-slate-400">
              Reembolso vía {{ ret.refundMethod }} · {{ formatDate(ret.createdAt) }}
            </p>
          </div>
        </div>

        <!-- Producto(s) -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
          <h2 class="text-sm font-bold text-slate-900 mb-4">Producto</h2>

          <div
            v-for="item in order.items"
            :key="item.id"
            class="flex items-center gap-4 py-3 border-b border-slate-50 last:border-0"
          >
            <div class="w-14 h-14 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0">
              <img
                v-if="imageUrl(item)"
                :src="imageUrl(item)"
                :alt="item.productName"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-slate-300">
                <AppIcon name="paw" :size="20" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-slate-900 truncate">{{ item.productName }}</p>
              <p class="text-xs text-slate-500">{{ item.quantity }} × $ {{ item.unitPrice.toLocaleString() }}</p>
            </div>
            <p class="text-sm font-bold text-slate-900">$ {{ item.total?.toLocaleString() }}</p>
          </div>

          <div class="pt-4 mt-2 border-t border-slate-100 space-y-1.5">
            <div class="flex justify-between text-sm text-slate-500">
              <span>Subtotal</span>
              <span>$ {{ order.subtotal.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between text-sm text-slate-500">
              <span>IVA</span>
              <span>$ {{ order.taxTotal.toLocaleString() }}</span>
            </div>
            <div class="flex justify-between text-base font-bold text-slate-900">
              <span>Total</span>
              <span>$ {{ order.total.toLocaleString() }}</span>
            </div>
          </div>
        </div>

        <!-- Facturación -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 class="text-sm font-bold text-slate-900 mb-4">Datos de facturación</h2>
          <div class="space-y-1.5 text-sm text-slate-600">
            <p><strong class="text-slate-900">{{ order.shippingName }}</strong></p>
            <p v-if="order.shippingPhone">{{ order.shippingPhone }}</p>
            <p>{{ order.shippingAddress }}, {{ order.shippingCity }}</p>
            <p class="text-xs text-slate-400 pt-2">
              Pago: {{ order.paymentMethod }} — recoges en tienda, no hacemos envíos
            </p>
            <p v-if="order.notes" class="pt-2 text-slate-500 italic">"{{ order.notes }}"</p>
          </div>
        </div>
      </template>
    </main>

    <Footer />
  </div>
</template>
