<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  modelValue: { type: String, default: '' },
})
defineEmits(['update:modelValue', 'search'])
</script>

<template>
  <div class="relative">
    <input
      type="text"
      :value="modelValue"
      placeholder="¿Qué estás buscando para tu mascota?"
      class="w-full rounded-full border border-slate-200 bg-slate-100 py-3 pl-12 pr-5 focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-100 focus:border-emerald-700 transition"
      @input="$emit('update:modelValue', $event.target.value)"
      @keyup.enter="$emit('search')"
    />

    <AppIcon name="search" :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
  </div>
</template>
