<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PetPhoto from '../components/PetPhoto.vue'
import CancelAppointmentModal from '../components/CancelAppointmentModal.vue'
import { useAppointmentsStore } from '../../../stores/appointments'
import { useToastStore } from '../../../stores/toast'

const STEPS = ['Pendiente', 'Confirmada', 'Completada']
const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Confirmada: 'bg-emerald-50 text-emerald-700',
  Completada: 'bg-slate-100 text-slate-600',
  Cancelada: 'bg-red-50 text-red-600',
}

const route = useRoute()
const appointmentsStore = useAppointmentsStore()
const toastStore = useToastStore()

const appointment = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const showCancelModal = ref(false)
const cancelling = ref(false)
const cancelError = ref('')

const canCancel = computed(
  () => appointment.value?.status === 'Pendiente' || appointment.value?.status === 'Confirmada'
)

const currentStepIndex = computed(() => STEPS.indexOf(appointment.value?.status))

function formatDate(isoDateTime) {
  const dt = new Date(isoDateTime)
  const label = dt.toLocaleDateString('es-CO', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
  return label.charAt(0).toUpperCase() + label.slice(1)
}

function formatTime(isoDateTime) {
  return new Date(isoDateTime).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
}

async function load() {
  loading.value = true
  try {
    appointment.value = await appointmentsStore.fetchAppointment(route.params.id)
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo cargar la cita.'
  } finally {
    loading.value = false
  }
}

async function confirmCancel(reason) {
  cancelling.value = true
  cancelError.value = ''
  try {
    appointment.value = await appointmentsStore.cancelAppointment(appointment.value.id, reason)
    toastStore.success('Cita cancelada.')
    showCancelModal.value = false
  } catch (err) {
    cancelError.value = err.response?.data?.message || 'No se pudo cancelar la cita.'
  } finally {
    cancelling.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-6xl mx-auto px-6 py-12 w-full">
      <RouterLink
        to="/mis-citas"
        class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-6"
      >
        <AppIcon name="arrow-left" :size="16" />
        Volver a Mis Citas
      </RouterLink>

      <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
      <p v-else-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div class="lg:col-span-8 flex flex-col gap-6">
          <div class="flex items-center gap-3 mb-2">
            <h1 class="text-2xl font-extrabold text-slate-900">Cita #{{ appointment.id }}</h1>
            <span
              class="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide"
              :class="STATUS_BADGE[appointment.status]"
            >
              {{ appointment.status }}
            </span>
          </div>

          <!-- Datos de la cita -->
          <section class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
            <h2 class="text-base font-bold text-slate-900 mb-6 flex items-center gap-2">
              <AppIcon name="calendar" :size="18" class="text-emerald-700" />
              Datos de la cita
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-1">Motivo</p>
                <p class="text-sm text-slate-800">{{ appointment.reason }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-1">Veterinario</p>
                <p class="text-sm text-slate-800">{{ appointment.veterinarianName || 'Por asignar' }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-1">Fecha</p>
                <p class="text-sm text-slate-800">{{ formatDate(appointment.appointmentDatetime) }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-1">Hora</p>
                <p class="text-sm text-slate-800">{{ formatTime(appointment.appointmentDatetime) }}</p>
              </div>
              <div v-if="appointment.notes" class="md:col-span-2">
                <p class="text-xs font-semibold text-slate-400 uppercase mb-1">Notas</p>
                <div class="p-4 bg-slate-50 rounded-lg border border-slate-100">
                  <p class="text-sm text-slate-700">{{ appointment.notes }}</p>
                </div>
              </div>
              <div v-if="appointment.status === 'Cancelada' && appointment.cancelReason" class="md:col-span-2">
                <p class="text-xs font-semibold text-red-500 uppercase mb-1">Motivo de cancelación</p>
                <div class="p-4 bg-red-50 rounded-lg border border-red-100">
                  <p class="text-sm text-red-700">{{ appointment.cancelReason }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Mascota -->
          <section v-if="appointment.pet" class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
            <h2 class="text-base font-bold text-slate-900 mb-6 flex items-center gap-2">
              <AppIcon name="paw" :size="18" class="text-emerald-700" />
              Información de la mascota
            </h2>
            <div class="flex flex-col sm:flex-row gap-5 items-start">
              <div class="w-20 h-20 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0">
                <PetPhoto :photo-url="appointment.pet.photoUrl" :icon-size="28" />
              </div>
              <div class="flex-grow w-full">
                <div class="flex justify-between items-center mb-3">
                  <h3 class="text-lg font-bold text-slate-900">{{ appointment.pet.name }}</h3>
                  <RouterLink
                    :to="{ name: 'pet-detail', params: { id: appointment.pet.id } }"
                    class="text-emerald-700 text-sm font-semibold hover:underline"
                  >
                    Ver perfil completo
                  </RouterLink>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-4 flex flex-col gap-6">
          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <h3 class="text-sm font-bold text-slate-900 mb-5">Estado de la cita</h3>

            <div v-if="appointment.status === 'Cancelada'" class="flex items-center gap-3">
              <div class="w-7 h-7 rounded-full bg-red-100 text-red-600 flex items-center justify-center flex-shrink-0">
                <AppIcon name="x" :size="14" />
              </div>
              <p class="text-sm font-semibold text-red-600">Esta cita fue cancelada</p>
            </div>

            <div v-else class="flex flex-col gap-6">
              <div
                v-for="(step, index) in STEPS"
                :key="step"
                class="flex items-start gap-3"
                :class="index > currentStepIndex ? 'opacity-40' : ''"
              >
                <div
                  class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
                  :class="index <= currentStepIndex ? 'bg-emerald-700 text-white' : 'bg-slate-200 text-slate-400'"
                >
                  <AppIcon v-if="index < currentStepIndex" name="check" :size="12" />
                  <div v-else class="w-2 h-2 rounded-full bg-current"></div>
                </div>
                <p
                  class="text-sm"
                  :class="index === currentStepIndex ? 'font-bold text-emerald-700' : 'text-slate-700'"
                >
                  {{ step }}
                </p>
              </div>
            </div>
          </div>

          <button
            v-if="canCancel"
            type="button"
            class="w-full bg-white border border-red-200 text-red-600 text-sm font-semibold py-3 rounded-lg hover:bg-red-50 transition flex items-center justify-center gap-2"
            @click="showCancelModal = true"
          >
            <AppIcon name="x" :size="16" />
            Cancelar Cita
          </button>
        </div>
      </div>
    </main>

    <Footer />

    <CancelAppointmentModal
      :open="showCancelModal"
      :appointment="appointment"
      :loading="cancelling"
      :error="cancelError"
      @cancel="showCancelModal = false"
      @confirm="confirmCancel"
    />
  </div>
</template>
