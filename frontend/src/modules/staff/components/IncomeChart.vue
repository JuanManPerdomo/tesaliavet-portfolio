<script setup>
import { computed, ref } from 'vue'
import { formatCompactCOP } from '../../../lib/pricing'

const props = defineProps({
  series: { type: Array, default: () => [] }, // [{ label, value }]
  loading: { type: Boolean, default: false },
})

const gradientId = `income-bar-${Math.random().toString(36).slice(2, 9)}`

const WIDTH = 600
const HEIGHT = 220
const PAD_LEFT = 10
const PAD_RIGHT = 10
const CHART_TOP = 34 // deja espacio arriba para el tooltip
const CHART_BOTTOM = 172
const LABEL_Y = 196

const hoveredIndex = ref(null)

const maxValue = computed(() => Math.max(1, ...props.series.map((s) => s.value)))

const chartWidth = computed(() => WIDTH - PAD_LEFT - PAD_RIGHT)
const slotWidth = computed(() => (props.series.length ? chartWidth.value / props.series.length : 0))
const barWidth = computed(() => Math.max(12, slotWidth.value * 0.42))

const bars = computed(() =>
  props.series.map((s, i) => {
    const slotCenter = PAD_LEFT + slotWidth.value * (i + 0.5)
    const barHeight = maxValue.value > 0 ? (s.value / maxValue.value) * (CHART_BOTTOM - CHART_TOP) : 0
    return {
      label: s.label,
      value: s.value,
      x: slotCenter - barWidth.value / 2,
      y: CHART_BOTTOM - barHeight,
      width: barWidth.value,
      height: Math.max(barHeight, s.value > 0 ? 3 : 0),
      cx: slotCenter,
      cy: CHART_BOTTOM - barHeight,
      isLast: i === props.series.length - 1,
    }
  })
)

// Curva suave en vez de una linea recta con esquinas entre cada punto -
// pedido por Juan Manuel ("se ve mas pro"). Spline cubica MONOTONA
// (Hermite, metodo Fritsch-Carlson COMPLETO, 2 pasos) - a proposito, no un
// Catmull-Rom simple: con datos reales de este negocio (casi todo en cero,
// con picos aislados en los dias que sí hubo ventas) una curva suave
// "ingenua" se pasa de largo en los picos y cae por debajo de la linea
// base antes de volver a subir - bug real reportado por Juan Manuel
// ("lineas hacia abajo" alrededor de los picos, ver captura).
//
// Paso 1: tangente en 0 en cada maximo/minimo local (donde la pendiente
// cambia de signo) - esto solo evita el overshoot JUSTO en un pico
// aislado. NO alcanza cuando dos tramos seguidos suben (o bajan) los dos
// pero con pendientes muy distintas (ej. un salto chico seguido de uno
// grande, como el 20 y 21 de agosto en los datos reales) - ahi el paso 1
// solo seguia dejando un overshoot chico mas atras en la curva.
//
// Paso 2 (el que faltaba en el primer intento): limitar la magnitud de
// cada tangente relativa a la pendiente real del tramo (alpha/beta,
// formula original de Fritsch-Carlson) - esto SI garantiza matematicamente
// cero overshoot en cualquier patron de datos, no solo en picos aislados.
// Verificado a mano contra los datos reales exactos que mostraban el
// problema (0 x18, 7140 x19, 192780 x20...): sin el paso 2 sobraban 3.2px
// de curva por debajo de la base: con los 2 pasos, 0px.
const linePath = computed(() => {
  const points = bars.value.map((b) => ({ x: b.cx, y: b.cy }))
  const n = points.length
  if (n < 2) return ''
  if (n === 2) return `M ${points[0].x},${points[0].y} L ${points[1].x},${points[1].y}`

  const slopes = []
  for (let i = 0; i < n - 1; i++) {
    const dx = points[i + 1].x - points[i].x
    slopes.push(dx === 0 ? 0 : (points[i + 1].y - points[i].y) / dx)
  }

  const tangents = [slopes[0]]
  for (let i = 1; i < n - 1; i++) {
    const isLocalExtreme = slopes[i - 1] === 0 || slopes[i] === 0 || (slopes[i - 1] > 0) !== (slopes[i] > 0)
    tangents.push(isLocalExtreme ? 0 : (slopes[i - 1] + slopes[i]) / 2)
  }
  tangents.push(slopes[n - 2])

  for (let i = 0; i < n - 1; i++) {
    const d = slopes[i]
    if (d === 0) {
      tangents[i] = 0
      tangents[i + 1] = 0
      continue
    }
    const alpha = tangents[i] / d
    const beta = tangents[i + 1] / d
    const h = alpha * alpha + beta * beta
    if (h > 9) {
      const t = 3 / Math.sqrt(h)
      tangents[i] = t * alpha * d
      tangents[i + 1] = t * beta * d
    }
  }

  const segments = [`M ${points[0].x},${points[0].y}`]
  for (let i = 0; i < n - 1; i++) {
    const step = (points[i + 1].x - points[i].x) / 3
    const cp1x = points[i].x + step
    const cp1y = points[i].y + tangents[i] * step
    const cp2x = points[i + 1].x - step
    const cp2y = points[i + 1].y - tangents[i + 1] * step
    segments.push(`C ${cp1x},${cp1y} ${cp2x},${cp2y} ${points[i + 1].x},${points[i + 1].y}`)
  }
  return segments.join(' ')
})

// Con muchas barras (ej. un año completo agrupado por mes) las etiquetas se
// amontonan y se vuelven ilegibles - se muestra 1 de cada N para dejar un
// maximo aproximado de 10 etiquetas visibles. El conteo va HACIA ATRAS desde
// la ultima barra (no desde la primera) - bug real reportado por Juan
// Manuel: contando desde el inicio, forzar "siempre mostrar la ultima"
// ademas del paso regular podia dejar dos etiquetas pegadas justo al final
// (ej. 12 meses con paso 2: se mostraban Nov Y Dic, uno de "el paso" y el
// otro de "la ultima", quedando amontonadas). Contando desde el final, la
// ultima siempre cae justo en el patron del paso, sin necesitar el caso
// especial.
const labelStep = computed(() => Math.max(1, Math.ceil(props.series.length / 10)))
function showLabel(index) {
  const lastIndex = props.series.length - 1
  return (lastIndex - index) % labelStep.value === 0
}
</script>

<template>
  <div class="relative">
    <div v-if="loading" class="h-56 flex items-center justify-center text-sm text-slate-400">
      Cargando...
    </div>
    <div v-else-if="!series.length" class="h-56 flex items-center justify-center text-sm text-slate-400">
      Sin datos para este rango.
    </div>
    <svg v-else :viewBox="`0 0 ${WIDTH} ${HEIGHT}`" class="w-full h-56" preserveAspectRatio="none">
      <defs>
        <linearGradient :id="gradientId" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#6ee7b7" />
          <stop offset="100%" stop-color="#10b981" />
        </linearGradient>
      </defs>

      <line
        :x1="PAD_LEFT"
        :y1="CHART_BOTTOM"
        :x2="WIDTH - PAD_RIGHT"
        :y2="CHART_BOTTOM"
        stroke="#e2e8f0"
        stroke-width="1"
      />

      <!-- barras -->
      <rect
        v-for="(b, i) in bars"
        :key="`bar-${i}`"
        :x="b.x"
        :y="b.y"
        :width="b.width"
        :height="b.height"
        rx="6"
        :fill="b.isLast ? '#047857' : `url(#${gradientId})`"
        :opacity="hoveredIndex === null || hoveredIndex === i ? 1 : 0.55"
        class="transition-opacity"
      />

      <!-- linea conectando los topes -->
      <path :d="linePath" fill="none" stroke="#047857" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      <circle
        v-for="(b, i) in bars"
        :key="`dot-${i}`"
        :cx="b.cx"
        :cy="b.cy"
        r="3.5"
        fill="white"
        stroke="#047857"
        stroke-width="2"
      />

      <!-- zonas de hover (invisibles, cubren todo el alto del slot) -->
      <rect
        v-for="(b, i) in bars"
        :key="`hover-${i}`"
        :x="PAD_LEFT + slotWidth * i"
        y="0"
        :width="slotWidth"
        :height="CHART_BOTTOM"
        fill="transparent"
        style="cursor: pointer"
        @mouseenter="hoveredIndex = i"
        @mouseleave="hoveredIndex = null"
      />

      <!-- etiquetas del eje -->
      <text
        v-for="(b, i) in bars"
        v-show="showLabel(i)"
        :key="`label-${i}`"
        :x="b.cx"
        :y="LABEL_Y"
        text-anchor="middle"
        class="fill-slate-400"
        :class="b.isLast ? 'font-bold' : ''"
        style="font-size: 11px"
      >
        {{ b.label }}
      </text>

      <!-- tooltip -->
      <g v-if="hoveredIndex !== null" :transform="`translate(${bars[hoveredIndex].cx}, ${bars[hoveredIndex].y - 14})`">
        <rect x="-28" y="-20" width="56" height="22" rx="6" fill="#0f172a" />
        <polygon points="-4,2 4,2 0,8" fill="#0f172a" />
        <text x="0" y="-5" text-anchor="middle" fill="white" style="font-size: 11px; font-weight: 700">
          {{ formatCompactCOP(bars[hoveredIndex].value) }}
        </text>
      </g>
    </svg>
  </div>
</template>
