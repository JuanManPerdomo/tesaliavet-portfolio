<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'

defineProps({
  subject: { type: String, required: true },
})
defineEmits(['update:subject'])
</script>

<template>
  <div class="mb-7">
    <div class="flex items-center gap-3 mb-3.5">
      <span class="text-xs font-bold text-slate-500 uppercase tracking-wide whitespace-nowrap">
        2. Asunto
      </span>
      <span class="flex-1 h-px bg-slate-200"></span>
    </div>

    <div>
      <label class="block text-xs font-semibold text-slate-900 mb-1.5">
        Asunto <span class="text-red-600">*</span>
      </label>
      <div class="relative flex items-center">
        <AppIcon name="edit" :size="16" class="absolute left-3 text-slate-400" />
        <input
          :value="subject"
          type="text"
          placeholder="Ej: Solicitud de información sobre planes de vacunación"
          class="w-full bg-white border border-slate-200 rounded-lg pl-10 pr-3 py-2.5 text-sm text-slate-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition"
          @input="$emit('update:subject', $event.target.value)"
        />
      </div>
    </div>
  </div>
</template>
