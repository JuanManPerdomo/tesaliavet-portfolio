<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'
</script>

<template>
  <section
    class="bg-gradient-to-br from-emerald-900 to-emerald-700 text-white px-8 py-16 rounded-b-[40px] flex flex-col lg:flex-row items-center gap-12 mb-10"
  >
    <div class="flex-1">
      <span
        class="inline-flex items-center gap-2 bg-emerald-200 text-emerald-950 text-xs font-bold px-3.5 py-1.5 rounded-full mb-4"
      >
        <AppIcon name="shield" :size="14" /> CUIDADO VETERINARIO Y AGROPECUARIO
      </span>

      <h1 class="text-4xl font-bold mb-4 leading-tight tracking-tight">
        El bienestar de tus animales empieza aquí.
      </h1>

      <p class="text-base text-white/90 leading-relaxed max-w-md">
        Atención veterinaria integral, farmacia especializada y planes de prevención para mascotas y
        ganado de producción.
      </p>
    </div>

    <div class="flex gap-4 shrink-0">
      <div
        class="bg-white/10 backdrop-blur border border-white/20 rounded-2xl p-5 text-center min-w-[110px]"
      >
        <div class="flex justify-center mb-2 text-emerald-200">
          <AppIcon name="clock" :size="24" />
        </div>
        <div class="text-xs font-medium leading-snug">Atención<br />Lun–Sáb</div>
      </div>
      <div
        class="bg-white/10 backdrop-blur border border-white/20 rounded-2xl p-5 text-center min-w-[110px]"
      >
        <div class="flex justify-center mb-2 text-emerald-200">
          <AppIcon name="map-pin" :size="24" />
        </div>
        <div class="text-xs font-medium leading-snug">Tesalia<br />Huila</div>
      </div>
      <div
        class="bg-white/10 backdrop-blur border border-white/20 rounded-2xl p-5 text-center min-w-[110px]"
      >
        <div class="flex justify-center mb-2 text-emerald-200">
          <AppIcon name="phone" :size="24" />
        </div>
        <div class="text-xs font-medium leading-snug">310<br />456 7890</div>
      </div>
    </div>
  </section>
</template>
