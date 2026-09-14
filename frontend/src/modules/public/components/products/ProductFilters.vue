<script setup>
import { ref } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useProductsStore } from '../../../../stores/products'

const productsStore = useProductsStore()

const openSections = ref({ species: true, brand: true, price: true })

function toggleSection(key) {
  openSections.value[key] = !openSections.value[key]
}

function toggleSpecies(speciesId) {
  const ids = productsStore.filters.speciesIds
  const index = ids.indexOf(speciesId)
  if (index === -1) {
    ids.push(speciesId)
  } else {
    ids.splice(index, 1)
  }
}

function toggleBrand(brand) {
  const brands = productsStore.filters.brands
  const index = brands.indexOf(brand)
  if (index === -1) {
    brands.push(brand)
  } else {
    brands.splice(index, 1)
  }
}
</script>

<template>
  <aside class="w-72 shrink-0">
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sticky top-24">
      <div class="flex items-center gap-2 mb-1">
        <AppIcon name="tag" :size="18" class="text-emerald-700" />
        <h2 class="font-bold text-lg text-slate-900">Filtros</h2>
      </div>
      <p class="text-xs text-slate-400 mb-2">Refina tu búsqueda</p>

      <!-- Especie -->
      <div class="border-t border-slate-100 pt-5 pb-1">
        <button
          type="button"
          class="w-full flex justify-between items-center mb-4 text-left"
          @click="toggleSection('species')"
        >
          <h3 class="font-bold text-slate-900">Especie / Mascota</h3>
          <AppIcon
            name="chevron-down"
            :size="16"
            class="text-slate-400 transition-transform"
            :class="{ '-rotate-180': openSections.species }"
          />
        </button>

        <div v-show="openSections.species">
          <p v-if="!productsStore.facets.species.length" class="text-sm text-slate-400">
            Sin datos todavía
          </p>

          <label
            v-for="item in productsStore.facets.species"
            :key="item.id"
            class="flex justify-between items-center py-1.5 cursor-pointer group"
          >
            <span class="flex items-center gap-3">
              <span class="relative flex-shrink-0">
                <input
                  type="checkbox"
                  class="peer sr-only"
                  :checked="productsStore.filters.speciesIds.includes(item.id)"
                  @change="toggleSpecies(item.id)"
                />
                <span
                  class="w-[18px] h-[18px] rounded flex items-center justify-center border-2 border-slate-300 peer-checked:bg-emerald-700 peer-checked:border-emerald-700 transition-colors"
                >
                  <AppIcon
                    v-if="productsStore.filters.speciesIds.includes(item.id)"
                    name="check"
                    :size="12"
                    class="text-white"
                  />
                </span>
              </span>

              <span class="text-sm text-slate-700 group-hover:text-emerald-700 transition">
                {{ item.name }}
              </span>
            </span>

            <span class="bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full text-[11px] font-semibold">
              {{ item.count }}
            </span>
          </label>
        </div>
      </div>

      <!-- Marca -->
      <div class="border-t border-slate-100 pt-5 pb-1">
        <button
          type="button"
          class="w-full flex justify-between items-center mb-4 text-left"
          @click="toggleSection('brand')"
        >
          <h3 class="font-bold text-slate-900">Marca</h3>
          <AppIcon
            name="chevron-down"
            :size="16"
            class="text-slate-400 transition-transform"
            :class="{ '-rotate-180': openSections.brand }"
          />
        </button>

        <div v-show="openSections.brand">
          <p v-if="!productsStore.facets.brands.length" class="text-sm text-slate-400">
            Sin datos todavía
          </p>

          <label
            v-for="item in productsStore.facets.brands"
            :key="item.name"
            class="flex justify-between items-center py-1.5 cursor-pointer group"
          >
            <span class="flex items-center gap-3">
              <span class="relative flex-shrink-0">
                <input
                  type="checkbox"
                  class="peer sr-only"
                  :checked="productsStore.filters.brands.includes(item.name)"
                  @change="toggleBrand(item.name)"
                />
                <span
                  class="w-[18px] h-[18px] rounded flex items-center justify-center border-2 border-slate-300 peer-checked:bg-emerald-700 peer-checked:border-emerald-700 transition-colors"
                >
                  <AppIcon
                    v-if="productsStore.filters.brands.includes(item.name)"
                    name="check"
                    :size="12"
                    class="text-white"
                  />
                </span>
              </span>

              <span class="text-sm text-slate-700 group-hover:text-emerald-700 transition">
                {{ item.name }}
              </span>
            </span>

            <span class="bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full text-[11px] font-semibold">
              {{ item.count }}
            </span>
          </label>
        </div>
      </div>

      <!-- Precio -->
      <div class="border-t border-slate-100 pt-5">
        <button
          type="button"
          class="w-full flex justify-between items-center mb-4 text-left"
          @click="toggleSection('price')"
        >
          <h3 class="font-bold text-slate-900">Rango de precio</h3>
          <AppIcon
            name="chevron-down"
            :size="16"
            class="text-slate-400 transition-transform"
            :class="{ '-rotate-180': openSections.price }"
          />
        </button>

        <div v-show="openSections.price">
          <div class="grid grid-cols-2 gap-3 mb-4">
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
              <input
                v-model="productsStore.filters.minPrice"
                type="number"
                :placeholder="`${productsStore.facets.price_range.min}`"
                class="w-full border border-slate-200 rounded-lg pl-6 pr-2 py-2.5 text-sm outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition"
              />
            </div>

            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
              <input
                v-model="productsStore.filters.maxPrice"
                type="number"
                :placeholder="`${productsStore.facets.price_range.max}`"
                class="w-full border border-slate-200 rounded-lg pl-6 pr-2 py-2.5 text-sm outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition"
              />
            </div>
          </div>

          <button
            class="w-full flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl py-3 text-sm font-semibold shadow-md hover:shadow-lg transition"
            @click="productsStore.applyFilters()"
          >
            <AppIcon name="search" :size="16" />
            Aplicar filtros
          </button>

          <button
            class="mt-3 w-full flex items-center justify-center gap-1.5 text-sm text-slate-500 hover:text-emerald-700 transition"
            @click="productsStore.resetFilters()"
          >
            <AppIcon name="refresh" :size="14" />
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>
