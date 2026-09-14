<script setup>
import PromoBar from '../components/PromoBar.vue'
import Navbar from '../components/Navbar.vue'
import HeroSection from '../components/HeroSection.vue'
import CategoriesSection from '../components/CategoriesSection.vue'
import HowItWorksSection from '../components/HowItWorksSection.vue'
import FeaturedProducts from '../components/FeaturedProducts.vue'
import RandomProductsCarousel from '../components/RandomProductsCarousel.vue'
import BannerStrip from '../components/BannerStrip.vue'
import ServicesSection from '../components/ServicesSection.vue'
import AboutSection from '../components/AboutSection.vue'
import Footer from '../components/Footer.vue'
import AuthenticatedHero from '../../client/components/AuthenticatedHero.vue'
import NextAppointmentCard from '../../client/components/NextAppointmentCard.vue'
import HomePetsPreview from '../../client/components/HomePetsPreview.vue'
import QuickAccessCard from '../../client/components/QuickAccessCard.vue'
import { useAuthStore } from '../../../stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <PromoBar />

    <Navbar />

    <template v-if="authStore.user">
      <AuthenticatedHero />

      <NextAppointmentCard />

      <HomePetsPreview />

      <section class="max-w-7xl mx-auto px-6 py-12">
        <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-6">
          Acceso rápido
        </p>

        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <QuickAccessCard
            icon="paw"
            label="Mis mascotas"
            sub="Ver registradas"
            to="/mis-mascotas"
            icon-bg-class="bg-emerald-50"
            icon-color-class="text-emerald-700"
          />
          <QuickAccessCard
            icon="calendar"
            label="Mis citas"
            sub="Ver agenda"
            to="/mis-citas"
            icon-bg-class="bg-sky-50"
            icon-color-class="text-sky-700"
          />
          <QuickAccessCard
            icon="package"
            label="Mis pedidos"
            sub="Ver historial"
            to="/mis-pedidos"
            icon-bg-class="bg-amber-50"
            icon-color-class="text-amber-700"
          />
          <QuickAccessCard
            icon="user"
            label="Mi perfil"
            sub="Editar datos"
            to="/mi-perfil"
            icon-bg-class="bg-pink-50"
            icon-color-class="text-pink-700"
          />
        </div>
      </section>

      <FeaturedProducts
        badge="Para ti"
        title="Productos recomendados."
        description="Los productos más vendidos entre nuestros clientes."
      />

      <RandomProductsCarousel />
    </template>

    <template v-else>
      <HeroSection />

      <CategoriesSection />

      <HowItWorksSection />

      <FeaturedProducts />

      <RandomProductsCarousel />

      <BannerStrip />

      <ServicesSection />

      <AboutSection />
    </template>

    <Footer />
  </div>
</template>
