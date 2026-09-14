<script setup>
import { computed } from 'vue'
import { useProductsStore } from '../../../../stores/products'

const productsStore = useProductsStore()

function selectCategory(categoryId) {
  productsStore.filters.categoryId = categoryId
  productsStore.applyFilters()
}

// Solo subcategorias del tab activo (Mascotas/Ganaderia) - un producto de
// Ganaderia nunca deberia aparecer como opcion mientras se navega Mascotas.
const scopedCategories = computed(() => {
  const scopeIds = productsStore.filters.categoryIds
  if (!scopeIds?.length) return productsStore.facets.categories
  return productsStore.facets.categories.filter((c) => scopeIds.includes(c.id))
})
</script>

<template>
  <div class="flex flex-wrap gap-3">
    <button
      :class="[
        'px-6 py-3 rounded-full text-sm font-medium transition',
        !productsStore.filters.categoryId
          ? 'bg-emerald-700 text-white'
          : 'bg-slate-100 hover:bg-slate-200 text-slate-700',
      ]"
      @click="selectCategory(null)"
    >
      Todos
    </button>

    <button
      v-for="category in scopedCategories"
      :key="category.id"
      :class="[
        'px-6 py-3 rounded-full text-sm font-medium transition',
        productsStore.filters.categoryId === category.id
          ? 'bg-emerald-700 text-white'
          : 'bg-slate-100 hover:bg-slate-200 text-slate-700',
      ]"
      @click="selectCategory(category.id)"
    >
      {{ category.name }} ({{ category.count }})
    </button>
  </div>
</template>
