<script setup>
import { icons } from './icons.js'

defineProps({
  name: { type: String, required: true },
  size: { type: [String, Number], default: 20 },
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    :fill="icons[name]?.filled ? 'currentColor' : 'none'"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <rect v-if="icons[name]?.rect" v-bind="icons[name].rect" />
    <circle v-for="(c, i) in icons[name]?.circles" :key="'c' + i" :cx="c.cx" :cy="c.cy" :r="c.r" />
    <path v-for="(p, i) in icons[name]?.paths" :key="'p' + i" :d="p" />
  </svg>
</template>
