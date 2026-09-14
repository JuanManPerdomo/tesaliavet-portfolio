<script setup>
import { computed } from 'vue'

// Colores puramente decorativos (identidad, no estado) - deliberadamente
// distintos de emerald/amber/red, que ya estan reservados en el panel para
// activo/advertencia/peligro.
const PALETTE = [
  'bg-sky-100 text-sky-700',
  'bg-violet-100 text-violet-700',
  'bg-rose-100 text-rose-700',
  'bg-indigo-100 text-indigo-700',
  'bg-teal-100 text-teal-700',
]

const props = defineProps({
  firstName: { type: String, default: '' },
  lastName: { type: String, default: '' },
  size: { type: Number, default: 40 },
})

const initials = computed(() => `${props.firstName[0] || ''}${props.lastName[0] || ''}`.toUpperCase())

const colorClass = computed(() => {
  const seed = (props.firstName + props.lastName).length
  return PALETTE[seed % PALETTE.length]
})
</script>

<template>
  <div
    class="rounded-full flex items-center justify-center font-bold flex-shrink-0"
    :class="colorClass"
    :style="{ width: `${size}px`, height: `${size}px`, fontSize: `${size * 0.4}px` }"
  >
    {{ initials }}
  </div>
</template>
