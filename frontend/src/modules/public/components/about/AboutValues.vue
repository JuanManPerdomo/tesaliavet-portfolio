<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'

const values = [
  {
    icon: 'heart',
    title: 'Compromiso',
    description: 'Entrega total hacia la salud de cada paciente que cruza nuestra puerta.',
  },
  {
    icon: 'clipboard',
    title: 'Responsabilidad',
    description: 'Manejo ético y seguro de todos nuestros tratamientos y suministros.',
  },
  {
    icon: 'users',
    title: 'Cercanía',
    description: 'Trato humano y cálido para los propietarios y sus compañeros animales.',
  },
  {
    icon: 'lightbulb',
    title: 'Innovación',
    description: 'Búsqueda constante de mejores tecnologías para el agro y la salud.',
  },
]
</script>

<template>
  <section class="mb-24">
    <div class="text-center mb-16">
      <h2 class="text-3xl font-bold text-slate-900 mb-4">Valores institucionales</h2>
      <p class="text-slate-500 max-w-2xl mx-auto">
        Los pilares que sostienen cada una de nuestras acciones y decisiones diarias.
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="value in values"
        :key="value.title"
        class="p-8 text-center rounded-3xl hover:bg-white hover:shadow-sm transition group"
      >
        <div
          class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center text-emerald-700 mx-auto mb-6 group-hover:bg-emerald-700 group-hover:text-white transition"
        >
          <AppIcon :name="value.icon" :size="28" />
        </div>
        <h4 class="font-semibold text-lg text-slate-900 mb-3">{{ value.title }}</h4>
        <p class="text-slate-500 text-sm">{{ value.description }}</p>
      </div>
    </div>
  </section>
</template>
