<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import BackHomeLink from '../../../components/ui/BackHomeLink.vue'
import AuthBrandPanel from '../components/login/AuthBrandPanel.vue'
import LoginAlert from '../components/login/LoginAlert.vue'
import LoginIconInput from '../components/login/LoginIconInput.vue'
import LoginPasswordInput from '../components/login/LoginPasswordInput.vue'
import SecureBadge from '../components/login/SecureBadge.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import { useAuthStore } from '../../../stores/auth'
import { useToastStore } from '../../../stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const emailError = ref('')
const submitting = ref(false)

async function handleSubmit() {
  errorMessage.value = ''
  submitting.value = true
  try {
    await authStore.login(email.value, password.value)
    toastStore.success('¡Inicio de sesión exitoso! Redirigiendo...')
    setTimeout(() => router.push({ name: 'home' }), 1200)
  } catch (err) {
    errorMessage.value =
      err.response?.data?.message || 'No se pudo iniciar sesión. Intenta de nuevo.'
    submitting.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen p-4 md:p-8 bg-slate-50">
    <BackHomeLink />

    <div
      class="w-full max-w-5xl flex flex-col md:flex-row bg-white rounded-xl overflow-hidden shadow-xl border border-slate-200 min-h-[600px]"
    >
      <AuthBrandPanel />

      <div class="flex-1 p-8 md:p-14 flex flex-col justify-center">
        <div class="mb-8">
          <h2 class="text-2xl font-semibold text-slate-900 mb-2">Inicia sesión</h2>
          <p class="text-sm text-slate-500">
            Ingresa tu correo y contraseña para acceder a tu cuenta
          </p>
        </div>

        <LoginAlert :message="errorMessage" />

        <form class="space-y-5" @submit.prevent="handleSubmit">
          <LoginIconInput
            v-model="email"
            label="Correo electrónico"
            type="email"
            icon="mail"
            placeholder="tu@correo.com"
            :error="emailError"
          />

          <LoginPasswordInput v-model="password" />

          <PrimaryButton
            type="submit"
            class="w-full justify-center py-3.5"
            :loading="submitting"
          >
            {{ submitting ? 'Ingresando...' : 'Ingresar' }}
          </PrimaryButton>

          <div class="flex items-center gap-4 py-2">
            <div class="flex-1 h-px bg-slate-200"></div>
            <span class="text-[12px] font-medium text-slate-500 whitespace-nowrap"
              >¿Eres nuevo en TesaliaVet?</span
            >
            <div class="flex-1 h-px bg-slate-200"></div>
          </div>

          <div class="text-center text-sm text-slate-500">
            <span>¿No tienes una cuenta? </span>
            <RouterLink
              :to="{ name: 'register' }"
              class="font-bold text-emerald-700 hover:underline underline-offset-4"
            >
              Regístrate gratis →
            </RouterLink>
          </div>

          <SecureBadge />
        </form>
      </div>
    </div>
  </div>
</template>
