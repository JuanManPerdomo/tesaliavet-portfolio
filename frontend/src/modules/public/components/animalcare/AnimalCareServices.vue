<script setup>
import AnimalCareServiceCard from './AnimalCareServiceCard.vue'

const services = [
  {
    icon: 'stethoscope',
    iconBg: 'bg-emerald-50 text-emerald-700',
    name: 'Consulta Veterinaria',
    description:
      'Atención clínica especializada por médicos veterinarios titulados. Diagnóstico, tratamiento y formulación.',
    features: ['Consulta general y urgencias', 'Diagnóstico por imagen', 'Seguimiento preventivo'],
    buttonIcon: 'calendar',
    buttonText: 'Agendar cita',
    buttonRoute: '/mis-citas',
    footerTag: 'Usuario registrado',
  },
  {
    icon: 'pill',
    iconBg: 'bg-blue-50 text-blue-700',
    name: 'Farmacia Veterinaria',
    description:
      'Medicamentos, antibióticos, antiparasitarios y suplementos. Disponibilidad inmediata y pedidos en línea.',
    features: ['Antibióticos y analgésicos', 'Control de parásitos', 'Nutrición avanzada'],
    buttonIcon: 'shopping-bag',
    buttonText: 'Ver productos',
    buttonRoute: '/productos',
    footerLinkText: 'Catálogo completo →',
    footerLinkRoute: '/productos',
  },
  {
    icon: 'droplet',
    iconBg: 'bg-amber-50 text-amber-700',
    name: 'Plan de Vacunación',
    description:
      'Esquemas completos de inmunización con recordatorios automáticos para mascotas y animales de granja.',
    features: ['Historial digital de vacunas', 'Alertas de refuerzo', 'Certificados oficiales'],
    buttonIcon: 'calendar',
    buttonText: 'Agendar',
    buttonRoute: '/mis-citas',
    footerTag: 'Usuario registrado',
  },
]
</script>

<template>
  <section class="mb-12">
    <div class="text-sm font-bold text-emerald-700 uppercase tracking-wide mb-6">
      Nuestros servicios especializados
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <AnimalCareServiceCard v-for="service in services" :key="service.name" v-bind="service" />
    </div>
  </section>
</template>
