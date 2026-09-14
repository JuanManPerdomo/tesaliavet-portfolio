<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
})
defineEmits(['update:modelValue'])
</script>

<template>
  <label class="flex items-start gap-3 cursor-pointer">
    <input
      type="checkbox"
      :checked="modelValue"
      class="sr-only peer"
      @change="$emit('update:modelValue', $event.target.checked)"
    />
    <span
      class="w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5 border-2 border-slate-300 peer-checked:bg-emerald-700 peer-checked:border-emerald-700 transition-colors"
    >
      <svg
        v-if="modelValue"
        class="w-3 h-3 text-white"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="3"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    </span>
    <p class="text-[12px] text-slate-500 leading-relaxed">
      He leído y acepto los
      <RouterLink
        :to="{ name: 'terms' }"
        class="text-emerald-700 font-bold hover:underline"
        @click.stop
      >
        Términos y condiciones
      </RouterLink>
      y la
      <RouterLink
        :to="{ name: 'privacy' }"
        class="text-emerald-700 font-bold hover:underline"
        @click.stop
      >
        Política de privacidad
      </RouterLink>
      de TesaliaVet. Entiendo que mis datos serán tratados conforme a la Ley 1581 de 2012
      (Colombia).
    </p>
  </label>
</template>
