<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { useProductsStore } from '../../../../stores/products'
import { useToastStore } from '../../../../stores/toast'
import {
  calcMargin,
  formatCOP,
  formatQuantity,
  TAX_RATE_OPTIONS,
  UNIT_OPTIONS,
  PACKAGE_UNITS,
} from '../../../../lib/pricing'
import api from '../../../../lib/api'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()
const toastStore = useToastStore()

const productId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => productId.value !== null)

const form = ref({
  sku: '',
  name: '',
  barcode: '',
  description: '',
  brand: '',
  purchasePrice: '',
  sellingPrice: '',
  taxRate: 19,
  stock: '',
  minStock: '',
  unitLabel: 'Unidad',
  unitWeightKg: '',
  topCategoryId: '',
  categoryId: '',
  speciesId: '',
  supplierId: '',
  isActive: true,
})

// SKU sugerido automaticamente por categoria (ej. MED-002, decision 62) -
// solo para productos nuevos, nunca pisa el SKU real de uno existente.
// skuIsSuggested distingue "el sistema lo puso" de "el admin lo escribio a
// mano", para no sobreescribir en silencio un SKU que el admin ya edito si
// vuelve a cambiar de subcategoria.
const skuIsSuggested = ref(false)
const suggestingSku = ref(false)

const existingPhotoUrl = ref(null)
const photoFile = ref(null)
const photoPreview = ref('')
const removePhoto = ref(false)
const fileInput = ref(null)

const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')

const margin = computed(() => calcMargin(form.value.purchasePrice, form.value.sellingPrice))
const stockIsLow = computed(() => {
  const stock = Number(form.value.stock)
  const minStock = Number(form.value.minStock)
  return form.value.stock !== '' && form.value.minStock !== '' && stock <= minStock
})
const isPackageUnit = computed(() => PACKAGE_UNITS.includes(form.value.unitLabel))
const subcategories = computed(() => productsStore.subcategoriesOf(form.value.topCategoryId))
const speciesOptions = computed(() => productsStore.speciesForCategory(form.value.topCategoryId))

function onPhotoChange(event) {
  const file = event.target.files[0]
  if (!file) return
  photoFile.value = file
  removePhoto.value = false
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value)
  photoPreview.value = URL.createObjectURL(file)
}

function clearPhoto() {
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value)
  photoFile.value = null
  photoPreview.value = ''
  removePhoto.value = !!existingPhotoUrl.value
  existingPhotoUrl.value = null
  if (fileInput.value) fileInput.value.value = ''
}

function onTopCategoryChange() {
  form.value.categoryId = ''
  form.value.speciesId = ''
}

function onSkuInput() {
  skuIsSuggested.value = false
}

async function applySkuSuggestion() {
  if (!form.value.categoryId) return
  suggestingSku.value = true
  try {
    form.value.sku = await productsStore.suggestSku(form.value.categoryId)
    skuIsSuggested.value = true
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo sugerir un SKU. Escríbelo manualmente.')
  } finally {
    suggestingSku.value = false
  }
}

// Solo para productos nuevos: al elegir subcategoria, si el SKU esta vacio
// o sigue siendo el que el sistema sugirio antes (no algo que el admin
// escribio a mano), se sugiere uno nuevo para la subcategoria elegida.
async function onCategoryChange() {
  if (isEdit.value) return
  if (form.value.sku && !skuIsSuggested.value) return
  await applySkuSuggestion()
}

onMounted(async () => {
  await Promise.all([
    productsStore.fetchCategories(),
    productsStore.fetchSuppliers(),
    productsStore.fetchSpecies(),
  ])

  if (isEdit.value) {
    try {
      const product = await productsStore.fetchProduct(productId.value)
      form.value = {
        sku: product.sku,
        name: product.name,
        barcode: product.barcode ?? '',
        description: product.description ?? '',
        brand: product.brand ?? '',
        purchasePrice: product.purchasePrice ?? '',
        sellingPrice: product.price ?? '',
        taxRate: product.taxRate ?? 19,
        stock: product.stock ?? '',
        minStock: product.minStock ?? '',
        unitLabel: product.unitLabel ?? 'Unidad',
        unitWeightKg: product.unitWeightKg ?? '',
        topCategoryId: product.category?.parentId ?? '',
        categoryId: product.category?.id ?? '',
        speciesId: product.species?.id ?? '',
        supplierId: product.supplier?.id ?? '',
        isActive: product.isActive,
      }
      existingPhotoUrl.value = product.image
    } catch {
      errorMessage.value = 'No se pudo cargar el producto.'
    }
  }

  loading.value = false
})

onBeforeUnmount(() => {
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value)
})

async function handleSubmit() {
  errorMessage.value = ''
  // Obligatorios pedidos por Juan Manuel (2026-08-31): todo excepto
  // proveedor y "Peso por unidad" (opcional a propósito, decision 33 - no
  // todos los productos vienen en paquetes de peso conocido).
  const requiredFields = [
    [form.value.sku, 'el SKU'],
    [form.value.name, 'el nombre'],
    [form.value.brand, 'la marca'],
    [form.value.description, 'la descripción'],
    [form.value.purchasePrice, 'el precio de compra'],
    [form.value.sellingPrice, 'el precio de venta'],
    [form.value.stock, 'el stock actual'],
    [form.value.minStock, 'el stock mínimo'],
    [form.value.topCategoryId, 'la categoría'],
    [form.value.categoryId, 'la subcategoría'],
    [form.value.speciesId, 'la especie'],
  ]
  const missing = requiredFields.find(([value]) => value === '' || value === null || value === undefined)
  if (missing) {
    errorMessage.value = `Falta completar ${missing[1]}.`
    return
  }
  // El stock se cuenta en unidades completas, sin decimales (a diferencia de
  // las cantidades de una venta/compra puntual, que si pueden ser
  // fraccionarias para productos por Kg/Litro, decision 33) - mismo criterio
  // validado en el backend, esto solo evita el viaje al servidor.
  if (form.value.stock !== '' && Number(form.value.stock) % 1 !== 0) {
    errorMessage.value = 'El stock debe ser un número entero, sin decimales.'
    return
  }
  if (form.value.minStock !== '' && Number(form.value.minStock) % 1 !== 0) {
    errorMessage.value = 'El stock mínimo debe ser un número entero, sin decimales.'
    return
  }

  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('sku', form.value.sku)
    payload.append('name', form.value.name)
    payload.append('categoryId', form.value.categoryId)
    payload.append('barcode', form.value.barcode || '')
    payload.append('description', form.value.description || '')
    payload.append('brand', form.value.brand || '')
    payload.append('purchasePrice', form.value.purchasePrice || '0')
    payload.append('sellingPrice', form.value.sellingPrice || '0')
    payload.append('stock', form.value.stock || '0')
    payload.append('minStock', form.value.minStock || '0')
    payload.append('unitLabel', form.value.unitLabel)
    payload.append('unitWeightKg', form.value.unitWeightKg || '')
    payload.append('taxRate', form.value.taxRate)
    payload.append('speciesId', form.value.speciesId || '')
    payload.append('supplierId', form.value.supplierId || '')
    payload.append('isActive', form.value.isActive)
    if (photoFile.value) payload.append('photo', photoFile.value)
    else if (removePhoto.value) payload.append('removePhoto', 'true')

    if (isEdit.value) {
      await productsStore.updateProduct(productId.value, payload)
      toastStore.success('Producto actualizado correctamente.')
    } else {
      await productsStore.createProduct(payload)
      toastStore.success('Producto creado exitosamente.')
    }
    router.push({ name: 'staff-products' })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo guardar el producto.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-5xl">
    <RouterLink
      :to="{ name: 'staff-products' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a productos
    </RouterLink>

    <h1 class="text-2xl font-extrabold text-slate-900 mb-6">
      {{ isEdit ? 'Editar producto' : 'Nuevo producto' }}
    </h1>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>

    <form v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start" @submit.prevent="handleSubmit">
      <!-- Columna izquierda: secciones -->
      <div class="lg:col-span-8 flex flex-col gap-6">
        <!-- Informacion basica -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
          <div class="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
            <div class="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <AppIcon name="file-text" :size="18" />
            </div>
            <h2 class="text-lg font-bold text-slate-900">Información básica</h2>
          </div>

          <div class="flex flex-col sm:flex-row gap-6">
            <div class="flex flex-col items-center text-center flex-shrink-0">
              <div
                class="w-32 h-32 rounded-2xl border-2 border-dashed border-emerald-200 relative overflow-hidden flex items-center justify-center bg-emerald-50/50 cursor-pointer mb-2"
                @click="fileInput.click()"
              >
                <img v-if="photoPreview" :src="photoPreview" class="w-full h-full object-cover" alt="" />
                <img
                  v-else-if="existingPhotoUrl"
                  :src="`${api.defaults.baseURL}${existingPhotoUrl}`"
                  class="w-full h-full object-cover"
                  alt=""
                />
                <div v-else class="flex flex-col items-center gap-1 text-emerald-700">
                  <AppIcon name="camera" :size="24" />
                  <span class="text-[11px] font-semibold">Subir foto</span>
                </div>
                <input ref="fileInput" type="file" accept="image/jpeg,image/png" class="hidden" @change="onPhotoChange" />
              </div>
              <p class="text-[11px] text-slate-400">JPG o PNG, máx 5MB</p>
              <button
                v-if="photoPreview || existingPhotoUrl"
                type="button"
                class="text-[11px] font-semibold text-red-600 hover:underline mt-1"
                @click="clearPhoto"
              >
                Quitar foto
              </button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5 flex-1">
              <div class="sm:col-span-2">
                <label class="block text-sm font-medium text-slate-600 mb-2" for="name">Nombre del producto *</label>
                <input
                  id="name"
                  v-model="form.name"
                  type="text"
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-600 mb-2" for="sku">SKU / Código *</label>
                <div class="flex gap-2">
                  <input
                    id="sku"
                    v-model="form.sku"
                    type="text"
                    class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                    @input="onSkuInput"
                  />
                  <button
                    v-if="!isEdit"
                    type="button"
                    title="Sugerir código según la subcategoría elegida"
                    class="shrink-0 px-3 border border-slate-200 rounded-lg text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-40 disabled:pointer-events-none"
                    :disabled="!form.categoryId || suggestingSku"
                    @click="applySkuSuggestion"
                  >
                    <AppIcon name="refresh" :size="14" />
                  </button>
                </div>
                <p v-if="!isEdit" class="text-xs text-slate-400 mt-1.5">
                  Se sugiere solo al elegir la subcategoría — prefijo por categoría (ej. MED-002), editable.
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-600 mb-2" for="barcode">Código de barras</label>
                <input
                  id="barcode"
                  v-model="form.barcode"
                  type="text"
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                />
              </div>

              <div class="sm:col-span-2">
                <label class="block text-sm font-medium text-slate-600 mb-2" for="brand">Marca *</label>
                <input
                  id="brand"
                  v-model="form.brand"
                  type="text"
                  required
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                />
              </div>

              <div class="sm:col-span-2">
                <label class="block text-sm font-medium text-slate-600 mb-2" for="description">Descripción *</label>
                <textarea
                  id="description"
                  v-model="form.description"
                  rows="3"
                  required
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                ></textarea>
              </div>
            </div>
          </div>
        </div>

        <!-- Precios e impuestos -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
          <div class="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
            <div class="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <AppIcon name="cash" :size="18" />
            </div>
            <h2 class="text-lg font-bold text-slate-900">Precios e impuestos</h2>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5">
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="purchasePrice">
                Precio de compra (COP) *
              </label>
              <input
                id="purchasePrice"
                v-model="form.purchasePrice"
                type="number"
                step="0.01"
                min="0"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="sellingPrice">
                Precio de venta (COP) *
              </label>
              <input
                id="sellingPrice"
                v-model="form.sellingPrice"
                type="number"
                step="0.01"
                min="0"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="taxRate">IVA *</label>
              <select
                id="taxRate"
                v-model="form.taxRate"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              >
                <option v-for="opt in TAX_RATE_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
            </div>

            <div class="flex flex-col justify-end">
              <span class="block text-sm font-medium text-slate-600 mb-2">Margen bruto</span>
              <div class="border border-slate-100 bg-slate-50 rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-800">
                {{ formatCOP(margin.amount) }} ({{ margin.percent.toFixed(0) }}% margen)
              </div>
            </div>
          </div>

          <p class="text-xs text-slate-500 mt-5 pt-4 border-t border-slate-100">
            El precio de venta incluye el IVA. El precio de compra se usa solo para cálculos
            internos de margen.
          </p>
        </div>

        <!-- Inventario -->
        <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
          <div class="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
            <div class="w-9 h-9 rounded-xl bg-sky-50 text-sky-700 flex items-center justify-center">
              <AppIcon name="package" :size="18" />
            </div>
            <h2 class="text-lg font-bold text-slate-900">Inventario</h2>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5">
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="stock">Stock actual *</label>
              <input
                id="stock"
                v-model="form.stock"
                type="number"
                step="1"
                min="0"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="minStock">Stock mínimo *</label>
              <input
                id="minStock"
                v-model="form.minStock"
                type="number"
                step="1"
                min="0"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
              <p v-if="stockIsLow" class="text-xs text-amber-600 font-semibold mt-1.5 flex items-center gap-1">
                <AppIcon name="alert-triangle" :size="12" />
                Alerta automática: el stock caerá por debajo del mínimo.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="unitLabel">Unidad de medida *</label>
              <select
                id="unitLabel"
                v-model="form.unitLabel"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              >
                <option v-for="unit in UNIT_OPTIONS" :key="unit" :value="unit">{{ unit }}</option>
              </select>
              <p v-if="isPackageUnit" class="text-xs text-slate-400 mt-1.5">
                El stock ({{ form.stock || 0 }}) cuenta paquetes — ej. 3 significa "3 {{ form.unitLabel }}s". Si
                cada uno pesa un valor conocido, complétalo en "Peso por unidad" para ver el total en kg.
              </p>
              <p v-else class="text-xs text-amber-700 bg-amber-50 rounded-lg px-2.5 py-1.5 mt-1.5">
                Con "{{ form.unitLabel }}" el stock ({{ form.stock || 0 }}) ya es la cantidad total — no la
                cantidad de paquetes. Si en realidad vendes por paquetes con un peso conocido (ej. latas de
                5.5 oz), usa "Unidad" y completa "Peso por unidad" en vez de esto.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="unitWeightKg">
                Peso por unidad (kg) — opcional
              </label>
              <input
                id="unitWeightKg"
                v-model="form.unitWeightKg"
                type="number"
                step="0.001"
                min="0"
                placeholder="Ej. 40 si cada Bulto pesa 40kg"
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
              <p class="text-xs text-slate-400 mt-1.5">
                Si lo llenas, el sistema calcula el total en kg donde se muestre la cantidad.
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="topCategoryId">Categoría *</label>
              <select
                id="topCategoryId"
                v-model="form.topCategoryId"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                @change="onTopCategoryChange"
              >
                <option value="" disabled>Selecciona categoría</option>
                <option v-for="top in productsStore.topCategories()" :key="top.id" :value="top.id">
                  {{ top.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="categoryId">Subcategoría *</label>
              <select
                id="categoryId"
                v-model="form.categoryId"
                :disabled="!form.topCategoryId"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-50 disabled:text-slate-400"
                @change="onCategoryChange"
              >
                <option value="" disabled>Selecciona subcategoría</option>
                <option v-for="sub in subcategories" :key="sub.id" :value="sub.id">{{ sub.name }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2" for="speciesId">
                Especie *
              </label>
              <select
                id="speciesId"
                v-model="form.speciesId"
                :disabled="!form.topCategoryId"
                required
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-50 disabled:text-slate-400"
              >
                <option value="" disabled>Selecciona especie</option>
                <option v-for="s in speciesOptions" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
              <p class="text-xs text-slate-500 mt-1.5">Las opciones dependen de la categoría elegida arriba.</p>
            </div>

            <div class="sm:col-span-2">
              <label class="block text-sm font-medium text-slate-600 mb-2" for="supplierId">Proveedor</label>
              <select
                id="supplierId"
                v-model="form.supplierId"
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              >
                <option value="">Sin proveedor asignado</option>
                <option v-for="s in productsStore.suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>

            <div class="sm:col-span-2 border-t border-slate-100 pt-5">
              <label class="flex items-center gap-3 cursor-pointer w-fit">
                <input v-model="form.isActive" type="checkbox" class="sr-only" />
                <!-- La perilla se mueve con :style (transform inline), no con
                     clases translate-x-*/peer-checked: de Tailwind - se
                     probó primero con peer-checked:translate-x-5 (nunca
                     alcanza a un div anidado, solo a hermanos directos del
                     input), después con peer-checked:after:translate-x-5, y
                     después alternando la clase translate-x-0/translate-x-5
                     por :class - ninguna terminó moviendo la perilla de
                     verdad al cambiar dinámicamente (confirmado midiendo la
                     posición real en el navegador, no solo mirando el
                     nombre de la clase aplicada). Un :style con transform
                     directo no depende de que Tailwind compile ninguna
                     combinación - siempre funciona. -->
                <div
                  class="w-11 h-6 rounded-full relative flex-shrink-0 transition-colors duration-200"
                  :class="form.isActive ? 'bg-emerald-600' : 'bg-slate-200'"
                >
                  <div
                    class="absolute top-0.5 left-0.5 bg-white w-5 h-5 rounded-full transition-transform duration-200"
                    :style="{ transform: form.isActive ? 'translateX(1.25rem)' : 'translateX(0)' }"
                  ></div>
                </div>
                <span class="text-sm font-semibold text-slate-700">
                  {{ form.isActive ? 'Producto activo' : 'Producto inactivo' }}
                </span>
              </label>
              <p class="text-xs text-slate-500 mt-1.5">Visible en el catálogo para los clientes.</p>
            </div>
          </div>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

        <div class="flex flex-col-reverse md:flex-row md:justify-end gap-3">
          <RouterLink
            :to="{ name: 'staff-products' }"
            class="w-full md:w-auto px-6 py-2.5 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition flex items-center justify-center gap-2"
          >
            <AppIcon name="x" :size="14" />
            Cancelar
          </RouterLink>
          <PrimaryButton type="submit" :loading="submitting" class="w-full md:w-auto gap-2">
            <AppIcon name="check" :size="16" />
            {{ isEdit ? 'Guardar cambios' : 'Crear producto' }}
          </PrimaryButton>
        </div>
      </div>

      <!-- Columna derecha: resumen en vivo -->
      <div class="lg:col-span-4">
        <div class="bg-white rounded-2xl border border-slate-200 p-6 sticky top-24">
          <h3 class="text-sm font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100">
            Resumen del producto
          </h3>
          <dl class="space-y-3 text-sm">
            <div class="flex justify-between">
              <dt class="text-slate-500">Precio de compra</dt>
              <dd class="font-semibold text-slate-800">{{ formatCOP(form.purchasePrice) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-slate-500">Precio de venta</dt>
              <dd class="font-semibold text-emerald-700">{{ formatCOP(form.sellingPrice) }}</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-slate-500">IVA aplicado</dt>
              <dd class="font-semibold text-slate-800">{{ form.taxRate }}%</dd>
            </div>
            <div class="flex justify-between border-t border-slate-100 pt-3">
              <dt class="text-slate-500">Margen bruto</dt>
              <dd class="font-semibold text-slate-800 text-right">
                {{ formatCOP(margin.amount) }}<br />
                <span class="text-xs text-slate-400">{{ margin.percent.toFixed(0) }}% margen</span>
              </dd>
            </div>
            <div class="flex justify-between border-t border-slate-100 pt-3">
              <dt class="text-slate-500">Stock disponible</dt>
              <dd class="font-semibold" :class="stockIsLow ? 'text-amber-600' : 'text-slate-800'">
                {{ formatQuantity(form.stock || 0, form.unitLabel, form.unitWeightKg) }}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </form>
  </div>
</template>
