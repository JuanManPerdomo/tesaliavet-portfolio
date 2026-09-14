<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '../../../../components/cards/StatCard.vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import api from '../../../../lib/api'

// Conteos reales, mismo endpoint publico que ya usa HeroSection.vue
// (decision 7: nunca numeros inventados como el "1.250+"/"500+" que traia
// esto antes).
const activeClients = ref(null)
const activeProducts = ref(null)

onMounted(async () => {
  try {
    const { data } = await api.get('/catalog/stats')
    activeClients.value = data.activeClients
    activeProducts.value = data.activeProducts
  } catch {
    // Sin datos reales disponibles, esas 2 tarjetas simplemente no se
    // muestran (ver v-if en el template) en vez de un numero inventado.
  }
})
</script>

<template>
  <section class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-24">
    <div class="order-2 lg:order-1">
      <span
        class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-50 text-emerald-700 text-sm font-semibold mb-6"
      >
        <AppIcon name="book" :size="16" /> Nuestra historia
      </span>

      <h1 class="text-4xl sm:text-5xl font-extrabold text-slate-900 leading-tight mb-6">
        Agroveterinaria Tesalia —
        <span class="text-emerald-700">+10 años</span>
        cuidando vidas
      </h1>

      <p class="text-lg text-slate-600 leading-relaxed mb-10 max-w-xl">
        Nos dedicamos a transformar el cuidado animal y agrícola en la región de Huila, combinando
        pasión veterinaria con tecnología de vanguardia.
      </p>

      <div
        class="grid grid-cols-3 gap-8 p-8 bg-white rounded-3xl shadow-sm border border-slate-100"
      >
        <StatCard v-if="activeClients !== null" :value="`+${activeClients}`" label="Clientes" />

        <StatCard value="+10" label="Años" />

        <StatCard v-if="activeProducts !== null" :value="`+${activeProducts}`" label="Productos" />
      </div>
    </div>

    <div class="order-1 lg:order-2 relative">
      <div class="relative z-10 rounded-3xl overflow-hidden shadow-2xl">
        <img
          src="https://lh3.googleusercontent.com/aida-public/AB6AXuDTyUz1i80V5geOna01CdvuyQ3lTY1nXRlOuKgP36cnDy6RnOAepbPhJsVoQCRLK_Anw-nbDp4_nN_4Zwhi5c_HhaJ8ObkhDunCQowtIKQ7HjAbVRguksQIEhYRv5sIIRzETYesr5QgBn2hab6TFO8g3gQsg_ckiFLQhaXE3CgKR9sRIS7SPITv136VUo17kyDJnMu6rCy_k4-FgCzO1Q1NMNdl_D9Q3iN4kCd5C_Ft8lF3ZxEeUoc5"
          alt="Clínica veterinaria TesaliaVet"
          class="w-full h-[380px] object-cover"
        />
      </div>

      <div
        class="absolute -bottom-6 -left-6 z-20 bg-white/90 backdrop-blur p-6 rounded-2xl shadow-lg flex items-center gap-4 max-w-[280px]"
      >
        <div
          class="w-12 h-12 bg-emerald-700 rounded-full flex items-center justify-center text-white"
        >
          <AppIcon name="check" :size="20" />
        </div>
        <div>
          <p class="font-semibold text-slate-900">Calidad Certificada</p>
          <p class="text-xs text-slate-500">Estándares internacionales de cuidado.</p>
        </div>
      </div>
    </div>
  </section>
</template>
