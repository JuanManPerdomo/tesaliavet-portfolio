<script setup>
defineProps({
  text: { type: String, default: 'Conexión segura · Tus datos están protegidos' },
})
</script>

<template>
  <div class="pt-4 flex items-center justify-center gap-2 text-[11px] font-medium text-slate-500">
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
    {{ text }}
  </div>
</template>
