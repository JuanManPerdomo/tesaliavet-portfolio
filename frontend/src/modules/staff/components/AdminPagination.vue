<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'

defineProps({
  pagination: { type: Object, required: true }, // { total, page, pages, perPage }
  itemLabel: { type: String, default: 'productos' },
})

const emit = defineEmits(['page-change', 'page-size-change'])

const PAGE_SIZES = [5, 10, 25, 50]
</script>

<template>
  <div v-if="pagination.total > 0" class="flex flex-col sm:flex-row items-center justify-between gap-4 mt-4 text-sm">
    <div class="flex items-center gap-2 text-slate-500">
      <span>
        Mostrando
        {{ Math.min((pagination.page - 1) * pagination.perPage + 1, pagination.total) }}–{{
          Math.min(pagination.page * pagination.perPage, pagination.total)
        }}
        de {{ pagination.total }} {{ itemLabel }}
      </span>
      <select
        :value="pagination.perPage"
        class="border border-slate-200 rounded-lg px-2 py-1 text-xs text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="emit('page-size-change', Number($event.target.value))"
      >
        <option v-for="size in PAGE_SIZES" :key="size" :value="size">{{ size }} por página</option>
      </select>
    </div>

    <div v-if="pagination.pages > 1" class="flex items-center gap-1">
      <button
        type="button"
        class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:border-emerald-700 hover:text-emerald-700 disabled:opacity-40 disabled:pointer-events-none"
        :disabled="pagination.page <= 1"
        @click="emit('page-change', pagination.page - 1)"
      >
        <AppIcon name="chevron-left" :size="14" />
      </button>
      <button
        v-for="page in pagination.pages"
        :key="page"
        type="button"
        class="w-8 h-8 rounded-lg border text-xs font-semibold transition"
        :class="
          page === pagination.page
            ? 'bg-emerald-700 text-white border-emerald-700'
            : 'border-slate-200 text-slate-600 hover:border-emerald-700 hover:text-emerald-700'
        "
        @click="emit('page-change', page)"
      >
        {{ page }}
      </button>
      <button
        type="button"
        class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:border-emerald-700 hover:text-emerald-700 disabled:opacity-40 disabled:pointer-events-none"
        :disabled="pagination.page >= pagination.pages"
        @click="emit('page-change', pagination.page + 1)"
      >
        <AppIcon name="chevron-right" :size="14" />
      </button>
    </div>
  </div>
</template>
