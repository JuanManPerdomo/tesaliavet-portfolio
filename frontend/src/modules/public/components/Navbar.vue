<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppIcon from '../../../components/ui/AppIcon.vue'
import { useAuthStore } from '../../../stores/auth'
import { useToastStore } from '../../../stores/toast'
import { useCartStore } from '../../../stores/cart'
import { useNotificationsStore } from '../../../stores/notifications'
import logoIcon from '../../../assets/tesaliavet_isotype_transparent_background.png'

const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)
const authStore = useAuthStore()
const toastStore = useToastStore()
const cartStore = useCartStore()
const notificationsStore = useNotificationsStore()
const router = useRouter()
const route = useRoute()

// El contador del carrito y el de notificaciones se refrescan en cada
// navegación mientras haya sesión, para que sumen/resten al agregar
// productos o al volver de /notificaciones desde cualquier pantalla.
watch(
  () => route.fullPath,
  () => {
    if (authStore.user) {
      cartStore.fetchCart()
      notificationsStore.fetchSummary()
    }
  },
  { immediate: true }
)

const desktopLinkBase = 'flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition'
const desktopLinkActive = `${desktopLinkBase} font-semibold text-emerald-700 bg-emerald-50`
const desktopLinkInactive = `${desktopLinkBase} font-medium text-slate-700 hover:bg-emerald-50 hover:text-emerald-700`

const mobileLinkBase = 'flex items-center gap-3 px-4 py-3 rounded-xl transition'
const mobileLinkActive = `${mobileLinkBase} font-semibold text-emerald-700 bg-emerald-50`
const mobileLinkInactive = `${mobileLinkBase} hover:bg-emerald-50`

function navLinkClass(routeName, variant = 'desktop') {
  const isActive = route.name === routeName
  if (variant === 'mobile') return isActive ? mobileLinkActive : mobileLinkInactive
  return isActive ? desktopLinkActive : desktopLinkInactive
}

async function handleLogout() {
  userMenuOpen.value = false
  mobileMenuOpen.value = false
  await authStore.logout()
  toastStore.success('Cerrando sesión...')
  setTimeout(() => router.push({ name: 'home' }), 1000)
}
</script>

<template>
  <header class="bg-white/90 backdrop-blur-lg border-b border-slate-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between">
      <!-- Logo -->
      <RouterLink :to="{ name: 'home' }" class="flex items-center gap-3">
        <img :src="logoIcon" alt="TESALIAVET" class="w-16 h-16 shrink-0" />

        <div>
          <h1 class="text-lg sm:text-xl font-extrabold text-emerald-700 tracking-tight">
            TESALIAVET
          </h1>

          <p class="text-xs text-slate-500 -mt-1">Agroveterinaria Tesalia</p>
        </div>
      </RouterLink>

      <!-- Desktop Nav -->
      <nav class="hidden lg:flex items-center gap-2">
        <RouterLink to="/" :class="navLinkClass('home')">
          <AppIcon name="home" :size="16" /> Inicio
        </RouterLink>

        <RouterLink to="/productos" :class="navLinkClass('products')">
          <AppIcon name="shopping-bag" :size="16" /> Productos
        </RouterLink>

        <RouterLink to="/nosotros" :class="navLinkClass('about')">
          <AppIcon name="users" :size="16" /> Nosotros
        </RouterLink>

        <RouterLink to="/cuidado-animal" :class="navLinkClass('animal-care')">
          <AppIcon name="stethoscope" :size="16" /> Cuidado Animal
        </RouterLink>

        <RouterLink to="/contacto" :class="navLinkClass('contact')">
          <AppIcon name="phone" :size="16" /> Contacto
        </RouterLink>
      </nav>

      <!-- Desktop Actions -->
      <div v-if="authStore.user" class="hidden md:flex items-center gap-2 relative">
        <RouterLink
          :to="{ name: 'cart' }"
          class="relative w-10 h-10 rounded-xl border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 transition"
        >
          <AppIcon name="shopping-cart" :size="20" />
          <span
            v-if="cartStore.itemCount > 0"
            class="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 rounded-full bg-emerald-700 text-white text-[10px] font-bold flex items-center justify-center"
          >
            {{ cartStore.itemCount }}
          </span>
        </RouterLink>

        <RouterLink
          :to="{ name: 'notifications' }"
          class="relative w-10 h-10 rounded-xl border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 transition"
        >
          <AppIcon name="bell" :size="20" />
          <span
            v-if="notificationsStore.unreadCount > 0"
            class="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 rounded-full bg-red-600 text-white text-[10px] font-bold flex items-center justify-center"
          >
            {{ notificationsStore.unreadCount > 9 ? '9+' : notificationsStore.unreadCount }}
          </span>
        </RouterLink>

        <div class="relative">
          <button
            class="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-full border border-slate-200 hover:border-emerald-700 transition"
            @click="userMenuOpen = !userMenuOpen"
          >
            <div
              class="w-7 h-7 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold"
            >
              {{ authStore.user.firstName?.[0] }}{{ authStore.user.lastName?.[0] }}
            </div>
            <span class="text-sm font-semibold text-slate-700">
              {{ authStore.user.firstName }}
            </span>
            <AppIcon name="chevron-down" :size="14" />
          </button>

          <div
            v-if="userMenuOpen"
            class="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-lg py-2 z-50"
          >
            <RouterLink
              to="/mis-mascotas"
              class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-700 hover:bg-emerald-50"
              @click="userMenuOpen = false"
            >
              <AppIcon name="paw" :size="16" /> Mis mascotas
            </RouterLink>
            <RouterLink
              to="/mis-citas"
              class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-700 hover:bg-emerald-50"
              @click="userMenuOpen = false"
            >
              <AppIcon name="calendar" :size="16" /> Mis citas
            </RouterLink>
            <RouterLink
              to="/mis-pedidos"
              class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-700 hover:bg-emerald-50"
              @click="userMenuOpen = false"
            >
              <AppIcon name="package" :size="16" /> Mis pedidos
            </RouterLink>
            <RouterLink
              to="/mi-perfil"
              class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-700 hover:bg-emerald-50"
              @click="userMenuOpen = false"
            >
              <AppIcon name="user" :size="16" /> Mi perfil
            </RouterLink>
            <RouterLink
              v-if="authStore.hasRole('admin', 'veterinario', 'bodeguero')"
              to="/panel"
              class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-700 hover:bg-emerald-50"
              @click="userMenuOpen = false"
            >
              <AppIcon name="shield" :size="16" /> Panel de personal
            </RouterLink>
            <hr class="my-2 border-slate-100" />
            <button
              class="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
              @click="handleLogout"
            >
              <AppIcon name="log-out" :size="16" /> Cerrar sesión
            </button>
          </div>
        </div>
      </div>

      <div v-else class="hidden md:flex items-center gap-3">
        <RouterLink
          to="/register"
          class="border border-emerald-700 text-emerald-700 px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-emerald-50 transition"
        >
          Registrarse
        </RouterLink>

        <RouterLink
          to="/login"
          class="bg-emerald-700 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-emerald-800 shadow-md hover:shadow-lg transition"
        >
          Iniciar sesión
        </RouterLink>
      </div>

      <!-- Mobile Button -->
      <button
        class="lg:hidden w-11 h-11 rounded-xl border border-slate-200 flex items-center justify-center"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="w-6 h-6 text-slate-700"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
    </div>

    <!-- Mobile Menu -->
    <div
      v-if="mobileMenuOpen"
      class="lg:hidden border-t border-slate-200 bg-white px-6 py-6 space-y-3"
    >
      <RouterLink to="/" :class="navLinkClass('home', 'mobile')">
        <AppIcon name="home" :size="18" /> Inicio
      </RouterLink>

      <RouterLink to="/productos" :class="navLinkClass('products', 'mobile')">
        <AppIcon name="shopping-bag" :size="18" /> Productos
      </RouterLink>

      <RouterLink to="/nosotros" :class="navLinkClass('about', 'mobile')">
        <AppIcon name="users" :size="18" /> Nosotros
      </RouterLink>

      <RouterLink to="/cuidado-animal" :class="navLinkClass('animal-care', 'mobile')">
        <AppIcon name="stethoscope" :size="18" /> Cuidado Animal
      </RouterLink>

      <RouterLink to="/contacto" :class="navLinkClass('contact', 'mobile')">
        <AppIcon name="phone" :size="18" /> Contacto
      </RouterLink>

      <template v-if="authStore.user">
        <RouterLink
          to="/mis-mascotas"
          class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-emerald-50 transition"
        >
          <AppIcon name="paw" :size="18" /> Mis mascotas
        </RouterLink>
        <RouterLink
          to="/mis-citas"
          class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-emerald-50 transition"
        >
          <AppIcon name="calendar" :size="18" /> Mis citas
        </RouterLink>
        <RouterLink
          :to="{ name: 'cart' }"
          class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-emerald-50 transition"
        >
          <AppIcon name="shopping-cart" :size="18" /> Carrito
          <span
            v-if="cartStore.itemCount > 0"
            class="ml-auto min-w-[18px] h-[18px] px-1 rounded-full bg-emerald-700 text-white text-[10px] font-bold flex items-center justify-center"
          >
            {{ cartStore.itemCount }}
          </span>
        </RouterLink>
        <RouterLink
          to="/mis-pedidos"
          class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-emerald-50 transition"
        >
          <AppIcon name="package" :size="18" /> Mis pedidos
        </RouterLink>
        <RouterLink
          :to="{ name: 'notifications' }"
          class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-emerald-50 transition"
        >
          <AppIcon name="bell" :size="18" /> Notificaciones
          <span
            v-if="notificationsStore.unreadCount > 0"
            class="ml-auto min-w-[18px] h-[18px] px-1 rounded-full bg-red-600 text-white text-[10px] font-bold flex items-center justify-center"
          >
            {{ notificationsStore.unreadCount > 9 ? '9+' : notificationsStore.unreadCount }}
          </span>
        </RouterLink>
        <RouterLink
          to="/mi-perfil"
          class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-emerald-50 transition"
        >
          <AppIcon name="user" :size="18" /> Mi perfil
        </RouterLink>
        <RouterLink
          v-if="authStore.hasRole('admin', 'veterinario', 'bodeguero')"
          to="/panel"
          class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-emerald-50 transition"
        >
          <AppIcon name="shield" :size="18" /> Panel de personal
        </RouterLink>
        <button
          class="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-600 hover:bg-red-50 transition"
          @click="handleLogout"
        >
          <AppIcon name="log-out" :size="18" /> Cerrar sesión
        </button>
      </template>

      <div v-else class="flex flex-col gap-3 pt-4">
        <RouterLink
          to="/register"
          class="border border-emerald-700 text-emerald-700 px-4 py-3 rounded-xl text-center font-semibold"
        >
          Registrarse
        </RouterLink>

        <RouterLink
          to="/login"
          class="bg-emerald-700 text-white px-4 py-3 rounded-xl text-center font-semibold"
        >
          Iniciar sesión
        </RouterLink>
      </div>
    </div>
  </header>
</template>
