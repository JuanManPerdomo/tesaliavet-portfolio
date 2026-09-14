<script setup>
import StatCard from '../../../components/cards/StatCard.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
</script>

<template>
  <section class="py-16 bg-white overflow-hidden">
    <div class="max-w-7xl mx-auto px-6">
      <div class="grid lg:grid-cols-2 gap-14 items-center">
        <!-- Left Images -->
        <div v-reveal class="relative group">
          <!-- Main Image -->
          <div class="overflow-hidden rounded-[36px] shadow-2xl">
            <img
              src="https://images.unsplash.com/photo-1770836037275-38b44e4b101f?q=80&w=1200&auto=format&fit=crop"
              alt="Veterinario aplicando una inyección a un perro pequeño"
              class="w-full h-[600px] object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
            />
          </div>

          <!-- Floating Card -->
          <div
            class="absolute -bottom-8 -right-8 bg-white rounded-3xl shadow-2xl p-6 border border-slate-100 max-w-xs"
          >
            <div class="flex items-center gap-4">
              <div
                class="w-16 h-16 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-700"
              >
                <AppIcon name="paw" :size="30" />
              </div>

              <div>
                <h4 class="text-2xl font-extrabold text-emerald-700">+10 años</h4>

                <p class="text-slate-500 text-sm">
                  Cuidando animales y apoyando el sector agropecuario.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Content -->
        <div v-reveal="{ delay: 150 }">
          <!-- Badge -->
          <span
            class="flex w-fit bg-emerald-100 text-emerald-700 px-5 py-2.5 rounded-full text-base font-semibold"
          >
            Sobre nosotros
          </span>

          <!-- Title -->
          <h2
            class="mt-5 text-4xl lg:text-5xl font-extrabold text-slate-900 leading-tight tracking-tight"
          >
            Comprometidos con el bienestar animal y el desarrollo agropecuario.
          </h2>

          <!-- Description -->
          <p class="mt-6 text-lg text-slate-600 leading-relaxed">
            En Agroveterinaria Tesalia trabajamos para brindar atención veterinaria profesional,
            productos especializados y soluciones integrales para mascotas y animales de producción.
          </p>

          <p class="mt-5 text-lg text-slate-600 leading-relaxed">
            Nuestro compromiso es ofrecer un servicio confiable, cercano y moderno que facilite el
            cuidado animal y fortalezca la salud de cada especie.
          </p>

          <!-- Features -->
          <div class="mt-10 space-y-5">
            <!-- Feature -->
            <div class="flex items-start gap-4">
              <div
                class="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-700"
              >
                <AppIcon name="check" :size="20" />
              </div>

              <div>
                <h4 class="text-lg font-bold text-slate-900">Atención profesional</h4>

                <p class="text-slate-600 mt-1">
                  Equipo capacitado para diagnóstico, tratamiento y seguimiento clínico.
                </p>
              </div>
            </div>

            <!-- Feature -->
            <div class="flex items-start gap-4">
              <div
                class="w-12 h-12 rounded-2xl bg-teal-100 flex items-center justify-center text-teal-700"
              >
                <AppIcon name="pill" :size="20" />
              </div>

              <div>
                <h4 class="text-lg font-bold text-slate-900">Productos especializados</h4>

                <p class="text-slate-600 mt-1">
                  Medicamentos, suplementos y productos veterinarios de calidad.
                </p>
              </div>
            </div>

            <!-- Feature -->
            <div class="flex items-start gap-4">
              <div
                class="w-12 h-12 rounded-2xl bg-cyan-100 flex items-center justify-center text-cyan-700"
              >
                <AppIcon name="leaf" :size="20" />
              </div>

              <div>
                <h4 class="text-lg font-bold text-slate-900">Enfoque agropecuario</h4>

                <p class="text-slate-600 mt-1">
                  Soluciones integrales para animales de producción y cuidado rural.
                </p>
              </div>
            </div>
          </div>

          <!-- Stats -->
          <div class="mt-12 grid grid-cols-3 gap-6">
            <div class="bg-slate-50 rounded-3xl p-6 text-center border border-slate-100">
              <StatCard value="+5K" label="Clientes" />
            </div>

            <div class="bg-slate-50 rounded-3xl p-6 text-center border border-slate-100">
              <StatCard value="+800" label="Productos" />
            </div>

            <div class="bg-slate-50 rounded-3xl p-6 text-center border border-slate-100">
              <StatCard value="24/7" label="Atención" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
