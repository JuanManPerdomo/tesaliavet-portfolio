<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import ClientAvatar from './ClientAvatar.vue'
import ClientFormModal from './ClientFormModal.vue'
import PetPhoto from '../../../client/components/PetPhoto.vue'
import { useStaffClientsStore } from '../../../../stores/staffClients'
import { useToastStore } from '../../../../stores/toast'

const route = useRoute()
const clientsStore = useStaffClientsStore()
const toastStore = useToastStore()

const clientId = computed(() => Number(route.params.id))
const client = ref(null)
const pets = ref([])
const loading = ref(true)
const errorMessage = ref('')

const showEditForm = ref(false)
const editSaving = ref(false)
const editError = ref('')

const showDeactivateConfirm = ref(false)
const deactivating = ref(false)
const activating = ref(false)

async function load() {
  loading.value = true
  try {
    const [clientData, petsData] = await Promise.all([
      clientsStore.fetchClient(clientId.value),
      clientsStore.fetchClientPets(clientId.value),
    ])
    client.value = clientData
    pets.value = petsData
  } catch {
    errorMessage.value = 'No se pudo cargar el cliente.'
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function handleEditSubmit(payload) {
  editSaving.value = true
  editError.value = ''
  try {
    client.value = await clientsStore.updateClient(clientId.value, payload)
    toastStore.success('Datos del cliente actualizados.')
    showEditForm.value = false
  } catch (err) {
    editError.value = err.response?.data?.message || 'No se pudo guardar el cliente.'
  } finally {
    editSaving.value = false
  }
}

async function confirmDeactivate() {
  deactivating.value = true
  try {
    client.value = await clientsStore.deactivateClient(clientId.value)
    toastStore.success('Cliente desactivado.')
    showDeactivateConfirm.value = false
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo desactivar el cliente.')
  } finally {
    deactivating.value = false
  }
}

async function handleActivate() {
  activating.value = true
  try {
    client.value = await clientsStore.reactivateClient(clientId.value)
    toastStore.success('Cliente activado.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo activar el cliente.')
  } finally {
    activating.value = false
  }
}
</script>

<template>
  <div class="max-w-5xl">
    <RouterLink
      :to="{ name: 'staff-clients' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a clientes
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="!client" class="text-sm text-red-600">{{ errorMessage }}</div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <div class="flex items-center gap-4 mb-4">
              <ClientAvatar :first-name="client.firstName" :last-name="client.lastName" :size="56" />
              <div>
                <h1 class="text-lg font-extrabold text-slate-900">{{ client.firstName }} {{ client.lastName }}</h1>
                <p class="text-xs text-slate-500">{{ client.tipoDocumento }} {{ client.numeroDocumento }}</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                class="text-[11px] font-bold uppercase px-3 py-1 rounded-full"
                :class="client.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ client.isActive ? 'Activo' : 'Inactivo' }}
              </span>
              <span class="text-[11px] font-bold uppercase px-3 py-1 rounded-full bg-sky-50 text-sky-700">
                {{ client.petsCount }} {{ client.petsCount === 1 ? 'Mascota' : 'Mascotas' }}
              </span>
            </div>
          </div>

          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 class="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wide mb-5">
              <AppIcon name="file-text" :size="14" />
              Datos de contacto
            </h2>
            <dl class="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
              <div>
                <dt class="text-xs text-slate-400">Teléfono</dt>
                <dd class="text-slate-800 font-medium">{{ client.phone || '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-400">Correo electrónico</dt>
                <dd class="text-slate-800 font-medium">{{ client.email }}</dd>
              </div>
              <div class="col-span-2">
                <dt class="text-xs text-slate-400">Dirección</dt>
                <dd class="text-slate-800 font-medium">
                  {{ [client.direccion, client.ciudad, client.departamento].filter(Boolean).join(', ') || '—' }}
                </dd>
              </div>
            </dl>
          </div>

          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 class="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wide mb-5">
              <AppIcon name="paw" :size="14" />
              Mascotas registradas
            </h2>
            <p v-if="!pets.length" class="text-sm text-slate-500 text-center py-6">
              Este cliente no tiene mascotas registradas.
            </p>
            <div v-else class="divide-y divide-slate-100">
              <div v-for="pet in pets" :key="pet.id" class="py-3 flex items-center gap-3">
                <div class="w-10 h-10 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
                  <PetPhoto :photo-url="pet.photoUrl" :icon-size="16" />
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-bold text-slate-900 truncate">{{ pet.name }}</p>
                  <p class="text-xs text-slate-500 truncate">
                    {{ pet.species || 'Especie sin definir' }}<span v-if="pet.breed"> · {{ pet.breed }}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <button
            type="button"
            class="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-2"
            @click="showEditForm = true"
          >
            <AppIcon name="edit" :size="16" />
            Editar datos
          </button>

          <RouterLink
            :to="{
              name: 'staff-appointments',
              query: { ownerId: client.id, ownerName: `${client.firstName} ${client.lastName}` },
            }"
            class="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-2"
          >
            <AppIcon name="calendar" :size="16" />
            Ver historial de citas
          </RouterLink>

          <RouterLink
            :to="{
              name: 'staff-orders',
              query: { ownerId: client.id, ownerName: `${client.firstName} ${client.lastName}` },
            }"
            class="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 flex items-center justify-center gap-2"
          >
            <AppIcon name="shopping-bag" :size="16" />
            Ver pedidos
          </RouterLink>

          <button
            v-if="client.isActive"
            type="button"
            class="w-full px-4 py-2.5 border border-red-200 rounded-lg text-sm font-semibold text-red-600 hover:bg-red-50 flex items-center justify-center gap-2"
            @click="showDeactivateConfirm = true"
          >
            <AppIcon name="archive" :size="16" />
            Desactivar cuenta
          </button>
          <button
            v-else
            type="button"
            class="w-full px-4 py-2.5 border border-emerald-200 rounded-lg text-sm font-semibold text-emerald-700 hover:bg-emerald-50 flex items-center justify-center gap-2 disabled:opacity-50"
            :disabled="activating"
            @click="handleActivate"
          >
            <AppIcon name="refresh" :size="16" />
            Activar cuenta
          </button>

          <div class="bg-emerald-50 rounded-2xl p-5">
            <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-3">Resumen del cliente</h3>
            <dl class="space-y-2 text-sm">
              <div class="flex items-center justify-between">
                <dt class="text-slate-500">Citas</dt>
                <dd class="font-semibold text-slate-800">{{ client.appointmentsCount }}</dd>
              </div>
              <div class="flex items-center justify-between">
                <dt class="text-slate-500">Mascotas</dt>
                <dd class="font-semibold text-slate-800">{{ client.petsCount }}</dd>
              </div>
              <div class="flex items-center justify-between">
                <dt class="text-slate-500">Pedidos</dt>
                <dd class="font-semibold text-slate-800">{{ client.ordersCount }}</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <ClientFormModal
        :open="showEditForm"
        :client="client"
        :saving="editSaving"
        :server-error="editError"
        @close="showEditForm = false"
        @submit="handleEditSubmit"
      />

      <ConfirmDialog
        :open="showDeactivateConfirm"
        title="Desactivar cliente"
        message="El cliente no podrá iniciar sesión mientras la cuenta esté desactivada. Podrás reactivarla cuando quieras."
        confirm-label="Sí, desactivar"
        :loading="deactivating"
        @cancel="showDeactivateConfirm = false"
        @confirm="confirmDeactivate"
      />
    </template>
  </div>
</template>
