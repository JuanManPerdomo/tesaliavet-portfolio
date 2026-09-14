<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import PetPhoto from '../components/PetPhoto.vue'
import { usePetsStore } from '../../../stores/pets'
import { useAppointmentsStore } from '../../../stores/appointments'
import { useToastStore } from '../../../stores/toast'

const REASON_OPTIONS = [
  'Consulta general',
  'Vacunación',
  'Control post-operatorio',
  'Desparasitación',
  'Urgencia',
  'Otro',
]

const route = useRoute()
const router = useRouter()
const petsStore = usePetsStore()
const appointmentsStore = useAppointmentsStore()
const toastStore = useToastStore()

const appointmentDate = route.query.date || ''
const appointmentTime = route.query.time || ''

const reasonType = ref(REASON_OPTIONS[0])
const customReason = ref('')
const notes = ref('')
const selectedPetId = ref(route.query.petId ? Number(route.query.petId) : null)

const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')

const selectedPet = computed(() =>
  petsStore.pets.find((p) => p.id === selectedPetId.value)
)

const finalReason = computed(() =>
  reasonType.value === 'Otro' ? customReason.value.trim() : reasonType.value
)

const dateTimeLabel = computed(() => {
  if (!appointmentDate || !appointmentTime) return ''
  const label = new Date(`${appointmentDate}T00:00:00`).toLocaleDateString('es-CO', {
    weekday: 'long',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
  const [h] = appointmentTime.split(':').map(Number)
  const period = h >= 12 ? 'PM' : 'AM'
  const hour12 = h % 12 === 0 ? 12 : h % 12
  return `${label.charAt(0).toUpperCase() + label.slice(1)} · ${String(hour12).padStart(2, '0')}:00 ${period}`
})

onMounted(async () => {
  if (!appointmentDate || !appointmentTime) {
    router.replace({ name: 'appointment-calendar' })
    return
  }
  await petsStore.fetchPets()
  if (!selectedPetId.value && petsStore.pets.length > 0) {
    selectedPetId.value = petsStore.pets[0].id
  }
  loading.value = false
})

async function handleSubmit() {
  errorMessage.value = ''

  if (!selectedPetId.value) {
    errorMessage.value = 'Selecciona para qué mascota es la cita.'
    return
  }
  if (!finalReason.value) {
    errorMessage.value = 'Indica el motivo de la cita.'
    return
  }

  submitting.value = true
  try {
    const appointment = await appointmentsStore.createAppointment({
      petId: selectedPetId.value,
      date: appointmentDate,
      time: appointmentTime,
      reason: finalReason.value,
      notes: notes.value || undefined,
    })
    toastStore.success('¡Cita agendada exitosamente!')
    router.push({ name: 'appointment-detail', params: { id: appointment.id } })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo agendar la cita.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-5xl mx-auto px-6 py-12 w-full">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 class="text-2xl font-extrabold text-slate-900 mb-2">Agendar nueva cita</h1>
          <p class="text-sm text-slate-500">Completa los datos para confirmar tu cita veterinaria</p>
        </div>
        <div
          class="inline-flex items-center gap-2 bg-white border border-emerald-200 rounded-full px-4 py-2 text-sm font-semibold text-emerald-700 shadow-sm"
        >
          <AppIcon name="clock" :size="16" />
          {{ dateTimeLabel }}
        </div>
      </div>

      <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>

      <form v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start" @submit.prevent="handleSubmit">
        <div class="lg:col-span-8 flex flex-col gap-6">
          <!-- Datos de la cita -->
          <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
            <h2
              class="text-base font-bold text-slate-900 mb-6 pb-4 border-b border-slate-100 flex items-center gap-2.5"
            >
              <span
                class="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center"
              >
                <AppIcon name="calendar" :size="18" />
              </span>
              Datos de la cita
            </h2>

            <div class="space-y-5">
              <div>
                <label class="block text-sm font-medium text-slate-600 mb-2" for="reasonType">
                  Motivo de la cita *
                </label>
                <select
                  id="reasonType"
                  v-model="reasonType"
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                >
                  <option v-for="opt in REASON_OPTIONS" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </div>

              <div v-if="reasonType === 'Otro'">
                <label class="block text-sm font-medium text-slate-600 mb-2" for="customReason">
                  Especifica el motivo *
                </label>
                <input
                  id="customReason"
                  v-model="customReason"
                  type="text"
                  placeholder="Ej. Revisión de piel"
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-600 mb-2" for="notes">
                  Notas adicionales
                </label>
                <textarea
                  id="notes"
                  v-model="notes"
                  rows="4"
                  placeholder="Describe brevemente los síntomas, comportamientos o cualquier detalle relevante para la cita..."
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Mascota -->
          <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
            <h2
              class="text-base font-bold text-slate-900 mb-6 pb-4 border-b border-slate-100 flex items-center gap-2.5"
            >
              <span
                class="w-9 h-9 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center"
              >
                <AppIcon name="paw" :size="18" />
              </span>
              ¿Para qué mascota es la cita? *
            </h2>

            <div v-if="petsStore.pets.length === 0" class="text-sm text-slate-500">
              No tienes mascotas registradas.
              <RouterLink to="/mis-mascotas/nueva" class="text-emerald-700 font-semibold hover:underline">
                Registra una primero
              </RouterLink>
            </div>

            <div v-else class="flex flex-col gap-3">
              <label
                v-for="pet in petsStore.pets"
                :key="pet.id"
                class="relative border rounded-xl p-4 flex items-center gap-4 cursor-pointer transition"
                :class="
                  selectedPetId === pet.id
                    ? 'border-2 border-emerald-700 bg-emerald-50'
                    : 'border-slate-200 hover:border-emerald-300 hover:bg-slate-50'
                "
              >
                <input
                  v-model="selectedPetId"
                  type="radio"
                  :value="pet.id"
                  class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div class="w-12 h-12 rounded-lg overflow-hidden bg-white flex-shrink-0">
                  <PetPhoto :photo-url="pet.photoUrl" :icon-size="22" />
                </div>
                <div class="flex-1">
                  <p class="text-sm font-bold text-slate-900">{{ pet.name }}</p>
                  <p class="text-xs text-slate-500">
                    {{ pet.species?.name }} · {{ pet.breed?.name || 'Sin raza' }} ·
                    {{ pet.gender }}
                    <template v-if="pet.age !== null"> · {{ pet.age }} años</template>
                    <template v-if="pet.weight !== null"> · {{ pet.weight }} kg</template>
                  </p>
                </div>
              </label>
            </div>
          </div>
        </div>

        <!-- Resumen -->
        <div class="lg:col-span-4">
          <div class="bg-white rounded-2xl border border-slate-200 p-6 lg:sticky lg:top-24">
            <h3 class="text-sm font-bold text-slate-900 mb-5 pb-4 border-b border-slate-100">
              Resumen de la cita
            </h3>

            <div class="flex items-start gap-3 mb-4">
              <span
                class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center flex-shrink-0"
              >
                <AppIcon name="calendar" :size="15" />
              </span>
              <div>
                <p class="text-[10px] font-semibold text-slate-400 uppercase">Fecha y hora</p>
                <p class="text-sm font-semibold text-slate-800">{{ dateTimeLabel }}</p>
              </div>
            </div>

            <div class="flex items-start gap-3 mb-4">
              <span
                class="w-8 h-8 rounded-lg bg-sky-50 text-sky-700 flex items-center justify-center flex-shrink-0"
              >
                <AppIcon name="stethoscope" :size="15" />
              </span>
              <div>
                <p class="text-[10px] font-semibold text-slate-400 uppercase">Motivo</p>
                <p class="text-sm font-semibold text-slate-800">{{ finalReason || '—' }}</p>
              </div>
            </div>

            <div class="flex items-start gap-3 mb-6">
              <span
                class="w-8 h-8 rounded-lg bg-pink-50 text-pink-700 flex items-center justify-center flex-shrink-0"
              >
                <AppIcon name="paw" :size="15" />
              </span>
              <div>
                <p class="text-[10px] font-semibold text-slate-400 uppercase">Mascota</p>
                <p class="text-sm font-semibold text-slate-800">
                  {{ selectedPet ? selectedPet.name : '—' }}
                </p>
              </div>
            </div>

            <p v-if="errorMessage" class="text-sm text-red-600 mb-4">{{ errorMessage }}</p>

            <PrimaryButton
              type="submit"
              :loading="submitting"
              class="w-full justify-center gap-2 mb-3"
            >
              <AppIcon name="check" :size="16" />
              Confirmar cita
            </PrimaryButton>
            <RouterLink
              :to="{ name: 'appointment-calendar' }"
              class="w-full flex items-center justify-center gap-2 text-sm font-semibold text-slate-500 hover:text-emerald-700 py-2 transition"
            >
              <AppIcon name="arrow-left" :size="14" />
              Volver a la agenda
            </RouterLink>

            <div class="mt-5 bg-slate-50 rounded-xl p-4 flex gap-2.5">
              <AppIcon name="info" :size="16" class="text-emerald-700 flex-shrink-0 mt-0.5" />
              <p class="text-xs text-slate-500 leading-relaxed">
                <strong class="text-slate-700">Recuerda:</strong> puedes cancelar tu cita hasta 2
                horas antes de la hora programada.
              </p>
            </div>
          </div>
        </div>
      </form>
    </main>

    <Footer />
  </div>
</template>
