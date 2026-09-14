<script setup>
import { ref, onMounted, watch } from 'vue'
import ProductCard from '../products/ProductCard.vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import api from '../../../../lib/api'

// "Farmacia Veterinaria" = las categorías que el admin marque desde
// /panel/categorias (checkbox "Mostrar en Farmacia Veterinaria") - antes
// era una lista fija de IDs escrita a mano. El catálogo general en
// /productos sí muestra todas las categorías, sin este filtro.
const pharmacyCategories = ref([])

const products = ref([])
const total = ref(0)
const loading = ref(false)
const search = ref('')
const selectedCategory = ref('')

function mapProduct(product) {
  return {
    id: product.id,
    name: product.name,
    category: product.category?.name ?? '',
    // product.image es una ruta relativa (/products/<id>/photo) servida por
    // el backend, no por Vite: hay que anteponer la baseURL de la API o el
    // navegador la busca contra el origen del frontend y nunca carga (mismo
    // problema ya resuelto en stores/products.js, decisión 19 de CLAUDE.md).
    image: product.image ? `${api.defaults.baseURL}${product.image}` : null,
    price: product.price,
    unitLabel: product.unitLabel,
    badge: product.stock <= 0 ? 'Agotado' : undefined,
  }
}

async function fetchPharmacyProducts() {
  const categoryIds = selectedCategory.value
    ? [Number(selectedCategory.value)]
    : pharmacyCategories.value.map((c) => c.id)

  // Sin categorias marcadas por el admin, no hay nada que mostrar - un
  // GET /products sin ningun category_id devolveria TODO el catalogo sin
  // filtrar, justo lo que esta seccion no debe hacer.
  if (!categoryIds.length) {
    products.value = []
    total.value = 0
    return
  }

  loading.value = true
  try {
    const params = new URLSearchParams()
    categoryIds.forEach((id) => params.append('category_id', id))
    if (search.value) params.append('search', search.value)
    params.append('per_page', 20)

    const { data } = await api.get('/products', { params })
    products.value = data.products.map(mapProduct)
    total.value = data.total
  } finally {
    loading.value = false
  }
}

let searchTimeout
watch(search, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(fetchPharmacyProducts, 400)
})
watch(selectedCategory, fetchPharmacyProducts)

onMounted(async () => {
  const { data } = await api.get('/catalog/pharmacy-categories')
  pharmacyCategories.value = data
  fetchPharmacyProducts()
})
</script>

<template>
  <section>
    <hr class="border-slate-200 my-6" />

    <div class="text-sm font-bold text-emerald-700 uppercase tracking-wide mb-6">
      Farmacia Veterinaria — Catálogo
    </div>

    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <p class="text-sm text-slate-500 font-medium">
        {{
          loading
            ? 'Cargando...'
            : `Mostrando ${total} producto${total === 1 ? '' : 's'} disponible${total === 1 ? '' : 's'}`
        }}
      </p>

      <div class="flex items-center gap-3 w-full sm:w-auto">
        <div
          class="flex items-center gap-2 bg-white border border-slate-200 rounded-full px-4 h-10 text-sm min-w-[240px]"
        >
          <AppIcon name="search" :size="16" class="text-slate-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Buscar por nombre…"
            class="bg-transparent border-none outline-none text-sm text-slate-700 placeholder-slate-400 w-full"
          />
        </div>

        <select
          v-model="selectedCategory"
          class="bg-white border border-slate-200 rounded-full px-4 h-10 text-sm font-medium text-slate-900 cursor-pointer"
        >
          <option value="">Todas las categorías</option>
          <option v-for="cat in pharmacyCategories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
    </div>

    <p v-if="!loading && !products.length" class="text-slate-500 text-sm">
      No hay productos de farmacia disponibles todavía.
    </p>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <ProductCard v-for="product in products" :key="product.id" v-bind="product" />
    </div>
  </section>
</template>
