<script setup>
defineProps({
  to: {
    type: [String, Object],
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <!-- RouterLink -->
  <RouterLink
    v-if="to"
    :to="to"
    class="bg-emerald-700 hover:bg-emerald-800 text-white px-6 py-3 rounded-2xl font-semibold transition inline-flex items-center justify-center"
  >
    <slot />
  </RouterLink>

  <!-- Button -->
  <button
    v-else
    :disabled="disabled || loading"
    class="bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2 rounded-2xl font-semibold transition inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:pointer-events-none"
  >
    <svg
      v-if="loading"
      class="animate-spin h-4 w-4 flex-shrink-0"
      viewBox="0 0 24 24"
      fill="none"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V4C7.373 4 4 7.373 4 12z"
      ></path>
    </svg>
    <slot />
  </button>
</template>
