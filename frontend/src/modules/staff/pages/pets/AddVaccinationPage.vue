<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { usePetsStore } from '../../../../stores/pets'
import { useToastStore } from '../../../../stores/toast'

const route = useRoute()
const router = useRouter()
const petsStore = usePetsStore()
const toastStore = useToastStore()

const petId = computed(() => Number(route.params.petId))
const petName = computed(() => route.query.petName || 'la mascota')

const form = ref({
  vaccineId: '',
  applicationDate: '',
  nextDueDate: '',
  batchNumber: '',
  expiresAt: '',
  notes: '',
})
const submitting = ref(false)
const errorMessage = ref('')

onMounted(() => {
  petsStore.fetchVaccines()
})

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.value.vaccineId || !form.value.applicationDate) {
    errorMessage.value = 'La vacuna y la fecha de aplicación son obligatorias.'
    return
  }
  submitting.value = true
  try {
    await petsStore.createVaccination(petId.value, form.value)
    toastStore.success('Vacuna registrada.')
    router.back()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo registrar la vacuna.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl">
    <button
      type="button"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
      @click="router.back()"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver
    </button>

    <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Nueva vacuna</h1>
    <p class="text-sm text-slate-500 mb-6">Para {{ petName }}.</p>

    <form class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-slate-600 mb-2" for="vaccineId">Vacuna *</label>
          <select
            id="vaccineId"
            v-model="form.vaccineId"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          >
            <option value="" disabled>Selecciona vacuna</option>
            <option v-for="v in petsStore.vaccines" :key="v.id" :value="v.id">{{ v.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="applicationDate">Fecha de aplicación *</label>
          <input
            id="applicationDate"
            v-model="form.applicationDate"
            type="date"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="nextDueDate">Próxima dosis</label>
          <input
            id="nextDueDate"
            v-model="form.nextDueDate"
            type="date"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="batchNumber">Lote</label>
          <input
            id="batchNumber"
            v-model="form.batchNumber"
            type="text"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="expiresAt">Vencimiento del lote</label>
          <input
            id="expiresAt"
            v-model="form.expiresAt"
            type="date"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          />
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-slate-600 mb-2" for="notes">Notas</label>
          <textarea
            id="notes"
            v-model="form.notes"
            rows="3"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          ></textarea>
        </div>
      </div>

      <p v-if="errorMessage" class="text-sm text-red-600 mt-6">{{ errorMessage }}</p>

      <div class="mt-8 pt-6 border-t border-slate-100 flex justify-end">
        <PrimaryButton type="submit" :loading="submitting" class="gap-2">
          <AppIcon name="check" :size="16" />
          Guardar vacuna
        </PrimaryButton>
      </div>
    </form>
  </div>
</template>
