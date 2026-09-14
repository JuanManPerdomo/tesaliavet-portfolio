<script setup>
import AuthPanelShell from '../auth/AuthPanelShell.vue'

defineProps({
  features: {
    type: Array,
    default: () => [
      { icon: 'calendar-check', text: 'Agenda citas veterinarias en minutos' },
      { icon: 'paw', text: 'Historial clínico y vacunas de tus mascotas' },
      { icon: 'shopping-bag', text: 'Compra productos y sigue tus pedidos' },
      { icon: 'bell', text: 'Notificaciones de vacunas y citas' },
    ],
  },
})

const currentYear = new Date().getFullYear()

const icons = {
  paw: 'M12 4a2 2 0 100 4 2 2 0 000-4zM7 8a1.6 1.6 0 100 3.2A1.6 1.6 0 007 8zm10 0a1.6 1.6 0 100 3.2A1.6 1.6 0 0017 8zM9 12a2 2 0 00-2 2v1a4 4 0 004 4h2a4 4 0 004-4v-1a2 2 0 00-2-2H9z',
  'calendar-check':
    'M8 3v3M16 3v3M4 8h16M5 6h14a1 1 0 011 1v12a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1zM9 14l2 2 4-4',
  'shopping-bag': 'M6 8h12l-1 12H7L6 8zM9 8V6a3 3 0 016 0v2',
  bell: 'M12 3a5 5 0 00-5 5v3l-2 4h14l-2-4V8a5 5 0 00-5-5zM10 19a2 2 0 004 0',
}
</script>

<template>
  <AuthPanelShell
    eyebrow-icon="heart"
    eyebrow-text="Bienvenido de vuelta"
    title="Tu veterinaria en línea"
    subtitle="Gestiona las citas, historial clínico y compras de tus mascotas desde un solo lugar."
  >
    <div v-for="feature in features" :key="feature.text" class="flex items-center gap-4">
      <div class="w-9 h-9 bg-white/10 rounded-lg flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path :d="icons[feature.icon]" />
        </svg>
      </div>
      <span class="text-[13px] text-white/90">{{ feature.text }}</span>
    </div>

    <template #footer>
      <div class="text-[11px] text-white/50 font-medium">© {{ currentYear }} TesaliaVet · Tesalia, Huila</div>
    </template>
  </AuthPanelShell>
</template>
