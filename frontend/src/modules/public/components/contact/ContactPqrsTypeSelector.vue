<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'

defineProps({
  modelValue: { type: String, required: true },
})
defineEmits(['update:modelValue'])

const types = [
  {
    value: 'peticion',
    icon: 'file-text',
    iconBg: 'bg-emerald-50 text-emerald-700',
    label: 'Petición',
    desc: 'Solicitud de información o servicio',
  },
  {
    value: 'queja',
    icon: 'frown',
    iconBg: 'bg-rose-50 text-rose-700',
    label: 'Queja',
    desc: 'Insatisfacción con el servicio',
  },
  {
    value: 'reclamo',
    icon: 'alert-triangle',
    iconBg: 'bg-amber-50 text-amber-700',
    label: 'Reclamo',
    desc: 'Inconformidad con producto o pedido',
  },
  {
    value: 'sugerencia',
    icon: 'lightbulb',
    iconBg: 'bg-blue-50 text-blue-700',
    label: 'Sugerencia',
    desc: 'Ideas para mejorar nuestro servicio',
  },
]
</script>

<template>
  <div class="mb-7">
    <div class="flex items-center gap-3 mb-3.5">
      <span class="text-xs font-bold text-slate-500 uppercase tracking-wide whitespace-nowrap">
        1. Tipo de solicitud
      </span>
      <span class="flex-1 h-px bg-slate-200"></span>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <button
        v-for="type in types"
        :key="type.value"
        type="button"
        class="border-[1.5px] rounded-xl px-3.5 py-3 flex items-center gap-3 text-left transition-all"
        :class="
          modelValue === type.value
            ? 'border-emerald-700 bg-emerald-50 shadow-sm'
            : 'border-slate-200 bg-white hover:border-emerald-700 hover:-translate-y-0.5'
        "
        @click="$emit('update:modelValue', type.value)"
      >
        <span
          :class="type.iconBg"
          class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
        >
          <AppIcon :name="type.icon" :size="18" />
        </span>
        <span>
          <span class="block text-sm font-bold text-slate-900">{{ type.label }}</span>
          <span class="block text-[11px] text-slate-500 leading-snug">{{ type.desc }}</span>
        </span>
      </button>
    </div>
  </div>
</template>
