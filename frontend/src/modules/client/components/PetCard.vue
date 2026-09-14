<script setup>
import PetPhoto from './PetPhoto.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'

const props = defineProps({
  pet: { type: Object, required: true },
  bannerClass: { type: String, default: 'bg-amber-50' },
})

const VACCINE_BADGE = {
  al_dia: { label: 'Vacunas al día', class: 'bg-emerald-50 text-emerald-700', icon: 'check' },
  pendiente: { label: 'Vacuna pendiente', class: 'bg-red-50 text-red-600', icon: 'alert-triangle' },
  sin_registro: null,
}

function formatDate(isoDate) {
  if (!isoDate) return '—'
  return new Date(isoDate + 'T00:00:00').toLocaleDateString('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const badge = VACCINE_BADGE[props.pet.vaccineStatus]
</script>

<template>
  <article
    class="bg-white rounded-2xl border border-slate-200 flex flex-col overflow-hidden shadow-sm hover:shadow-md transition-shadow"
  >
    <div :class="bannerClass" class="h-24 w-full relative flex items-end justify-center">
      <div
        v-if="badge"
        class="absolute top-3 right-3 font-bold text-[10px] uppercase tracking-wider px-2 py-1 rounded-full flex items-center gap-1"
        :class="badge.class"
      >
        <AppIcon :name="badge.icon" :size="11" />
        {{ badge.label }}
      </div>

      <div
        class="w-20 h-20 rounded-full overflow-hidden border-4 border-white shadow-sm translate-y-10 bg-white"
      >
        <PetPhoto :photo-url="pet.photoUrl" :icon-size="28" />
      </div>
    </div>

    <div class="pt-12 pb-6 px-6 flex-grow flex flex-col items-center text-center">
      <h2 class="text-lg font-bold text-slate-900 mb-1">{{ pet.name }}</h2>
      <p class="text-sm text-slate-500 mb-4">
        {{ pet.breed?.name || pet.species?.name || 'Sin raza registrada' }} • {{ pet.gender }}
      </p>

      <div class="w-full bg-slate-50 rounded-lg p-3 flex justify-between items-center mb-5">
        <div class="flex flex-col items-start">
          <span class="text-[10px] font-semibold text-slate-400 uppercase">Nacimiento</span>
          <span class="text-sm font-semibold text-slate-700">{{ formatDate(pet.birthDate) }}</span>
        </div>
        <div class="h-8 w-px bg-slate-200"></div>
        <div class="flex flex-col items-end">
          <span class="text-[10px] font-semibold text-slate-400 uppercase">Edad</span>
          <span class="text-sm font-semibold text-slate-700">
            {{ pet.age !== null ? `${pet.age} años` : '—' }}
          </span>
        </div>
      </div>

      <div class="mt-auto w-full flex gap-3">
        <RouterLink
          :to="{ name: 'pet-detail', params: { id: pet.id } }"
          class="flex-grow bg-emerald-700 hover:bg-emerald-800 text-white text-sm font-semibold py-2 rounded-lg flex items-center justify-center gap-1.5 transition"
        >
          <AppIcon name="clock" :size="16" />
          Ver Historial
        </RouterLink>
        <RouterLink
          :to="{ name: 'pet-edit', params: { id: pet.id } }"
          aria-label="Editar mascota"
          class="w-11 h-10 border border-emerald-700 text-emerald-700 rounded-lg flex items-center justify-center hover:bg-emerald-50 transition"
        >
          <AppIcon name="edit" :size="16" />
        </RouterLink>
      </div>
    </div>
  </article>
</template>
