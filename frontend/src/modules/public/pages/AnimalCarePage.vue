<script setup>
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import AnimalCareHero from '../components/animalcare/AnimalCareHero.vue'
import AnimalCareServices from '../components/animalcare/AnimalCareServices.vue'
import AnimalCarePharmacy from '../components/animalcare/AnimalCarePharmacy.vue'
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <Navbar />

    <div class="max-w-[1200px] mx-auto">
      <AnimalCareHero />

      <div class="px-8 pb-16">
        <AnimalCareServices />
        <AnimalCarePharmacy />
      </div>
    </div>

    <Footer />
  </div>
</template>
