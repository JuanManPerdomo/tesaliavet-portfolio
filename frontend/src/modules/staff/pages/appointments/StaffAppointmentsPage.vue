<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PetPhoto from '../../../client/components/PetPhoto.vue'
import { useAppointmentsStore } from '../../../../stores/appointments'

const FILTERS = [
  { value: '', label: 'Todas' },
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

const route = useRoute()
const appointmentsStore = useAppointmentsStore()
const activeFilter = ref('')

const mineOnly = computed(() => route.name === 'staff-appointments-mine')
const ownerId = computed(() => route.query.ownerId || undefined)
const ownerName = computed(() => route.query.ownerName || '')

function load() {
  appointmentsStore.fetchStaffAppointments(activeFilter.value || undefined, mineOnly.value, ownerId.value)
}

onMounted(load)

function formatDateTime(isoDateTime) {
  const dt = new Date(isoDateTime)
  return {
    date: dt.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' }),
    time: dt.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }),
  }
}
</script>

<template>
  <div>
    <RouterLink
      v-if="ownerId"
      :to="{ name: 'staff-client-detail', params: { id: ownerId } }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver al cliente
    </RouterLink>

    <h1 class="text-2xl font-extrabold text-slate-900 mb-1">
      {{ ownerId ? `Citas de ${ownerName}` : mineOnly ? 'Citas asignadas' : 'Citas' }}
    </h1>
    <p class="text-sm text-slate-500 mb-6">
      {{
        ownerId
          ? 'Historial de citas de este cliente.'
          : mineOnly
            ? 'Las citas asignadas a ti como veterinario.'
            : 'Gestiona las citas veterinarias de la clínica.'
      }}
    </p>

    <div class="flex overflow-x-auto gap-6 border-b border-slate-200 mb-6">
      <button
        v-for="f in FILTERS"
        :key="f.value"
        class="pb-3 text-sm font-semibold whitespace-nowrap border-b-2 transition"
        :class="
          activeFilter === f.value
            ? 'text-emerald-700 border-emerald-700'
            : 'text-slate-500 border-transparent hover:text-emerald-700'
        "
        @click="activeFilter = f.value; load()"
      >
        {{ f.label }}
      </button>
    </div>

    <div v-if="appointmentsStore.staffLoading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="appointmentsStore.staffError" class="text-sm text-red-600">{{ appointmentsStore.staffError }}</div>
    <div
      v-else-if="!appointmentsStore.staffAppointments.length"
      class="bg-white border border-slate-200 rounded-2xl p-12 text-center"
    >
      <AppIcon name="calendar" :size="28" class="text-slate-300 mx-auto mb-3" />
      <p class="text-sm text-slate-500">No hay citas en esta categoría.</p>
    </div>

    <div v-else class="flex flex-col gap-3">
      <RouterLink
        v-for="appointment in appointmentsStore.staffAppointments"
        :key="appointment.id"
        :to="{ name: 'staff-appointment-detail', params: { id: appointment.id } }"
        class="bg-white rounded-2xl border border-slate-200 p-5 flex flex-col md:flex-row md:items-center gap-4 hover:border-emerald-300 transition"
      >
        <div class="flex flex-col w-full md:w-32 flex-shrink-0">
          <span class="text-sm font-bold text-slate-900">{{ formatDateTime(appointment.appointmentDatetime).date }}</span>
          <span class="text-xs text-slate-500">{{ formatDateTime(appointment.appointmentDatetime).time }}</span>
        </div>

        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="w-10 h-10 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
            <PetPhoto :photo-url="appointment.pet?.photoUrl" :icon-size="18" />
          </div>
          <div class="min-w-0">
            <p class="text-sm font-bold text-slate-900 truncate">{{ appointment.pet?.name }}</p>
            <p class="text-xs text-slate-500 truncate">{{ appointment.ownerName }} — {{ appointment.reason }}</p>
          </div>
        </div>

        <div class="w-full md:w-40 flex-shrink-0">
          <p class="text-xs text-slate-400">Veterinario</p>
          <p class="text-sm text-slate-700">{{ appointment.veterinarianName || 'Por asignar' }}</p>
        </div>

        <span
          class="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide flex-shrink-0"
          :class="STATUS_BADGE[appointment.status]"
        >
          {{ appointment.status }}
        </span>
      </RouterLink>
    </div>
  </div>
</template>
