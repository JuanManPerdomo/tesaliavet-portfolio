<script setup>
import { ref, watch } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'

const DOCUMENT_TYPES = ['NIT', 'CC', 'CE']

const EMPTY_FORM = {
  name: '',
  documentType: '',
  documentNumber: '',
  contactName: '',
  contactPhone: '',
  contactEmail: '',
  address: '',
  city: '',
  notes: '',
}

const props = defineProps({
  open: { type: Boolean, default: false },
  supplier: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  serverError: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])

const form = ref({ ...EMPTY_FORM })

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    form.value = props.supplier
      ? {
          name: props.supplier.name || '',
          documentType: props.supplier.documentType || '',
          documentNumber: props.supplier.documentNumber || '',
          contactName: props.supplier.contactName || '',
          contactPhone: props.supplier.contactPhone || '',
          contactEmail: props.supplier.contactEmail || '',
          address: props.supplier.address || '',
          city: props.supplier.city || '',
          notes: props.supplier.notes || '',
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

      <div class="relative bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          class="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="16" />
        </button>

        <h3 class="text-lg font-bold text-slate-900 mb-4">
          {{ supplier ? 'Editar proveedor' : 'Nuevo proveedor' }}
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

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Tipo de documento</label>
              <select
                v-model="form.documentType"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              >
                <option value="">Sin especificar</option>
                <option v-for="type in DOCUMENT_TYPES" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Número de documento</label>
              <input
                v-model="form.documentNumber"
                type="text"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Contacto</label>
              <input
                v-model="form.contactName"
                type="text"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Teléfono</label>
              <input
                v-model="form.contactPhone"
                type="text"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Correo de contacto</label>
            <input
              v-model="form.contactEmail"
              type="email"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Dirección</label>
              <input
                v-model="form.address"
                type="text"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Ciudad</label>
              <input
                v-model="form.city"
                type="text"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Notas</label>
            <textarea
              v-model="form.notes"
              rows="2"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            ></textarea>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
              @click="emit('close')"
            >
              Cancelar
            </button>
            <PrimaryButton type="submit" :loading="saving">
              {{ supplier ? 'Guardar cambios' : 'Crear proveedor' }}
            </PrimaryButton>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
