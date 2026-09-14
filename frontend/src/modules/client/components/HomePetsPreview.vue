<script setup>
import { computed, onMounted } from 'vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PetCard from './PetCard.vue'
import { usePetsStore } from '../../../stores/pets'

const petsStore = usePetsStore()

// Mismo ciclo de bannerClass que ya usa MyPetsPage.vue - el Home solo
// muestra una vista previa (hasta 3), no reemplaza /mis-mascotas.
const BANNER_CLASSES = ['bg-amber-50', 'bg-emerald-50', 'bg-sky-50']
const MAX_PREVIEW = 3

onMounted(() => {
  petsStore.fetchPets()
})

const previewPets = computed(() => petsStore.pets.slice(0, MAX_PREVIEW))
const hasMore = computed(() => petsStore.pets.length > MAX_PREVIEW)
const showAddTile = computed(() => petsStore.pets.length < MAX_PREVIEW)
</script>

<template>
  <section v-if="!petsStore.loading" class="max-w-7xl mx-auto px-6 pt-10">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-extrabold text-slate-900">Mis mascotas</h2>

      <RouterLink
        v-if="hasMore"
        to="/mis-mascotas"
        class="text-sm font-semibold text-emerald-700 hover:underline"
      >
        Ver todas ({{ petsStore.pets.length }}) →
      </RouterLink>
    </div>

    <div
      v-if="!petsStore.pets.length"
      class="bg-white rounded-3xl border border-slate-100 p-10 text-center"
    >
      <div
        class="w-14 h-14 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center mx-auto mb-4"
      >
        <AppIcon name="paw" :size="26" />
      </div>
      <p class="font-semibold text-slate-700 mb-1">Aún no tienes mascotas registradas.</p>
      <p class="text-sm text-slate-500 mb-5">
        Registra tu primera mascota para llevar el control de su salud.
      </p>
      <RouterLink
        to="/mis-mascotas/nueva"
        class="inline-flex items-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition"
      >
        <AppIcon name="plus" :size="16" />
        Registrar mascota
      </RouterLink>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PetCard
        v-for="(pet, index) in previewPets"
        :key="pet.id"
        :pet="pet"
        :banner-class="BANNER_CLASSES[index % BANNER_CLASSES.length]"
      />

      <RouterLink
        v-if="showAddTile"
        to="/mis-mascotas/nueva"
        class="bg-white/50 border-2 border-dashed border-slate-200 rounded-2xl hover:border-emerald-700 hover:bg-emerald-50/40 transition-all flex flex-col items-center justify-center min-h-[320px] p-6 group"
      >
        <div
          class="w-14 h-14 rounded-full bg-slate-100 group-hover:bg-emerald-700 flex items-center justify-center mb-4 transition-colors"
        >
          <AppIcon
            name="plus"
            :size="26"
            class="text-slate-400 group-hover:text-white transition-colors"
          />
        </div>
        <h3 class="text-base font-semibold text-slate-800 mb-1 group-hover:text-emerald-700">
          Nueva mascota
        </h3>
        <p class="text-sm text-slate-500 text-center max-w-[220px]">
          Registra una nueva mascota para llevar el control de su salud.
        </p>
      </RouterLink>
    </div>
  </section>
</template>
