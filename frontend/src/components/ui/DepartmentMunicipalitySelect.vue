<script setup>
import { computed } from 'vue'
import { COLOMBIA_DEPARTMENTS } from '../../lib/colombiaLocations'

const props = defineProps({
  departamento: { type: String, default: '' },
  municipio: { type: String, default: '' },
})

const emit = defineEmits(['update:departamento', 'update:municipio'])

const municipalities = computed(
  () => COLOMBIA_DEPARTMENTS.find((d) => d.name === props.departamento)?.municipalities || []
)

function handleDepartamentoChange(event) {
  const value = event.target.value
  emit('update:departamento', value)
  // Si el municipio actual no pertenece al nuevo departamento, se resetea -
  // evita dejar seleccionado un municipio de otro departamento por error.
  const nextMunicipalities = COLOMBIA_DEPARTMENTS.find((d) => d.name === value)?.municipalities || []
  if (!nextMunicipalities.includes(props.municipio)) {
    emit('update:municipio', '')
  }
}

function handleMunicipioChange(event) {
  emit('update:municipio', event.target.value)
}
</script>

<template>
  <div class="grid sm:grid-cols-2 gap-4">
    <div>
      <label class="block text-xs font-semibold text-slate-500 mb-1">Departamento</label>
      <select
        :value="departamento"
        class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @change="handleDepartamentoChange"
      >
        <option value="">Selecciona un departamento</option>
        <option v-for="d in COLOMBIA_DEPARTMENTS" :key="d.name" :value="d.name">{{ d.name }}</option>
      </select>
    </div>

    <div>
      <label class="block text-xs font-semibold text-slate-500 mb-1">Municipio</label>
      <select
        :value="municipio"
        :disabled="!departamento"
        class="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-50 disabled:text-slate-400"
        @change="handleMunicipioChange"
      >
        <option value="">{{ departamento ? 'Selecciona un municipio' : 'Elige primero un departamento' }}</option>
        <option v-for="m in municipalities" :key="m" :value="m">{{ m }}</option>
      </select>
    </div>
  </div>
</template>
