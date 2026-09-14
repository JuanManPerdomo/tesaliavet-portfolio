<script setup>
defineProps({
  label: { type: String, required: true },
})
</script>

<template>
  <div class="flex items-center gap-3">
    <span
      class="text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap"
      >{{ label }}</span
    >
    <div class="h-px w-full bg-slate-200"></div>
  </div>
</template>
