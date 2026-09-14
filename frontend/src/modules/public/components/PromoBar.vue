<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'
</script>

<template>
  <div class="bg-emerald-900 text-emerald-50 text-xs sm:text-[13px]">
    <div
      class="max-w-7xl mx-auto px-4 sm:px-6 h-9 flex items-center justify-between gap-4 overflow-hidden"
    >
      <div class="flex items-center gap-5 whitespace-nowrap">
        <span class="flex items-center gap-1.5">
          <AppIcon name="clock" :size="14" class="text-emerald-300 flex-shrink-0" />
          Lun-Sáb 7am-7pm · Dom 8am-7pm
        </span>

        <span class="hidden sm:flex items-center gap-1.5">
          <AppIcon name="map-pin" :size="14" class="text-emerald-300 flex-shrink-0" />
          Tesalia, Huila
        </span>
      </div>

      <div class="hidden md:flex items-center gap-5 whitespace-nowrap">
        <a
          href="tel:+573104567890"
          class="flex items-center gap-1.5 hover:text-white transition-colors"
        >
          <AppIcon name="phone" :size="14" class="text-emerald-300 flex-shrink-0" />
          310 456 7890
        </a>

        <RouterLink
          :to="{ name: 'contact' }"
          class="flex items-center gap-1.5 hover:text-white transition-colors"
        >
          <AppIcon name="mail" :size="14" class="text-emerald-300 flex-shrink-0" />
          contacto@tesaliavet.com
        </RouterLink>
      </div>
    </div>
  </div>
</template>
