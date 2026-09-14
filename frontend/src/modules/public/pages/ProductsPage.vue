<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

import ProductTabs from '../components/products/ProductTabs.vue'
import SearchInput from '../../../components/ui/SearchInput.vue'
import ProductSubcategories from '../components/products/ProductSubcategories.vue'
import ProductFilters from '../components/products/ProductFilters.vue'
import ProductCatalog from '../components/products/ProductCatalog.vue'
import { useProductsStore } from '../../../stores/products'

const route = useRoute()
const productsStore = useProductsStore()

// ?categoria=mascotas|ganaderia permite llegar con un tab preseleccionado
// (ej. desde la nueva seccion de categorias del Home) - sin el query param,
// arranca en Mascotas como siempre.
const TAB_BY_QUERY = { mascotas: 'Mascotas', ganaderia: 'Ganadería' }

onMounted(async () => {
  productsStore.fetchFacets()
  await productsStore.fetchCategories()
  const initialTab = TAB_BY_QUERY[route.query.categoria] || 'Mascotas'
  productsStore.resetFilters(productsStore.topCategoryIdByName(initialTab))
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <Navbar />

    <ProductTabs />

    <!-- Barra superior: un solo contenedor con el margen izquierdo, para que
         buscador y pills queden alineados con los tabs de arriba (antes cada
         uno traía su propio max-w-7xl/px-6 anidado, desalineaba todo). -->
    <section class="bg-white border-y border-slate-200">
      <div class="max-w-7xl mx-auto px-6 py-8 space-y-6">
        <div class="max-w-md">
          <SearchInput
            v-model="productsStore.filters.search"
            @search="productsStore.applyFilters()"
          />
        </div>

        <ProductSubcategories />
      </div>
    </section>

    <!-- Catálogo -->

    <section class="max-w-[1600px] mx-auto px-6 md:px-8 py-10">
      <div class="flex flex-col lg:flex-row gap-10">
        <ProductFilters />

        <ProductCatalog />
      </div>
    </section>

    <Footer />
  </div>
</template>
