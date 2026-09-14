<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthBrandPanel from '../components/login/AuthBrandPanel.vue'
import PasswordResetWizard from '../components/login/PasswordResetWizard.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import BackHomeLink from '../../../components/ui/BackHomeLink.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'

const router = useRouter()
const done = ref(false)
</script>

<template>
  <div class="flex items-center justify-center min-h-screen p-4 md:p-8 bg-slate-50">
    <BackHomeLink />

    <div
      class="w-full max-w-5xl flex flex-col md:flex-row bg-white rounded-xl overflow-hidden shadow-xl border border-slate-200 min-h-[600px]"
    >
      <AuthBrandPanel />

      <div class="flex-1 p-8 md:p-14 flex flex-col justify-center">
        <template v-if="!done">
          <RouterLink
            :to="{ name: 'login' }"
            class="inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:underline mb-6"
          >
            <AppIcon name="arrow-left" :size="16" />
            Volver a inicio de sesión
          </RouterLink>

          <PasswordResetWizard @success="done = true" />
        </template>

        <template v-else>
          <div class="text-center space-y-5">
            <div
              class="w-14 h-14 mx-auto bg-emerald-50 rounded-full flex items-center justify-center"
            >
              <AppIcon name="check" :size="28" class="text-emerald-700" />
            </div>
            <h2 class="text-2xl font-semibold text-slate-900">Contraseña actualizada</h2>
            <p class="text-sm text-slate-500 max-w-sm mx-auto">
              Ya puedes iniciar sesión con tu nueva contraseña.
            </p>
            <PrimaryButton class="inline-flex" @click="router.push({ name: 'login' })">
              Ir a iniciar sesión
            </PrimaryButton>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
