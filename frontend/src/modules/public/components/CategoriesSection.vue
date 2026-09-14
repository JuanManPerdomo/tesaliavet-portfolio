<script setup>
import SectionHeader from '../../../components/common/SectionHeader.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'

// Solo los 2 pilares reales del negocio (Mascotas/Ganadería, categorias de
// nivel 1 - decision 19/20), no una mezcla de niveles como traia el mockup
// original (mezclaba categorias padre con subcategorias medicas sueltas).
// Ganaderia enlaza a su categoria real aunque hoy este vacia de productos -
// es honesto (categoria real, no dato inventado, decision 7) y consistente
// con como ya se comporta el catalogo publico para ese tab (decision 37).
const categories = [
  {
    name: 'Mascotas',
    query: 'mascotas',
    description: 'Alimentos, medicamentos, accesorios y cuidado para tus mascotas.',
    // Perro y gato juntos, foto horizontal a color con aire alrededor
    image: 'https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?q=80&w=1200&auto=format&fit=crop',
    icon: 'paw',
  },
  {
    name: 'Ganadería',
    query: 'ganaderia',
    description: 'Insumos y soluciones para el cuidado de animales de producción.',
    // Ganado en potrero, foto horizontal a color con aire alrededor
    image: 'https://images.unsplash.com/photo-1778064731318-fa2bc70f5635?q=80&w=1200&auto=format&fit=crop',
    icon: 'leaf',
  },
]
</script>

<template>
  <section class="py-16 bg-emerald-50/40">
    <div class="max-w-7xl mx-auto px-6">
      <div v-reveal class="text-center mb-14">
        <SectionHeader
          badge="Categorías"
          title="Encuentra lo que necesitas"
          description="Dos líneas de negocio, una sola veterinaria de confianza."
          class="mx-auto"
        />
      </div>

      <div class="grid sm:grid-cols-2 gap-8">
        <RouterLink
          v-for="(category, index) in categories"
          :key="category.query"
          v-reveal="{ delay: index * 150 }"
          :to="{ path: '/productos', query: { categoria: category.query } }"
          class="group relative rounded-3xl overflow-hidden shadow-lg hover:shadow-2xl hover:-translate-y-1 transition-all"
        >
          <div class="aspect-[4/3] sm:aspect-[16/11]">
            <img
              :src="category.image"
              :alt="category.name"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          </div>

          <div
            class="absolute inset-0 bg-gradient-to-t from-slate-900/85 via-slate-900/20 to-transparent"
          ></div>

          <div class="absolute inset-x-0 bottom-0 p-6 sm:p-8">
            <div
              class="flex w-fit items-center gap-2 bg-white/15 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold mb-4"
            >
              <AppIcon :name="category.icon" :size="16" />
              {{ category.name }}
            </div>

            <p class="text-white/85 leading-relaxed max-w-sm mb-4">
              {{ category.description }}
            </p>

            <span
              class="inline-flex items-center gap-1.5 text-white font-semibold group-hover:gap-2.5 transition-all"
            >
              Explorar
              <AppIcon name="chevron-right" :size="18" />
            </span>
          </div>
        </RouterLink>
      </div>
    </div>
  </section>
</template>
