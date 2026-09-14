<script setup>
defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, required: true },
  required: { type: Boolean, default: false },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  icon: { type: String, default: 'user' }, // 'user' | 'id-badge' | 'mail' | 'phone'
  hint: { type: String, default: '' },
  valid: { type: Boolean, default: false }, // true = fondo verde + check
})
defineEmits(['update:modelValue'])

const icons = {
  user: 'M12 12a4 4 0 100-8 4 4 0 000 8zM4 21a8 8 0 0116 0',
  'id-badge': 'M4 4h16v16H4V4zm4 4h2m-2 4h8m-8 4h5M15 8h1',
  mail: 'M4 4h16v16H4V4zm0 0l8 8 8-8',
  phone: 'M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z',
}
</script>

<template>
  <div class="space-y-1.5">
    <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-widest">
      {{ label }} <span v-if="required" class="text-red-500">*</span>
    </label>
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
        class="w-full pl-11 pr-11 py-3 rounded-lg text-[14px] text-slate-900 outline-none transition-all"
        :class="
          valid
            ? 'bg-emerald-50 border-2 border-emerald-700/20'
            : 'bg-slate-50 border border-slate-200 focus:border-emerald-700 focus:ring-2 focus:ring-emerald-600/20'
        "
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <svg
        v-if="valid"
        class="absolute right-3.5 top-1/2 -translate-y-1/2 h-5 w-5 text-emerald-700"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
      </svg>
    </div>
    <p v-if="hint" class="text-[10px] text-slate-500 px-0.5">{{ hint }}</p>
  </div>
</template>
