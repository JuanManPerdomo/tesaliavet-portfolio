<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import BackHomeLink from '../../../components/ui/BackHomeLink.vue'
import RegisterBrandPanel from '../components/register/RegisterBrandPanel.vue'
import RegisterFieldInput from '../components/register/RegisterFieldInput.vue'
import RegisterSelect from '../components/register/RegisterSelect.vue'
import PasswordStrengthInput from '../components/register/PasswordStrengthInput.vue'
import ConfirmPasswordInput from '../components/register/ConfirmPasswordInput.vue'
import FormSectionDivider from '../components/register/FormSectionDivider.vue'
import TermsCheckbox from '../components/register/TermsCheckbox.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import { useAuthStore } from '../../../stores/auth'
import { useToastStore } from '../../../stores/toast'
import { validatePasswordStrength } from '../../../lib/passwordPolicy'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

// Persistimos el formulario en sessionStorage para que no se pierda al visitar
// "Términos y condiciones" o "Política de privacidad" (son rutas aparte y
// desmontan este componente).
const STORAGE_KEY = 'tesaliavet_register_form'

function loadSavedForm() {
  try {
    const saved = sessionStorage.getItem(STORAGE_KEY)
    if (saved) return JSON.parse(saved)
  } catch {
    // sessionStorage no disponible o JSON corrupto: seguimos con el formulario vacío
  }
  return null
}

const form = ref(
  loadSavedForm() ?? {
    firstName: '',
    lastName: '',
    documentType: 'CC',
    documentNumber: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    acceptedTerms: false,
  }
)

watch(
  form,
  (val) => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(val))
    } catch {
      // almacenamiento lleno o bloqueado: no es crítico, simplemente no persiste
    }
  },
  { deep: true }
)

const documentTypes = [
  { value: 'CC', label: 'Cédula de Ciudadanía (CC)' },
  { value: 'CE', label: 'Cédula de Extranjería (CE)' },
  { value: 'NIT', label: 'NIT' },
  { value: 'PA', label: 'Pasaporte' },
]

// --- Validaciones en vivo (para el check verde en cada campo) ---
const isFirstNameValid = computed(() => form.value.firstName.trim().length >= 2)
const isLastNameValid = computed(() => form.value.lastName.trim().length >= 2)
const isDocumentValid = computed(() => form.value.documentNumber.trim().length >= 5)
const isEmailValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email))
const isPhoneValid = computed(() => form.value.phone.trim().length >= 7)

const passwordsMatch = computed(
  () => form.value.password.length > 0 && form.value.password === form.value.confirmPassword
)

const isFormValid = computed(
  () =>
    isFirstNameValid.value &&
    isLastNameValid.value &&
    isDocumentValid.value &&
    isEmailValid.value &&
    isPhoneValid.value &&
    !validatePasswordStrength(form.value.password) &&
    passwordsMatch.value &&
    form.value.acceptedTerms
)

const submitting = ref(false)
const submitError = ref('')

async function handleSubmit() {
  if (!isFormValid.value) return
  submitting.value = true
  submitError.value = ''
  try {
    await authStore.register({
      firstName: form.value.firstName,
      lastName: form.value.lastName,
      documentType: form.value.documentType,
      documentNumber: form.value.documentNumber,
      email: form.value.email,
      phone: form.value.phone,
      password: form.value.password,
    })
    sessionStorage.removeItem(STORAGE_KEY)
    toastStore.success('¡Cuenta creada exitosamente! Redirigiendo...')
    setTimeout(() => router.push({ name: 'home' }), 1200)
  } catch (err) {
    submitError.value =
      err.response?.data?.message || 'No se pudo crear la cuenta. Intenta de nuevo.'
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen p-4 md:p-8 bg-slate-50">
    <BackHomeLink />

    <div
      class="w-full max-w-6xl flex flex-col md:flex-row bg-white rounded-xl overflow-hidden shadow-xl border border-slate-200 min-h-[700px]"
    >
      <RegisterBrandPanel />

      <div class="flex-1 overflow-y-auto max-h-[850px]">
        <div class="p-8 md:p-12">
          <div class="mb-10">
            <h2 class="text-2xl font-semibold text-slate-900 mb-2">Crear cuenta</h2>
            <p class="text-sm text-slate-500">
              Todos los campos marcados con <span class="text-red-500">*</span> son obligatorios
            </p>
          </div>

          <form class="space-y-8" @submit.prevent="handleSubmit">
            <!-- Información personal -->
            <div class="space-y-5">
              <FormSectionDivider label="Información personal" />
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <RegisterFieldInput
                  v-model="form.firstName"
                  label="Nombre"
                  required
                  icon="user"
                  :valid="isFirstNameValid"
                />
                <RegisterFieldInput
                  v-model="form.lastName"
                  label="Apellidos"
                  required
                  icon="user"
                  :valid="isLastNameValid"
                />
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <RegisterSelect
                  v-model="form.documentType"
                  label="Tipo de documento"
                  required
                  :options="documentTypes"
                />
                <RegisterFieldInput
                  v-model="form.documentNumber"
                  label="Número de documento"
                  required
                  icon="id-badge"
                  :valid="isDocumentValid"
                  hint="Este número es único e irrepetible en el sistema"
                />
              </div>
            </div>

            <!-- Datos de contacto -->
            <div class="space-y-5">
              <FormSectionDivider label="Datos de contacto" />
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <RegisterFieldInput
                  v-model="form.email"
                  label="Correo electrónico"
                  required
                  type="email"
                  icon="mail"
                  :valid="isEmailValid"
                />
                <RegisterFieldInput
                  v-model="form.phone"
                  label="Teléfono / Celular"
                  required
                  icon="phone"
                  placeholder="Ej: 310 123 4567"
                  :valid="isPhoneValid"
                  hint="Para recordatorios de citas y vacunas"
                />
              </div>
            </div>

            <!-- Seguridad -->
            <div class="space-y-5">
              <FormSectionDivider label="Seguridad" />
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <PasswordStrengthInput v-model="form.password" />
                <ConfirmPasswordInput v-model="form.confirmPassword" :matches="passwordsMatch" />
              </div>
            </div>

            <!-- Términos y envío -->
            <div class="pt-4 space-y-6">
              <TermsCheckbox v-model="form.acceptedTerms" />

              <p v-if="submitError" class="text-[13px] text-red-600">{{ submitError }}</p>

              <PrimaryButton
                type="submit"
                class="w-full justify-center py-4 rounded-xl"
                :disabled="!isFormValid"
                :loading="submitting"
              >
                {{ submitting ? 'Creando cuenta...' : 'Crear mi cuenta gratis' }}
              </PrimaryButton>

              <div
                class="flex items-center justify-center gap-2 text-[11px] font-medium text-slate-500"
              >
                <svg
                  class="w-4 h-4 text-emerald-700"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" />
                  <path d="M9 12l2 2 4-4" />
                </svg>
                Registro seguro · Nunca compartiremos tus datos con terceros
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
