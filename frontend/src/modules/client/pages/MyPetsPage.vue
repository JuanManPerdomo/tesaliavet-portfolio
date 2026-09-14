<script setup>
import { onMounted } from 'vue'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import PetCard from '../components/PetCard.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import { usePetsStore } from '../../../stores/pets'

const petsStore = usePetsStore()

const BANNER_CLASSES = ['bg-amber-50', 'bg-emerald-50', 'bg-sky-50', 'bg-pink-50']

onMounted(() => {
  petsStore.fetchPets()
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-7xl mx-auto px-6 py-12 w-full">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-10">
        <div>
          <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Mis Mascotas</h1>
          <p class="text-sm text-slate-500">
            Tienes <strong class="text-emerald-700 font-semibold">{{ petsStore.pets.length }}</strong>
            {{ petsStore.pets.length === 1 ? 'mascota registrada' : 'mascotas registradas' }}
            actualmente.
          </p>
        </div>

        <PrimaryButton :to="'/mis-mascotas/nueva'" class="gap-2">
          <AppIcon name="plus" :size="18" />
          Agregar mascota
        </PrimaryButton>
      </div>

      <p v-if="petsStore.error" class="text-sm text-red-600 mb-6">{{ petsStore.error }}</p>

      <div v-if="petsStore.loading" class="text-sm text-slate-500">Cargando tus mascotas...</div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PetCard
          v-for="(pet, index) in petsStore.pets"
          :key="pet.id"
          :pet="pet"
          :banner-class="BANNER_CLASSES[index % BANNER_CLASSES.length]"
        />

        <RouterLink
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
    </main>

    <Footer />
  </div>
</template>
