<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import { useAppointmentsStore } from '../../../stores/appointments'

const appointmentsStore = useAppointmentsStore()
const loading = ref(true)

onMounted(async () => {
  await appointmentsStore.fetchAppointments()
  loading.value = false
})

// Mismo filtro/orden que ya usa NotificationsPage.vue para "tus próximas
// citas" - acá solo se toma la primera en vez de las primeras 5.
const nextAppointment = computed(() => {
  const upcoming = appointmentsStore.appointments
    .filter((a) => a.status !== 'Cancelada' && new Date(a.appointmentDatetime) > new Date())
    .sort((a, b) => new Date(a.appointmentDatetime) - new Date(b.appointmentDatetime))
  return upcoming[0] || null
})

const STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Confirmada: 'bg-emerald-50 text-emerald-700',
  Completada: 'bg-slate-100 text-slate-600',
  Cancelada: 'bg-red-50 text-red-600',
}

function formatDateTime(iso) {
  if (!iso) return '—'
  const dt = new Date(iso)
  return `${dt.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })} · ${dt.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}`
}
</script>

<template>
  <div v-if="!loading" class="relative z-10 max-w-7xl mx-auto px-6 -mt-10 md:-mt-12">
    <div
      class="bg-white rounded-3xl shadow-xl border border-slate-100 p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
    >
      <div v-if="nextAppointment" class="flex items-center gap-4 min-w-0">
        <div
          class="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0"
        >
          <AppIcon name="calendar" :size="22" />
        </div>

        <div class="min-w-0">
          <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wide">
            Próxima actividad
          </p>
          <p class="font-bold text-slate-900 truncate">
            {{ nextAppointment.pet?.name || 'Mascota' }} — {{ nextAppointment.reason || 'Consulta veterinaria' }}
          </p>
          <p class="text-sm text-slate-500 flex flex-wrap items-center gap-2 mt-0.5">
            <span class="inline-flex items-center gap-1.5">
              <AppIcon name="clock" :size="14" />
              {{ formatDateTime(nextAppointment.appointmentDatetime) }}
            </span>
            <span
              class="text-[11px] font-bold px-2 py-0.5 rounded-full"
              :class="STATUS_BADGE[nextAppointment.status]"
            >
              {{ nextAppointment.status }}
            </span>
          </p>
        </div>
      </div>

      <div v-else class="flex items-center gap-4">
        <div
          class="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center shrink-0"
        >
          <AppIcon name="calendar" :size="22" />
        </div>

        <div>
          <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wide">
            Próxima actividad
          </p>
          <p class="font-semibold text-slate-600">No tienes citas próximas.</p>
        </div>
      </div>

      <RouterLink
        v-if="nextAppointment"
        :to="{ name: 'appointment-detail', params: { id: nextAppointment.id } }"
        class="shrink-0 border border-slate-200 hover:border-emerald-700 hover:text-emerald-700 text-slate-700 px-5 py-2.5 rounded-xl text-sm font-semibold transition text-center"
      >
        Ver detalles
      </RouterLink>

      <RouterLink
        v-else
        :to="{ name: 'appointment-calendar' }"
        class="shrink-0 bg-emerald-700 hover:bg-emerald-800 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition text-center"
      >
        Agendar cita
      </RouterLink>
    </div>
  </div>
</template>
