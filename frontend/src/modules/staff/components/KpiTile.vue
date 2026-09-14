<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'

defineProps({
  icon: { type: String, required: true },
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  sub: { type: String, default: '' },
  badge: { type: String, default: '' },
  changePercent: { type: Number, default: null },
  to: { type: [String, Object], default: null },
  iconBgClass: { type: String, default: 'bg-emerald-50' },
  iconColorClass: { type: String, default: 'text-emerald-700' },
})
</script>

<template>
  <component
    :is="to ? 'RouterLink' : 'div'"
    :to="to"
    class="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col gap-3 transition"
    :class="to ? 'hover:border-emerald-300 hover:shadow-md' : ''"
  >
    <div class="flex items-center justify-between">
      <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="[iconBgClass, iconColorClass]">
        <AppIcon :name="icon" :size="18" />
      </div>
      <span
        v-if="badge"
        class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-red-50 text-red-600"
      >
        {{ badge }}
      </span>
      <span
        v-else-if="changePercent !== null"
        class="text-[10px] font-bold px-2 py-0.5 rounded-full"
        :class="changePercent >= 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
      >
        {{ changePercent >= 0 ? '+' : '' }}{{ changePercent.toFixed(1) }}%
      </span>
    </div>

    <div>
      <p class="text-[11px] font-bold text-slate-400 uppercase tracking-wide">{{ label }}</p>
      <p class="text-2xl font-extrabold text-slate-900 mt-0.5">{{ value }}</p>
      <p v-if="sub" class="text-xs text-slate-500 mt-1">{{ sub }}</p>
    </div>
  </component>
</template>
