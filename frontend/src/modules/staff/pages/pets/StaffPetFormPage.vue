<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import PetPhoto from '../../../client/components/PetPhoto.vue'
import { useStaffPetsStore } from '../../../../stores/staffPets'
import { usePetsStore } from '../../../../stores/pets'
import { useToastStore } from '../../../../stores/toast'

const route = useRoute()
const router = useRouter()
const staffPetsStore = useStaffPetsStore()
const petsStore = usePetsStore()
const toastStore = useToastStore()

const petId = computed(() => Number(route.params.id))

const GENDER_OPTIONS = [
  { value: 'Macho', label: 'Macho', icon: 'gender-male' },
  { value: 'Hembra', label: 'Hembra', icon: 'gender-female' },
  { value: 'Desconocido', label: 'Desconocido', icon: 'help-circle' },
]

const form = ref({
  name: '',
  speciesId: '',
  breedId: '',
  gender: 'Desconocido',
  birthDate: '',
  weight: '',
  color: '',
  notes: '',
})

const ownerName = ref('')
const existingPhotoUrl = ref(null)
const photoFile = ref(null)
const photoPreview = ref('')
const removePhoto = ref(false)
const fileInput = ref(null)

const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')

function onPhotoChange(event) {
  const file = event.target.files[0]
  if (!file) return
  photoFile.value = file
  removePhoto.value = false
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value)
  photoPreview.value = URL.createObjectURL(file)
}

function clearPhoto() {
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value)
  photoFile.value = null
  photoPreview.value = ''
  removePhoto.value = !!existingPhotoUrl.value
  existingPhotoUrl.value = null
  if (fileInput.value) fileInput.value.value = ''
}

function onSpeciesChange() {
  form.value.breedId = ''
  petsStore.fetchBreeds(form.value.speciesId)
}

onMounted(async () => {
  // Reutiliza el catalogo de especies/razas del store del cliente (mismo
  // catalogo, no hay razon para duplicarlo).
  await petsStore.fetchSpecies()

  try {
    const pet = await staffPetsStore.fetchPet(petId.value)
    form.value = {
      name: pet.name,
      speciesId: pet.species?.id ?? '',
      breedId: pet.breed?.id ?? '',
      gender: pet.gender,
      birthDate: pet.birthDate ?? '',
      weight: pet.weight ?? '',
      color: pet.color ?? '',
      notes: pet.notes ?? '',
    }
    existingPhotoUrl.value = pet.photoUrl
    ownerName.value = pet.owner?.name || ''
    if (pet.species?.id) await petsStore.fetchBreeds(pet.species.id)
  } catch {
    errorMessage.value = 'No se pudo cargar la mascota.'
  }

  loading.value = false
})

onBeforeUnmount(() => {
  if (photoPreview.value) URL.revokeObjectURL(photoPreview.value)
})

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.value.name || !form.value.speciesId) {
    errorMessage.value = 'Nombre y especie son obligatorios.'
    return
  }

  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('name', form.value.name)
    payload.append('speciesId', form.value.speciesId)
    payload.append('breedId', form.value.breedId || '')
    payload.append('gender', form.value.gender)
    payload.append('birthDate', form.value.birthDate || '')
    payload.append('weight', form.value.weight || '')
    payload.append('color', form.value.color || '')
    payload.append('notes', form.value.notes || '')
    if (photoFile.value) payload.append('photo', photoFile.value)
    else if (removePhoto.value) payload.append('removePhoto', 'true')

    const pet = await staffPetsStore.updatePet(petId.value, payload)
    toastStore.success('Mascota actualizada correctamente.')
    router.push({ name: 'staff-pet-detail', params: { id: pet.id } })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo guardar la mascota.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl">
    <RouterLink
      :to="{ name: 'staff-pet-detail', params: { id: petId } }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a la ficha
    </RouterLink>

    <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Editar mascota</h1>
    <p class="text-sm text-slate-500 mb-6">
      {{ ownerName ? `Dueño: ${ownerName}` : '' }}
    </p>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>

    <form v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start" @submit.prevent="handleSubmit">
      <!-- Photo panel -->
      <div class="lg:col-span-4 bg-white rounded-2xl border border-slate-200 p-6 flex flex-col items-center text-center">
        <div
          class="w-40 h-40 rounded-full border-2 border-dashed border-emerald-200 relative overflow-hidden flex items-center justify-center bg-emerald-50/50 cursor-pointer mb-5"
          @click="fileInput.click()"
        >
          <img v-if="photoPreview" :src="photoPreview" class="w-full h-full object-cover" alt="" />
          <PetPhoto v-else-if="existingPhotoUrl" :photo-url="existingPhotoUrl" :icon-size="36" />
          <div v-else class="flex flex-col items-center gap-1 text-emerald-700">
            <AppIcon name="camera" :size="30" />
            <span class="text-xs font-semibold">Subir foto</span>
          </div>
          <input ref="fileInput" type="file" accept="image/jpeg,image/png" class="hidden" @change="onPhotoChange" />
        </div>
        <h3 class="text-sm font-semibold text-slate-800 mb-1">Foto de perfil</h3>
        <p class="text-xs text-slate-500 mb-1">Formatos JPG o PNG. Tamaño máximo 5MB.</p>
        <button
          v-if="photoPreview || existingPhotoUrl"
          type="button"
          class="text-xs font-semibold text-red-600 hover:underline"
          @click="clearPhoto"
        >
          Quitar foto
        </button>
      </div>

      <!-- Fields -->
      <div class="lg:col-span-8 bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
        <h2 class="text-lg font-bold text-slate-900 mb-6 pb-4 border-b border-slate-100">Datos principales</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-slate-600 mb-2" for="petName">Nombre de la mascota *</label>
            <input
              id="petName"
              v-model="form.name"
              type="text"
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-600 mb-2" for="species">Especie</label>
            <select
              id="species"
              v-model="form.speciesId"
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              @change="onSpeciesChange"
            >
              <option value="" disabled>Selecciona especie</option>
              <option v-for="s in petsStore.species" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-600 mb-2" for="breed">Raza</label>
            <select
              id="breed"
              v-model="form.breedId"
              :disabled="!form.speciesId"
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-50 disabled:text-slate-400"
            >
              <option value="">Selecciona raza (opcional)</option>
              <option v-for="b in petsStore.breeds" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-slate-600 mb-3">Género</label>
            <div class="grid grid-cols-3 gap-3">
              <label v-for="option in GENDER_OPTIONS" :key="option.value" class="relative cursor-pointer block">
                <input
                  v-model="form.gender"
                  type="radio"
                  :value="option.value"
                  class="absolute inset-0 w-full h-full opacity-0 cursor-pointer peer"
                />
                <div
                  class="flex flex-col items-center justify-center gap-2 p-4 border border-slate-200 rounded-xl text-slate-500 transition h-full peer-checked:border-emerald-700 peer-checked:bg-emerald-50 peer-checked:text-emerald-700"
                >
                  <AppIcon :name="option.icon" :size="20" />
                  <span class="text-sm font-semibold">{{ option.label }}</span>
                </div>
              </label>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-600 mb-2" for="birthDate">Fecha de nacimiento (Aprox.)</label>
            <input
              id="birthDate"
              v-model="form.birthDate"
              type="date"
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-600 mb-2" for="weight">Peso (kg)</label>
            <input
              id="weight"
              v-model="form.weight"
              type="number"
              step="0.1"
              min="0"
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-slate-600 mb-2" for="color">Color predominante / Marcas distintivas</label>
            <input
              id="color"
              v-model="form.color"
              type="text"
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <div class="md:col-span-2 border-t border-slate-100 pt-5">
            <label class="block text-sm font-medium text-slate-600 mb-2" for="notes">Notas clínicas u observaciones</label>
            <textarea
              id="notes"
              v-model="form.notes"
              rows="4"
              class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            ></textarea>
          </div>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600 mt-6">{{ errorMessage }}</p>

        <div class="mt-8 pt-6 border-t border-slate-100 flex justify-end gap-3">
          <RouterLink
            :to="{ name: 'staff-pet-detail', params: { id: petId } }"
            class="px-6 py-2.5 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition flex items-center justify-center gap-2"
          >
            <AppIcon name="x" :size="14" />
            Cancelar
          </RouterLink>
          <PrimaryButton type="submit" :loading="submitting" class="gap-2">
            <AppIcon name="check" :size="16" />
            Guardar cambios
          </PrimaryButton>
        </div>
      </div>
    </form>
  </div>
</template>
