<script setup>
import { ref, watch } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'

const EMPTY_FORM = { name: '', description: '', parentId: '', isPharmacy: false }

const props = defineProps({
  open: { type: Boolean, default: false },
  category: { type: Object, default: null },
  parentOptions: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
  serverError: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])

const form = ref({ ...EMPTY_FORM })

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    form.value = props.category
      ? {
          name: props.category.name || '',
          description: props.category.description || '',
          parentId: props.category.parentId || '',
          isPharmacy: props.category.isPharmacy || false,
        }
      : { ...EMPTY_FORM }
  }
)

function handleSubmit() {
  emit('submit', { ...form.value })
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('close')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
        <button
          type="button"
          class="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="16" />
        </button>

        <h3 class="text-lg font-bold text-slate-900 mb-4">
          {{ category ? 'Editar categoría' : 'Nueva categoría' }}
        </h3>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <p v-if="serverError" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ serverError }}</p>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Nombre *</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Categoría padre</label>
            <select
              v-model="form.parentId"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
            >
              <option value="">Ninguna (categoría principal)</option>
              <option v-for="parent in parentOptions" :key="parent.id" :value="parent.id">{{ parent.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Descripción</label>
            <textarea
              v-model="form.description"
              rows="2"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            ></textarea>
          </div>

          <label
            v-if="form.parentId"
            class="flex items-start gap-2.5 rounded-lg border border-slate-200 px-3 py-2.5 cursor-pointer hover:border-emerald-700"
          >
            <input v-model="form.isPharmacy" type="checkbox" class="mt-0.5 accent-emerald-700" />
            <span class="text-sm text-slate-700">
              Mostrar en Farmacia Veterinaria
              <span class="block text-xs text-slate-400">
                Aparece en la sección "Cuidado Animal" del sitio público.
              </span>
            </span>
          </label>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
              @click="emit('close')"
            >
              Cancelar
            </button>
            <PrimaryButton type="submit" :loading="saving">
              {{ category ? 'Guardar cambios' : 'Crear categoría' }}
            </PrimaryButton>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
