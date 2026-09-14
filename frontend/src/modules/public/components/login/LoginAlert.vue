<script setup>
defineProps({
  message: { type: String, default: '' },
})
</script>

<template>
  <div
    v-if="message"
    class="flex items-start gap-3 bg-red-50 border border-red-200 rounded-lg p-3.5 mb-6"
  >
    <svg
      class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v5M12 16h.01" />
    </svg>
    <p class="text-[13px] text-red-600 leading-snug">{{ message }}</p>
  </div>
</template>
