<script setup>
import { ref, computed, onMounted } from 'vue'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import PetPhoto from '../components/PetPhoto.vue'
import CancelAppointmentModal from '../components/CancelAppointmentModal.vue'
import { useAppointmentsStore } from '../../../stores/appointments'
import { useToastStore } from '../../../stores/toast'

const appointmentsStore = useAppointmentsStore()
const toastStore = useToastStore()

const FILTERS = [
  { value: 'all', label: 'Todas' },
  { value: 'Pendiente', label: 'Pendientes' },
  { value: 'Confirmada', label: 'Confirmadas' },
  { value: 'Completada', label: 'Completadas' },
  { value: 'Cancelada', label: 'Canceladas' },
]

const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Confirmada: 'bg-emerald-50 text-emerald-700',
  Completada: 'bg-slate-100 text-slate-600',
  Cancelada: 'bg-red-50 text-red-600',
}

const activeFilter = ref('all')
const cancelTarget = ref(null)
const cancelling = ref(false)
const cancelError = ref('')

const filteredAppointments = computed(() => {
  if (activeFilter.value === 'all') return appointmentsStore.appointments
  return appointmentsStore.appointments.filter((a) => a.status === activeFilter.value)
})

function canCancel(appointment) {
  return appointment.status === 'Pendiente' || appointment.status === 'Confirmada'
}

function formatDateTime(isoDateTime) {
  const dt = new Date(isoDateTime)
  return {
    date: dt.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' }),
    time: dt.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
  }
}

function openCancel(appointment) {
  cancelError.value = ''
  cancelTarget.value = appointment
}

async function confirmCancel(reason) {
  cancelling.value = true
  cancelError.value = ''
  try {
    await appointmentsStore.cancelAppointment(cancelTarget.value.id, reason)
    toastStore.success('Cita cancelada.')
    cancelTarget.value = null
    appointmentsStore.fetchAppointments()
  } catch (err) {
    cancelError.value = err.response?.data?.message || 'No se pudo cancelar la cita.'
  } finally {
    cancelling.value = false
  }
}

onMounted(() => {
  appointmentsStore.fetchAppointments()
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-6xl mx-auto px-6 py-12 w-full">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Mis Citas Veterinarias</h1>
          <p class="text-sm text-slate-500">
            Gestiona tus próximas visitas y revisa el historial de citas pasadas.
          </p>
        </div>
        <PrimaryButton :to="'/mis-citas/agendar'" class="gap-2">
          <AppIcon name="plus" :size="18" />
          Nueva Cita
        </PrimaryButton>
      </div>

      <div class="flex overflow-x-auto gap-6 border-b border-slate-200 mb-6">
        <button
          v-for="filter in FILTERS"
          :key="filter.value"
          type="button"
          class="pb-3 text-sm font-semibold whitespace-nowrap border-b-2 transition"
          :class="
            activeFilter === filter.value
              ? 'text-emerald-700 border-emerald-700'
              : 'text-slate-500 border-transparent hover:text-emerald-700'
          "
          @click="activeFilter = filter.value"
        >
          {{ filter.label }}
        </button>
      </div>

      <p v-if="appointmentsStore.error" class="text-sm text-red-600 mb-6">
        {{ appointmentsStore.error }}
      </p>

      <div v-if="appointmentsStore.loading" class="text-sm text-slate-500">Cargando...</div>

      <div
        v-else-if="filteredAppointments.length === 0"
        class="bg-white border border-slate-200 rounded-2xl p-12 text-center"
      >
        <AppIcon name="calendar" :size="28" class="text-slate-300 mx-auto mb-3" />
        <p class="text-sm text-slate-500">No tienes citas en esta categoría.</p>
      </div>

      <div v-else class="flex flex-col gap-3">
        <div
          v-for="appointment in filteredAppointments"
          :key="appointment.id"
          class="bg-white rounded-2xl border border-slate-200 p-5 flex flex-col md:flex-row md:items-center gap-4"
        >
          <div class="flex flex-col w-full md:w-32 flex-shrink-0">
            <span class="text-sm font-bold text-slate-900">
              {{ formatDateTime(appointment.appointmentDatetime).date }}
            </span>
            <span class="text-xs text-slate-500">
              {{ formatDateTime(appointment.appointmentDatetime).time }}
            </span>
          </div>

          <div class="flex items-center gap-3 flex-1 min-w-0">
            <div class="w-10 h-10 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
              <PetPhoto :photo-url="appointment.pet?.photoUrl" :icon-size="18" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-bold text-slate-900 truncate">{{ appointment.pet?.name }}</p>
              <p class="text-xs text-slate-500 truncate">{{ appointment.reason }}</p>
            </div>
          </div>

          <div class="w-full md:w-40 flex-shrink-0">
            <p class="text-xs text-slate-400">Veterinario</p>
            <p class="text-sm text-slate-700">{{ appointment.veterinarianName || 'Por asignar' }}</p>
          </div>

          <div class="flex-shrink-0">
            <span
              class="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide"
              :class="STATUS_BADGE[appointment.status]"
            >
              {{ appointment.status }}
            </span>
          </div>

          <div class="flex items-center gap-2 flex-shrink-0 md:ml-auto">
            <RouterLink
              :to="{ name: 'appointment-detail', params: { id: appointment.id } }"
              class="p-2 text-slate-400 hover:text-emerald-700 rounded-lg hover:bg-slate-50 transition"
              title="Ver detalle"
            >
              <AppIcon name="eye" :size="18" />
            </RouterLink>
            <button
              v-if="canCancel(appointment)"
              type="button"
              class="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition"
              title="Cancelar cita"
              @click="openCancel(appointment)"
            >
              <AppIcon name="x" :size="18" />
            </button>
          </div>
        </div>
      </div>
    </main>

    <Footer />

    <CancelAppointmentModal
      :open="!!cancelTarget"
      :appointment="cancelTarget"
      :loading="cancelling"
      :error="cancelError"
      @cancel="cancelTarget = null"
      @confirm="confirmCancel"
    />
  </div>
</template>
