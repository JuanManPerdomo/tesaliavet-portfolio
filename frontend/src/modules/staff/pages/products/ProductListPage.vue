<script setup>
import { ref, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import ProductViewModal from './ProductViewModal.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import { useProductsStore } from '../../../../stores/products'
import { useToastStore } from '../../../../stores/toast'
import { formatCOP, formatQuantity } from '../../../../lib/pricing'
import api from '../../../../lib/api'

// Las fotos de producto son publicas (sin @jwt_required, a diferencia de
// las de mascota) - basta anteponer el origen del backend, mismo patron
// que ProductViewModal.vue/ProductFormPage.vue (decision 19).
function productPhotoUrl(product) {
  return product.image ? `${api.defaults.baseURL}${product.image}` : null
}

const STATUS_OPTIONS = [
  { value: 'active', label: 'Activos' },
  { value: 'inactive', label: 'Inactivos' },
  { value: 'all', label: 'Todos' },
]

const productsStore = useProductsStore()
const toastStore = useToastStore()

const search = ref('')
const categoryFilter = ref('')
const speciesFilter = ref('')
const statusFilter = ref('active')
const perPage = ref(10)

const viewingProduct = ref(null)

const deactivatingId = ref(null)
const showDeactivateConfirm = ref(false)
const deactivating = ref(false)

const deletingId = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

const activatingId = ref(null)

function load(page = 1) {
  productsStore.fetchAdminProducts({
    search: search.value,
    categoryId: categoryFilter.value || undefined,
    speciesId: speciesFilter.value || undefined,
    status: statusFilter.value,
    page,
    perPage: perPage.value,
  })
}

onMounted(async () => {
  await Promise.all([productsStore.fetchCategories(), productsStore.fetchSpecies()])
  load()
})

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

function askDeactivate(id) {
  deactivatingId.value = id
  showDeactivateConfirm.value = true
}

async function confirmDeactivate() {
  deactivating.value = true
  try {
    await productsStore.deactivateProduct(deactivatingId.value)
    toastStore.success('Producto desactivado.')
    showDeactivateConfirm.value = false
    load(productsStore.adminPagination.page)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo desactivar el producto.')
  } finally {
    deactivating.value = false
  }
}

async function handleActivate(id) {
  activatingId.value = id
  try {
    await productsStore.reactivateProduct(id)
    toastStore.success('Producto activado.')
    load(productsStore.adminPagination.page)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo activar el producto.')
  } finally {
    activatingId.value = null
  }
}

function askDelete(id) {
  deletingId.value = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await productsStore.deleteProduct(deletingId.value)
    toastStore.success('Producto eliminado permanentemente.')
    showDeleteConfirm.value = false
    load(1)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar el producto.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900">Productos</h1>
        <p class="text-sm text-slate-500 mt-1">Catálogo de productos de la veterinaria.</p>
      </div>
      <PrimaryButton :to="{ name: 'staff-product-new' }" class="gap-2">
        <AppIcon name="plus" :size="16" />
        Nuevo producto
      </PrimaryButton>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nombre o SKU..."
        class="flex-1 min-w-[220px] border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @keyup.enter="handleSearch"
      />
      <select
        v-model="categoryFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleSearch"
      >
        <option value="">Todas las categorías</option>
        <optgroup v-for="top in productsStore.topCategories()" :key="top.id" :label="top.name">
          <option v-for="sub in productsStore.subcategoriesOf(top.id)" :key="sub.id" :value="sub.id">
            {{ sub.name }}
          </option>
        </optgroup>
      </select>
      <select
        v-model="speciesFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleSearch"
      >
        <option value="">Todas las especies</option>
        <optgroup v-for="top in productsStore.topCategories()" :key="top.id" :label="top.name">
          <option v-for="s in productsStore.speciesForCategory(top.id)" :key="s.id" :value="s.id">
            {{ s.name }}
          </option>
        </optgroup>
      </select>
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
      <div v-if="productsStore.adminLoading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="productsStore.adminError" class="p-8 text-sm text-red-600">
        {{ productsStore.adminError }}
      </div>
      <div v-else-if="!productsStore.adminProducts.length" class="p-8 text-sm text-slate-500 text-center">
        No hay productos con estos filtros.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="product in productsStore.adminProducts" :key="product.id" class="p-4 flex gap-3">
          <div class="w-14 h-14 rounded-lg overflow-hidden bg-emerald-50 flex items-center justify-center shrink-0">
            <img
              v-if="productPhotoUrl(product)"
              :src="productPhotoUrl(product)"
              class="w-full h-full object-cover"
              alt=""
            />
            <AppIcon v-else name="package" :size="20" class="text-emerald-600" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="font-semibold text-slate-800 truncate">{{ product.name }}</p>
                <p class="text-xs text-slate-400">{{ product.sku }}</p>
              </div>
              <span
                class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold"
                :class="product.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ product.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-1">
              {{ product.category?.name || '—' }} · {{ product.species?.name || 'Todas' }}
            </p>
            <div class="flex items-center justify-between mt-2">
              <div class="text-sm">
                <span class="text-emerald-700 font-semibold">{{ formatCOP(product.price) }}</span>
                <span class="text-slate-400 text-xs"> / {{ formatCOP(product.purchasePrice) }} compra</span>
              </div>
              <span
                class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                :class="product.stock <= product.minStock ? 'bg-amber-50 text-amber-700' : 'text-slate-600'"
              >
                {{ formatQuantity(product.stock, product.unitLabel, product.unitWeightKg) }}
              </span>
            </div>

            <div class="flex gap-2 mt-3">
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                title="Ver resumen"
                @click="viewingProduct = product"
              >
                <AppIcon name="eye" :size="14" />
              </button>

              <template v-if="product.isActive">
                <RouterLink
                  :to="{ name: 'staff-product-edit', params: { id: product.id } }"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Editar"
                >
                  <AppIcon name="edit" :size="14" />
                </RouterLink>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                  title="Desactivar"
                  @click="askDeactivate(product.id)"
                >
                  <AppIcon name="archive" :size="14" />
                </button>
              </template>

              <template v-else>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                  title="Activar"
                  :disabled="activatingId === product.id"
                  @click="handleActivate(product.id)"
                >
                  <AppIcon name="refresh" :size="14" />
                </button>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                  title="Eliminar permanentemente"
                  @click="askDelete(product.id)"
                >
                  <AppIcon name="x" :size="14" />
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <table v-if="productsStore.adminProducts.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Foto</th>
            <th class="px-5 py-3">SKU</th>
            <th class="px-5 py-3">Nombre</th>
            <th class="px-5 py-3">Categoría</th>
            <th class="px-5 py-3">Especie</th>
            <th class="px-5 py-3 text-right">P. compra</th>
            <th class="px-5 py-3 text-right">P. venta</th>
            <th class="px-5 py-3">Estado</th>
            <th class="px-5 py-3 text-right">Stock</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="product in productsStore.adminProducts"
            :key="product.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3">
              <div class="w-10 h-10 rounded-lg overflow-hidden bg-emerald-50 flex items-center justify-center">
                <img
                  v-if="productPhotoUrl(product)"
                  :src="productPhotoUrl(product)"
                  class="w-full h-full object-cover"
                  alt=""
                />
                <AppIcon v-else name="package" :size="16" class="text-emerald-600" />
              </div>
            </td>
            <td class="px-5 py-3 text-slate-500">{{ product.sku }}</td>
            <td class="px-5 py-3 font-semibold text-slate-800">{{ product.name }}</td>
            <td class="px-5 py-3 text-slate-500">{{ product.category?.name || '—' }}</td>
            <td class="px-5 py-3 text-slate-500">{{ product.species?.name || 'Todas' }}</td>
            <td class="px-5 py-3 text-right text-slate-600">{{ formatCOP(product.purchasePrice) }}</td>
            <td class="px-5 py-3 text-right text-emerald-700 font-semibold">{{ formatCOP(product.price) }}</td>
            <td class="px-5 py-3">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-bold"
                :class="product.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ product.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-bold"
                :class="product.stock <= product.minStock ? 'bg-amber-50 text-amber-700' : 'text-slate-600'"
              >
                {{ formatQuantity(product.stock, product.unitLabel, product.unitWeightKg) }}
              </span>
            </td>
            <td class="px-5 py-3">
              <div class="flex justify-end gap-2">
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Ver resumen"
                  @click="viewingProduct = product"
                >
                  <AppIcon name="eye" :size="14" />
                </button>

                <template v-if="product.isActive">
                  <RouterLink
                    :to="{ name: 'staff-product-edit', params: { id: product.id } }"
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                    title="Editar"
                  >
                    <AppIcon name="edit" :size="14" />
                  </RouterLink>
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                    title="Desactivar"
                    @click="askDeactivate(product.id)"
                  >
                    <AppIcon name="archive" :size="14" />
                  </button>
                </template>

                <template v-else>
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                    title="Activar"
                    :disabled="activatingId === product.id"
                    @click="handleActivate(product.id)"
                  >
                    <AppIcon name="refresh" :size="14" />
                  </button>
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                    title="Eliminar permanentemente"
                    @click="askDelete(product.id)"
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
      :pagination="productsStore.adminPagination"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />

    <ProductViewModal
      :open="!!viewingProduct"
      :product="viewingProduct"
      @close="viewingProduct = null"
    />

    <ConfirmDialog
      :open="showDeactivateConfirm"
      title="Desactivar producto"
      message="El producto dejará de mostrarse en el catálogo. Podrás reactivarlo cuando quieras."
      confirm-label="Sí, desactivar"
      :loading="deactivating"
      @cancel="showDeactivateConfirm = false"
      @confirm="confirmDeactivate"
    />

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar producto permanentemente"
      message="Esta acción no se puede deshacer: el producto se borrará por completo de la base de datos, no solo del catálogo."
      confirm-label="Sí, eliminar para siempre"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
