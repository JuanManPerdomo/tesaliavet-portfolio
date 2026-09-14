<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { EffectFade } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/effect-fade'

import SecondaryButton from '../../../components/ui/SecondaryButton.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import StatCard from '../../../components/cards/StatCard.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import api from '../../../lib/api'

// 3 mensajes que rotan (texto + imagen + tarjeta flotante juntos) para
// mostrar las 3 propuestas de valor reales del negocio sin saturar una sola
// pantalla - inspirado en un mockup que mandó Juan Manuel, pero reconstruido
// con Swiper (ya instalado, decision 2: nunca JS vainilla para esto) en vez
// del carrusel en JS plano del mockup original.
const slides = [
  {
    label: 'Bienestar animal',
    badgeIcon: 'paw',
    badge: 'Cuidado veterinario y agropecuario',
    title: 'El bienestar de tus animales empieza aquí.',
    description:
      'Productos veterinarios, atención especializada y soluciones agropecuarias para el cuidado integral de tus mascotas y animales. Tu veterinaria de confianza en Tesalia Huila.',
    primaryTo: '/productos',
    primaryLabel: 'Explorar productos',
    secondaryTo: '/mis-citas',
    secondaryLabel: 'Agendar cita',
    // Consulta veterinaria, horizontal real (evita el recorte agresivo de
    // object-cover sobre una foto vertical, ver decision del carrusel)
    image: 'https://images.unsplash.com/photo-1700665537604-412e89a285c3?q=80&w=1200&auto=format&fit=crop',
    floatingIcon: 'paw',
    floatingTitle: 'Atención veterinaria',
    floatingSubtitle: 'Servicios especializados',
  },
  {
    label: 'Productos',
    badgeIcon: 'package',
    badge: 'Productos especializados',
    title: 'Todo lo que necesitas para cuidar a tus animales.',
    description:
      'Encuentra productos veterinarios, medicamentos, alimentos y soluciones para mascotas y animales de producción.',
    primaryTo: '/productos',
    primaryLabel: 'Explorar productos',
    secondaryTo: '/cuidado-animal',
    secondaryLabel: 'Ver farmacia veterinaria',
    // Frascos de suplementos/medicamentos en estantería, a color
    image: 'https://images.unsplash.com/photo-1606235357537-84aea24d4c4f?q=80&w=1200&auto=format&fit=crop',
    floatingIcon: 'package',
    floatingTitle: 'Catálogo especializado',
    floatingSubtitle: 'Para mascotas y producción',
  },
  {
    label: 'Agropecuario',
    badgeIcon: 'leaf',
    badge: 'Soluciones agropecuarias',
    title: 'También cuidamos a quienes hacen crecer el campo.',
    description:
      'Soluciones y atención especializada para animales de producción y las necesidades del sector agropecuario.',
    primaryTo: '/cuidado-animal',
    primaryLabel: 'Conocer servicios',
    secondaryTo: '/productos',
    secondaryLabel: 'Explorar productos',
    // Ganado en potrero, horizontal real con aire alrededor del ganado
    image: 'https://images.unsplash.com/photo-1594987057733-1fb3fe5707c9?q=80&w=1200&auto=format&fit=crop',
    floatingIcon: 'leaf',
    floatingTitle: 'Enfoque agropecuario',
    floatingSubtitle: 'Soluciones para el sector',
  },
]

const activeIndex = ref(0)
const activeSlide = computed(() => slides[activeIndex.value])
const swiperInstance = ref(null)

function onSwiper(swiper) {
  swiperInstance.value = swiper
}

function onSlideChange(swiper) {
  activeIndex.value = swiper.activeIndex
}

function goTo(index) {
  activeIndex.value = index
  swiperInstance.value?.slideTo(index)
}

// Autoplay manejado a mano en vez de con el modulo Autoplay de Swiper: con
// loop+fade el "active class" de Swiper queda desincronizado del slide que
// realmente se ve (bug real de Swiper, verificado en navegador) - llevando
// el indice nosotros mismos, el indicador activo nunca se desincroniza.
let autoplayTimer = null

function startAutoplay() {
  stopAutoplay()
  autoplayTimer = setInterval(() => {
    goTo((activeIndex.value + 1) % slides.length)
  }, 4500)
}

function stopAutoplay() {
  if (autoplayTimer) clearInterval(autoplayTimer)
}

onMounted(startAutoplay)
onBeforeUnmount(stopAutoplay)

// Conteos reales para las estadisticas de confianza (decision 7: nunca
// numeros inventados como el "+5K"/"+800" que traia esto antes) - sin
// autenticacion, GET /catalog/stats es publico. Si la request falla se
// deja en null y StatCard simplemente no anima nada raro (ver template).
const activeClients = ref(null)
const activeProducts = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/catalog/stats')
    activeClients.value = data.activeClients
    activeProducts.value = data.activeProducts
  } catch {
    // Sin numeros reales disponibles, las tarjetas de stats no se muestran
    // (ver v-if en el template) en vez de mostrar un placeholder inventado.
  }
})
</script>

<template>
  <section
    class="relative overflow-hidden bg-gradient-to-br from-emerald-50 via-white to-teal-50"
    @mouseenter="stopAutoplay"
    @mouseleave="startAutoplay"
  >
    <!-- Decorative blobs -->
    <div
      class="pointer-events-none absolute -top-24 -left-24 w-96 h-96 bg-emerald-200/40 rounded-full blur-3xl animate-blob-float"
    ></div>

    <div
      class="pointer-events-none absolute top-1/3 -right-32 w-[28rem] h-[28rem] bg-teal-200/30 rounded-full blur-3xl animate-blob-float-slow"
    ></div>

    <div class="relative max-w-7xl mx-auto px-6 py-8 md:py-20 lg:py-16">
      <div class="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
        <!-- Left: un solo <Transition mode="out-in"> envolviendo TODO el
             bloque (nunca transiciones separadas por elemento) - a
             proposito, para no repetir el bug real que ya paso en este
             mismo componente con multiples Transition simultaneos
             (elementos huerfanos en opacity:0, ver mas abajo en el <style>).
             min-w-0: sin esto, el item de grid se mide por el ancho natural
             de su contenido (el Swiper de la derecha calcula un ancho propio
             en px que termina empujando la columna entera) y desborda en
             mobile. -->
        <Transition name="hero-text-fade" mode="out-in">
          <div :key="activeIndex" class="min-w-0">
            <!-- Badge -->
            <div
              class="flex w-fit items-center gap-2 bg-emerald-100 text-emerald-700 px-5 py-2.5 rounded-full text-base font-semibold mb-6"
            >
              <AppIcon :name="activeSlide.badgeIcon" :size="18" />
              {{ activeSlide.badge }}
            </div>

            <!-- Title -->
            <h1
              class="text-4xl md:text-5xl font-extrabold text-slate-900 leading-tight tracking-tight"
            >
              {{ activeSlide.title }}
            </h1>

            <!-- Description -->
            <p class="mt-8 text-lg text-slate-600 leading-relaxed max-w-xl">
              {{ activeSlide.description }}
            </p>

            <!-- Buttons -->
            <div class="mt-10 flex flex-wrap gap-4">
              <SecondaryButton
                :to="activeSlide.primaryTo"
                class="bg-emerald-700 hover:bg-emerald-800 text-white px-8 py-4 rounded-2xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 transition"
              >
                {{ activeSlide.primaryLabel }}
              </SecondaryButton>

              <PrimaryButton
                :to="activeSlide.secondaryTo"
                class="border border-slate-300 hover:border-emerald-700 hover:text-emerald-700 hover:-translate-y-0.5 active:translate-y-0 text-slate-700 px-8 py-4 rounded-2xl font-semibold transition"
              >
                {{ activeSlide.secondaryLabel }}
              </PrimaryButton>
            </div>
          </div>
        </Transition>

        <!-- Right: la tarjeta con la foto es lo único dentro del Swiper (es
             lo único que necesita el cross-fade de Swiper); la tarjeta
             flotante y la insignia quedan FUERA, como hermanas del Swiper,
             para no quedar recortadas por el overflow:hidden que Swiper le
             pone a su propio contenedor raíz (bug real encontrado en
             navegador: con las tarjetas adentro, la insignia "+10 años" y la
             tarjeta flotante se veían cortadas en el borde). min-w-0: mismo
             motivo que la columna izquierda. -->
        <div class="relative min-w-0">
          <Swiper
            :modules="[EffectFade]"
            effect="fade"
            :fade-effect="{ crossFade: true }"
            :speed="700"
            class="hero-image-swiper"
            @swiper="onSwiper"
            @slide-change="onSlideChange"
          >
            <SwiperSlide v-for="slide in slides" :key="slide.image">
              <div class="bg-white rounded-[32px] shadow-2xl p-8 border border-slate-100">
                <img
                  :src="slide.image"
                  :alt="slide.title"
                  class="w-full h-[320px] md:h-[380px] lg:h-[400px] object-cover rounded-3xl"
                />
              </div>
            </SwiperSlide>
          </Swiper>

          <!-- Floating Card -->
          <div
            class="absolute -bottom-6 -left-6 z-10 bg-white rounded-2xl shadow-xl p-5 border border-slate-100 hover:-translate-y-1 transition-transform"
          >
            <div class="flex items-center gap-4">
              <div
                class="w-14 h-14 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-700"
              >
                <AppIcon :name="activeSlide.floatingIcon" :size="26" />
              </div>

              <div>
                <h4 class="font-bold text-slate-800">{{ activeSlide.floatingTitle }}</h4>

                <p class="text-sm text-slate-500">{{ activeSlide.floatingSubtitle }}</p>
              </div>
            </div>
          </div>

          <!-- Floating Badge (fijo, no cambia por slide - es un dato real de la empresa) -->
          <div
            class="absolute -top-5 -right-5 z-10 bg-white rounded-2xl shadow-xl px-5 py-3 border border-slate-100 hover:-translate-y-1 transition-transform"
          >
            <div class="flex items-center gap-3">
              <div
                class="relative w-10 h-10 rounded-full bg-emerald-700 flex items-center justify-center text-white flex-shrink-0"
              >
                <span
                  class="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-40"
                ></span>
                <AppIcon name="shield-check" :size="18" class="relative" />
              </div>

              <div class="leading-tight">
                <p class="font-extrabold text-slate-800 text-sm">+10 años</p>

                <p class="text-xs text-slate-500">de experiencia</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Indicadores + flechas -->
      <div class="mt-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div class="flex items-center gap-6 sm:gap-8">
          <button
            v-for="(slide, index) in slides"
            :key="slide.label"
            type="button"
            class="flex flex-col items-start gap-1.5 text-sm font-semibold transition-colors"
            :class="activeIndex === index ? 'text-slate-900' : 'text-slate-400 hover:text-slate-600'"
            @click="goTo(index)"
          >
            <span class="flex items-center gap-2">
              <span class="font-mono text-xs opacity-60">{{ String(index + 1).padStart(2, '0') }}</span>
              {{ slide.label }}
            </span>
            <span
              class="h-0.5 rounded-full bg-emerald-600 transition-all"
              :class="activeIndex === index ? 'w-10' : 'w-0'"
            ></span>
          </button>
        </div>

        <div class="flex items-center gap-3">
          <button
            type="button"
            class="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-600 hover:bg-emerald-700 hover:border-emerald-700 hover:text-white transition"
            @click="swiperInstance?.slidePrev()"
          >
            <AppIcon name="chevron-left" :size="18" />
          </button>
          <button
            type="button"
            class="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-600 hover:bg-emerald-700 hover:border-emerald-700 hover:text-white transition"
            @click="swiperInstance?.slideNext()"
          >
            <AppIcon name="chevron-right" :size="18" />
          </button>
        </div>
      </div>

      <!-- Stats (constantes, no cambian por slide) - conteos reales de
           GET /catalog/stats, no numeros inventados (decision 7). El
           horario tampoco es "24/7" (eso era falso, contradice el horario
           real de decision 12: Lun-Sáb 7am-7pm, Dom 8am-7pm). -->
      <div class="mt-10 grid grid-cols-3 gap-8 max-w-xl">
        <StatCard v-if="activeClients !== null" :value="`+${activeClients}`" label="Clientes activos" />

        <StatCard
          v-if="activeProducts !== null"
          :value="`+${activeProducts}`"
          label="Productos disponibles"
        />

        <StatCard value="7am–7pm" label="Lun–Sáb (Dom 8am–7pm)" />
      </div>
    </div>
  </section>
</template>

<style scoped>
@keyframes blob-float {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(20px, 30px) scale(1.08);
  }
}

.animate-blob-float {
  animation: blob-float 9s ease-in-out infinite;
}

.animate-blob-float-slow {
  animation: blob-float 13s ease-in-out infinite reverse;
}

@media (prefers-reduced-motion: reduce) {
  .animate-blob-float,
  .animate-blob-float-slow {
    animation: none;
  }
}

/* Un solo wrapper con mode="out-in" (nunca dos instancias montadas a la vez)
   - evita a proposito el bug real que ya paso con Transition en este mismo
   componente (decision 66: multiples Transition simultaneos dejaban
   elementos huerfanos en opacity:0). */
.hero-text-fade-enter-active,
.hero-text-fade-leave-active {
  transition: opacity 0.35s ease;
}

.hero-text-fade-enter-from,
.hero-text-fade-leave-to {
  opacity: 0;
}
</style>
