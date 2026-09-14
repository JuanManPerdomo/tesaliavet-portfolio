<script setup>
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import SecondaryButton from '../../../../components/ui/SecondaryButton.vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
</script>

<template>
  <section class="bg-emerald-700 text-white rounded-[2.5rem] p-10 lg:p-20 text-center shadow-xl">
    <h2 class="text-3xl sm:text-4xl font-extrabold mb-6">¿Listo para cuidar mejor a tu animal?</h2>
    <p class="text-white/90 text-lg mb-10 max-w-2xl mx-auto">
      Unimos tecnología y corazón para que tus mascotas y ganado reciban siempre lo mejor.
    </p>

    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <SecondaryButton to="/mis-citas" class="inline-flex items-center gap-2">
        <AppIcon name="calendar" :size="18" /> Agendar cita
      </SecondaryButton>
      <PrimaryButton to="/productos" class="inline-flex items-center gap-2">
        <AppIcon name="shopping-cart" :size="18" /> Ver productos
      </PrimaryButton>
    </div>
  </section>
</template>
