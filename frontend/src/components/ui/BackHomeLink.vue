<script setup>
import AppIcon from './AppIcon.vue'
</script>

<template>
  <RouterLink
    :to="{ name: 'home' }"
    class="fixed top-5 left-5 sm:top-6 sm:left-6 z-50 inline-flex items-center gap-2 bg-white/90 backdrop-blur border border-slate-200 text-slate-600 hover:text-emerald-700 hover:border-emerald-700 text-sm font-semibold px-4 py-2 rounded-xl shadow-sm transition"
  >
    <AppIcon name="arrow-left" :size="16" />
    Inicio
  </RouterLink>
</template>
