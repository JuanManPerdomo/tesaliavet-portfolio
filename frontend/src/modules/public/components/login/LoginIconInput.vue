<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, required: true },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  icon: { type: String, default: 'mail' }, // 'mail' | 'lock'
  error: { type: String, default: '' },
})
defineEmits(['update:modelValue'])

const icons = {
  mail: 'M4 4h16v16H4V4zm0 0l8 8 8-8',
  lock: 'M6 10V8a6 6 0 1112 0v2m-14 0h16v10H4V10z',
}
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
        <path stroke-linecap="round" stroke-linejoin="round" :d="icons[icon]" />
      </svg>
      <input
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        class="w-full pl-11 pr-4 py-3 bg-slate-50 border-2 rounded-lg text-[14px] text-slate-900 outline-none transition-all focus:ring-2 focus:ring-emerald-600/20"
        :class="error ? 'border-red-400' : 'border-slate-200 focus:border-emerald-700'"
        @input="$emit('update:modelValue', $event.target.value)"
      />
    </div>
    <div v-if="error" class="flex items-center gap-1.5 text-red-500 text-[11px] font-medium px-0.5">
      <svg
        class="w-3.5 h-3.5"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <circle cx="12" cy="12" r="9" />
        <path d="M12 8v5M12 16h.01" />
      </svg>
      {{ error }}
    </div>
  </div>
</template>
