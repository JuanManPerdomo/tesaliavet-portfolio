<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useProductsStore } from '../../../../stores/products'

const productsStore = useProductsStore()
</script>

<template>
  <section v-if="productsStore.pagination.pages > 1" class="py-10">
    <div class="max-w-7xl mx-auto flex flex-col items-center gap-3">
      <div class="flex justify-center items-center gap-2">
        <button
          type="button"
          class="w-10 h-10 rounded-xl border border-slate-200 flex items-center justify-center text-slate-500 hover:border-emerald-700 hover:text-emerald-700 transition disabled:opacity-40 disabled:pointer-events-none"
          :disabled="productsStore.pagination.page <= 1"
          @click="productsStore.setPage(productsStore.pagination.page - 1)"
        >
          <AppIcon name="chevron-left" :size="18" />
        </button>

        <button
          v-for="page in productsStore.pagination.pages"
          :key="page"
          type="button"
          :class="[
            'w-10 h-10 rounded-xl border font-medium transition',
            page === productsStore.pagination.page
              ? 'bg-emerald-700 text-white border-emerald-700 shadow-sm'
              : 'border-slate-200 text-slate-600 hover:border-emerald-700 hover:text-emerald-700',
          ]"
          @click="productsStore.setPage(page)"
        >
          {{ page }}
        </button>

        <button
          type="button"
          class="w-10 h-10 rounded-xl border border-slate-200 flex items-center justify-center text-slate-500 hover:border-emerald-700 hover:text-emerald-700 transition disabled:opacity-40 disabled:pointer-events-none"
          :disabled="productsStore.pagination.page >= productsStore.pagination.pages"
          @click="productsStore.setPage(productsStore.pagination.page + 1)"
        >
          <AppIcon name="chevron-right" :size="18" />
        </button>
      </div>

      <p class="text-xs text-slate-400">
        Página {{ productsStore.pagination.page }} de {{ productsStore.pagination.pages }}
      </p>
    </div>
  </section>
</template>
