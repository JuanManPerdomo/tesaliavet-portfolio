<script setup>
import { computed } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useProductsStore } from '../../../../stores/products'

const productsStore = useProductsStore()

const categoryName = computed(() => {
  const match = productsStore.facets.categories.find(
    (c) => c.id === productsStore.filters.categoryId
  )
  return match ? match.name : 'Todos los productos'
})
</script>

<template>
  <section class="mb-8">
    <div class="flex flex-wrap justify-between items-end gap-4">
      <div>
        <span
          class="inline-flex items-center gap-2 bg-emerald-100 text-emerald-700 px-3.5 py-1.5 rounded-full text-xs font-semibold mb-3"
        >
          <AppIcon name="shopping-bag" :size="14" />
          Catálogo
        </span>

        <h1 class="text-4xl font-extrabold text-slate-900 tracking-tight">
          {{ categoryName }}
        </h1>

        <p class="mt-2 text-emerald-700 font-medium">
          {{ productsStore.pagination.total }} producto{{
            productsStore.pagination.total === 1 ? '' : 's'
          }}
          encontrado{{ productsStore.pagination.total === 1 ? '' : 's' }}
        </p>
      </div>

      <div class="flex items-center gap-3">
        <span class="text-sm text-slate-500 whitespace-nowrap">Ordenar por</span>

        <div class="relative">
          <select
            v-model="productsStore.filters.sort"
            class="appearance-none border border-slate-200 rounded-xl pl-4 pr-10 py-2.5 bg-white text-sm font-medium text-slate-700 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition cursor-pointer"
            @change="productsStore.applyFilters()"
          >
            <option value="">Más relevantes</option>
            <option value="price_asc">Precio menor</option>
            <option value="price_desc">Precio mayor</option>
            <option value="newest">Más recientes</option>
          </select>

          <AppIcon
            name="chevron-down"
            :size="14"
            class="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400"
          />
        </div>
      </div>
    </div>
  </section>
</template>
