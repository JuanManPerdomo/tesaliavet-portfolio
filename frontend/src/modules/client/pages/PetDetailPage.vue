<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PetPhoto from '../components/PetPhoto.vue'
import { usePetsStore } from '../../../stores/pets'
import { useAppointmentsStore } from '../../../stores/appointments'

const route = useRoute()
const petsStore = usePetsStore()
const appointmentsStore = useAppointmentsStore()

const petId = computed(() => Number(route.params.id))

const pet = ref(null)
const medicalRecords = ref([])
const vaccinations = ref([])
const appointments = ref([])
const loading = ref(true)
const errorMessage = ref('')
const activeTab = ref('historial')

const VACCINE_BADGE = {
  al_dia: { label: 'Vacunas al día', class: 'bg-emerald-50 text-emerald-700', icon: 'check' },
  pendiente: { label: 'Vacuna pendiente', class: 'bg-red-50 text-red-600', icon: 'alert-triangle' },
  sin_registro: null,
}

const APPOINTMENT_STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Confirmada: 'bg-emerald-50 text-emerald-700',
  Completada: 'bg-slate-100 text-slate-600',
  Cancelada: 'bg-red-50 text-red-600',
}

function formatDate(isoDate) {
  if (!isoDate) return '—'
  return new Date(isoDate + 'T00:00:00').toLocaleDateString('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function formatDateTime(isoDateTime) {
  if (!isoDateTime) return '—'
  return new Date(isoDateTime).toLocaleDateString('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function initials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}

onMounted(async () => {
  try {
    const [petData, records, vaccines] = await Promise.all([
      petsStore.fetchPet(petId.value),
      petsStore.fetchMedicalRecords(petId.value),
      petsStore.fetchVaccinations(petId.value),
      appointmentsStore.fetchAppointments(),
    ])
    pet.value = petData
    medicalRecords.value = records
    vaccinations.value = vaccines
    appointments.value = appointmentsStore.appointments.filter((a) => a.pet?.id === petId.value)
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo cargar la mascota.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-7xl mx-auto px-6 py-10 w-full">
      <RouterLink
        to="/mis-mascotas"
        class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-6"
      >
        <AppIcon name="arrow-left" :size="16" />
        Volver a Mis Mascotas
      </RouterLink>

      <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
      <p v-else-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <!-- Sidebar -->
        <aside class="lg:col-span-4 flex flex-col gap-6 lg:sticky lg:top-24">
          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <div class="relative w-full aspect-square rounded-xl overflow-hidden mb-6 bg-slate-100">
              <PetPhoto :photo-url="pet.photoUrl" :icon-size="48" />
              <div
                v-if="VACCINE_BADGE[pet.vaccineStatus]"
                class="absolute bottom-3 right-3 font-bold text-[10px] uppercase tracking-wider px-2.5 py-1.5 rounded-full flex items-center gap-1 shadow-sm"
                :class="VACCINE_BADGE[pet.vaccineStatus].class"
              >
                <AppIcon :name="VACCINE_BADGE[pet.vaccineStatus].icon" :size="12" />
                {{ VACCINE_BADGE[pet.vaccineStatus].label }}
              </div>
            </div>

            <div class="mb-5 text-center">
              <h1 class="text-2xl font-extrabold text-slate-900 mb-1">{{ pet.name }}</h1>
              <p class="text-sm text-slate-500 flex items-center justify-center gap-1.5">
                <AppIcon name="paw" :size="14" />
                {{ pet.breed?.name || 'Sin raza registrada' }} • {{ pet.species?.name }}
              </p>
            </div>

            <div class="grid grid-cols-3 gap-3 mb-6">
              <div class="bg-slate-50 rounded-lg p-3 flex flex-col items-center text-center">
                <span class="text-[10px] font-semibold text-slate-400 uppercase mb-1">Edad</span>
                <span class="text-sm font-bold text-emerald-700">
                  {{ pet.age !== null ? `${pet.age} años` : '—' }}
                </span>
              </div>
              <div class="bg-slate-50 rounded-lg p-3 flex flex-col items-center text-center">
                <span class="text-[10px] font-semibold text-slate-400 uppercase mb-1">Peso</span>
                <span class="text-sm font-bold text-emerald-700">
                  {{ pet.weight !== null ? `${pet.weight} kg` : '—' }}
                </span>
              </div>
              <div class="bg-slate-50 rounded-lg p-3 flex flex-col items-center text-center">
                <span class="text-[10px] font-semibold text-slate-400 uppercase mb-1">Sexo</span>
                <span class="text-sm font-bold text-emerald-700">{{ pet.gender }}</span>
              </div>
            </div>

            <div class="flex flex-col gap-3">
              <RouterLink
                :to="{ name: 'appointment-calendar', query: { petId: pet.id } }"
                class="w-full bg-emerald-700 hover:bg-emerald-800 text-white text-sm font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 transition"
              >
                <AppIcon name="calendar" :size="18" />
                Agendar Cita
              </RouterLink>
              <RouterLink
                :to="{ name: 'pet-edit', params: { id: pet.id } }"
                class="w-full border border-slate-200 text-slate-700 text-sm font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 hover:bg-slate-50 transition"
              >
                <AppIcon name="edit" :size="16" />
                Editar Perfil
              </RouterLink>
            </div>
          </div>

          <div
            v-if="pet.nextVaccine"
            class="bg-amber-50 border border-amber-100 rounded-2xl p-5 flex items-start gap-3"
          >
            <div class="bg-white p-2 rounded-full text-amber-600 shadow-sm">
              <AppIcon name="pill" :size="18" />
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-800 mb-1">
                {{ pet.nextVaccine.isOverdue ? 'Vacuna vencida' : 'Próxima vacuna' }}
              </h4>
              <p class="text-sm text-slate-500">
                {{ pet.nextVaccine.vaccineName }} — {{ formatDate(pet.nextVaccine.nextDueDate) }}
              </p>
            </div>
          </div>
        </aside>

        <!-- Tabs & content -->
        <section class="lg:col-span-8 flex flex-col">
          <div class="w-full border-b border-slate-200 mb-6 flex gap-2">
            <button
              class="px-5 py-3 text-sm font-semibold border-b-2 transition"
              :class="
                activeTab === 'historial'
                  ? 'text-emerald-700 border-emerald-700'
                  : 'text-slate-500 border-transparent hover:text-emerald-700'
              "
              @click="activeTab = 'historial'"
            >
              Historial Clínico
            </button>
            <button
              class="px-5 py-3 text-sm font-semibold border-b-2 transition"
              :class="
                activeTab === 'vacunas'
                  ? 'text-emerald-700 border-emerald-700'
                  : 'text-slate-500 border-transparent hover:text-emerald-700'
              "
              @click="activeTab = 'vacunas'"
            >
              Vacunas
            </button>
            <button
              class="px-5 py-3 text-sm font-semibold border-b-2 transition"
              :class="
                activeTab === 'citas'
                  ? 'text-emerald-700 border-emerald-700'
                  : 'text-slate-500 border-transparent hover:text-emerald-700'
              "
              @click="activeTab = 'citas'"
            >
              Citas
            </button>
          </div>

          <!-- Historial Clínico -->
          <div v-if="activeTab === 'historial'" class="flex flex-col gap-5">
            <div
              v-if="medicalRecords.length === 0"
              class="bg-white border border-slate-200 rounded-2xl p-10 text-center"
            >
              <AppIcon name="clipboard" :size="28" class="text-slate-300 mx-auto mb-3" />
              <p class="text-sm text-slate-500">Aún no hay registros médicos para esta mascota.</p>
            </div>

            <article
              v-for="record in medicalRecords"
              :key="record.id"
              class="bg-white rounded-2xl p-6 md:p-7 border border-slate-200 relative overflow-hidden"
            >
              <div class="absolute left-0 top-0 bottom-0 w-1 bg-emerald-700"></div>

              <div class="flex flex-col md:flex-row md:justify-between md:items-start gap-4 mb-5">
                <div>
                  <div
                    class="inline-flex items-center gap-1.5 bg-slate-50 rounded-full px-3 py-1 mb-3 border border-slate-100"
                  >
                    <AppIcon name="calendar" :size="12" class="text-slate-400" />
                    <span class="text-xs font-medium text-slate-500">
                      {{ formatDateTime(record.visitDate) }}
                    </span>
                  </div>
                  <div v-if="record.veterinarianName" class="flex items-center gap-2.5">
                    <div
                      class="w-9 h-9 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center text-xs font-bold flex-shrink-0"
                    >
                      {{ initials(record.veterinarianName) }}
                    </div>
                    <div>
                      <p class="text-xs text-slate-400">Atendido por</p>
                      <p class="text-sm font-semibold text-emerald-700">
                        {{ record.veterinarianName }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                <div v-if="record.symptoms" class="flex flex-col gap-1.5">
                  <h4
                    class="text-xs font-semibold text-slate-400 uppercase flex items-center gap-1.5"
                  >
                    <AppIcon name="stethoscope" :size="14" />
                    Síntomas
                  </h4>
                  <p class="text-sm text-slate-700">{{ record.symptoms }}</p>
                </div>
                <div v-if="record.diagnosis" class="flex flex-col gap-1.5">
                  <h4
                    class="text-xs font-semibold text-slate-400 uppercase flex items-center gap-1.5"
                  >
                    <AppIcon name="heart" :size="14" />
                    Diagnóstico
                  </h4>
                  <p class="text-sm font-medium text-slate-800">{{ record.diagnosis }}</p>
                </div>
                <div
                  v-if="record.treatment || record.observations"
                  class="md:col-span-2 bg-slate-50 rounded-lg p-4 mt-1"
                >
                  <h4
                    class="text-xs font-semibold text-emerald-700 uppercase flex items-center gap-1.5 mb-2"
                  >
                    <AppIcon name="pill" :size="14" />
                    Tratamiento y observaciones
                  </h4>
                  <p class="text-sm text-slate-700">
                    {{ [record.treatment, record.observations].filter(Boolean).join(' — ') }}
                  </p>
                </div>
              </div>
            </article>
          </div>

          <!-- Vacunas -->
          <div v-else-if="activeTab === 'vacunas'" class="flex flex-col gap-4">
            <div
              v-if="vaccinations.length === 0"
              class="bg-white border border-slate-200 rounded-2xl p-10 text-center"
            >
              <AppIcon name="pill" :size="28" class="text-slate-300 mx-auto mb-3" />
              <p class="text-sm text-slate-500">Aún no hay vacunas registradas para esta mascota.</p>
            </div>

            <div
              v-for="v in vaccinations"
              :key="v.id"
              class="bg-white rounded-2xl p-5 border border-slate-200 flex items-center justify-between gap-4"
            >
              <div>
                <p class="text-sm font-bold text-slate-800">{{ v.vaccineName }}</p>
                <p class="text-xs text-slate-500 mt-1">
                  Aplicada: {{ formatDate(v.applicationDate) }}
                  <span v-if="v.veterinarianName"> • {{ v.veterinarianName }}</span>
                </p>
                <p v-if="v.notes" class="text-xs text-slate-500 mt-1">{{ v.notes }}</p>
              </div>
              <div v-if="v.nextDueDate" class="text-right flex-shrink-0">
                <p class="text-[10px] font-semibold text-slate-400 uppercase">Próxima dosis</p>
                <p class="text-sm font-semibold text-slate-700">{{ formatDate(v.nextDueDate) }}</p>
              </div>
            </div>
          </div>

          <!-- Citas -->
          <div v-else class="flex flex-col gap-4">
            <div
              v-if="appointments.length === 0"
              class="bg-white border border-slate-200 rounded-2xl p-10 text-center"
            >
              <AppIcon name="calendar" :size="28" class="text-slate-300 mx-auto mb-3" />
              <p class="text-sm text-slate-500 mb-4">Aún no hay citas para esta mascota.</p>
              <RouterLink
                :to="{ name: 'appointment-calendar', query: { petId: pet.id } }"
                class="text-emerald-700 text-sm font-semibold hover:underline"
              >
                Agendar una cita →
              </RouterLink>
            </div>

            <RouterLink
              v-for="appointment in appointments"
              :key="appointment.id"
              :to="{ name: 'appointment-detail', params: { id: appointment.id } }"
              class="bg-white rounded-2xl p-5 border border-slate-200 flex items-center justify-between gap-4 hover:border-emerald-300 transition"
            >
              <div>
                <p class="text-sm font-bold text-slate-800">{{ appointment.reason }}</p>
                <p class="text-xs text-slate-500 mt-1">
                  {{ formatDateTime(appointment.appointmentDatetime) }}
                  <span v-if="appointment.veterinarianName"> • {{ appointment.veterinarianName }}</span>
                </p>
              </div>
              <span
                class="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide flex-shrink-0"
                :class="APPOINTMENT_STATUS_BADGE[appointment.status]"
              >
                {{ appointment.status }}
              </span>
            </RouterLink>
          </div>
        </section>
      </div>
    </main>

    <Footer />
  </div>
</template>
