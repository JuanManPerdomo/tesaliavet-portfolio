<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'
import logoIcon from '../../../assets/tesaliavet_isotype_transparent_background.png'

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="bg-slate-950 text-white pt-20 pb-10">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Top -->
      <div class="grid lg:grid-cols-4 gap-14 pb-16 border-b border-slate-800">
        <!-- Brand -->
        <div>
          <!-- Logo -->
          <div class="flex items-center gap-3">
            <img :src="logoIcon" alt="TESALIAVET" class="w-12 h-12 shrink-0" />

            <div>
              <h3 class="text-2xl font-extrabold tracking-tight">TESALIAVET</h3>

              <p class="text-slate-400 text-sm">Agroveterinaria Tesalia</p>
            </div>
          </div>

          <!-- Description -->
          <p class="mt-6 text-slate-400 leading-relaxed">
            Soluciones veterinarias y agropecuarias enfocadas en el bienestar animal, la salud y el
            cuidado profesional.
          </p>

          <!-- Social -->
          <div class="mt-8 flex items-center gap-4">
            <a
              href="https://facebook.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Facebook de TesaliaVet (próximamente)"
              title="Próximamente"
              class="w-11 h-11 rounded-2xl bg-slate-900 hover:bg-emerald-700 transition flex items-center justify-center"
            >
              <AppIcon name="facebook" :size="18" />
            </a>

            <a
              href="https://instagram.com"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Instagram de TesaliaVet (próximamente)"
              title="Próximamente"
              class="w-11 h-11 rounded-2xl bg-slate-900 hover:bg-emerald-700 transition flex items-center justify-center"
            >
              <AppIcon name="instagram" :size="18" />
            </a>

            <a
              href="https://wa.me/573104567890"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Escríbenos por WhatsApp"
              title="WhatsApp: 310 456 7890"
              class="w-11 h-11 rounded-2xl bg-slate-900 hover:bg-emerald-700 transition flex items-center justify-center"
            >
              <AppIcon name="message-circle" :size="18" />
            </a>
          </div>
        </div>

        <!-- Navigation -->
        <div>
          <h4 class="text-lg font-bold mb-6">Navegación</h4>

          <ul class="space-y-4 text-slate-400">
            <li>
              <RouterLink :to="{ name: 'home' }" class="hover:text-white transition">
                Inicio
              </RouterLink>
            </li>

            <li>
              <RouterLink :to="{ name: 'products' }" class="hover:text-white transition">
                Productos
              </RouterLink>
            </li>

            <li>
              <RouterLink :to="{ name: 'about' }" class="hover:text-white transition">
                Nosotros
              </RouterLink>
            </li>

            <li>
              <RouterLink :to="{ name: 'animal-care' }" class="hover:text-white transition">
                Cuidado animal
              </RouterLink>
            </li>

            <li>
              <RouterLink :to="{ name: 'contact' }" class="hover:text-white transition">
                Contacto
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Services -->
        <div>
          <h4 class="text-lg font-bold mb-6">Servicios</h4>

          <ul class="space-y-4 text-slate-400">
            <li>Consulta veterinaria</li>

            <li>Farmacia veterinaria</li>

            <li>Plan de vacunación</li>

            <li>Atención especializada</li>

            <li>Productos agropecuarios</li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h4 class="text-lg font-bold mb-6">Contacto</h4>

          <div class="space-y-5 text-slate-400">
            <div>
              <p class="text-white font-semibold">Dirección</p>

              <p class="mt-1">Tesalia, Huila - Colombia</p>
            </div>

            <div>
              <p class="text-white font-semibold">Teléfono</p>

              <p class="mt-1">310 456 7890</p>
            </div>

            <div>
              <p class="text-white font-semibold">Correo electrónico</p>

              <p class="mt-1">contacto@tesaliavet.com</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom -->
      <div
        class="pt-8 flex flex-col lg:flex-row items-center justify-between gap-4 text-sm text-slate-500"
      >
        <p>© {{ currentYear }} TESALIAVET. Todos los derechos reservados.</p>

        <div class="flex items-center gap-6">
          <RouterLink :to="{ name: 'privacy' }" class="hover:text-white transition">
            Política de privacidad
          </RouterLink>

          <RouterLink :to="{ name: 'terms' }" class="hover:text-white transition">
            Términos y condiciones
          </RouterLink>
        </div>
      </div>
    </div>
  </footer>
</template>
