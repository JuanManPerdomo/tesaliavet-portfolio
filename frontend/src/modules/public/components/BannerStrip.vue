<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'
</script>

<template>
  <section class="py-14">
    <div class="max-w-7xl mx-auto px-6">
      <div
        v-reveal
        class="relative overflow-hidden rounded-[36px] bg-gradient-to-r from-emerald-700 via-teal-600 to-emerald-800 px-10 py-14 lg:px-16"
      >
        <!-- Decorative circles -->
        <div class="absolute -top-16 -right-16 w-64 h-64 bg-white/10 rounded-full"></div>

        <div class="absolute -bottom-24 -left-16 w-72 h-72 bg-white/5 rounded-full"></div>

        <AppIcon
          name="paw"
          :size="140"
          class="hidden lg:block absolute top-1/2 -translate-y-1/2 -right-4 text-white/10 rotate-12"
        />

        <!-- Content -->
        <div
          class="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-10"
        >
          <!-- Left -->
          <div class="max-w-2xl">
            <span
              class="flex w-fit bg-white/20 backdrop-blur-sm text-white px-5 py-2.5 rounded-full text-base font-semibold"
            >
              Atención especializada
            </span>

            <h2
              class="mt-5 text-4xl lg:text-5xl font-extrabold text-white leading-tight tracking-tight"
            >
              Cuidamos la salud y bienestar de tus animales.
            </h2>

            <p class="mt-5 text-emerald-50 text-lg leading-relaxed">
              Agenda citas veterinarias, encuentra productos especializados y recibe atención
              profesional para tus mascotas y animales de producción.
            </p>
          </div>

          <!-- Right -->
          <div class="flex flex-col sm:flex-row gap-4">
            <RouterLink
              to="/mis-citas"
              class="inline-flex items-center justify-center gap-2 bg-white text-emerald-700 hover:bg-slate-100 px-7 py-4 rounded-2xl font-bold transition shadow-lg"
            >
              <AppIcon name="calendar" :size="18" /> Agendar cita
            </RouterLink>

            <RouterLink
              to="/cuidado-animal"
              class="inline-flex items-center justify-center gap-2 border border-white/30 hover:bg-white/10 text-white px-7 py-4 rounded-2xl font-bold transition"
            >
              <AppIcon name="stethoscope" :size="18" /> Ver servicios
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
