<script setup>
defineProps({
  to: {
    type: String,
    default: null,
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
    class="bg-emerald-700 hover:bg-emerald-800 text-white px-6 py-3 rounded-2xl font-semibold transition"
  >
    <slot />
  </button>
</template>
