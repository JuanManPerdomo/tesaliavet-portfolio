<script setup>
import { computed, ref } from 'vue'
import { getPresetRange } from '../../../lib/reportDatePresets'

const props = defineProps({
  dateFrom: { type: String, default: '' },
  dateTo: { type: String, default: '' },
})
const emit = defineEmits(['update:dateFrom', 'update:dateTo', 'change'])

const PRESETS = [
  { value: 'hoy', label: 'Hoy' },
  { value: 'semana', label: 'Esta semana' },
  { value: 'mes', label: 'Este mes' },
  { value: 'anio', label: 'Este año' },
]

// Bug real reportado por Juan Manuel: el lunes, "Hoy" y "Esta semana"
// calculan exactamente el mismo rango (la semana recien empieza) - derivar
// el atajo activo solo de las fechas (como antes) siempre encontraba "Hoy"
// primero en la lista y lo marcaba activo aunque se hubiera hecho clic en
// "Esta semana". Ahora se recuerda cuál botón se clickeó explícitamente;
// solo se vuelve a derivar de las fechas si el usuario edita los inputs a
// mano (ahí sí puede no coincidir con ningún atajo, o coincidir con otro).
const clickedPreset = ref(null)

const activePreset = computed(() => {
  if (clickedPreset.value !== null) return clickedPreset.value
  for (const preset of PRESETS) {
    const range = getPresetRange(preset.value)
    if (range.dateFrom === props.dateFrom && range.dateTo === props.dateTo) return preset.value
  }
  return ''
})

function applyPreset(preset) {
  clickedPreset.value = preset
  const range = getPresetRange(preset)
  emit('update:dateFrom', range.dateFrom)
  emit('update:dateTo', range.dateTo)
  emit('change')
}

function handleFromChange(event) {
  clickedPreset.value = null
  emit('update:dateFrom', event.target.value)
  emit('change')
}

function handleToChange(event) {
  clickedPreset.value = null
  emit('update:dateTo', event.target.value)
  emit('change')
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <div class="flex gap-1 bg-slate-50 rounded-lg p-1">
      <button
        v-for="preset in PRESETS"
        :key="preset.value"
        type="button"
        class="px-3 py-1.5 rounded-md text-xs font-semibold transition"
        :class="
          activePreset === preset.value
            ? 'bg-white text-emerald-700 shadow-sm'
            : 'text-slate-500 hover:text-emerald-700'
        "
        @click="applyPreset(preset.value)"
      >
        {{ preset.label }}
      </button>
    </div>
    <input
      :value="dateFrom"
      type="date"
      class="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
      @change="handleFromChange"
    />
    <span class="text-slate-400 text-sm">—</span>
    <input
      :value="dateTo"
      type="date"
      class="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
      @change="handleToChange"
    />
  </div>
</template>
