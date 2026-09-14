<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'Contraseña' },
})
defineEmits(['update:modelValue'])

const visible = ref(false)

const REQUIREMENTS = [
  { label: 'Al menos 8 caracteres', test: (v) => v.length >= 8 },
  { label: 'Una letra mayúscula', test: (v) => /[A-Z]/.test(v) },
  { label: 'Un número', test: (v) => /[0-9]/.test(v) },
  { label: 'Un carácter especial (!@#$%...)', test: (v) => /[^A-Za-z0-9]/.test(v) },
]

const checklist = computed(() =>
  REQUIREMENTS.map((req) => ({ label: req.label, met: req.test(props.modelValue) }))
)

const metCount = computed(() => checklist.value.filter((r) => r.met).length)
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

    <div v-if="modelValue" class="pt-1 grid grid-cols-2 gap-x-3 gap-y-1">
      <div
        v-for="req in checklist"
        :key="req.label"
        class="flex items-center gap-1.5 text-[11px] font-medium"
        :class="req.met ? 'text-emerald-700' : 'text-slate-400'"
      >
        <svg v-if="req.met" class="w-3 h-3 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        <span v-else class="w-3 h-3 shrink-0 rounded-full border border-slate-300"></span>
        {{ req.label }}
      </div>
    </div>
    <p v-if="modelValue && metCount < REQUIREMENTS.length" class="text-[10px] text-slate-400 pt-0.5">
      Faltan {{ REQUIREMENTS.length - metCount }} requisito{{ REQUIREMENTS.length - metCount === 1 ? '' : 's' }}.
    </p>
  </div>
</template>
