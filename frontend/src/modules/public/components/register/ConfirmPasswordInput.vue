<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'Confirmar contraseña' },
  matches: { type: Boolean, default: false }, // true cuando coincide con la contraseña original
})
defineEmits(['update:modelValue'])
</script>

<template>
  <div class="space-y-1.5">
    <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-widest">
      {{ label }} <span class="text-red-500">*</span>
    </label>
    <div class="relative">
      <svg
        class="absolute left-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M6 10V8a6 6 0 1112 0v2m-14 0h16v10H4V10zM9 14l2 2 4-4"
        />
      </svg>
      <input
        type="password"
        :value="modelValue"
        class="w-full pl-11 pr-11 py-3 rounded-lg text-[14px] text-slate-900 outline-none transition-all"
        :class="
          matches
            ? 'bg-emerald-50 border-2 border-emerald-700/20'
            : 'bg-slate-50 border border-slate-200 focus:border-emerald-700 focus:ring-2 focus:ring-emerald-600/20'
        "
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <svg
        v-if="matches"
        class="absolute right-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-emerald-700"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    </div>
    <p v-if="matches" class="text-[10px] text-emerald-700 font-medium px-0.5">
      Las contraseñas coinciden
    </p>
  </div>
</template>
