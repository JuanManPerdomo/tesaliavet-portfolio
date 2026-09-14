<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import CategoryFormModal from './CategoryFormModal.vue'
import { useCategoriesStore } from '../../../../stores/categories'
import { useToastStore } from '../../../../stores/toast'

const STATUS_OPTIONS = [
  { value: 'active', label: 'Activas' },
  { value: 'inactive', label: 'Inactivas' },
  { value: 'all', label: 'Todas' },
]

const categoriesStore = useCategoriesStore()
const toastStore = useToastStore()

const statusFilter = ref('active')

const showForm = ref(false)
const editingCategory = ref(null)
const saving = ref(false)
const formError = ref('')

const deactivatingId = ref(null)
const showDeactivateConfirm = ref(false)
const deactivating = ref(false)

const deletingId = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

const activatingId = ref(null)

// El filtro de estado se aplica acá, no en la request al backend (ver
// stores/categories.js) - un padre se muestra si el o alguna de sus hijas
// coincide con el filtro, para no dejar huerfana una subcategoria inactiva
// cuyo padre esta activo.
function matchesStatus(category) {
  if (statusFilter.value === 'all') return true
  return statusFilter.value === 'active' ? category.isActive : !category.isActive
}

const tree = computed(() =>
  categoriesStore
    .topLevel()
    .map((parent) => ({
      ...parent,
      children: categoriesStore.childrenOf(parent.id).filter(matchesStatus),
    }))
    .filter((parent) => matchesStatus(parent) || parent.children.length > 0)
)

const parentOptions = computed(() =>
  categoriesStore.categories.filter(
    (c) => !c.parentId && c.isActive && c.id !== editingCategory.value?.id
  )
)

function load() {
  categoriesStore.fetchCategories()
}

onMounted(load)

function openCreate() {
  editingCategory.value = null
  formError.value = ''
  showForm.value = true
}

function openEdit(category) {
  editingCategory.value = category
  formError.value = ''
  showForm.value = true
}

async function handleFormSubmit(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editingCategory.value) {
      await categoriesStore.updateCategory(editingCategory.value.id, payload)
      toastStore.success('Categoría actualizada.')
    } else {
      await categoriesStore.createCategory(payload)
      toastStore.success('Categoría creada.')
    }
    showForm.value = false
    load()
  } catch (err) {
    formError.value = err.response?.data?.message || 'No se pudo guardar la categoría.'
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
    await categoriesStore.deactivateCategory(deactivatingId.value)
    toastStore.success('Categoría desactivada.')
    showDeactivateConfirm.value = false
    load()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo desactivar la categoría.')
  } finally {
    deactivating.value = false
  }
}

async function handleActivate(id) {
  activatingId.value = id
  try {
    await categoriesStore.reactivateCategory(id)
    toastStore.success('Categoría activada.')
    load()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo activar la categoría.')
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
    await categoriesStore.deleteCategory(deletingId.value)
    toastStore.success('Categoría eliminada permanentemente.')
    showDeleteConfirm.value = false
    load()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar la categoría.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900">Categorías</h1>
        <p class="text-sm text-slate-500 mt-1">Categorías y subcategorías del catálogo de productos.</p>
      </div>
      <PrimaryButton class="gap-2" @click="openCreate">
        <AppIcon name="plus" :size="16" />
        Nueva categoría
      </PrimaryButton>
    </div>

    <div class="mb-4 flex flex-wrap gap-2">
      <select
        v-model="statusFilter"
        class="border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
      >
        <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
    </div>

    <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
      <div v-if="categoriesStore.loading" class="p-8 text-sm text-slate-500">Cargando...</div>
      <div v-else-if="categoriesStore.error" class="p-8 text-sm text-red-600">{{ categoriesStore.error }}</div>
      <div v-else-if="!tree.length" class="p-8 text-sm text-slate-500 text-center">
        No hay categorías con estos filtros.
      </div>
      <!-- RF48: en pantallas chicas el arbol se vuelve una lista de tarjetas -->
      <div v-else class="md:hidden divide-y divide-slate-100">
        <template v-for="parent in tree" :key="parent.id">
          <div class="p-4 bg-slate-50/60">
            <div class="flex items-start justify-between gap-2">
              <p class="font-bold text-slate-800">{{ parent.name }}</p>
              <span
                class="shrink-0 px-2 py-0.5 rounded-full text-[10px] font-bold"
                :class="parent.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
              >
                {{ parent.isActive ? 'Activa' : 'Inactiva' }}
              </span>
            </div>
            <p class="text-xs text-slate-500 mt-1">{{ parent.description || 'Sin descripción' }}</p>
            <div class="flex gap-2 mt-3">
              <template v-if="parent.isActive">
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Editar"
                  @click="openEdit(parent)"
                >
                  <AppIcon name="edit" :size="14" />
                </button>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                  title="Desactivar"
                  @click="askDeactivate(parent.id)"
                >
                  <AppIcon name="archive" :size="14" />
                </button>
              </template>
              <template v-else>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                  title="Activar"
                  :disabled="activatingId === parent.id"
                  @click="handleActivate(parent.id)"
                >
                  <AppIcon name="refresh" :size="14" />
                </button>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                  title="Eliminar permanentemente"
                  @click="askDelete(parent.id)"
                >
                  <AppIcon name="x" :size="14" />
                </button>
              </template>
            </div>
          </div>

          <div v-for="child in parent.children" :key="child.id" class="p-4 pl-8">
            <div class="flex items-start justify-between gap-2">
              <p class="font-semibold text-slate-700">{{ child.name }}</p>
              <div class="flex shrink-0 gap-1.5">
                <span
                  v-if="child.isPharmacy"
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700"
                >
                  Farmacia
                </span>
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                  :class="child.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                >
                  {{ child.isActive ? 'Activa' : 'Inactiva' }}
                </span>
              </div>
            </div>
            <p class="text-xs text-slate-500 mt-1">{{ child.description || 'Sin descripción' }}</p>
            <div class="flex gap-2 mt-3">
              <template v-if="child.isActive">
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Editar"
                  @click="openEdit(child)"
                >
                  <AppIcon name="edit" :size="14" />
                </button>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                  title="Desactivar"
                  @click="askDeactivate(child.id)"
                >
                  <AppIcon name="archive" :size="14" />
                </button>
              </template>
              <template v-else>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                  title="Activar"
                  :disabled="activatingId === child.id"
                  @click="handleActivate(child.id)"
                >
                  <AppIcon name="refresh" :size="14" />
                </button>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                  title="Eliminar permanentemente"
                  @click="askDelete(child.id)"
                >
                  <AppIcon name="x" :size="14" />
                </button>
              </template>
            </div>
          </div>
        </template>
      </div>

      <table v-if="tree.length" class="hidden md:table w-full text-sm">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
            <th class="px-5 py-3">Nombre</th>
            <th class="px-5 py-3">Descripción</th>
            <th class="px-5 py-3">Estado</th>
            <th class="px-5 py-3 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="parent in tree" :key="parent.id">
            <tr class="border-b border-slate-100 bg-slate-50/60 hover:bg-slate-50">
              <td class="px-5 py-3 font-bold text-slate-800">{{ parent.name }}</td>
              <td class="px-5 py-3 text-slate-500">{{ parent.description || '—' }}</td>
              <td class="px-5 py-3">
                <span
                  class="px-2 py-0.5 rounded-full text-xs font-bold"
                  :class="parent.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                >
                  {{ parent.isActive ? 'Activa' : 'Inactiva' }}
                </span>
              </td>
              <td class="px-5 py-3">
                <div class="flex justify-end gap-2">
                  <template v-if="parent.isActive">
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                      title="Editar"
                      @click="openEdit(parent)"
                    >
                      <AppIcon name="edit" :size="14" />
                    </button>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                      title="Desactivar"
                      @click="askDeactivate(parent.id)"
                    >
                      <AppIcon name="archive" :size="14" />
                    </button>
                  </template>
                  <template v-else>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                      title="Activar"
                      :disabled="activatingId === parent.id"
                      @click="handleActivate(parent.id)"
                    >
                      <AppIcon name="refresh" :size="14" />
                    </button>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                      title="Eliminar permanentemente"
                      @click="askDelete(parent.id)"
                    >
                      <AppIcon name="x" :size="14" />
                    </button>
                  </template>
                </div>
              </td>
            </tr>

            <tr v-for="child in parent.children" :key="child.id" class="border-b border-slate-50 last:border-0">
              <td class="px-5 py-2.5 pl-10 text-slate-700">{{ child.name }}</td>
              <td class="px-5 py-2.5 text-slate-500">{{ child.description || '—' }}</td>
              <td class="px-5 py-2.5">
                <div class="flex gap-1.5">
                  <span
                    v-if="child.isPharmacy"
                    class="px-2 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700"
                  >
                    Farmacia
                  </span>
                  <span
                    class="px-2 py-0.5 rounded-full text-xs font-bold"
                    :class="child.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                  >
                    {{ child.isActive ? 'Activa' : 'Inactiva' }}
                  </span>
                </div>
              </td>
              <td class="px-5 py-2.5">
                <div class="flex justify-end gap-2">
                  <template v-if="child.isActive">
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                      title="Editar"
                      @click="openEdit(child)"
                    >
                      <AppIcon name="edit" :size="14" />
                    </button>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-amber-600 hover:border-amber-300"
                      title="Desactivar"
                      @click="askDeactivate(child.id)"
                    >
                      <AppIcon name="archive" :size="14" />
                    </button>
                  </template>
                  <template v-else>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700 disabled:opacity-50"
                      title="Activar"
                      :disabled="activatingId === child.id"
                      @click="handleActivate(child.id)"
                    >
                      <AppIcon name="refresh" :size="14" />
                    </button>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                      title="Eliminar permanentemente"
                      @click="askDelete(child.id)"
                    >
                      <AppIcon name="x" :size="14" />
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <CategoryFormModal
      :open="showForm"
      :category="editingCategory"
      :parent-options="parentOptions"
      :saving="saving"
      :server-error="formError"
      @close="showForm = false"
      @submit="handleFormSubmit"
    />

    <ConfirmDialog
      :open="showDeactivateConfirm"
      title="Desactivar categoría"
      message="La categoría dejará de aparecer como opción al asignarla a productos. Podrás reactivarla cuando quieras."
      confirm-label="Sí, desactivar"
      :loading="deactivating"
      @cancel="showDeactivateConfirm = false"
      @confirm="confirmDeactivate"
    />

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar categoría permanentemente"
      message="Esta acción no se puede deshacer: la categoría se borrará por completo de la base de datos."
      confirm-label="Sí, eliminar para siempre"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
