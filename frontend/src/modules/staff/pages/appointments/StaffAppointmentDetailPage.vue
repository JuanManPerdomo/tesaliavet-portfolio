<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import PetPhoto from '../../../client/components/PetPhoto.vue'
import { useAppointmentsStore } from '../../../../stores/appointments'
import { useStaffUsersStore } from '../../../../stores/staffUsers'
import { useAuthStore } from '../../../../stores/auth'
import { useToastStore } from '../../../../stores/toast'

const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Confirmada: 'bg-emerald-50 text-emerald-700',
  Completada: 'bg-slate-100 text-slate-600',
  Cancelada: 'bg-red-50 text-red-600',
}

const route = useRoute()
const router = useRouter()
const appointmentsStore = useAppointmentsStore()
const staffUsersStore = useStaffUsersStore()
const authStore = useAuthStore()
const toastStore = useToastStore()

const appointmentId = computed(() => Number(route.params.id))
const appointment = ref(null)
const loading = ref(true)
const errorMessage = ref('')
const updating = ref(false)

const isAdmin = computed(() => authStore.hasRole('admin'))

async function load() {
  loading.value = true
  try {
    appointment.value = await appointmentsStore.fetchAppointment(appointmentId.value)
  } catch {
    errorMessage.value = 'No se pudo cargar la cita.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  if (isAdmin.value) {
    await staffUsersStore.fetchUsers({ role: 'veterinario', perPage: 100 })
  }
})

function formatDateTime(isoDateTime) {
  const dt = new Date(isoDateTime)
  return {
    date: dt.toLocaleDateString('es-CO', { day: '2-digit', month: 'long', year: 'numeric' }),
    time: dt.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
  }
}

async function updateStatus(status) {
  updating.value = true
  errorMessage.value = ''
  try {
    appointment.value = await appointmentsStore.updateAppointmentStaff(appointmentId.value, { status })
    toastStore.success(status === 'Confirmada' ? 'Cita confirmada.' : 'Cita marcada como completada.')
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo actualizar la cita.'
  } finally {
    updating.value = false
  }
}

async function assignVet(event) {
  const veterinarianId = event.target.value || null
  updating.value = true
  try {
    appointment.value = await appointmentsStore.updateAppointmentStaff(appointmentId.value, { veterinarianId })
    toastStore.success('Veterinario asignado.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo asignar el veterinario.')
  } finally {
    updating.value = false
  }
}

function goToMedicalRecord() {
  router.push({
    name: 'staff-medical-record-new',
    params: { petId: appointment.value.pet.id },
    query: { petName: appointment.value.pet.name },
  })
}

function goToVaccination() {
  router.push({
    name: 'staff-vaccination-new',
    params: { petId: appointment.value.pet.id },
    query: { petName: appointment.value.pet.name },
  })
}
</script>

<template>
  <div class="max-w-3xl">
    <RouterLink
      :to="{ name: 'staff-appointments' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a citas
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="!appointment" class="text-sm text-red-600">{{ errorMessage }}</div>

    <template v-else>
      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <div class="flex items-start justify-between mb-5">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
              <PetPhoto :photo-url="appointment.pet?.photoUrl" :icon-size="20" />
            </div>
            <div>
              <h1 class="text-lg font-extrabold text-slate-900">{{ appointment.pet?.name }}</h1>
              <p class="text-sm text-slate-500">Dueño: {{ appointment.ownerName }}</p>
            </div>
          </div>
          <span class="text-[11px] font-bold uppercase px-3 py-1 rounded-full" :class="STATUS_BADGE[appointment.status]">
            {{ appointment.status }}
          </span>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm border-t border-slate-100 pt-5">
          <div>
            <p class="text-xs text-slate-400 mb-1">Fecha</p>
            <p class="font-semibold text-slate-800">{{ formatDateTime(appointment.appointmentDatetime).date }}</p>
          </div>
          <div>
            <p class="text-xs text-slate-400 mb-1">Hora</p>
            <p class="font-semibold text-slate-800">{{ formatDateTime(appointment.appointmentDatetime).time }}</p>
          </div>
          <div class="col-span-2">
            <p class="text-xs text-slate-400 mb-1">Motivo</p>
            <p class="text-slate-700">{{ appointment.reason }}</p>
          </div>
          <div v-if="appointment.notes" class="col-span-2">
            <p class="text-xs text-slate-400 mb-1">Notas</p>
            <p class="text-slate-700">{{ appointment.notes }}</p>
          </div>
        </div>

        <div v-if="isAdmin" class="border-t border-slate-100 pt-5 mt-5">
          <label class="block text-xs text-slate-400 mb-2" for="vet">Veterinario asignado</label>
          <select
            id="vet"
            :value="appointment.veterinarianId || ''"
            :disabled="updating"
            class="w-full max-w-xs border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
            @change="assignVet"
          >
            <option value="">Sin asignar</option>
            <option v-for="vet in staffUsersStore.users" :key="vet.id" :value="vet.id">
              {{ vet.firstName }} {{ vet.lastName }}
            </option>
          </select>
        </div>
      </div>

      <p v-if="errorMessage" class="text-sm text-red-600 mb-4">{{ errorMessage }}</p>

      <div class="flex flex-wrap gap-3">
        <PrimaryButton
          v-if="appointment.status === 'Pendiente'"
          :loading="updating"
          class="gap-2"
          @click="updateStatus('Confirmada')"
        >
          <AppIcon name="check" :size="16" />
          Confirmar cita
        </PrimaryButton>

        <PrimaryButton
          v-if="appointment.status === 'Confirmada'"
          :loading="updating"
          class="gap-2"
          @click="updateStatus('Completada')"
        >
          <AppIcon name="check" :size="16" />
          Marcar como completada
        </PrimaryButton>

        <button
          type="button"
          class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center gap-2"
          @click="goToMedicalRecord"
        >
          <AppIcon name="clipboard" :size="16" />
          Agregar registro médico
        </button>

        <button
          type="button"
          class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center gap-2"
          @click="goToVaccination"
        >
          <AppIcon name="pill" :size="16" />
          Agregar vacuna
        </button>
      </div>
    </template>
  </div>
</template>
