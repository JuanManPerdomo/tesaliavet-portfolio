<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  value: { type: String, required: true },
  label: { type: String, required: true },
  duration: { type: Number, default: 1500 },
})

const match = props.value.match(/^([+-]?)(\d+)(K)?$/i)
const displayValue = ref(match ? `${match[1]}0${match[3] || ''}` : props.value)
const el = ref(null)

function animate() {
  const [, prefix, digits, suffix] = match
  const target = parseInt(digits, 10)
  const start = performance.now()

  function tick(now) {
    const progress = Math.min((now - start) / props.duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    displayValue.value = `${prefix}${Math.round(target * eased)}${suffix || ''}`
    if (progress < 1) requestAnimationFrame(tick)
  }

  requestAnimationFrame(tick)
}

onMounted(() => {
  if (!match) return

  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        animate()
        observer.unobserve(el.value)
      }
    },
    { threshold: 0.3 }
  )

  observer.observe(el.value)
})
</script>

<template>
  <div ref="el">
    <h3 class="text-3xl font-extrabold text-emerald-700">
      {{ displayValue }}
    </h3>

    <p class="text-slate-500 mt-1 text-sm">
      {{ label }}
    </p>
  </div>
</template>
