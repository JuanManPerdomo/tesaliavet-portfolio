<script setup>
import { computed } from 'vue'
import ProductCard from './ProductCard.vue'

// Cinta continua de velocidad constante ("línea recta extendiéndose
// infinitamente", como lo pidió Juan Manuel) - a diferencia de un carrusel
// de Swiper (avanza, pausa, avanza), acá nunca frena ni acelera. También
// resuelve que Productos Destacados se viera estático con solo 2 productos:
// minItems repite la lista las veces necesarias para que la cinta nunca se
// sienta vacía, sin importar cuántos productos reales haya.
const props = defineProps({
  products: { type: Array, required: true },
  actionLabel: { type: String, default: undefined },
  minItems: { type: Number, default: 6 },
  speed: { type: Number, default: 90 }, // px/segundo, constante
})

const CARD_WIDTH = 288 // w-72
const GAP = 24 // gap-6

const unit = computed(() => {
  if (!props.products.length) return []
  const repeats = Math.max(1, Math.ceil(props.minItems / props.products.length))
  return Array.from({ length: repeats }, () => props.products).flat()
})

// Un solo arreglo plano, la unidad duplicada UNA vez seguida (nunca
// wrappers anidados distintos entre la primera y la segunda copia).
const trackItems = computed(() => [...unit.value, ...unit.value])

// Trasladar por "-50%" del contenedor (en vez de esto) NO da un loop
// perfecto: con gap-6 entre tarjetas, el ancho total tiene (2N-1) gaps pero
// el 50% del ancho no cae justo donde empieza la segunda copia - queda
// corto por GAP/2 (12px), un salto real y visible en cada vuelta (probado
// a mano, verificado con la formula). El calculo correcto es la distancia
// en PIXELES hasta el inicio de la segunda copia: N tarjetas + N gaps
// (el ultimo gap es el que conecta el final de la primera copia con el
// inicio de la segunda) - eso es exactamente N*(CARD_WIDTH+GAP).
const unitWidthPx = computed(() => unit.value.length * (CARD_WIDTH + GAP))
const durationSeconds = computed(() => (unitWidthPx.value / props.speed).toFixed(2))
</script>

<template>
  <div class="marquee-viewport overflow-hidden py-3 -my-3">
    <div
      class="marquee-track flex gap-6 w-max"
      :style="{ animationDuration: `${durationSeconds}s`, '--marquee-distance': `${unitWidthPx}px` }"
    >
      <div
        v-for="(product, index) in trackItems"
        :key="`${index < unit.length ? 'a' : 'b'}-${index}-${product.id}`"
        class="w-72 shrink-0"
        v-bind="index >= unit.length ? { 'aria-hidden': 'true', inert: true } : {}"
      >
        <ProductCard v-bind="product" :action-label="actionLabel" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.marquee-track {
  animation-name: marquee-scroll;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

.marquee-viewport:hover .marquee-track {
  animation-play-state: paused;
}

@keyframes marquee-scroll {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(calc(-1 * var(--marquee-distance)));
  }
}

@media (prefers-reduced-motion: reduce) {
  .marquee-track {
    animation: none;
  }
}
</style>
