<script setup>
import { ref, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import PetPhoto from '../../../client/components/PetPhoto.vue'
import { useStaffPetsStore } from '../../../../stores/staffPets'
import { useAuthStore } from '../../../../stores/auth'
import { useToastStore } from '../../../../stores/toast'

const VACCINE_BADGE = {
  al_dia: { label: 'Al día', class: 'bg-emerald-50 text-emerald-700' },
  pendiente: { label: 'Pendiente', class: 'bg-red-50 text-red-600' },
  sin_registro: { label: 'Sin registro', class: 'bg-slate-100 text-slate-500' },
}

const petsStore = useStaffPetsStore()
const authStore = useAuthStore()
const toastStore = useToastStore()
const search = ref('')

function load() {
  petsStore.fetchPets(search.value || undefined)
}

onMounted(load)

const petToDelete = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

function askDelete(pet) {
  petToDelete.value = pet
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await petsStore.deletePet(petToDelete.value.id)
    toastStore.success('Mascota eliminada permanentemente.')
    showDeleteConfirm.value = false
    load()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar la mascota.')
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-extrabold text-slate-900">Mascotas registradas</h1>
      <p class="text-sm text-slate-500 mt-1">Mascotas de todos los clientes de la clínica.</p>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nombre de mascota o dueño..."
        class="flex-1 min-w-[220px] border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @keyup.enter="load"
      />
      <button
        class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
        @click="load"
      >
        Buscar
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="petsStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="petsStore.error" class="p-8 text-sm text-red-600">{{ petsStore.error }}</div>
      <div v-else-if="!petsStore.pets.length" class="p-8 text-sm text-slate-500 text-center">
        No hay mascotas con estos filtros.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="pet in petsStore.pets" :key="pet.id" class="p-4 flex gap-3">
          <div class="w-12 h-12 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
            <PetPhoto :photo-url="pet.photoUrl" :icon-size="18" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="font-semibold text-slate-800 truncate">{{ pet.name }}</p>
                <p class="text-xs text-slate-400">{{ pet.breed?.name || pet.species?.name || 'Especie sin definir' }}</p>
              </div>
              <span class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold" :class="VACCINE_BADGE[pet.vaccineStatus].class">
                {{ VACCINE_BADGE[pet.vaccineStatus].label }}
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-1">
              {{ pet.owner?.name || '—' }} · {{ pet.age !== null ? `${pet.age} años` : 'Edad sin definir' }}
            </p>

            <div class="flex gap-2 mt-3">
              <RouterLink
                :to="{ name: 'staff-pet-detail', params: { id: pet.id } }"
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                title="Ver ficha"
              >
                <AppIcon name="eye" :size="14" />
              </RouterLink>
              <RouterLink
                :to="{ name: 'staff-pet-edit', params: { id: pet.id } }"
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                title="Editar"
              >
                <AppIcon name="edit" :size="14" />
              </RouterLink>
              <button
                v-if="authStore.hasRole('admin')"
                type="button"
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                title="Eliminar"
                @click="askDelete(pet)"
              >
                <AppIcon name="x" :size="14" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <table v-if="petsStore.pets.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Mascota</th>
            <th class="px-5 py-3">Dueño</th>
            <th class="px-5 py-3">Edad</th>
            <th class="px-5 py-3">Vacunas</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pet in petsStore.pets"
            :key="pet.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
                  <PetPhoto :photo-url="pet.photoUrl" :icon-size="18" />
                </div>
                <div>
                  <p class="font-semibold text-slate-800">{{ pet.name }}</p>
                  <p class="text-xs text-slate-400">
                    {{ pet.breed?.name || pet.species?.name || 'Especie sin definir' }}
                  </p>
                </div>
              </div>
            </td>
            <td class="px-5 py-3 text-slate-600">{{ pet.owner?.name || '—' }}</td>
            <td class="px-5 py-3 text-slate-500">{{ pet.age !== null ? `${pet.age} años` : '—' }}</td>
            <td class="px-5 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-bold" :class="VACCINE_BADGE[pet.vaccineStatus].class">
                {{ VACCINE_BADGE[pet.vaccineStatus].label }}
              </span>
            </td>
            <td class="px-5 py-3">
              <div class="flex justify-end gap-2">
                <RouterLink
                  :to="{ name: 'staff-pet-detail', params: { id: pet.id } }"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Ver ficha"
                >
                  <AppIcon name="eye" :size="14" />
                </RouterLink>
                <RouterLink
                  :to="{ name: 'staff-pet-edit', params: { id: pet.id } }"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Editar"
                >
                  <AppIcon name="edit" :size="14" />
                </RouterLink>
                <button
                  v-if="authStore.hasRole('admin')"
                  type="button"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                  title="Eliminar"
                  @click="askDelete(pet)"
                >
                  <AppIcon name="x" :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar mascota permanentemente"
      :message="`Esta acción no se puede deshacer. Se eliminará a &quot;${petToDelete?.name}&quot; junto con su historial médico, vacunas y citas.`"
      confirm-label="Sí, eliminar para siempre"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
