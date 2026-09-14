<script setup>
import { ref, watch } from 'vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import PasswordStrengthInput from '../../public/components/register/PasswordStrengthInput.vue'
import PasswordResetWizard from '../../public/components/login/PasswordResetWizard.vue'
import { useAuthStore } from '../../../stores/auth'
import { useToastStore } from '../../../stores/toast'
import { validatePasswordStrength } from '../../../lib/passwordPolicy'

const props = defineProps({
  open: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const toastStore = useToastStore()

// 'change' -> con la contraseña actual (por defecto) | 'forgot' -> mismo
// wizard de codigo de 6 digitos que /olvide-contrasena, para cuando el
// usuario no recuerda la contraseña actual - vuelve a este mismo perfil en
// vez de mandar a /login, ya que sigue con la sesion iniciada.
const mode = ref('change')

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const saving = ref(false)
const errorMessage = ref('')

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) return
    mode.value = 'change'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    errorMessage.value = ''
  }
)

async function handleSubmit() {
  errorMessage.value = ''

  const strengthError = validatePasswordStrength(newPassword.value)
  if (strengthError) {
    errorMessage.value = strengthError
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = 'Las contraseñas nuevas no coinciden.'
    return
  }

  saving.value = true
  try {
    await authStore.changePassword({
      currentPassword: currentPassword.value,
      newPassword: newPassword.value,
    })
    toastStore.success('Contraseña actualizada correctamente.')
    emit('close')
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo actualizar la contraseña.'
  } finally {
    saving.value = false
  }
}

function handleWizardSuccess() {
  toastStore.success('Contraseña actualizada correctamente.')
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('close')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-sm w-full p-6">
        <button
          type="button"
          class="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="16" />
        </button>

        <template v-if="mode === 'change'">
          <div class="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-4">
            <AppIcon name="shield-check" :size="20" />
          </div>

          <h3 class="text-lg font-bold text-slate-900 mb-1">Cambiar contraseña</h3>
          <p class="text-sm text-slate-500 mb-5">Necesitas tu contraseña actual para confirmar el cambio.</p>

          <form class="space-y-4" @submit.prevent="handleSubmit">
            <p v-if="errorMessage" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{{ errorMessage }}</p>

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Contraseña actual</label>
              <input
                v-model="currentPassword"
                type="password"
                required
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
              <button
                type="button"
                class="text-xs font-semibold text-emerald-700 hover:underline mt-1.5"
                @click="mode = 'forgot'"
              >
                ¿Olvidaste tu contraseña actual?
              </button>
            </div>

            <PasswordStrengthInput v-model="newPassword" label="Nueva contraseña" />

            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">Confirmar nueva contraseña</label>
              <input
                v-model="confirmPassword"
                type="password"
                required
                class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
              />
            </div>

            <div class="flex justify-end gap-3 pt-2">
              <button
                type="button"
                class="px-4 py-2 border border-slate-200 text-slate-600 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
                @click="emit('close')"
              >
                Cancelar
              </button>
              <PrimaryButton type="submit" :loading="saving">Guardar</PrimaryButton>
            </div>
          </form>
        </template>

        <template v-else>
          <button
            type="button"
            class="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700 hover:underline mb-4"
            @click="mode = 'change'"
          >
            <AppIcon name="arrow-left" :size="14" />
            Volver
          </button>
          <PasswordResetWizard :initial-email="authStore.user?.email" @success="handleWizardSuccess" />
        </template>
      </div>
    </div>
  </Teleport>
</template>
