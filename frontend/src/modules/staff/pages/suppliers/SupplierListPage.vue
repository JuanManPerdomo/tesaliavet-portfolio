<script setup>
import { ref, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import SupplierFormModal from './SupplierFormModal.vue'
import AdminPagination from '../../components/AdminPagination.vue'
import { useSuppliersStore } from '../../../../stores/suppliers'
import { useToastStore } from '../../../../stores/toast'

const STATUS_OPTIONS = [
  { value: 'active', label: 'Activos' },
  { value: 'inactive', label: 'Inactivos' },
  { value: 'all', label: 'Todos' },
]

const suppliersStore = useSuppliersStore()
const toastStore = useToastStore()

const search = ref('')
const statusFilter = ref('active')
const perPage = ref(10)

const showForm = ref(false)
const editingSupplier = ref(null)
const saving = ref(false)
const formError = ref('')

const deactivatingId = ref(null)
const showDeactivateConfirm = ref(false)
const deactivating = ref(false)

const deletingId = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

const activatingId = ref(null)

function load(page = 1) {
  suppliersStore.fetchSuppliers({
    search: search.value,
    status: statusFilter.value,
    page,
    perPage: perPage.value,
  })
}

onMounted(() => load())

function handleSearch() {
  load(1)
}

function handlePageChange(page) {
  load(page)
}

function handlePageSizeChange(size) {
  perPage.value = size
  load(1)
}

function openCreate() {
  editingSupplier.value = null
  formError.value = ''
  showForm.value = true
}

function openEdit(supplier) {
  editingSupplier.value = supplier
  formError.value = ''
  showForm.value = true
}

async function handleFormSubmit(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editingSupplier.value) {
      await suppliersStore.updateSupplier(editingSupplier.value.id, payload)
      toastStore.success('Proveedor actualizado.')
    } else {
      await suppliersStore.createSupplier(payload)
      toastStore.success('Proveedor creado.')
    }
    showForm.value = false
    load(suppliersStore.pagination.page)
  } catch (err) {
    formError.value = err.response?.data?.message || 'No se pudo guardar el proveedor.'
  } finally {
    saving.value = false
  }
}

function askDeactivate(id) {
  deactivatingId.value = id
  showDeactivateConfirm.value = true
}

async function confirmDeactivate() {
  deactivating.value = true
  try {
    await suppliersStore.deactivateSupplier(deactivatingId.value)
    toastStore.success('Proveedor desactivado.')
    showDeactivateConfirm.value = false
    load(suppliersStore.pagination.page)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo desactivar el proveedor.')
  } finally {
    deactivating.value = false
  }
}

async function handleActivate(id) {
  activatingId.value = id
  try {
    await suppliersStore.reactivateSupplier(id)
    toastStore.success('Proveedor activado.')
    load(suppliersStore.pagination.page)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo activar el proveedor.')
  } finally {
    activatingId.value = null
  }
}

function askDelete(id) {
  deletingId.value = id
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  deleting.value = true
  try {
    await suppliersStore.deleteSupplier(deletingId.value)
    toastStore.success('Proveedor eliminado permanentemente.')
    showDeleteConfirm.value = false
    load(1)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar el proveedor.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900">Proveedores</h1>
        <p class="text-sm text-slate-500 mt-1">Proveedores registrados para el abastecimiento de productos.</p>
      </div>
      <PrimaryButton class="gap-2" @click="openCreate">
        <AppIcon name="plus" :size="16" />
        Nuevo proveedor
      </PrimaryButton>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nombre o documento..."
        class="flex-1 min-w-[220px] border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @keyup.enter="handleSearch"
      />
      <select
        v-model="statusFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
        @change="handleSearch"
      >
        <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <button
        class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
        @click="handleSearch"
      >
        Buscar
      </button>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="suppliersStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="suppliersStore.error" class="p-8 text-sm text-red-600">{{ suppliersStore.error }}</div>
      <div v-else-if="!suppliersStore.suppliers.length" class="p-8 text-sm text-slate-500 text-center">
        No hay proveedores con estos filtros.
      </div>
      <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <div v-for="supplier in suppliersStore.suppliers" :key="supplier.id" class="p-4">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="font-semibold text-slate-800 truncate">{{ supplier.name }}</p>
              <p class="text-xs text-slate-400">
                <span v-if="supplier.documentNumber">{{ supplier.documentType }} {{ supplier.documentNumber }}</span>
                <span v-else>Sin documento</span>
              </p>
            </div>
            <span
              class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold"
              :class="supplier.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            >
              {{ supplier.isActive ? 'Activo' : 'Inactivo' }}
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-1">{{ supplier.contactName || '—' }}</p>
          <p v-if="supplier.contactPhone || supplier.contactEmail" class="text-xs text-slate-400">
            {{ supplier.contactPhone }}<span v-if="supplier.contactPhone && supplier.contactEmail"> · </span>{{ supplier.contactEmail }}
          </p>
          <p class="text-xs text-slate-500 mt-1">{{ supplier.city || '—' }}</p>

          <div class="flex gap-2 mt-3">
            <RouterLink
              :to="{ name: 'staff-supplier-detail', params: { id: supplier.id } }"
              class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
              title="Ver detalle"
            >
              <AppIcon name="eye" :size="14" />
            </RouterLink>

            <template v-if="supplier.isActive">
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                title="Editar"
                @click="openEdit(supplier)"
              >
                <AppIcon name="edit" :size="14" />
              </button>
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                title="Desactivar"
                @click="askDeactivate(supplier.id)"
              >
                <AppIcon name="archive" :size="14" />
              </button>
            </template>

            <template v-else>
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                title="Activar"
                :disabled="activatingId === supplier.id"
                @click="handleActivate(supplier.id)"
              >
                <AppIcon name="refresh" :size="14" />
              </button>
              <button
                class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                title="Eliminar permanentemente"
                @click="askDelete(supplier.id)"
              >
                <AppIcon name="x" :size="14" />
              </button>
            </template>
          </div>
        </div>
      </div>

      <table v-if="suppliersStore.suppliers.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Nombre</th>
            <th class="px-5 py-3">Documento</th>
            <th class="px-5 py-3">Contacto</th>
            <th class="px-5 py-3">Ciudad</th>
            <th class="px-5 py-3">Estado</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="supplier in suppliersStore.suppliers"
            :key="supplier.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
          >
            <td class="px-5 py-3 font-semibold text-slate-800">{{ supplier.name }}</td>
            <td class="px-5 py-3 text-slate-500">
              <span v-if="supplier.documentNumber">{{ supplier.documentType }} {{ supplier.documentNumber }}</span>
              <span v-else>—</span>
            </td>
            <td class="px-5 py-3 text-slate-500">
              <div>{{ supplier.contactName || '—' }}</div>
              <div v-if="supplier.contactPhone || supplier.contactEmail" class="text-xs text-slate-400">
                {{ supplier.contactPhone }}<span v-if="supplier.contactPhone && supplier.contactEmail"> · </span>{{ supplier.contactEmail }}
              </div>
            </td>
            <td class="px-5 py-3 text-slate-500">{{ supplier.city || '—' }}</td>
            <td class="px-5 py-3">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-bold"
                :class="supplier.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ supplier.isActive ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3">
              <div class="flex justify-end gap-2">
                <RouterLink
                  :to="{ name: 'staff-supplier-detail', params: { id: supplier.id } }"
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Ver detalle"
                >
                  <AppIcon name="eye" :size="14" />
                </RouterLink>

                <template v-if="supplier.isActive">
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                    title="Editar"
                    @click="openEdit(supplier)"
                  >
                    <AppIcon name="edit" :size="14" />
                  </button>
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                    title="Desactivar"
                    @click="askDeactivate(supplier.id)"
                  >
                    <AppIcon name="archive" :size="14" />
                  </button>
                </template>

                <template v-else>
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                    title="Activar"
                    :disabled="activatingId === supplier.id"
                    @click="handleActivate(supplier.id)"
                  >
                    <AppIcon name="refresh" :size="14" />
                  </button>
                  <button
                    class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                    title="Eliminar permanentemente"
                    @click="askDelete(supplier.id)"
                  >
                    <AppIcon name="x" :size="14" />
                  </button>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminPagination
      :pagination="suppliersStore.pagination"
      item-label="proveedores"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />

    <SupplierFormModal
      :open="showForm"
      :supplier="editingSupplier"
      :saving="saving"
      :server-error="formError"
      @close="showForm = false"
      @submit="handleFormSubmit"
    />

    <ConfirmDialog
      :open="showDeactivateConfirm"
      title="Desactivar proveedor"
      message="El proveedor dejará de aparecer como opción al asignarlo a productos. Podrás reactivarlo cuando quieras."
      confirm-label="Sí, desactivar"
      :loading="deactivating"
      @cancel="showDeactivateConfirm = false"
      @confirm="confirmDeactivate"
    />

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar proveedor permanentemente"
      message="Esta acción no se puede deshacer: el proveedor se borrará por completo de la base de datos."
      confirm-label="Sí, eliminar para siempre"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
