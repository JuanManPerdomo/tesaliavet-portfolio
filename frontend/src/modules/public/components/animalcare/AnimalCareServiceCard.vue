<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'

defineProps({
  icon: { type: String, required: true },
  iconBg: {
    type: String,
    default: 'bg-emerald-50 text-emerald-700',
  },
  name: { type: String, required: true },
  description: { type: String, required: true },
  features: {
    type: Array,
    default: () => [],
  },
  // Solo se renderizan si buttonRoute viene puesto (ver v-if abajo) -
  // opcionales en conjunto, no cada uno por separado.
  buttonIcon: { type: String, default: null },
  buttonText: { type: String, default: null },
  buttonRoute: {
    type: String,
    default: null,
  },
  footerTag: {
    type: String,
    default: null,
  },
  footerLinkText: {
    type: String,
    default: null,
  },
  footerLinkRoute: {
    type: String,
    default: null,
  },
})
</script>

<template>
  <div
    class="bg-white rounded-3xl border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all flex flex-col"
  >
    <div class="p-8 flex-1">
      <div :class="iconBg" class="w-14 h-14 rounded-2xl flex items-center justify-center mb-5">
        <AppIcon :name="icon" :size="28" />
      </div>

      <h3 class="text-xl font-bold text-slate-900 mb-2">{{ name }}</h3>
      <p class="text-sm text-slate-500 leading-relaxed mb-5">{{ description }}</p>

      <div class="flex flex-col gap-2.5">
        <div
          v-for="feature in features"
          :key="feature"
          class="flex items-center gap-2.5 text-[13px] font-medium text-slate-900"
        >
          <AppIcon name="check" :size="16" class="text-emerald-700" />
          {{ feature }}
        </div>
      </div>
    </div>

    <div class="px-8 pb-8 pt-6 flex items-center gap-4">
      <RouterLink
        v-if="buttonRoute"
        :to="buttonRoute"
        class="bg-emerald-700 text-white rounded-full px-4 py-2.5 text-[13px] font-bold hover:opacity-90 transition inline-flex items-center gap-1.5 whitespace-nowrap shrink-0"
      >
        <AppIcon :name="buttonIcon" :size="16" />
        {{ buttonText }}
      </RouterLink>

      <span
        v-if="footerTag"
        class="text-[11px] bg-slate-100 text-slate-500 px-2.5 py-1 rounded-full font-semibold whitespace-nowrap shrink-0"
      >
        {{ footerTag }}
      </span>

      <RouterLink
        v-else-if="footerLinkText"
        :to="footerLinkRoute"
        class="text-emerald-700 text-[13px] font-bold whitespace-nowrap shrink-0"
      >
        {{ footerLinkText }}
      </RouterLink>
    </div>
  </div>
</template>
