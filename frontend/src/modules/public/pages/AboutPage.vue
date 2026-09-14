<script setup>
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import AboutHero from '../components/about/AboutHero.vue'
import AboutHistoryMissionExperience from '../components/about/AboutHistoryMissionExperience.vue'
import AboutWebsiteUsage from '../components/about/AboutWebsiteUsage.vue'
import AboutValues from '../components/about/AboutValues.vue'
import AboutTeam from '../components/about/AboutTeam.vue'
import AboutCta from '../components/about/AboutCta.vue'
</script>

<template>
  <div class="bg-slate-50">
    <Navbar />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-12">
      <AboutHero />
      <AboutHistoryMissionExperience />
      <AboutWebsiteUsage />
      <AboutValues />
      <AboutTeam />
      <AboutCta />
    </main>

    <Footer />
  </div>
</template>
