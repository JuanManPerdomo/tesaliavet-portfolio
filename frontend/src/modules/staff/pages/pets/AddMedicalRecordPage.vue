<script setup>
import { ref, computed } from 'vue'
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

const form = ref({ symptoms: '', diagnosis: '', treatment: '', observations: '' })
const attachmentFile = ref(null)
const submitting = ref(false)
const errorMessage = ref('')

function onAttachmentChange(event) {
  attachmentFile.value = event.target.files[0] || null
}

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.value.diagnosis) {
    errorMessage.value = 'El diagnóstico es obligatorio.'
    return
  }
  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('symptoms', form.value.symptoms || '')
    payload.append('diagnosis', form.value.diagnosis)
    payload.append('treatment', form.value.treatment || '')
    payload.append('observations', form.value.observations || '')
    if (attachmentFile.value) payload.append('attachment', attachmentFile.value)

    await petsStore.createMedicalRecord(petId.value, payload)
    toastStore.success('Registro médico agregado.')
    router.back()
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo guardar el registro.'
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

    <h1 class="text-2xl font-extrabold text-slate-900 mb-1">Nuevo registro médico</h1>
    <p class="text-sm text-slate-500 mb-6">Para {{ petName }}.</p>

    <form class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8" @submit.prevent="handleSubmit">
      <div class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="symptoms">Síntomas</label>
          <textarea
            id="symptoms"
            v-model="form.symptoms"
            rows="3"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="diagnosis">Diagnóstico *</label>
          <textarea
            id="diagnosis"
            v-model="form.diagnosis"
            rows="3"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="treatment">Tratamiento</label>
          <textarea
            id="treatment"
            v-model="form.treatment"
            rows="3"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="observations">Observaciones</label>
          <textarea
            id="observations"
            v-model="form.observations"
            rows="3"
            class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2" for="attachment">Adjunto (opcional)</label>
          <input
            id="attachment"
            type="file"
            accept="application/pdf,image/jpeg,image/png"
            class="w-full text-sm text-slate-600 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
            @change="onAttachmentChange"
          />
          <p class="text-xs text-slate-400 mt-1">PDF, JPG o PNG. Máximo 5MB.</p>
        </div>
      </div>

      <p v-if="errorMessage" class="text-sm text-red-600 mt-6">{{ errorMessage }}</p>

      <div class="mt-8 pt-6 border-t border-slate-100 flex justify-end">
        <PrimaryButton type="submit" :loading="submitting" class="gap-2">
          <AppIcon name="check" :size="16" />
          Guardar registro
        </PrimaryButton>
      </div>
    </form>
  </div>
</template>
