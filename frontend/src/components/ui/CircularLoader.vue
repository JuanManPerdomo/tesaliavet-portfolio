<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  label: { type: String, default: 'Cargando...' },
  icon: { type: String, default: 'paw' },
  duration: { type: Number, default: 2000 },
})

const RADIUS = 52
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const progress = ref(0)

onMounted(() => {
  const start = performance.now()

  function tick(now) {
    const linear = Math.min((now - start) / props.duration, 1)
    // ease-out cubico: arranca rapido y cierra suave, se siente menos robotico
    // que una barra lineal.
    const eased = 1 - Math.pow(1 - linear, 3)
    progress.value = Math.round(eased * 100)
    if (linear < 1) requestAnimationFrame(tick)
  }

  requestAnimationFrame(tick)
})

const dashOffset = computed(() => CIRCUMFERENCE * (1 - progress.value / 100))
</script>

<template>
  <div class="flex flex-col items-center gap-6">
    <div class="relative w-32 h-32">
      <svg class="relative w-full h-full" viewBox="0 0 120 120">
        <g transform="rotate(-90 60 60)">
          <circle cx="60" cy="60" :r="RADIUS" fill="none" stroke="#e4f1ec" stroke-width="8" />
          <circle
            cx="60"
            cy="60"
            :r="RADIUS"
            fill="none"
            stroke="#0f6e56"
            stroke-width="8"
            stroke-linecap="round"
            :stroke-dasharray="CIRCUMFERENCE"
            :stroke-dashoffset="dashOffset"
          />
        </g>
      </svg>

      <div class="absolute inset-0 flex items-center justify-center">
        <div
          class="w-14 h-14 rounded-full bg-white shadow-md shadow-emerald-900/10 flex items-center justify-center text-emerald-700 animate-pulse"
        >
          <AppIcon :name="icon" :size="26" />
        </div>
      </div>
    </div>

    <div class="text-center">
      <p class="text-base font-bold text-slate-800">{{ label }}</p>
      <p class="text-sm font-semibold text-emerald-600 mt-1 tabular-nums">{{ progress }}%</p>
    </div>
  </div>
</template>
