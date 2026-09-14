<script setup>
import { ref, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import VaccineFormModal from './VaccineFormModal.vue'
import { useStaffVaccinesStore } from '../../../../stores/staffVaccines'
import { useToastStore } from '../../../../stores/toast'

const vaccinesStore = useStaffVaccinesStore()
const toastStore = useToastStore()

const showForm = ref(false)
const editingVaccine = ref(null)
const saving = ref(false)
const formError = ref('')

const deletingId = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

onMounted(() => vaccinesStore.fetchVaccines())

function openCreate() {
  editingVaccine.value = null
  formError.value = ''
  showForm.value = true
}

function openEdit(vaccine) {
  editingVaccine.value = vaccine
  formError.value = ''
  showForm.value = true
}

async function handleFormSubmit(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editingVaccine.value) {
      await vaccinesStore.updateVaccine(editingVaccine.value.id, payload)
      toastStore.success('Vacuna actualizada.')
    } else {
      await vaccinesStore.createVaccine(payload)
      toastStore.success('Vacuna creada.')
    }
    showForm.value = false
    vaccinesStore.fetchVaccines()
  } catch (err) {
    formError.value = err.response?.data?.message || 'No se pudo guardar la vacuna.'
  } finally {
    saving.value = false
  }
}

function askDelete(id) {
  deletingId.value = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await vaccinesStore.deleteVaccine(deletingId.value)
    toastStore.success('Vacuna eliminada.')
    showDeleteConfirm.value = false
    vaccinesStore.fetchVaccines()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar la vacuna.')
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900">Catálogo de vacunas</h1>
        <p class="text-sm text-slate-500 mt-1">Tipos de vacuna disponibles al registrar una aplicación.</p>
      </div>
      <PrimaryButton class="gap-2" @click="openCreate">
        <AppIcon name="plus" :size="16" />
        Nueva vacuna
      </PrimaryButton>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="vaccinesStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="vaccinesStore.error" class="p-8 text-sm text-red-600">{{ vaccinesStore.error }}</div>
      <div v-else-if="!vaccinesStore.vaccines.length" class="p-8 text-sm text-slate-500 text-center">
        No hay vacunas registradas todavía.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="vaccine in vaccinesStore.vaccines" :key="vaccine.id" class="p-4">
          <p class="font-semibold text-slate-800">{{ vaccine.name }}</p>
          <p class="text-xs text-slate-500 mt-1">{{ vaccine.description || 'Sin descripción' }}</p>

          <div class="flex gap-2 mt-3">
            <button
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
              title="Editar"
              @click="openEdit(vaccine)"
            >
              <AppIcon name="edit" :size="14" />
            </button>
            <button
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
              title="Eliminar"
              @click="askDelete(vaccine.id)"
            >
              <AppIcon name="x" :size="14" />
            </button>
          </div>
        </div>
      </div>

      <table v-if="vaccinesStore.vaccines.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Nombre</th>
            <th class="px-5 py-3">Descripción</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="vaccine in vaccinesStore.vaccines"
            :key="vaccine.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3 font-semibold text-slate-800">{{ vaccine.name }}</td>
            <td class="px-5 py-3 text-slate-500">{{ vaccine.description || '—' }}</td>
            <td class="px-5 py-3">
              <div class="flex justify-end gap-2">
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Editar"
                  @click="openEdit(vaccine)"
                >
                  <AppIcon name="edit" :size="14" />
                </button>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                  title="Eliminar"
                  @click="askDelete(vaccine.id)"
                >
                  <AppIcon name="x" :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <VaccineFormModal
      :open="showForm"
      :vaccine="editingVaccine"
      :saving="saving"
      :server-error="formError"
      @close="showForm = false"
      @submit="handleFormSubmit"
    />

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar vacuna"
      message="Esta acción no se puede deshacer. Solo se puede eliminar si ninguna mascota tiene aplicaciones registradas de esta vacuna."
      confirm-label="Sí, eliminar"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
