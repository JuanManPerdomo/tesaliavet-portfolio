<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'

const steps = [
  {
    icon: 'search',
    title: 'Explora el catálogo',
    description:
      'Busca medicamentos, alimentos y accesorios filtrando por especie, categoría o precio.',
    to: '/productos',
    cta: 'Ver productos',
  },
  {
    icon: 'calendar',
    title: 'Agenda o compra',
    description:
      'Reserva tu cita veterinaria en el horario disponible o arma tu pedido en minutos.',
    to: '/mis-citas',
    cta: 'Agendar cita',
  },
  {
    icon: 'shield-check',
    title: 'Recibe atención',
    description:
      'Nuestro equipo profesional acompaña a tu mascota o animal con seguimiento real.',
    to: '/cuidado-animal',
    cta: 'Conocer servicios',
  },
]
</script>

<template>
  <section class="py-16 bg-white">
    <div class="max-w-7xl mx-auto px-6">
      <div v-reveal class="text-center max-w-2xl mx-auto mb-16">
        <span
          class="inline-flex bg-emerald-100 text-emerald-700 px-5 py-2.5 rounded-full text-base font-semibold"
        >
          Cómo funciona
        </span>

        <h2 class="mt-5 text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight">
          Tres pasos y listo.
        </h2>

        <p class="mt-5 text-lg text-slate-600 leading-relaxed">
          Así de simple es empezar a cuidar a tus animales con TesaliaVet.
        </p>
      </div>

      <div class="relative grid md:grid-cols-3 gap-10 md:gap-8">
        <!-- Connector line (desktop only) -->
        <div
          class="hidden md:block absolute top-8 left-[16.5%] right-[16.5%] border-t-2 border-dashed border-emerald-200"
        ></div>

        <RouterLink
          v-for="(step, index) in steps"
          :key="step.title"
          v-reveal="{ delay: index * 150 }"
          :to="step.to"
          class="group relative flex flex-col items-center text-center"
        >
          <!-- Icon circle -->
          <div class="relative z-10">
            <div
              class="w-16 h-16 rounded-2xl bg-emerald-700 text-white flex items-center justify-center shadow-lg shadow-emerald-700/20 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-300"
            >
              <AppIcon :name="step.icon" :size="26" />
            </div>

            <span
              class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-white border-2 border-emerald-700 text-emerald-700 text-xs font-extrabold flex items-center justify-center"
            >
              {{ index + 1 }}
            </span>
          </div>

          <h3 class="mt-6 text-xl font-bold text-slate-900">
            {{ step.title }}
          </h3>

          <p class="mt-3 text-slate-600 leading-relaxed max-w-xs">
            {{ step.description }}
          </p>

          <span
            class="mt-5 flex items-center gap-1.5 text-emerald-700 font-semibold text-sm group-hover:gap-2.5 transition-all"
          >
            {{ step.cta }}
            <AppIcon name="chevron-right" :size="16" />
          </span>
        </RouterLink>
      </div>
    </div>
  </section>
</template>
