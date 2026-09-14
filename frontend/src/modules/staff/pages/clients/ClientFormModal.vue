<script setup>
import { ref, watch } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import DepartmentMunicipalitySelect from '../../../../components/ui/DepartmentMunicipalitySelect.vue'

const EMPTY_FORM = { firstName: '', lastName: '', email: '', phone: '', direccion: '', ciudad: '', departamento: '' }

const props = defineProps({
  open: { type: Boolean, default: false },
  client: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  serverError: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])

const form = ref({ ...EMPTY_FORM })

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen || !props.client) return
    form.value = {
      firstName: props.client.firstName || '',
      lastName: props.client.lastName || '',
      email: props.client.email || '',
      phone: props.client.phone || '',
      direccion: props.client.direccion || '',
      ciudad: props.client.ciudad || '',
      departamento: props.client.departamento || '',
    }
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

        <h3 class="text-lg font-bold text-slate-900 mb-4">Editar datos del cliente</h3>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <p v-if="serverError" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ serverError }}</p>

          <div class="grid grid-cols-2 gap-3">
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
          </div>

          <div>
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

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">Dirección</label>
            <input
              v-model="form.direccion"
              type="text"
              class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            />
          </div>

          <DepartmentMunicipalitySelect
            :departamento="form.departamento"
            :municipio="form.ciudad"
            @update:departamento="form.departamento = $event"
            @update:municipio="form.ciudad = $event"
          />

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
              @click="emit('close')"
            >
              Cancelar
            </button>
            <PrimaryButton type="submit" :loading="saving">Guardar cambios</PrimaryButton>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
