<script setup>
import { computed } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useProductsStore } from '../../../../stores/products'

const productsStore = useProductsStore()

const mascotasId = computed(() => productsStore.topCategoryIdByName('Mascotas'))
const ganaderiaId = computed(() => productsStore.topCategoryIdByName('Ganadería'))

function selectTab(name) {
  productsStore.resetFilters(productsStore.topCategoryIdByName(name))
}
</script>

<template>
  <section class="border-b border-slate-200 bg-white">
    <div class="max-w-7xl mx-auto px-6">
      <div class="flex gap-12">
        <button
          :class="[
            'inline-flex items-center gap-2 py-5 font-semibold border-b-2 transition',
            productsStore.filters.topCategoryId === mascotasId
              ? 'border-emerald-700 text-emerald-700'
              : 'border-transparent text-slate-500 hover:text-emerald-700',
          ]"
          @click="selectTab('Mascotas')"
        >
          <AppIcon name="paw" :size="18" /> Mascotas
        </button>

        <button
          :class="[
            'inline-flex items-center gap-2 py-5 font-semibold border-b-2 transition',
            productsStore.filters.topCategoryId === ganaderiaId
              ? 'border-emerald-700 text-emerald-700'
              : 'border-transparent text-slate-500 hover:text-emerald-700',
          ]"
          @click="selectTab('Ganadería')"
        >
          <AppIcon name="leaf" :size="18" /> Ganadería
        </button>
      </div>
    </div>
  </section>
</template>
