<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../../../stores/auth'
import AppIcon from '../../../components/ui/AppIcon.vue'

const authStore = useAuthStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Buenos días'
  if (hour < 19) return 'Buenas tardes'
  return 'Buenas noches'
})

const initials = computed(() => {
  const first = authStore.user?.firstName?.[0] || ''
  const last = authStore.user?.lastName?.[0] || ''
  return `${first}${last}`.toUpperCase()
})
</script>

<template>
  <section
    class="relative overflow-hidden bg-gradient-to-br from-emerald-800 via-emerald-700 to-teal-700"
  >
    <!-- Decorative blobs -->
    <div
      class="pointer-events-none absolute -top-20 -left-20 w-80 h-80 bg-white/5 rounded-full blur-3xl"
    ></div>

    <div
      class="pointer-events-none absolute bottom-0 right-0 w-96 h-96 bg-teal-400/10 rounded-full blur-3xl"
    ></div>

    <div class="relative max-w-7xl mx-auto px-6 py-16 md:py-20">
      <div class="grid lg:grid-cols-[1fr_320px] gap-10 items-start">
        <!-- Left -->
        <div class="text-white">
          <div
            v-reveal
            class="flex w-fit items-center gap-2 bg-white/15 backdrop-blur-sm px-5 py-2.5 rounded-full text-base font-semibold mb-6"
          >
            <AppIcon name="paw" :size="16" />
            {{ greeting }}, {{ authStore.user?.firstName }}
          </div>

          <h1
            v-reveal="{ delay: 100 }"
            class="text-4xl md:text-5xl font-extrabold leading-tight tracking-tight mb-4"
          >
            ¿Qué necesita tu mascota hoy?
          </h1>

          <p v-reveal="{ delay: 150 }" class="text-lg text-white/80 max-w-xl mb-8">
            Explora el catálogo, agenda una cita o gestiona a tus mascotas desde tu cuenta.
          </p>

          <div v-reveal="{ delay: 200 }" class="flex flex-wrap gap-4">
            <RouterLink
              to="/productos"
              class="bg-white hover:bg-slate-100 text-emerald-800 px-6 py-3.5 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0 transition inline-flex items-center justify-center"
            >
              Ver productos
            </RouterLink>

            <RouterLink
              to="/mis-citas"
              class="bg-white/15 hover:bg-white/25 border border-white/30 text-white px-6 py-3.5 rounded-xl font-semibold hover:-translate-y-0.5 active:translate-y-0 transition inline-flex items-center justify-center"
            >
              Mis citas
            </RouterLink>
          </div>
        </div>

        <!-- Account card -->
        <div
          v-reveal="{ delay: 250 }"
          class="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 text-white hover:bg-white/[0.13] transition-colors"
        >
          <p class="text-[11px] font-bold uppercase tracking-widest text-white/60 mb-4">
            Tu cuenta
          </p>

          <div class="flex items-center gap-3 mb-5">
            <div
              class="w-12 h-12 rounded-full bg-white/15 border border-white/25 flex items-center justify-center text-base font-extrabold flex-shrink-0"
            >
              {{ initials }}
            </div>

            <div class="min-w-0">
              <p class="text-lg font-bold truncate">
                {{ authStore.user?.firstName }} {{ authStore.user?.lastName }}
              </p>

              <p class="text-sm text-white/70 truncate">
                {{ authStore.user?.email }}
              </p>
            </div>
          </div>

          <p class="text-sm text-white/80 leading-relaxed">
            Gestiona tus mascotas, citas y pedidos desde el menú de tu cuenta, arriba a la
            derecha.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
