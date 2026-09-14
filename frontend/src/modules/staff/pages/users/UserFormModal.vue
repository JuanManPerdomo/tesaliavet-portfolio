<script setup>
import { ref, watch } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { validatePasswordStrength, PASSWORD_HINT } from '../../../../lib/passwordPolicy'

const DOCUMENT_TYPES = [
  { value: 'CC', label: 'Cédula de Ciudadanía (CC)' },
  { value: 'CE', label: 'Cédula de Extranjería (CE)' },
  { value: 'NIT', label: 'NIT' },
]

const EMPTY_FORM = {
  firstName: '',
  lastName: '',
  documentType: 'CC',
  documentNumber: '',
  email: '',
  phone: '',
  password: '',
  roles: [],
}

const props = defineProps({
  open: { type: Boolean, default: false },
  availableRoles: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
  serverError: { type: String, default: '' },
})

const emit = defineEmits(['close', 'submit'])

const form = ref({ ...EMPTY_FORM })
const passwordError = ref('')

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      form.value = { ...EMPTY_FORM }
      passwordError.value = ''
    }
  }
)

function toggleRole(roleName, checked) {
  form.value.roles = checked
    ? [...form.value.roles, roleName]
    : form.value.roles.filter((r) => r !== roleName)
}

function handleSubmit() {
  passwordError.value = validatePasswordStrength(form.value.password) || ''
  if (passwordError.value) return
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

        <h3 class="text-lg font-bold text-slate-900 mb-1">Nuevo usuario</h3>
        <p class="text-sm text-slate-500 mb-4">
          Para clientes que se registran en la tienda física, o para crear otra cuenta de personal.
        </p>

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

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Tipo de documento *</label>
              <select
                v-model="form.documentType"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
              >
                <option v-for="type in DOCUMENT_TYPES" :key="type.value" :value="type.value">{{ type.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Número de documento *</label>
              <input
                v-model="form.documentNumber"
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

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Teléfono</label>
              <input
                v-model="form.phone"
                type="text"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Contraseña temporal *</label>
              <input
                v-model="form.password"
                type="text"
                required
                placeholder="Mínimo 8 caracteres"
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
              <p v-if="passwordError" class="text-[11px] text-red-600 mt-1">{{ passwordError }}</p>
              <p v-else class="text-[11px] text-slate-400 mt-1">{{ PASSWORD_HINT }}</p>
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-2">Roles *</label>
            <div class="flex flex-wrap gap-4">
              <label
                v-for="role in availableRoles"
                :key="role.id"
                class="flex items-center gap-2 text-sm text-slate-700"
              >
                <input
                  type="checkbox"
                  :checked="form.roles.includes(role.name)"
                  class="w-4 h-4 accent-emerald-700 cursor-pointer"
                  @change="toggleRole(role.name, $event.target.checked)"
                />
                {{ role.name }}
              </label>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
              @click="emit('close')"
            >
              Cancelar
            </button>
            <PrimaryButton type="submit" :loading="saving">Crear usuario</PrimaryButton>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
