<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import ConfirmDialog from '../../../../components/ui/ConfirmDialog.vue'
import SpeciesFormModal from './SpeciesFormModal.vue'
import { useStaffSpeciesStore } from '../../../../stores/staffSpecies'
import { useProductsStore } from '../../../../stores/products'
import { useToastStore } from '../../../../stores/toast'

const speciesStore = useStaffSpeciesStore()
const productsStore = useProductsStore()
const toastStore = useToastStore()

const showForm = ref(false)
const editingSpecies = ref(null)
const saving = ref(false)
const formError = ref('')

const deletingId = ref(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

// Insignia por categoria (mismo criterio de colores que otras insignias del
// panel, ej. "Farmacia" en Categorias, decision 74) - emerald para Mascotas
// (ya es el color principal del sitio), ambar para Ganaderia.
const CATEGORY_BADGE = {
  Mascotas: 'bg-emerald-50 text-emerald-700',
  Ganadería: 'bg-amber-50 text-amber-700',
}

onMounted(() => {
  speciesStore.fetchSpecies()
  productsStore.fetchCategories()
})

// Agrupado por categoria (pedido por Juan Manuel: la lista plana se veia
// desordenada) - el orden de los grupos sigue el mismo orden real de
// /catalog/categories (Mascotas/Ganaderia), no alfabetico a ciegas. Las
// especies sin categoria (dato legado - hoy es obligatoria al crear, ver
// decision 94) quedan en un grupo aparte al final, sin inventar una
// categoria que no tienen.
const groupedSpecies = computed(() => {
  const tops = productsStore.topCategories()
  const groups = tops.map((cat) => ({
    id: cat.id,
    name: cat.name,
    items: speciesStore.species.filter((s) => s.categoryId === cat.id),
  }))
  const withoutCategory = speciesStore.species.filter((s) => !s.categoryId)
  if (withoutCategory.length) {
    groups.push({ id: null, name: 'Sin categoría', items: withoutCategory })
  }
  return groups.filter((g) => g.items.length)
})

function openCreate() {
  editingSpecies.value = null
  formError.value = ''
  showForm.value = true
}

function openEdit(item) {
  editingSpecies.value = item
  formError.value = ''
  showForm.value = true
}

async function handleFormSubmit(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editingSpecies.value) {
      await speciesStore.updateSpecies(editingSpecies.value.id, payload)
      toastStore.success('Especie actualizada.')
    } else {
      await speciesStore.createSpecies(payload)
      toastStore.success('Especie creada.')
    }
    showForm.value = false
    speciesStore.fetchSpecies()
  } catch (err) {
    formError.value = err.response?.data?.message || 'No se pudo guardar la especie.'
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
    await speciesStore.deleteSpecies(deletingId.value)
    toastStore.success('Especie eliminada.')
    showDeleteConfirm.value = false
    speciesStore.fetchSpecies()
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo eliminar la especie.')
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
        <h1 class="text-2xl font-extrabold text-slate-900">Especies</h1>
        <p class="text-sm text-slate-500 mt-1">
          Catálogo de especies disponible al registrar una mascota o un producto.
        </p>
      </div>
      <PrimaryButton class="gap-2" @click="openCreate">
        <AppIcon name="plus" :size="16" />
        Nueva especie
      </PrimaryButton>
    </div>

    <div v-if="speciesStore.loading" class="bg-white rounded-2xl border border-slate-200 p-8 text-sm text-slate-500">
      Cargando...
    </div>
    <div
      v-else-if="speciesStore.error"
      class="bg-white rounded-2xl border border-slate-200 p-8 text-sm text-red-600"
    >
      {{ speciesStore.error }}
    </div>
    <div
      v-else-if="!speciesStore.species.length"
      class="bg-white rounded-2xl border border-slate-200 p-8 text-sm text-slate-500 text-center"
    >
      No hay especies registradas todavía.
    </div>

    <div v-else class="space-y-6">
      <div v-for="group in groupedSpecies" :key="group.id ?? 'sin-categoria'">
        <div class="flex items-center gap-2 mb-3">
          <span
            class="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full"
            :class="CATEGORY_BADGE[group.name] || 'bg-slate-100 text-slate-500'"
          >
            {{ group.name }}
          </span>
          <span class="text-xs text-slate-400">{{ group.items.length }} especie{{ group.items.length === 1 ? '' : 's' }}</span>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <!-- RF48: en pantallas chicas la tabla se vuelve una lista de tarjetas -->
          <div class="md:hidden divide-y divide-slate-100">
            <div v-for="item in group.items" :key="item.id" class="p-4 flex items-center justify-between">
              <p class="font-semibold text-slate-800">{{ item.name }}</p>
              <div class="flex gap-2">
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                  title="Editar"
                  @click="openEdit(item)"
                >
                  <AppIcon name="edit" :size="14" />
                </button>
                <button
                  class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                  title="Eliminar"
                  @click="askDelete(item.id)"
                >
                  <AppIcon name="x" :size="14" />
                </button>
              </div>
            </div>
          </div>

          <table class="hidden md:table w-full text-sm">
            <thead>
              <tr class="bg-slate-50 border-b border-slate-200 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                <th class="px-5 py-3">Nombre</th>
                <th class="px-5 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in group.items"
                :key="item.id"
                class="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
              >
                <td class="px-5 py-3 font-semibold text-slate-800">{{ item.name }}</td>
                <td class="px-5 py-3">
                  <div class="flex justify-end gap-2">
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-emerald-700 hover:border-emerald-700"
                      title="Editar"
                      @click="openEdit(item)"
                    >
                      <AppIcon name="edit" :size="14" />
                    </button>
                    <button
                      class="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-500 hover:text-red-600 hover:border-red-300"
                      title="Eliminar"
                      @click="askDelete(item.id)"
                    >
                      <AppIcon name="x" :size="14" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <SpeciesFormModal
      :open="showForm"
      :species="editingSpecies"
      :top-categories="productsStore.topCategories()"
      :saving="saving"
      :server-error="formError"
      @close="showForm = false"
      @submit="handleFormSubmit"
    />

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Eliminar especie"
      message="Esta acción no se puede deshacer. Solo se puede eliminar si ninguna mascota, raza o producto la está usando."
      confirm-label="Sí, eliminar"
      :loading="deleting"
      @cancel="showDeleteConfirm = false"
      @confirm="confirmDelete"
    />
  </div>
</template>
