<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import PetPhoto from '../../../client/components/PetPhoto.vue'
import { useStaffPetsStore } from '../../../../stores/staffPets'
import { useAppointmentsStore } from '../../../../stores/appointments'
import { useAuthStore } from '../../../../stores/auth'
import { useToastStore } from '../../../../stores/toast'
import api from '../../../../lib/api'

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

const route = useRoute()
const router = useRouter()
const petsStore = useStaffPetsStore()
const appointmentsStore = useAppointmentsStore()
const authStore = useAuthStore()
const toastStore = useToastStore()

const petId = computed(() => Number(route.params.id))
const pet = ref(null)
const medicalRecords = ref([])
const vaccinations = ref([])
const loading = ref(true)
const errorMessage = ref('')
const activeTab = ref('historial')

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

async function load() {
  loading.value = true
  try {
    const [petData, records, vaccines] = await Promise.all([
      petsStore.fetchPet(petId.value),
      petsStore.fetchMedicalRecords(petId.value),
      petsStore.fetchVaccinations(petId.value),
      appointmentsStore.fetchStaffAppointments(undefined, false, undefined, petId.value),
    ])
    pet.value = petData
    medicalRecords.value = records
    vaccinations.value = vaccines
  } catch {
    errorMessage.value = 'No se pudo cargar la mascota.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function openAttachment(url) {
  // El endpoint exige JWT, asi que no puede abrirse con un <a href> ni
  // window.open directo (no llevaria el header de auth) - se trae como blob
  // autenticado, mismo patron que PetPhoto.vue.
  const { data } = await api.get(url, { responseType: 'blob' })
  window.open(URL.createObjectURL(data), '_blank')
}

const showDeleteConfirm = ref(false)
const deleting = ref(false)

async function confirmDelete() {
  deleting.value = true
  try {
    await petsStore.deletePet(petId.value)
    toastStore.success('Mascota eliminada permanentemente.')
    router.push({ name: 'staff-pets' })
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar la mascota.')
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="max-w-5xl">
    <RouterLink
      :to="{ name: 'staff-pets' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a mascotas
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <p v-else-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      <!-- Sidebar -->
      <aside class="lg:col-span-4 flex flex-col gap-6 lg:sticky lg:top-24">
        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <div class="relative w-32 h-32 mx-auto rounded-full overflow-hidden mb-4 bg-slate-100">
            <PetPhoto :photo-url="pet.photoUrl" :icon-size="40" />
          </div>

          <div class="mb-5 text-center">
            <h1 class="text-xl font-extrabold text-slate-900 mb-1">{{ pet.name }}</h1>
            <p class="text-sm text-slate-500">{{ pet.breed?.name || pet.species?.name || 'Sin raza registrada' }}</p>
            <span
              v-if="VACCINE_BADGE[pet.vaccineStatus]"
              class="inline-flex items-center gap-1 mt-2 font-bold text-[10px] uppercase tracking-wider px-2.5 py-1 rounded-full"
              :class="VACCINE_BADGE[pet.vaccineStatus].class"
            >
              <AppIcon :name="VACCINE_BADGE[pet.vaccineStatus].icon" :size="11" />
              {{ VACCINE_BADGE[pet.vaccineStatus].label }}
            </span>
          </div>

          <div v-if="authStore.hasRole('admin')" class="flex flex-col gap-2">
            <RouterLink
              :to="{ name: 'staff-pet-edit', params: { id: pet.id } }"
              class="w-full bg-emerald-700 hover:bg-emerald-800 text-white text-sm font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 transition"
            >
              <AppIcon name="edit" :size="16" />
              Editar perfil
            </RouterLink>
            <button
              type="button"
              class="w-full border border-red-200 text-red-600 hover:bg-red-50 text-sm font-semibold py-2.5 rounded-lg flex items-center justify-center gap-2 transition"
              @click="showDeleteConfirm = true"
            >
              <AppIcon name="x" :size="16" />
              Eliminar mascota
            </button>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-4">Detalles del paciente</h2>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-[10px] font-semibold text-slate-400 uppercase mb-1">Edad</p>
              <p class="text-sm font-bold text-slate-800">{{ pet.age !== null ? `${pet.age} años` : '—' }}</p>
            </div>
            <div>
              <p class="text-[10px] font-semibold text-slate-400 uppercase mb-1">Género</p>
              <p class="text-sm font-bold text-slate-800">{{ pet.gender }}</p>
            </div>
            <div>
              <p class="text-[10px] font-semibold text-slate-400 uppercase mb-1">Peso</p>
              <p class="text-sm font-bold text-slate-800">{{ pet.weight !== null ? `${pet.weight} kg` : '—' }}</p>
            </div>
            <div>
              <p class="text-[10px] font-semibold text-slate-400 uppercase mb-1">Color</p>
              <p class="text-sm font-bold text-slate-800">{{ pet.color || '—' }}</p>
            </div>
          </div>

          <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wide mt-6 mb-3">Información del dueño</h2>
          <div v-if="pet.owner" class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
              {{ initials(pet.owner.name) }}
            </div>
            <div class="min-w-0 flex-1">
              <RouterLink
                :to="{ name: 'staff-client-detail', params: { id: pet.owner.id } }"
                class="text-sm font-semibold text-slate-800 hover:text-emerald-700 truncate block"
              >
                {{ pet.owner.name }}
              </RouterLink>
              <p v-if="pet.owner.phone" class="text-xs text-slate-500">{{ pet.owner.phone }}</p>
            </div>
            <a
              v-if="pet.owner.email"
              :href="`mailto:${pet.owner.email}`"
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-400 hover:text-emerald-700 hover:border-emerald-700 flex-shrink-0"
              title="Enviar correo"
            >
              <AppIcon name="mail" :size="14" />
            </a>
          </div>
        </div>
      </aside>

      <!-- Tabs & content -->
      <section class="lg:col-span-8 flex flex-col">
        <div class="w-full border-b border-slate-200 mb-6 flex items-center justify-between flex-wrap gap-3">
          <div class="flex gap-2">
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

          <RouterLink
            v-if="activeTab === 'historial'"
            :to="{ name: 'staff-medical-record-new', params: { petId: pet.id }, query: { petName: pet.name } }"
            class="text-xs font-semibold text-white bg-emerald-700 hover:bg-emerald-800 rounded-lg px-3.5 py-2 flex items-center gap-1.5 mb-2"
          >
            <AppIcon name="plus" :size="14" />
            Nuevo registro médico
          </RouterLink>
          <RouterLink
            v-else-if="activeTab === 'vacunas'"
            :to="{ name: 'staff-vaccination-new', params: { petId: pet.id }, query: { petName: pet.name } }"
            class="text-xs font-semibold text-white bg-emerald-700 hover:bg-emerald-800 rounded-lg px-3.5 py-2 flex items-center gap-1.5 mb-2"
          >
            <AppIcon name="plus" :size="14" />
            Aplicar vacuna
          </RouterLink>
        </div>

        <!-- Historial Clínico -->
        <div v-if="activeTab === 'historial'" class="flex flex-col gap-5">
          <div v-if="medicalRecords.length === 0" class="bg-white border border-slate-200 rounded-2xl p-10 text-center">
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
                <div class="inline-flex items-center gap-1.5 bg-slate-50 rounded-full px-3 py-1 mb-3 border border-slate-100">
                  <AppIcon name="calendar" :size="12" class="text-slate-400" />
                  <span class="text-xs font-medium text-slate-500">{{ formatDateTime(record.visitDate) }}</span>
                </div>
                <div v-if="record.veterinarianName" class="flex items-center gap-2.5">
                  <div class="w-9 h-9 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
                    {{ initials(record.veterinarianName) }}
                  </div>
                  <div>
                    <p class="text-xs text-slate-400">Atendido por</p>
                    <p class="text-sm font-semibold text-emerald-700">{{ record.veterinarianName }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
              <div v-if="record.symptoms" class="flex flex-col gap-1.5">
                <h4 class="text-xs font-semibold text-slate-400 uppercase flex items-center gap-1.5">
                  <AppIcon name="stethoscope" :size="14" />
                  Síntomas
                </h4>
                <p class="text-sm text-slate-700">{{ record.symptoms }}</p>
              </div>
              <div v-if="record.diagnosis" class="flex flex-col gap-1.5">
                <h4 class="text-xs font-semibold text-slate-400 uppercase flex items-center gap-1.5">
                  <AppIcon name="heart" :size="14" />
                  Diagnóstico
                </h4>
                <p class="text-sm font-medium text-slate-800">{{ record.diagnosis }}</p>
              </div>
              <div v-if="record.treatment || record.observations" class="md:col-span-2 bg-slate-50 rounded-lg p-4 mt-1">
                <h4 class="text-xs font-semibold text-emerald-700 uppercase flex items-center gap-1.5 mb-2">
                  <AppIcon name="pill" :size="14" />
                  Tratamiento y observaciones
                </h4>
                <p class="text-sm text-slate-700">
                  {{ [record.treatment, record.observations].filter(Boolean).join(' — ') }}
                </p>
              </div>
              <button
                v-if="record.attachmentUrl"
                type="button"
                class="md:col-span-2 flex items-center gap-2 text-xs font-semibold text-emerald-700 hover:underline w-fit"
                @click="openAttachment(record.attachmentUrl)"
              >
                <AppIcon name="file-text" :size="14" />
                {{ record.attachmentName }}
              </button>
            </div>
          </article>
        </div>

        <!-- Vacunas -->
        <div v-else-if="activeTab === 'vacunas'" class="flex flex-col gap-4">
          <div v-if="vaccinations.length === 0" class="bg-white border border-slate-200 rounded-2xl p-10 text-center">
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
          <div v-if="!appointmentsStore.staffAppointments.length" class="bg-white border border-slate-200 rounded-2xl p-10 text-center">
            <AppIcon name="calendar" :size="28" class="text-slate-300 mx-auto mb-3" />
            <p class="text-sm text-slate-500">Aún no hay citas para esta mascota.</p>
          </div>

          <RouterLink
            v-for="appointment in appointmentsStore.staffAppointments"
            :key="appointment.id"
            :to="{ name: 'staff-appointment-detail', params: { id: appointment.id } }"
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

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar mascota permanentemente"
      :message="`Esta acción no se puede deshacer. Se eliminará a &quot;${pet?.name}&quot; junto con su historial médico, vacunas y citas.`"
      confirm-label="Sí, eliminar para siempre"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
