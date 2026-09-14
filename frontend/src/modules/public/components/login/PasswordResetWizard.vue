<script setup>
import { ref, onMounted } from 'vue'
import LoginIconInput from './LoginIconInput.vue'
import OtpCodeInput from './OtpCodeInput.vue'
import PasswordStrengthInput from '../register/PasswordStrengthInput.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useAuthStore } from '../../../../stores/auth'
import { validatePasswordStrength } from '../../../../lib/passwordPolicy'

const props = defineProps({
  // Si se pasa (ej. desde el perfil de un usuario ya logueado, decision del
  // 2026-08-25), se salta el paso de pedir el correo - se manda el codigo
  // directo a esa cuenta, sin que el usuario tenga que volver a escribir un
  // correo que el sistema ya conoce.
  initialEmail: { type: String, default: '' },
})
const emit = defineEmits(['success'])

const authStore = useAuthStore()

const step = ref(props.initialEmail ? 'code' : 'email')

const email = ref(props.initialEmail)
const emailError = ref('')
const submittingEmail = ref(false)
const resending = ref(false)

const code = ref('')
const codeError = ref('')
const verifyingCode = ref(false)

const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const submittingReset = ref(false)

const isEmailValid = () => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)

function maskEmail(value) {
  const [local, domain] = value.split('@')
  if (!domain) return value
  const visible = local.slice(0, Math.min(2, local.length))
  return `${visible}***@${domain}`
}

onMounted(() => {
  if (props.initialEmail) authStore.forgotPassword(props.initialEmail)
})

async function handleSubmitEmail() {
  emailError.value = ''
  if (!isEmailValid()) {
    emailError.value = 'Ingresa un correo electrónico válido'
    return
  }
  submittingEmail.value = true
  try {
    // El backend siempre responde igual exista o no la cuenta (no revela si
    // un correo esta registrado) - no hay un "error" real que mostrar aca
    // salvo que la request falle de plano.
    await authStore.forgotPassword(email.value)
    step.value = 'code'
  } catch {
    emailError.value = 'No pudimos procesar tu solicitud, intenta de nuevo.'
  } finally {
    submittingEmail.value = false
  }
}

async function handleResend() {
  resending.value = true
  codeError.value = ''
  try {
    await authStore.forgotPassword(email.value)
  } finally {
    resending.value = false
  }
}

async function handleVerifyCode() {
  codeError.value = ''
  if (code.value.length !== 6) {
    codeError.value = 'Ingresa el código de 6 dígitos que te enviamos'
    return
  }
  verifyingCode.value = true
  try {
    await authStore.verifyResetCode(email.value, code.value)
    step.value = 'password'
  } catch (err) {
    codeError.value = err.response?.data?.message || 'Código inválido o vencido'
  } finally {
    verifyingCode.value = false
  }
}

async function handleSubmitPassword() {
  passwordError.value = ''
  const strengthError = validatePasswordStrength(newPassword.value)
  if (strengthError) {
    passwordError.value = strengthError
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'Las contraseñas no coinciden'
    return
  }
  submittingReset.value = true
  try {
    await authStore.resetPassword(email.value, code.value, newPassword.value)
    emit('success')
  } catch (err) {
    passwordError.value = err.response?.data?.message || 'No pudimos restablecer tu contraseña.'
  } finally {
    submittingReset.value = false
  }
}
</script>

<template>
  <div>
    <template v-if="step === 'email'">
      <div class="mb-6">
        <h2 class="text-xl font-semibold text-slate-900 mb-2">¿Olvidaste tu contraseña?</h2>
        <p class="text-sm text-slate-500">
          Ingresa tu correo electrónico y te enviaremos un código de verificación de 6 dígitos.
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmitEmail">
        <LoginIconInput
          v-model="email"
          label="Correo electrónico"
          type="email"
          icon="mail"
          placeholder="tu@correo.com"
          :error="emailError"
        />

        <PrimaryButton
          type="submit"
          class="w-full justify-center py-3.5"
          :class="{ 'opacity-50 pointer-events-none': submittingEmail }"
        >
          {{ submittingEmail ? 'Enviando...' : 'Enviar código de verificación' }}
        </PrimaryButton>
      </form>
    </template>

    <template v-else-if="step === 'code'">
      <div class="mb-6 text-center">
        <button
          v-if="!initialEmail"
          type="button"
          class="inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:underline mb-6 float-left"
          @click="step = 'email'"
        >
          <AppIcon name="arrow-left" :size="16" />
          Cambiar correo
        </button>
        <div class="clear-both"></div>
        <div class="w-14 h-14 mx-auto bg-emerald-50 rounded-full flex items-center justify-center mb-4">
          <AppIcon name="mail" :size="26" class="text-emerald-700" />
        </div>
        <h2 class="text-xl font-semibold text-slate-900 mb-2">Ingresa tu código</h2>
        <p class="text-sm text-slate-500 max-w-sm mx-auto">
          Te enviamos un código de 6 dígitos, válido por 10 minutos, a tu correo electrónico
          asociado a <strong>{{ maskEmail(email) }}</strong>.
        </p>
      </div>

      <form class="space-y-5" @submit.prevent="handleVerifyCode">
        <OtpCodeInput v-model="code" :error="!!codeError" @complete="handleVerifyCode" />
        <p v-if="codeError" class="text-center text-red-500 text-xs font-medium">{{ codeError }}</p>

        <PrimaryButton
          type="submit"
          class="w-full justify-center py-3.5"
          :class="{ 'opacity-50 pointer-events-none': verifyingCode }"
        >
          {{ verifyingCode ? 'Verificando...' : 'Verificar código' }}
        </PrimaryButton>

        <button
          type="button"
          class="w-full text-center text-xs font-semibold text-slate-500 hover:text-emerald-700 disabled:opacity-50"
          :disabled="resending"
          @click="handleResend"
        >
          {{ resending ? 'Reenviando...' : '¿No te llegó? Reenviar código' }}
        </button>
      </form>
    </template>

    <template v-else-if="step === 'password'">
      <div class="mb-6">
        <h2 class="text-xl font-semibold text-slate-900 mb-2">Elige tu nueva contraseña</h2>
        <p class="text-sm text-slate-500">Código verificado — ya puedes definir tu nueva contraseña.</p>
      </div>

      <form class="space-y-5" @submit.prevent="handleSubmitPassword">
        <PasswordStrengthInput v-model="newPassword" label="Nueva contraseña" />

        <LoginIconInput
          v-model="confirmPassword"
          label="Confirmar nueva contraseña"
          type="password"
          icon="lock"
          :error="passwordError"
        />

        <PrimaryButton
          type="submit"
          class="w-full justify-center py-3.5"
          :class="{ 'opacity-50 pointer-events-none': submittingReset }"
        >
          {{ submittingReset ? 'Guardando...' : 'Restablecer contraseña' }}
        </PrimaryButton>
      </form>
    </template>
  </div>
</template>
