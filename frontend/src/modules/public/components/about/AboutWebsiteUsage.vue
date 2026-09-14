<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'
</script>

<template>
  <section class="bg-white rounded-[2.5rem] p-10 lg:p-16 mb-24 border border-slate-100">
    <div class="max-w-3xl">
      <h2 class="text-3xl font-bold text-slate-900 mb-8">Uso del sitio web</h2>

      <p class="text-slate-600 text-lg mb-6">
        Esta plataforma ha sido diseñada para ser el puente digital entre su necesidad de cuidado
        animal y nuestras soluciones expertas. A través de este portal, los usuarios pueden:
      </p>

      <ul class="space-y-4 text-slate-600 text-lg">
        <li class="flex items-start gap-4">
          <AppIcon name="check" :size="20" class="text-emerald-700 mt-1" />
          <span>Explorar nuestro catálogo completo de medicamentos y productos agropecuarios.</span>
        </li>
        <li class="flex items-start gap-4">
          <AppIcon name="check" :size="20" class="text-emerald-700 mt-1" />
          <span>Agendar citas presenciales con nuestro equipo veterinario de manera ágil.</span>
        </li>
        <li class="flex items-start gap-4">
          <AppIcon name="check" :size="20" class="text-emerald-700 mt-1" />
          <span>Acceder a guías de cuidado animal actualizadas por especialistas.</span>
        </li>
      </ul>
    </div>
  </section>
</template>
