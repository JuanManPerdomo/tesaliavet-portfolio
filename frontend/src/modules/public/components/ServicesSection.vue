<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'
</script>

<template>
  <section class="py-16 bg-slate-50">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Header -->
      <div class="text-center max-w-3xl mx-auto mb-14">
        <span
          class="inline-flex bg-emerald-100 text-emerald-700 px-5 py-2.5 rounded-full text-base font-semibold"
        >
          Nuestros servicios
        </span>

        <h2 class="mt-5 text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight">
          Atención integral para el cuidado animal.
        </h2>

        <p class="mt-5 text-lg text-slate-600 leading-relaxed">
          Servicios veterinarios especializados enfocados en la salud, prevención y bienestar de
          mascotas y animales de producción.
        </p>
      </div>

      <!-- Services Grid -->
      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Card 1 -->
        <div
          v-reveal
          class="group bg-white rounded-3xl p-8 border border-slate-100 hover:shadow-2xl hover:-translate-y-2 transition duration-300"
        >
          <!-- Icon -->
          <div
            class="w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-700 group-hover:bg-emerald-700 group-hover:text-white group-hover:-rotate-6 transition-all duration-300"
          >
            <AppIcon name="medical-cross" :size="28" />
          </div>

          <!-- Content -->
          <h3 class="mt-6 text-2xl font-bold text-slate-900">Consulta veterinaria</h3>

          <p class="mt-4 text-slate-600 leading-relaxed">
            Atención clínica especializada para mascotas y animales de producción. Diagnóstico,
            tratamiento y seguimiento.
          </p>

          <!-- Link -->
          <RouterLink
            to="/mis-citas"
            class="mt-8 flex items-center gap-2 text-emerald-700 font-semibold group-hover:gap-3 transition-all"
          >
            Agendar cita →
          </RouterLink>
        </div>

        <!-- Card 2 -->
        <div
          v-reveal="{ delay: 120 }"
          class="group bg-white rounded-3xl p-8 border border-slate-100 hover:shadow-2xl hover:-translate-y-2 transition duration-300"
        >
          <!-- Icon -->
          <div
            class="w-16 h-16 rounded-2xl bg-teal-100 flex items-center justify-center text-teal-700 group-hover:bg-teal-700 group-hover:text-white group-hover:-rotate-6 transition-all duration-300"
          >
            <AppIcon name="pill" :size="28" />
          </div>

          <!-- Content -->
          <h3 class="mt-6 text-2xl font-bold text-slate-900">Farmacia veterinaria</h3>

          <p class="mt-4 text-slate-600 leading-relaxed">
            Amplio catálogo de medicamentos, antibióticos, antiparasitarios y suplementos.
            Disponible para entrega inmediata.
          </p>

          <!-- Link -->
          <RouterLink
            to="/cuidado-animal"
            class="mt-8 flex items-center gap-2 text-emerald-700 font-semibold group-hover:gap-3 transition-all"
          >
            Ver productos →
          </RouterLink>
        </div>

        <!-- Card 3 -->
        <div
          v-reveal="{ delay: 240 }"
          class="group bg-white rounded-3xl p-8 border border-slate-100 hover:shadow-2xl hover:-translate-y-2 transition duration-300"
        >
          <!-- Icon -->
          <div
            class="w-16 h-16 rounded-2xl bg-cyan-100 flex items-center justify-center text-cyan-700 group-hover:bg-cyan-700 group-hover:text-white group-hover:-rotate-6 transition-all duration-300"
          >
            <AppIcon name="droplet" :size="28" />
          </div>

          <!-- Content -->
          <h3 class="mt-6 text-2xl font-bold text-slate-900">Plan de vacunación</h3>

          <p class="mt-4 text-slate-600 leading-relaxed">
            Planes personalizados de vacunación para mascotas con recordatorios automáticos y
            seguimiento del esquema completo.
          </p>

          <!-- Link -->
          <RouterLink
            to="/cuidado-animal"
            class="mt-8 flex items-center gap-2 text-emerald-700 font-semibold group-hover:gap-3 transition-all"
          >
            Ver planes →
          </RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>
