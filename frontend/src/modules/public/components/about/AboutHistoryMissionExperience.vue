<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'
</script>

<template>
  <section class="mb-24">
    <h2 class="text-3xl font-bold text-center text-slate-900 mb-16">
      Historia, misión y experiencia
    </h2>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div
        class="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 hover:shadow-xl transition"
      >
        <div
          class="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-5"
        >
          <AppIcon name="book" :size="28" />
        </div>
        <h3 class="text-xl font-bold text-slate-900 mb-3">Historia</h3>
        <p class="text-slate-600 leading-relaxed">
          Nacimos como una pequeña farmacia veterinaria familiar con un propósito claro: servir a
          los productores de Huila con honestidad y conocimiento técnico especializado.
        </p>
      </div>

      <div class="bg-emerald-700 text-white p-8 rounded-3xl shadow-xl hover:shadow-2xl transition">
        <div class="w-14 h-14 rounded-2xl bg-white/15 flex items-center justify-center mb-5">
          <AppIcon name="flag" :size="28" />
        </div>
        <h3 class="text-xl font-bold mb-3">Misión</h3>
        <p class="text-white/90 leading-relaxed">
          Garantizar el bienestar animal y la productividad del campo mediante el suministro
          responsable de medicamentos, alimentos y asesoría veterinaria de excelencia.
        </p>
      </div>

      <div
        class="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 hover:shadow-xl transition"
      >
        <div
          class="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-5"
        >
          <AppIcon name="stethoscope" :size="28" />
        </div>
        <h3 class="text-xl font-bold text-slate-900 mb-3">Experiencia</h3>
        <p class="text-slate-600 leading-relaxed">
          Contamos con un equipo de profesionales apasionados que han atendido a miles de mascotas y
          ganado, estableciendo un legado de salud animal impecable.
        </p>
      </div>
    </div>
  </section>
</template>
