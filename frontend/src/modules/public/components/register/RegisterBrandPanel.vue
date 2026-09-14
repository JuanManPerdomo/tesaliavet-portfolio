<script setup>
import { RouterLink } from 'vue-router'
import AuthPanelShell from '../auth/AuthPanelShell.vue'

defineProps({
  steps: {
    type: Array,
    default: () => [
      'Completa tu información personal',
      'Registra a tus mascotas',
      'Agenda citas y compra productos',
    ],
  },
})
</script>

<template>
  <AuthPanelShell
    width-class="md:w-[38%]"
    eyebrow-icon="user-plus"
    eyebrow-text="Nueva cuenta"
    title="Únete a TesaliaVet"
    subtitle="Crea tu cuenta gratuita y empieza a disfrutar de todos nuestros servicios veterinarios en línea."
  >
    <div v-for="(step, index) in steps" :key="step" class="flex items-center gap-4">
      <div
        class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 text-[12px] font-bold"
      >
        {{ index + 1 }}
      </div>
      <span class="text-[13px] text-white/90">{{ step }}</span>
    </div>

    <template #footer>
      <div class="bg-white/10 backdrop-blur-md border border-white/15 rounded-xl p-5 space-y-3">
        <div class="text-[12px] text-white/80">¿Ya tienes una cuenta?</div>
        <RouterLink
          :to="{ name: 'login' }"
          class="flex items-center gap-2 text-white font-semibold text-[13px] hover:translate-x-1 transition-transform"
        >
          <svg
            class="w-4 h-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4M10 17l5-5-5-5M15 12H3"
            />
          </svg>
          Iniciar sesión →
        </RouterLink>
      </div>
    </template>
  </AuthPanelShell>
</template>
