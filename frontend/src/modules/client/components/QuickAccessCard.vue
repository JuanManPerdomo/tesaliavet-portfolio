<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'

defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  sub: { type: String, required: true },
  to: { type: [String, Object], required: true },
  iconBgClass: { type: String, default: 'bg-emerald-50' },
  iconColorClass: { type: String, default: 'text-emerald-700' },
})
</script>

<template>
  <RouterLink
    :to="to"
    class="group bg-white border border-slate-200 rounded-2xl p-5 flex items-center gap-4 hover:border-emerald-600 hover:shadow-lg hover:-translate-y-1 transition"
  >
    <div
      class="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
      :class="[iconBgClass, iconColorClass]"
    >
      <AppIcon :name="icon" :size="24" />
    </div>

    <div class="flex-1">
      <p class="font-semibold text-slate-900">{{ label }}</p>
      <p class="text-sm text-slate-500">{{ sub }}</p>
    </div>

    <svg
      class="w-4 h-4 text-slate-300 group-hover:text-emerald-600 transition"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 6l6 6-6 6" />
    </svg>
  </RouterLink>
</template>
