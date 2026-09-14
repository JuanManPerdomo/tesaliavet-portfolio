<script setup>
import { onMounted } from 'vue'
import SectionHeader from '../../../components/common/SectionHeader.vue'
import ProductMarquee from './products/ProductMarquee.vue'
import { useProductsStore } from '../../../stores/products'

const productsStore = useProductsStore()

onMounted(async () => {
  // Excluye lo que ya se ve en "Productos Destacados" justo arriba - se
  // espera su propio fetch aca (en vez de leer featuredProducts a ciegas)
  // porque FeaturedProducts.vue monta en paralelo, no antes: sin este await
  // la lista de exclusion podria quedar vacia por una carrera real.
  await productsStore.fetchFeaturedProducts()
  const excludeIds = productsStore.featuredProducts.map((p) => p.id)
  productsStore.fetchRandomProducts(8, excludeIds)
})
</script>

<template>
  <section v-if="productsStore.randomLoading || productsStore.randomProducts.length" class="py-16 bg-slate-50 overflow-hidden">
    <div class="max-w-7xl mx-auto px-6">
      <div v-reveal class="text-center mb-14">
        <SectionHeader
          badge="Explora más"
          title="Podrían interesarte."
          description="Una selección distinta cada vez que visitas la tienda — date una vuelta por el catálogo."
          class="mx-auto"
        />
      </div>

      <p v-if="productsStore.randomLoading" class="text-slate-500 text-center">Cargando productos...</p>

      <!-- Cinta continua de velocidad constante ("línea recta extendiéndose
           infinitamente"), no un carrusel de avanza-pausa - mismo
           componente que Productos Destacados. -->
      <ProductMarquee v-else v-reveal="{ delay: 150 }" :products="productsStore.randomProducts" :speed="110" />
    </div>
  </section>
</template>
