<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Pagination, Autoplay } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

import { onMounted } from 'vue'
import SectionHeader from '../../../components/common/SectionHeader.vue'
import ProductCard from './products/ProductCard.vue'
import { useProductsStore } from '../../../stores/products'

defineProps({
  badge: { type: String, default: 'Productos destacados' },
  title: { type: String, default: 'Todo para el cuidado animal.' },
  description: {
    type: String,
    default:
      'Descubre productos veterinarios y agropecuarios seleccionados para garantizar el bienestar y la salud de tus animales.',
  },
  actionLabel: { type: String, default: 'Ver más' },
})

const productsStore = useProductsStore()

onMounted(() => {
  productsStore.fetchFeaturedProducts()
})
</script>

<template>
  <section class="py-16 bg-white overflow-hidden">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Header: centrado, como el resto de las secciones del Home
           (Categorías, Servicios) - antes el bloque de texto quedaba a la
           izquierda con el botón encajado a la derecha, se sentía
           desalineado con el resto de la página. -->
      <div v-reveal class="text-center mb-14">
        <SectionHeader :badge="badge" :title="title" :description="description" class="mx-auto" />

        <RouterLink
          to="/productos"
          class="mt-8 inline-flex bg-emerald-700 hover:bg-emerald-800 text-white px-8 py-4 rounded-2xl font-semibold transition shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
        >
          Ver catálogo completo
        </RouterLink>
      </div>

      <p v-if="productsStore.featuredLoading" class="text-slate-500 text-center">Cargando productos...</p>

      <p v-else-if="!productsStore.featuredProducts.length" class="text-slate-500 text-center">
        Todavía no tenemos suficientes ventas registradas para mostrar destacados.
      </p>

      <!-- Carrusel con flechas y puntos (avanza-pausa, con movimiento pero
           sin ser una cinta continua) - pedido explícito de Juan Manuel:
           "no que sea así carrusel seguido... sino más bien como estaba
           antes con las cositas abajo para mirar en dónde va el carrusel".
           Sin `loop`: con pocos productos reales (hoy 2), el loop de Swiper
           duplica slides de forma poco confiable - sin loop, autoplay
           igual avanza y vuelve al inicio solo (rewind).

           flex justify-center + w-fit en el propio Swiper: con
           slides-per-view="auto" y pocos productos, Swiper NUNCA centra su
           contenido solo (decision 68 - centerInsufficientSlides ya se
           probó y no funciona en este proyecto), queda pegado a la
           izquierda con un hueco grande a la derecha. w-fit funciona sin
           problema circular porque cada slide ya tiene un ancho explícito
           (!w-72) - no depende del ancho del contenedor para medirse.
           max-w-full: si el catálogo real crece más allá de lo que cabe en
           pantalla, el Swiper vuelve a ocupar todo el ancho y scrollea
           normal, sin quedar centrado a la fuerza fuera de la pantalla. -->
      <div v-else v-reveal="{ delay: 150 }" class="flex justify-center">
        <Swiper
          :modules="[Navigation, Pagination, Autoplay]"
          slides-per-view="auto"
          :space-between="24"
          :navigation="true"
          :pagination="{ clickable: true }"
          :autoplay="{ delay: 3500, disableOnInteraction: false, pauseOnMouseEnter: true }"
          rewind
          class="featured-products-swiper !pb-12 w-fit max-w-full"
        >
          <SwiperSlide
            v-for="product in productsStore.featuredProducts"
            :key="product.id"
            class="!w-72"
          >
            <ProductCard v-bind="product" :action-label="actionLabel" />
          </SwiperSlide>
        </Swiper>
      </div>
    </div>
  </section>
</template>

<style scoped>
.featured-products-swiper :deep(.swiper-button-next),
.featured-products-swiper :deep(.swiper-button-prev) {
  color: #047857;
  background: white;
  width: 44px;
  height: 44px;
  border-radius: 9999px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}

.featured-products-swiper :deep(.swiper-button-next)::after,
.featured-products-swiper :deep(.swiper-button-prev)::after {
  font-size: 16px;
  font-weight: bold;
}

.featured-products-swiper :deep(.swiper-pagination-bullet) {
  background: #10b981;
  opacity: 0.3;
  width: 9px;
  height: 9px;
}

.featured-products-swiper :deep(.swiper-pagination-bullet-active) {
  opacity: 1;
  background: #047857;
  width: 24px;
  border-radius: 9999px;
}
</style>
