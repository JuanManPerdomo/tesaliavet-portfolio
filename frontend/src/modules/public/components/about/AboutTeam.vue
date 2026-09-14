<script setup>
// TODO: reemplaza esta URL por la de tu Cloudinary/CDN cuando la tengas
const team = [
  {
    name: 'Dr. Rodrigo Méndez',
    role: 'Director Médico - Cirujano y Especialista',
    image:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBHX4yVmZVUnA-J2-SrRWU4q4SwKwVToJAknS7Ewt7O2vJNlCk3N8FCDZiR4K5p_Tj7gd7AGjKfvDuZ_9YojIfMAYHFMK6prVCi-D3LZDd8-kzpd6kEDoGerpMgXjESwUd7vRLqWcDLftJRPp93nSrxfWmHYW0B-gZTMuSRw-9_1HAvA6yyOaBrruu_pqxebnFhvO8xHL0w1iyrUxNVpRl6oe_n5RD4scDMrpQAHgXtL_xKP_pg6Lvn',
  },
]
</script>

<template>
  <section class="mb-24">
    <h2 class="text-3xl font-bold text-center text-slate-900 mb-16">Nuestro equipo veterinario</h2>

    <div class="flex justify-center">
      <div v-for="member in team" :key="member.name" class="group w-full max-w-xs">
        <div class="relative overflow-hidden rounded-3xl aspect-[4/5] mb-6 bg-slate-100">
          <img
            :src="member.image"
            :alt="member.name"
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          />
        </div>
        <div class="text-center">
          <h4 class="text-xl font-bold text-slate-900 mb-1">{{ member.name }}</h4>
          <p class="text-emerald-700 text-sm font-semibold">{{ member.role }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
