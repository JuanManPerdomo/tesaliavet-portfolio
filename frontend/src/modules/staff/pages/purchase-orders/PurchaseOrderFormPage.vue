<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { usePurchaseOrdersStore } from '../../../../stores/purchaseOrders'
import { useProductsStore } from '../../../../stores/products'
import { useSuppliersStore } from '../../../../stores/suppliers'
import { useToastStore } from '../../../../stores/toast'
import { formatCOP, formatQuantity } from '../../../../lib/pricing'

const route = useRoute()
const router = useRouter()
const purchaseOrdersStore = usePurchaseOrdersStore()
const productsStore = useProductsStore()
const suppliersStore = useSuppliersStore()
const toastStore = useToastStore()

const orderId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => orderId.value !== null)

const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')

const supplierId = ref('')
const expectedDeliveryDate = ref('')
const notes = ref('')
const shippingCost = ref('')
const taxAmount = ref('')
const items = ref([{ productId: '', quantityOrdered: 1, unitCost: '' }])

// Productos asociados al proveedor elegido (supplier_products, decision 19)
// - una orden no puede mezclar productos de varios proveedores.
const supplierProducts = ref([])
const loadingSupplierProducts = ref(false)

async function loadSupplierProducts(id) {
  if (!id) {
    supplierProducts.value = []
    return
  }
  loadingSupplierProducts.value = true
  try {
    const detail = await suppliersStore.fetchSupplierDetail(id)
    supplierProducts.value = detail.products.map((p) => ({
      id: p.productId,
      name: p.productName,
      sku: p.sku,
      purchasePrice: p.purchasePrice,
      unitLabel: p.unitLabel,
      unitWeightKg: p.unitWeightKg,
    }))
  } finally {
    loadingSupplierProducts.value = false
  }
}

// Disparado solo por el @change real del <select> (nunca por la asignacion
// programatica de supplierId.value durante la carga inicial en edicion) -
// evitar un watch() aqui es a proposito: un watch corria en paralelo con la
// carga de la orden y, segun el timing de red, a veces terminaba DESPUES de
// que load() ya habia puesto los items reales, borrandolos de nuevo (bug
// real reportado por Juan Manuel el 2026-08-13 - "al editar la orden
// aparece como nueva").
async function onSupplierChange() {
  const hadSelections = items.value.some((item) => item.productId)
  await loadSupplierProducts(supplierId.value)
  if (hadSelections) {
    toastStore.success('Se reiniciaron los productos porque cambiaste de proveedor.')
  }
  items.value = [{ productId: '', quantityOrdered: 1, unitCost: '' }]
}

// Opciones del selector de producto para una fila: los productos del
// proveedor, sin los que ya se usaron en otra fila (no se repite producto
// en la misma orden) - pero sin ocultar la propia seleccion actual de la
// fila, incluso si ya no esta asociada al proveedor (dato historico al
// editar).
function optionsForRow(index) {
  const usedElsewhere = new Set(
    items.value.filter((_, i) => i !== index).map((it) => Number(it.productId)).filter(Boolean)
  )
  const options = supplierProducts.value.filter((p) => !usedElsewhere.has(p.id))

  const currentId = Number(items.value[index].productId)
  if (currentId && !options.some((p) => p.id === currentId)) {
    const known = productsStore.adminProducts.find((p) => p.id === currentId)
    if (known) {
      options.push({
        id: known.id,
        name: known.name,
        sku: known.sku,
        purchasePrice: known.purchasePrice,
        unitLabel: known.unitLabel,
        unitWeightKg: known.unitWeightKg,
      })
    }
  }
  return options
}

function addItem() {
  items.value.push({ productId: '', quantityOrdered: 1, unitCost: '' })
}

function removeItem(index) {
  items.value.splice(index, 1)
}

function onProductChange(item) {
  if (item.unitCost !== '') return
  const product = supplierProducts.value.find((p) => p.id === Number(item.productId))
  if (product) item.unitCost = product.purchasePrice
}

function unitInfoForItem(item) {
  const id = Number(item.productId)
  return (
    supplierProducts.value.find((p) => p.id === id) ||
    productsStore.adminProducts.find((p) => p.id === id)
  )
}

function subtotal(item) {
  const qty = Number(item.quantityOrdered) || 0
  const cost = Number(item.unitCost) || 0
  return qty * cost
}

const itemsSubtotal = computed(() => items.value.reduce((sum, item) => sum + subtotal(item), 0))
const total = computed(
  () => itemsSubtotal.value + (Number(shippingCost.value) || 0) + (Number(taxAmount.value) || 0)
)

async function load() {
  loading.value = true
  try {
    await Promise.all([
      productsStore.fetchSuppliers(),
      productsStore.fetchAdminProducts({ status: 'active', perPage: 100 }),
    ])

    if (isEdit.value) {
      const order = await purchaseOrdersStore.fetchPurchaseOrderDetail(orderId.value)
      if (order.status !== 'Borrador') {
        toastStore.error('Solo se puede editar una orden en estado Borrador.')
        router.replace({ name: 'staff-purchase-order-detail', params: { id: orderId.value } })
        return
      }
      supplierId.value = order.supplierId
      await loadSupplierProducts(order.supplierId)
      expectedDeliveryDate.value = order.expectedDeliveryDate || ''
      notes.value = order.notes || ''
      shippingCost.value = order.shippingCost || ''
      taxAmount.value = order.taxAmount || ''
      items.value = order.items.map((item) => ({
        productId: item.productId,
        quantityOrdered: item.quantityOrdered,
        unitCost: item.unitCost,
      }))
    }
  } catch {
    errorMessage.value = 'No se pudo cargar la información necesaria.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function handleSubmit() {
  errorMessage.value = ''

  if (!supplierId.value) {
    errorMessage.value = 'Selecciona un proveedor'
    return
  }
  if (!items.value.length) {
    errorMessage.value = 'Agrega al menos un producto'
    return
  }

  const payload = {
    supplierId: supplierId.value,
    expectedDeliveryDate: expectedDeliveryDate.value || null,
    notes: notes.value || null,
    shippingCost: shippingCost.value || 0,
    taxAmount: taxAmount.value || 0,
    items: items.value.map((item) => ({
      productId: item.productId,
      quantityOrdered: item.quantityOrdered,
      unitCost: item.unitCost,
    })),
  }

  saving.value = true
  try {
    let order
    if (isEdit.value) {
      order = await purchaseOrdersStore.updatePurchaseOrder(orderId.value, payload)
      toastStore.success('Orden de compra actualizada.')
    } else {
      order = await purchaseOrdersStore.createPurchaseOrder(payload)
      toastStore.success('Orden de compra creada.')
    }
    router.push({ name: 'staff-purchase-order-detail', params: { id: order.id } })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo guardar la orden.'
  } finally {
    saving.value = false
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

    <h1 class="text-2xl font-extrabold text-slate-900 mb-6">
      {{ isEdit ? 'Editar orden de compra' : 'Nueva orden de compra' }}
    </h1>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>

    <form v-else class="space-y-5" @submit.prevent="handleSubmit">
      <div class="bg-white rounded-2xl border border-slate-200 p-6 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Proveedor *</label>
            <select
              v-model="supplierId"
              required
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              @change="onSupplierChange"
            >
              <option value="" disabled>Selecciona un proveedor</option>
              <option v-for="supplier in productsStore.suppliers" :key="supplier.id" :value="supplier.id">
                {{ supplier.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Entrega esperada</label>
            <input
              v-model="expectedDeliveryDate"
              type="date"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-500 mb-1">Notas</label>
          <textarea
            v-model="notes"
            rows="2"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          ></textarea>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-slate-900">Productos</h2>
          <button
            type="button"
            class="inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-700 hover:underline disabled:opacity-40 disabled:pointer-events-none"
            :disabled="!supplierId || !supplierProducts.length"
            @click="addItem"
          >
            <AppIcon name="plus" :size="14" />
            Agregar producto
          </button>
        </div>

        <p v-if="!supplierId" class="text-sm text-slate-500 mb-2">
          Selecciona un proveedor para ver sus productos asociados.
        </p>
        <p v-else-if="!loadingSupplierProducts && !supplierProducts.length" class="text-sm text-amber-700 bg-amber-50 rounded-lg px-3 py-2 mb-2">
          Este proveedor no tiene productos asociados todavía. Asócialos primero desde su ficha
          (Proveedores → {{ productsStore.suppliers.find((s) => s.id === Number(supplierId))?.name }} → "Asociar producto").
        </p>

        <div v-if="supplierId && supplierProducts.length" class="space-y-3">
          <div
            v-for="(item, index) in items"
            :key="index"
            class="grid grid-cols-[1fr_90px_110px_100px_32px] gap-2 items-end"
          >
            <div>
              <label v-if="index === 0" class="block text-[11px] font-semibold text-slate-500 mb-1">Producto</label>
              <select
                v-model="item.productId"
                required
                class="w-full border border-slate-200 rounded-lg px-2.5 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
                @change="onProductChange(item)"
              >
                <option value="" disabled>Selecciona</option>
                <option v-for="product in optionsForRow(index)" :key="product.id" :value="product.id">
                  {{ product.name }} ({{ product.sku }}) — {{ product.unitLabel }}
                </option>
              </select>
            </div>
            <div>
              <label v-if="index === 0" class="block text-[11px] font-semibold text-slate-500 mb-1">Cantidad</label>
              <input
                v-model="item.quantityOrdered"
                type="number"
                min="0.01"
                step="0.01"
                required
                class="w-full border border-slate-200 rounded-lg px-2.5 py-2 text-sm text-slate-800 focus:outline-none focus:border-emerald-700"
              />
              <p v-if="unitInfoForItem(item)" class="text-[11px] text-slate-400 mt-1">
                {{ formatQuantity(item.quantityOrdered, unitInfoForItem(item).unitLabel, unitInfoForItem(item).unitWeightKg) }}
              </p>
            </div>
            <div>
              <label v-if="index === 0" class="block text-[11px] font-semibold text-slate-500 mb-1">Costo unit.</label>
              <input
                v-model="item.unitCost"
                type="number"
                min="0"
                step="0.01"
                required
                class="w-full border border-slate-200 rounded-lg px-2.5 py-2 text-sm text-slate-800 focus:outline-none focus:border-emerald-700"
              />
            </div>
            <div>
              <label v-if="index === 0" class="block text-[11px] font-semibold text-slate-500 mb-1">Subtotal</label>
              <p class="px-2.5 py-2 text-sm font-semibold text-slate-800">
                {{ formatCOP(subtotal(item)) }}
              </p>
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

        <div class="border-t border-slate-100 mt-5 pt-4 space-y-3">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Costo de transporte</label>
              <input
                v-model="shippingCost"
                type="number"
                min="0"
                step="0.01"
                placeholder="0"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:border-emerald-700"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Impuestos</label>
              <input
                v-model="taxAmount"
                type="number"
                min="0"
                step="0.01"
                placeholder="0"
                class="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:border-emerald-700"
              />
            </div>
          </div>
          <p class="text-[11px] text-slate-400">
            Déjalos en 0 si el proveedor ya incluye todo en el precio del producto.
          </p>

          <div class="flex flex-col items-end gap-0.5 text-sm text-slate-500 pt-1">
            <p>Subtotal productos: {{ formatCOP(itemsSubtotal) }}</p>
            <p v-if="Number(shippingCost) > 0">Transporte: {{ formatCOP(Number(shippingCost)) }}</p>
            <p v-if="Number(taxAmount) > 0">Impuestos: {{ formatCOP(Number(taxAmount)) }}</p>
            <p class="text-right mt-1">
              <span class="text-xs text-slate-400 block">Total de la orden</span>
              <span class="text-xl font-extrabold text-slate-900">{{ formatCOP(total) }}</span>
            </p>
          </div>
        </div>
      </div>

      <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

      <div class="flex justify-end gap-3">
        <RouterLink
          :to="{ name: 'staff-purchase-orders' }"
          class="px-4 py-2.5 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
        >
          Cancelar
        </RouterLink>
        <PrimaryButton type="submit" :loading="saving">
          {{ isEdit ? 'Guardar cambios' : 'Crear orden' }}
        </PrimaryButton>
      </div>
    </form>
  </div>
</template>
