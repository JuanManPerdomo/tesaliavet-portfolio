<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'Contraseña' },
})
defineEmits(['update:modelValue'])

const visible = ref(false)
</script>

<template>
  <div class="space-y-1.5">
    <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-widest">{{
      label
    }}</label>
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
          d="M6 10V8a6 6 0 1112 0v2m-14 0h16v10H4V10z"
        />
      </svg>
      <input
        :type="visible ? 'text' : 'password'"
        :value="modelValue"
        class="w-full pl-11 pr-11 py-3 bg-slate-50 border border-slate-200 rounded-lg text-[14px] text-slate-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-600/20 transition-all"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <button
        type="button"
        class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 transition-colors"
        @click="visible = !visible"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path v-if="!visible" d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z" />
          <circle v-if="!visible" cx="12" cy="12" r="3" />
          <path
            v-else
            d="M3 3l18 18M9.9 9.9a3 3 0 004.2 4.2M6.5 6.7C4 8.3 2 12 2 12s4 7 10 7c2 0 3.7-.6 5.1-1.4M17.9 17.9C20.4 16.1 22 12 22 12s-1.2-2.1-3.2-3.9"
          />
        </svg>
      </button>
    </div>
    <div class="text-right">
      <RouterLink
        :to="{ name: 'forgot-password' }"
        class="text-[12px] font-semibold text-emerald-700 hover:text-emerald-900 transition-colors"
      >
        ¿Olvidaste tu contraseña?
      </RouterLink>
    </div>
  </div>
</template>
