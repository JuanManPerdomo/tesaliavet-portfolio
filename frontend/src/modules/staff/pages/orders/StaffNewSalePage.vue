<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { useOrdersStore } from '../../../../stores/orders'
import { useStaffClientsStore } from '../../../../stores/staffClients'
import { useProductsStore } from '../../../../stores/products'
import { useCashRegisterStore } from '../../../../stores/cashRegister'
import { useToastStore } from '../../../../stores/toast'
import { formatCOP, formatQuantity } from '../../../../lib/pricing'

const router = useRouter()
const ordersStore = useOrdersStore()
const staffClientsStore = useStaffClientsStore()
const productsStore = useProductsStore()
const cashRegisterStore = useCashRegisterStore()
const toastStore = useToastStore()

const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')

// Paso 1: cliente - siempre una cuenta ya registrada (decision 81), se
// busca igual que en Devoluciones/Clientes, nunca se crea aca.
const customerSearch = ref('')
const searchingCustomer = ref(false)
const customerResults = ref([])
const selectedCustomer = ref(null)

async function searchCustomer() {
  searchingCustomer.value = true
  try {
    await staffClientsStore.fetchClients({ search: customerSearch.value || undefined, status: 'active' })
    customerResults.value = staffClientsStore.clients
  } finally {
    searchingCustomer.value = false
  }
}

function selectCustomer(client) {
  selectedCustomer.value = client
}

function changeCustomer() {
  selectedCustomer.value = null
}

// Paso 2: productos - mismo patron de lineas dinamicas que Ordenes de
// compra, pero sobre cualquier producto activo (sin scope de proveedor).
const items = ref([{ productId: '', quantity: 1 }])

function addItem() {
  items.value.push({ productId: '', quantity: 1 })
}

function removeItem(index) {
  items.value.splice(index, 1)
}

function optionsForRow(index) {
  const usedElsewhere = new Set(
    items.value.filter((_, i) => i !== index).map((it) => Number(it.productId)).filter(Boolean)
  )
  return productsStore.adminProducts.filter((p) => !usedElsewhere.has(p.id))
}

function productInfo(item) {
  return productsStore.adminProducts.find((p) => p.id === Number(item.productId))
}

function subtotal(item) {
  const info = productInfo(item)
  const qty = Number(item.quantity) || 0
  return info ? qty * Number(info.price) : 0
}

function taxOf(item) {
  const info = productInfo(item)
  const qty = Number(item.quantity) || 0
  return info ? qty * Number(info.price) * (Number(info.taxRate) / 100) : 0
}

const itemsSubtotal = computed(() => items.value.reduce((sum, item) => sum + subtotal(item), 0))
const itemsTax = computed(() => items.value.reduce((sum, item) => sum + taxOf(item), 0))
const total = computed(() => itemsSubtotal.value + itemsTax.value)

// Paso 3: pago - mismo metodo/gate que el resto del sistema (decision 28/46).
const paymentMethod = ref('Efectivo')
const paymentReference = ref('')

async function load() {
  loading.value = true
  try {
    await Promise.all([
      productsStore.fetchAdminProducts({ status: 'active', perPage: 100 }),
      cashRegisterStore.fetchCurrent(),
    ])
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function handleSubmit() {
  errorMessage.value = ''

  if (!selectedCustomer.value) {
    errorMessage.value = 'Selecciona un cliente'
    return
  }
  const validItems = items.value.filter((it) => it.productId && Number(it.quantity) > 0)
  if (!validItems.length) {
    errorMessage.value = 'Agrega al menos un producto'
    return
  }

  const payload = {
    customerId: selectedCustomer.value.id,
    paymentMethod: paymentMethod.value,
    reference: paymentReference.value.trim() || undefined,
    items: validItems.map((it) => ({ productId: it.productId, quantity: it.quantity })),
  }

  saving.value = true
  try {
    const order = await ordersStore.registerWalkinSale(payload)
    toastStore.success(`Venta registrada — pedido #${order.id}.`)
    router.push({ name: 'staff-order-detail', params: { id: order.id } })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo registrar la venta.'
  } finally {
    saving.value = false
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
      Volver a pedidos
    </RouterLink>

    <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Nueva venta presencial</h1>
    <p class="text-sm text-slate-500 mb-6">
      Registra una compra hecha en el mostrador — queda como pedido pagado de una vez.
    </p>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>

    <div
      v-else-if="!cashRegisterStore.current"
      class="flex items-start gap-2 text-sm text-amber-700 bg-amber-50 rounded-lg px-4 py-3 mb-5"
    >
      <AppIcon name="alert-triangle" :size="16" class="shrink-0 mt-0.5" />
      <span>
        No hay una caja abierta — no se pueden registrar ventas.
        <RouterLink :to="{ name: 'staff-cash-register' }" class="font-semibold underline">Ir a Caja</RouterLink>
      </span>
    </div>

    <form v-else class="space-y-5" @submit.prevent="handleSubmit">
      <!-- Cliente -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="font-bold text-slate-900 mb-4">Cliente</h2>

        <div v-if="!selectedCustomer">
          <div class="flex gap-2 mb-3">
            <input
              v-model="customerSearch"
              type="text"
              placeholder="Buscar por nombre o correo..."
              class="flex-1 border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              @keyup.enter="searchCustomer"
            />
            <button
              type="button"
              class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
              @click="searchCustomer"
            >
              <AppIcon name="search" :size="16" />
            </button>
          </div>

          <div v-if="searchingCustomer" class="text-sm text-slate-500 py-3">Buscando...</div>
          <div
            v-else-if="customerResults.length === 0 && customerSearch"
            class="text-sm text-slate-500 bg-slate-50 rounded-lg px-3 py-3"
          >
            No se encontró ningún cliente con esa búsqueda.
            <RouterLink :to="{ name: 'staff-users' }" class="font-semibold text-emerald-700 hover:underline">
              Crear cliente nuevo
            </RouterLink>
            desde Usuarios y roles.
          </div>
          <div v-else class="divide-y divide-slate-50">
            <button
              v-for="client in customerResults"
              :key="client.id"
              type="button"
              class="w-full flex items-center justify-between gap-3 py-2.5 text-left hover:bg-slate-50 rounded-lg px-2 -mx-2"
              @click="selectCustomer(client)"
            >
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-800 truncate">
                  {{ client.firstName }} {{ client.lastName }}
                </p>
                <p class="text-xs text-slate-400 truncate">{{ client.email }}</p>
              </div>
              <AppIcon name="chevron-right" :size="16" class="text-slate-300 shrink-0" />
            </button>
          </div>
        </div>

        <div v-else class="flex items-center justify-between gap-3 bg-emerald-50 rounded-lg px-4 py-3">
          <div class="flex items-center gap-2 min-w-0">
            <AppIcon name="user-check" :size="18" class="text-emerald-700 shrink-0" />
            <div class="min-w-0">
              <p class="text-sm font-semibold text-slate-800 truncate">
                {{ selectedCustomer.firstName }} {{ selectedCustomer.lastName }}
              </p>
              <p class="text-xs text-slate-500 truncate">{{ selectedCustomer.email }}</p>
            </div>
          </div>
          <button
            type="button"
            class="text-xs font-semibold text-emerald-700 hover:underline shrink-0"
            @click="changeCustomer"
          >
            Cambiar
          </button>
        </div>
      </div>

      <!-- Productos -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-slate-900">Productos</h2>
          <button
            type="button"
            class="inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-700 hover:underline"
            @click="addItem"
          >
            <AppIcon name="plus" :size="14" />
            Agregar producto
          </button>
        </div>

        <div class="space-y-3">
          <div
            v-for="(item, index) in items"
            :key="index"
            class="grid grid-cols-[1fr_90px_110px_32px] gap-2 items-end"
          >
            <div>
              <label v-if="index === 0" class="block text-[11px] font-semibold text-slate-500 mb-1">Producto</label>
              <select
                v-model="item.productId"
                required
                class="w-full border border-slate-200 rounded-lg px-2.5 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              >
                <option value="" disabled>Selecciona</option>
                <option v-for="product in optionsForRow(index)" :key="product.id" :value="product.id">
                  {{ product.name }} ({{ product.sku }}) — {{ formatCOP(product.price) }}
                </option>
              </select>
            </div>
            <div>
              <label v-if="index === 0" class="block text-[11px] font-semibold text-slate-500 mb-1">Cantidad</label>
              <input
                v-model="item.quantity"
                type="number"
                min="0.01"
                step="0.01"
                required
                class="w-full border border-slate-200 rounded-lg px-2.5 py-2 text-sm text-slate-800 focus:outline-none focus:border-emerald-700"
              />
              <p v-if="productInfo(item)" class="text-[11px] text-slate-400 mt-1">
                {{ formatQuantity(item.quantity, productInfo(item).unitLabel, productInfo(item).unitWeightKg) }}
                — stock: {{ productInfo(item).stock }}
              </p>
            </div>
            <div>
              <label v-if="index === 0" class="block text-[11px] font-semibold text-slate-500 mb-1">Subtotal</label>
              <p class="px-2.5 py-2 text-sm font-semibold text-slate-800">{{ formatCOP(subtotal(item)) }}</p>
            </div>
            <button
              type="button"
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-400 hover:text-red-600 hover:border-red-300 disabled:opacity-30 disabled:pointer-events-none"
              :disabled="items.length === 1"
              title="Quitar producto"
              @click="removeItem(index)"
            >
              <AppIcon name="x" :size="14" />
            </button>
          </div>
        </div>

        <div class="border-t border-slate-100 mt-5 pt-4 flex flex-col items-end gap-0.5 text-sm text-slate-500">
          <p>Subtotal: {{ formatCOP(itemsSubtotal) }}</p>
          <p>IVA: {{ formatCOP(itemsTax) }}</p>
          <p class="text-right mt-1">
            <span class="text-xs text-slate-400 block">Total a cobrar</span>
            <span class="text-xl font-extrabold text-slate-900">{{ formatCOP(total) }}</span>
          </p>
        </div>
      </div>

      <!-- Pago -->
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h2 class="font-bold text-slate-900 mb-4">Pago</h2>
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Método</label>
            <select
              v-model="paymentMethod"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
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
              v-model="paymentReference"
              type="text"
              placeholder="Número de comprobante"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
            />
          </div>
        </div>
      </div>

      <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

      <div class="flex justify-end gap-3">
        <RouterLink
          :to="{ name: 'staff-orders' }"
          class="px-4 py-2.5 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
        >
          Cancelar
        </RouterLink>
        <PrimaryButton type="submit" :loading="saving">
          Registrar venta — {{ formatCOP(total) }}
        </PrimaryButton>
      </div>
    </form>
  </div>
</template>
