<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import DepartmentMunicipalitySelect from '../../../components/ui/DepartmentMunicipalitySelect.vue'
import PetPhoto from '../components/PetPhoto.vue'
import ChangePasswordModal from '../components/ChangePasswordModal.vue'
import { useAuthStore } from '../../../stores/auth'
import { usePetsStore } from '../../../stores/pets'
import { useAppointmentsStore } from '../../../stores/appointments'
import { usePqrsStore } from '../../../stores/pqrs'
import { useToastStore } from '../../../stores/toast'
import api from '../../../lib/api'

const VACCINE_BADGE = {
  al_dia: { label: 'Vacunas al día', class: 'bg-emerald-50 text-emerald-700' },
  pendiente: { label: 'Vacuna pendiente', class: 'bg-red-50 text-red-600' },
  sin_registro: null,
}

const router = useRouter()
const authStore = useAuthStore()
const petsStore = usePetsStore()
const appointmentsStore = useAppointmentsStore()
const pqrsStore = usePqrsStore()
const toastStore = useToastStore()

const profile = ref(null)
const myPqrs = ref([])
const loading = ref(true)
const errorMessage = ref('')

const editingInfo = ref(false)
const savingInfo = ref(false)
const infoError = ref('')
const form = ref({ firstName: '', lastName: '', email: '', phone: '', direccion: '', ciudad: '', departamento: '' })

const showPasswordModal = ref(false)

const photoObjectUrl = ref('')
const photoInput = ref(null)
const uploadingPhoto = ref(false)

async function loadPhoto(url) {
  if (photoObjectUrl.value) {
    URL.revokeObjectURL(photoObjectUrl.value)
    photoObjectUrl.value = ''
  }
  if (!url) return
  try {
    const { data } = await api.get(url, { responseType: 'blob' })
    photoObjectUrl.value = URL.createObjectURL(data)
  } catch {
    photoObjectUrl.value = ''
  }
}

onBeforeUnmount(() => {
  if (photoObjectUrl.value) URL.revokeObjectURL(photoObjectUrl.value)
})

async function onPhotoChange(event) {
  const file = event.target.files[0]
  event.target.value = ''
  if (!file) return

  uploadingPhoto.value = true
  try {
    profile.value = await authStore.uploadPhoto(file)
    await loadPhoto(profile.value.profileImageUrl)
    toastStore.success('Foto de perfil actualizada.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo subir la foto.')
  } finally {
    uploadingPhoto.value = false
  }
}

async function handleRemovePhoto() {
  uploadingPhoto.value = true
  try {
    profile.value = await authStore.removePhoto()
    await loadPhoto(profile.value.profileImageUrl)
    toastStore.success('Foto de perfil eliminada.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo quitar la foto.')
  } finally {
    uploadingPhoto.value = false
  }
}

onMounted(async () => {
  try {
    const [me] = await Promise.all([
      authStore.fetchMe(),
      petsStore.fetchPets(),
      appointmentsStore.fetchAppointments(),
    ])
    profile.value = me
    await loadPhoto(me.profileImageUrl)
    myPqrs.value = await pqrsStore.fetchMine()
  } catch {
    errorMessage.value = 'No se pudo cargar tu perfil.'
  } finally {
    loading.value = false
  }
})

const initials = computed(() => {
  if (!profile.value) return ''
  return `${profile.value.firstName?.[0] || ''}${profile.value.lastName?.[0] || ''}`.toUpperCase()
})

const memberSinceYear = computed(() => {
  if (!profile.value?.createdAt) return null
  return new Date(profile.value.createdAt).getFullYear()
})

const activeAppointmentsCount = computed(
  () => appointmentsStore.appointments.filter((a) => a.status === 'Pendiente' || a.status === 'Confirmada').length
)
const completedAppointmentsCount = computed(
  () => appointmentsStore.appointments.filter((a) => a.status === 'Completada').length
)
const openPqrsCount = computed(
  () => myPqrs.value.filter((p) => p.status === 'Abierto' || p.status === 'En Proceso').length
)

const nextVaccineReminder = computed(() => {
  const upcoming = petsStore.pets
    .filter((p) => p.nextVaccine)
    .map((p) => ({ petName: p.name, ...p.nextVaccine }))
    .sort((a, b) => new Date(a.nextDueDate) - new Date(b.nextDueDate))
  return upcoming[0] || null
})

const daysUntilNextVaccine = computed(() => {
  if (!nextVaccineReminder.value) return null
  const diff = Math.ceil(
    (new Date(nextVaccineReminder.value.nextDueDate) - new Date()) / (1000 * 60 * 60 * 24)
  )
  return diff
})

function startEdit() {
  form.value = {
    firstName: profile.value.firstName || '',
    lastName: profile.value.lastName || '',
    email: profile.value.email || '',
    phone: profile.value.phone || '',
    direccion: profile.value.direccion || '',
    ciudad: profile.value.ciudad || '',
    departamento: profile.value.departamento || '',
  }
  infoError.value = ''
  editingInfo.value = true
}

async function saveInfo() {
  infoError.value = ''
  if (!form.value.firstName || !form.value.lastName || !form.value.email) {
    infoError.value = 'Nombre, apellido y correo son obligatorios.'
    return
  }
  savingInfo.value = true
  try {
    profile.value = await authStore.updateProfile({ ...form.value })
    toastStore.success('Perfil actualizado correctamente.')
    editingInfo.value = false
  } catch (err) {
    infoError.value = err.response?.data?.message || 'No se pudo guardar tu perfil.'
  } finally {
    savingInfo.value = false
  }
}

async function handleLogout() {
  await authStore.logout()
  toastStore.success('Cerrando sesión...')
  setTimeout(() => router.push({ name: 'home' }), 1000)
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-6xl mx-auto px-6 py-8 w-full">
      <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
      <div v-else-if="!profile" class="text-sm text-red-600">{{ errorMessage }}</div>

      <div v-else class="flex flex-col lg:flex-row gap-6 items-start">
        <!-- Main column -->
        <div class="flex-1 bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm w-full">
          <!-- Header -->
          <div class="relative bg-gradient-to-br from-emerald-800 to-emerald-600 px-8 py-8">
            <button
              v-if="!editingInfo"
              type="button"
              class="absolute top-5 right-6 bg-white/15 hover:bg-white/25 border border-white/30 text-white rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors flex items-center gap-1.5 backdrop-blur-sm"
              @click="startEdit"
            >
              <AppIcon name="edit" :size="14" />
              Editar perfil
            </button>

            <div class="flex items-center gap-4">
              <div class="relative flex-shrink-0">
                <div
                  class="relative w-20 h-20 rounded-full bg-white border-4 border-white/40 shadow-md flex items-center justify-center text-2xl font-bold text-emerald-700 cursor-pointer overflow-hidden group"
                  title="Cambiar foto de perfil"
                  @click="photoInput.click()"
                >
                  <img v-if="photoObjectUrl" :src="photoObjectUrl" class="w-full h-full object-cover" alt="" />
                  <span v-else>{{ initials }}</span>
                  <div
                    class="absolute inset-0 bg-slate-900/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                  >
                    <AppIcon v-if="!uploadingPhoto" name="camera" :size="20" class="text-white" />
                    <span v-else class="text-white text-[10px] font-semibold">Subiendo...</span>
                  </div>
                  <input
                    ref="photoInput"
                    type="file"
                    accept="image/jpeg,image/png"
                    class="hidden"
                    @change="onPhotoChange"
                  />
                </div>
                <button
                  v-if="photoObjectUrl"
                  type="button"
                  class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center shadow-md ring-2 ring-white"
                  title="Quitar foto de perfil"
                  :disabled="uploadingPhoto"
                  @click.stop="handleRemovePhoto"
                >
                  <AppIcon name="x" :size="12" />
                </button>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-white tracking-tight mb-1">
                  {{ profile.firstName }} {{ profile.lastName }}
                </h1>
                <div class="flex items-center gap-1.5 text-sm text-white/80 font-medium">
                  <AppIcon name="shield-check" :size="15" />
                  Cliente registrada{{ memberSinceYear ? ` · Desde ${memberSinceYear}` : '' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Body -->
          <div class="p-6 md:p-8">
            <!-- Personal info -->
            <div class="mb-8">
              <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <AppIcon name="user" :size="15" />
                Información personal
              </h2>

              <template v-if="!editingInfo">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
                  <div class="bg-slate-50 border border-slate-100 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Documento</div>
                    <div class="text-sm font-semibold text-slate-800">
                      {{ profile.documentType }} {{ profile.documentNumber }}
                    </div>
                  </div>
                  <div class="bg-slate-50 border border-slate-100 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Nombre completo</div>
                    <div class="text-sm font-semibold text-slate-800">{{ profile.firstName }} {{ profile.lastName }}</div>
                  </div>
                  <div class="bg-slate-50 border border-slate-100 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Teléfono</div>
                    <div class="text-sm font-semibold text-slate-800">{{ profile.phone || '—' }}</div>
                  </div>
                  <div class="bg-slate-50 border border-slate-100 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Correo electrónico</div>
                    <div class="text-sm font-semibold text-slate-800">{{ profile.email }}</div>
                  </div>
                  <div class="bg-slate-50 border border-slate-100 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Departamento</div>
                    <div class="text-sm font-semibold text-slate-800">{{ profile.departamento || '—' }}</div>
                  </div>
                  <div class="bg-slate-50 border border-slate-100 rounded-lg p-3">
                    <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Municipio</div>
                    <div class="text-sm font-semibold text-slate-800">{{ profile.ciudad || '—' }}</div>
                  </div>
                  <div class="bg-slate-50 border border-slate-100 rounded-lg p-3 md:col-span-2">
                    <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Dirección</div>
                    <div class="text-sm font-semibold text-slate-800">{{ profile.direccion || '—' }}</div>
                  </div>
                </div>

                <button
                  type="button"
                  class="flex items-center gap-1.5 text-sm font-semibold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-100 rounded-lg px-4 py-2 transition-colors"
                  @click="showPasswordModal = true"
                >
                  <AppIcon name="shield-check" :size="16" />
                  Cambiar contraseña
                </button>
              </template>

              <form v-else class="space-y-4" @submit.prevent="saveInfo">
                <p v-if="infoError" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ infoError }}</p>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-xs font-semibold text-slate-500 mb-1">Nombre *</label>
                    <input
                      v-model="form.firstName"
                      type="text"
                      required
                      class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-slate-500 mb-1">Apellido *</label>
                    <input
                      v-model="form.lastName"
                      type="text"
                      required
                      class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                    />
                  </div>
                  <div class="sm:col-span-2">
                    <label class="block text-xs font-semibold text-slate-500 mb-1">Correo electrónico *</label>
                    <input
                      v-model="form.email"
                      type="email"
                      required
                      class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                    />
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-slate-500 mb-1">Teléfono</label>
                    <input
                      v-model="form.phone"
                      type="text"
                      class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                    />
                  </div>
                  <div class="sm:col-span-2">
                    <DepartmentMunicipalitySelect
                      :departamento="form.departamento"
                      :municipio="form.ciudad"
                      @update:departamento="form.departamento = $event"
                      @update:municipio="form.ciudad = $event"
                    />
                  </div>
                  <div class="sm:col-span-2">
                    <label class="block text-xs font-semibold text-slate-500 mb-1">Dirección</label>
                    <input
                      v-model="form.direccion"
                      type="text"
                      class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                    />
                  </div>
                </div>

                <div class="flex justify-end gap-3 pt-2">
                  <button
                    type="button"
                    class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
                    @click="editingInfo = false"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    :disabled="savingInfo"
                    class="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-sm font-semibold rounded-lg transition disabled:opacity-50"
                  >
                    {{ savingInfo ? 'Guardando...' : 'Guardar cambios' }}
                  </button>
                </div>
              </form>
            </div>

            <hr class="border-slate-100 mb-8" />

            <!-- Pets -->
            <div>
              <h2 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <AppIcon name="paw" :size="15" />
                Mis mascotas
              </h2>

              <p v-if="!petsStore.pets.length" class="text-sm text-slate-500 mb-4">
                Todavía no has registrado ninguna mascota.
              </p>

              <div v-else class="flex flex-col gap-3 mb-4">
                <div
                  v-for="pet in petsStore.pets"
                  :key="pet.id"
                  class="flex items-center gap-4 bg-white border border-slate-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div class="w-12 h-12 rounded-lg overflow-hidden bg-emerald-50 flex-shrink-0">
                    <PetPhoto :photo-url="pet.photoUrl" :icon-size="22" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-0.5">
                      <h3 class="text-sm font-bold text-slate-900 truncate">{{ pet.name }}</h3>
                      <span
                        v-if="VACCINE_BADGE[pet.vaccineStatus]"
                        class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold"
                        :class="VACCINE_BADGE[pet.vaccineStatus].class"
                      >
                        {{ VACCINE_BADGE[pet.vaccineStatus].label }}
                      </span>
                    </div>
                    <p class="text-xs text-slate-500 truncate">
                      {{ pet.species?.name || 'Mascota' }} · {{ pet.breed?.name || 'Sin raza registrada' }} ·
                      {{ pet.gender }} · {{ pet.age !== null ? `${pet.age} años` : 'Edad desconocida' }}
                    </p>
                  </div>
                  <div class="flex gap-2 flex-shrink-0">
                    <RouterLink
                      :to="{ name: 'pet-detail', params: { id: pet.id } }"
                      class="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-md transition-colors"
                    >
                      Historial
                    </RouterLink>
                    <RouterLink
                      :to="{ name: 'pet-edit', params: { id: pet.id } }"
                      class="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-md transition-colors"
                    >
                      Editar
                    </RouterLink>
                  </div>
                </div>
              </div>

              <RouterLink
                to="/mis-mascotas/nueva"
                class="inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-700 hover:text-emerald-800 transition-colors"
              >
                <AppIcon name="plus" :size="16" />
                Agregar mascota
              </RouterLink>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="w-full lg:w-72 flex flex-col gap-4 flex-shrink-0">
          <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <h3 class="text-sm font-bold text-slate-900 mb-4">Acceso rápido</h3>
            <div class="flex flex-col">
              <RouterLink
                :to="{ name: 'my-appointments' }"
                class="flex items-center gap-3 py-2.5 border-b border-slate-100 group"
              >
                <div class="w-8 h-8 rounded-lg bg-sky-50 text-sky-700 flex items-center justify-center">
                  <AppIcon name="calendar" :size="16" />
                </div>
                <span class="text-sm font-medium text-slate-800 flex-1">Mis citas</span>
                <span class="text-xs text-slate-500">{{ activeAppointmentsCount }} activa{{ activeAppointmentsCount === 1 ? '' : 's' }}</span>
              </RouterLink>
              <RouterLink
                :to="{ name: 'notifications' }"
                class="flex items-center gap-3 py-2.5 group"
              >
                <div class="w-8 h-8 rounded-lg bg-pink-50 text-pink-700 flex items-center justify-center">
                  <AppIcon name="message-circle" :size="16" />
                </div>
                <span class="text-sm font-medium text-slate-800 flex-1">Mis PQRS</span>
                <span class="text-xs text-slate-500">{{ openPqrsCount }} abierta{{ openPqrsCount === 1 ? '' : 's' }}</span>
              </RouterLink>
            </div>
          </div>

          <div class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <h3 class="text-sm font-bold text-slate-900 mb-4">Resumen de cuenta</h3>
            <div class="flex flex-col gap-3">
              <div class="flex justify-between items-center text-sm">
                <span class="text-slate-500">Estado</span>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700">
                  <AppIcon name="check" :size="10" /> Activa
                </span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-slate-500">Mascotas registradas</span>
                <span class="font-semibold text-slate-800">{{ petsStore.pets.length }}</span>
              </div>
              <div class="flex justify-between items-center text-sm" :class="nextVaccineReminder ? 'border-b border-slate-100 pb-3' : ''">
                <span class="text-slate-500">Citas realizadas</span>
                <span class="font-semibold text-slate-800">{{ completedAppointmentsCount }}</span>
              </div>
              <div v-if="nextVaccineReminder" class="flex justify-between items-center text-sm pt-1">
                <span class="text-slate-500 font-medium truncate pr-2">Próx. vacuna {{ nextVaccineReminder.petName }}</span>
                <span
                  class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold whitespace-nowrap"
                  :class="daysUntilNextVaccine < 0 ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-700'"
                >
                  {{ daysUntilNextVaccine < 0 ? 'Vencida' : `${daysUntilNextVaccine} días` }}
                </span>
              </div>
            </div>
          </div>

          <button
            type="button"
            class="w-full flex items-center justify-center gap-2 bg-red-50 hover:bg-red-100 border border-red-100 text-red-600 font-semibold text-sm py-3 rounded-xl transition-colors shadow-sm"
            @click="handleLogout"
          >
            <AppIcon name="log-out" :size="16" />
            Cerrar sesión
          </button>
        </div>
      </div>
    </main>

    <Footer />

    <ChangePasswordModal :open="showPasswordModal" @close="showPasswordModal = false" />
  </div>
</template>
