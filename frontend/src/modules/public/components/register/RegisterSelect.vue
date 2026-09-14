<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, required: true },
  required: { type: Boolean, default: false },
  options: { type: Array, default: () => [] }, // [{ value, label }]
})
defineEmits(['update:modelValue'])
</script>

<template>
  <div class="space-y-1.5">
    <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-widest">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <select
        :value="modelValue"
        class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-[14px] text-slate-900 outline-none appearance-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-600/20 transition-all"
        @change="$emit('update:modelValue', $event.target.value)"
      >
        <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
      </select>
      <svg
        class="absolute right-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6" />
      </svg>
    </div>
  </div>
</template>
