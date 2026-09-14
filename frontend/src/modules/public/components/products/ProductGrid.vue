<script setup>
import ProductCard from './ProductCard.vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useProductsStore } from '../../../../stores/products'

const productsStore = useProductsStore()
</script>

<template>
  <!-- Loading: skeleton -->
  <div v-if="productsStore.loading" class="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
    <div
      v-for="n in 8"
      :key="n"
      class="h-full flex flex-col bg-white border border-slate-100 rounded-3xl overflow-hidden animate-pulse"
    >
      <div class="w-full h-64 bg-slate-100"></div>
      <div class="p-5 flex-1 flex flex-col gap-3">
        <div class="h-3 w-1/3 bg-slate-100 rounded"></div>
        <div class="h-5 w-3/4 bg-slate-100 rounded"></div>
        <div class="mt-auto flex justify-between items-center pt-5">
          <div class="h-6 w-16 bg-slate-100 rounded"></div>
          <div class="h-9 w-20 bg-slate-100 rounded-2xl"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Error -->
  <div
    v-else-if="productsStore.error"
    class="flex flex-col items-center text-center gap-3 bg-white border border-red-100 rounded-2xl py-16 px-6"
  >
    <div class="w-14 h-14 rounded-full bg-red-50 text-red-600 flex items-center justify-center">
      <AppIcon name="alert-triangle" :size="26" />
    </div>
    <p class="text-red-600 font-medium">{{ productsStore.error }}</p>
  </div>

  <!-- Empty -->
  <div
    v-else-if="!productsStore.products.length"
    class="flex flex-col items-center text-center gap-3 bg-white border border-slate-100 rounded-2xl py-16 px-6"
  >
    <div class="w-14 h-14 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center">
      <AppIcon name="search" :size="26" />
    </div>
    <p class="text-slate-700 font-semibold">No encontramos productos con esos filtros</p>
    <p class="text-slate-500 text-sm max-w-sm">
      Prueba con otra combinación de especie, marca o rango de precio.
    </p>
    <button
      class="mt-2 inline-flex items-center gap-2 text-emerald-700 font-semibold hover:gap-3 transition-all"
      @click="productsStore.resetFilters()"
    >
      <AppIcon name="refresh" :size="16" />
      Limpiar filtros
    </button>
  </div>

  <!-- Results -->
  <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
    <div
      v-for="(product, index) in productsStore.products"
      :key="product.id"
      v-reveal="{ delay: (index % 4) * 100 }"
      class="h-full"
    >
      <ProductCard v-bind="product" />
    </div>
  </div>
</template>
