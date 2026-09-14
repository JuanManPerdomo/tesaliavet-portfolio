<script setup>
defineProps({
  badge: { type: String, default: null },
  title: { type: String, required: true },
  description: { type: String, default: null },
})
</script>

<template>
  <div class="max-w-3xl">
    <!-- Badge: inline-flex (no mx-auto) para heredar el text-align del
         contenedor - centrado si el llamador envuelve en text-center
         (ej. CategoriesSection.vue), pegado a la izquierda si no
         (ej. FeaturedProducts.vue). Con "flex w-fit mx-auto" se centraba
         siempre, aunque el título/descripción de abajo quedaran a la
         izquierda - se veía torcido. -->
    <span
      v-if="badge"
      class="inline-flex w-fit bg-emerald-100 text-emerald-700 px-5 py-2.5 rounded-full text-base font-semibold"
    >
      {{ badge }}
    </span>

    <!-- Title -->
    <h2 class="mt-5 text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight">
      {{ title }}
    </h2>

    <!-- Description -->
    <p v-if="description" class="mt-5 text-slate-600 text-lg leading-relaxed">
      {{ description }}
    </p>
  </div>
</template>
