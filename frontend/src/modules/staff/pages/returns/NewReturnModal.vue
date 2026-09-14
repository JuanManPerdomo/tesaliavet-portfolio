<script setup>
import { ref, watch } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { useOrdersStore } from '../../../../stores/orders'
import { returnableItems, isOrderReturnable } from '../../../../lib/returnEligibility'

const props = defineProps({
  open: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  serverError: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])

const ordersStore = useOrdersStore()

const search = ref('')
const searching = ref(false)
const rows = ref([])

const selected = ref(null) // { orderId, orderItemId, productName, customerName, remaining }
const quantity = ref('')
const reason = ref('')
const refundMethod = ref('Efectivo')
const refundReference = ref('')

function flattenRows(orders) {
  const flat = []
  for (const order of orders) {
    if (!isOrderReturnable(order)) continue
    for (const item of returnableItems(order)) {
      if (item.remaining <= 0) continue
      flat.push({
        orderId: order.id,
        orderItemId: item.id,
        productName: item.productName,
        customerName: order.customerName,
        remaining: item.remaining,
        unitPrice: item.unitPrice,
      })
    }
  }
  return flat
}

async function runSearch() {
  searching.value = true
  try {
    await ordersStore.fetchStaffOrders({ status: 'Entregado', search: search.value || undefined })
    rows.value = flattenRows(ordersStore.staffOrders)
  } finally {
    searching.value = false
  }
}

function selectRow(row) {
  selected.value = row
  quantity.value = row.remaining
  reason.value = ''
  refundReference.value = ''
}

function backToSearch() {
  selected.value = null
}

function handleSubmit() {
  const qty = Number(quantity.value)
  if (!qty || qty <= 0 || qty > selected.value.remaining) return
  if (!reason.value.trim()) return

  emit('submit', {
    orderId: selected.value.orderId,
    payload: {
      reason: reason.value.trim(),
      refundMethod: refundMethod.value,
      refundReference: refundReference.value.trim() || undefined,
      items: [{ salesOrderItemId: selected.value.orderItemId, quantity: qty }],
    },
  })
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      search.value = ''
      selected.value = null
      runSearch()
    }
  }
)
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('close')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 max-h-[85vh] flex flex-col">
        <button
          type="button"
          class="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="16" />
        </button>

        <h3 class="text-lg font-bold text-slate-900 mb-4">Nueva devolución</h3>

        <!-- Paso 1: buscar producto -->
        <template v-if="!selected">
          <div class="flex gap-2 mb-4">
            <input
              v-model="search"
              type="text"
              placeholder="Buscar por producto, cliente o # de pedido..."
              class="flex-1 border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              @keyup.enter="runSearch"
            />
            <button
              class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
              @click="runSearch"
            >
              Buscar
            </button>
          </div>

          <div class="overflow-y-auto flex-1 -mx-6 px-6">
            <div v-if="searching" class="text-sm text-slate-500 text-center py-6">Buscando...</div>
            <div v-else-if="!rows.length" class="text-sm text-slate-500 text-center py-6">
              No hay productos elegibles para devolución con estos criterios (pedido Entregado, dentro de 8 días).
            </div>
            <button
              v-for="row in rows"
              :key="`${row.orderId}-${row.orderItemId}`"
              type="button"
              class="w-full flex items-center justify-between gap-3 py-3 px-3 -mx-3 rounded-lg border-b border-slate-50 last:border-0 hover:bg-slate-50 text-left"
              @click="selectRow(row)"
            >
              <div class="min-w-0">
                <p class="text-sm font-semibold text-slate-800 truncate">{{ row.productName }}</p>
                <p class="text-xs text-slate-400 truncate">
                  Pedido #{{ row.orderId }} — {{ row.customerName }} — disponible: {{ row.remaining }}
                </p>
              </div>
              <AppIcon name="chevron-right" :size="16" class="text-slate-300 shrink-0" />
            </button>
          </div>
        </template>

        <!-- Paso 2: formulario de devolución -->
        <template v-else>
          <button
            type="button"
            class="inline-flex items-center gap-2 text-emerald-700 text-xs font-semibold hover:underline mb-4 self-start"
            @click="backToSearch"
          >
            <AppIcon name="arrow-left" :size="14" />
            Buscar otro producto
          </button>

          <div class="bg-slate-50 rounded-lg p-3 mb-4">
            <p class="text-sm font-semibold text-slate-800">{{ selected.productName }}</p>
            <p class="text-xs text-slate-500">
              Pedido #{{ selected.orderId }} — {{ selected.customerName }} — disponible: {{ selected.remaining }}
            </p>
          </div>

          <form class="space-y-4 overflow-y-auto flex-1" @submit.prevent="handleSubmit">
            <p v-if="serverError" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ serverError }}</p>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Cantidad a devolver *</label>
              <input
                v-model="quantity"
                type="number"
                min="0"
                :max="selected.remaining"
                step="0.01"
                required
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Motivo *</label>
              <textarea
                v-model="reason"
                rows="2"
                required
                placeholder="Ej. producto defectuoso, cliente cambió de opinión..."
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 resize-none focus:outline-none focus:border-emerald-700"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">Reembolso vía</label>
                <select
                  v-model="refundMethod"
                  class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
                >
                  <option value="Efectivo">Efectivo</option>
                  <option value="Transferencia">Transferencia</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-500 mb-1">Referencia</label>
                <input
                  v-model="refundReference"
                  type="text"
                  placeholder="Número de comprobante"
                  class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
                />
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-2">
              <button
                type="button"
                class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
                @click="emit('close')"
              >
                Cancelar
              </button>
              <PrimaryButton type="submit" :loading="saving">Confirmar devolución</PrimaryButton>
            </div>
          </form>
        </template>
      </div>
    </div>
  </Teleport>
</template>
