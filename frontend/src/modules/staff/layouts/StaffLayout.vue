<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppIcon from '../../../components/ui/AppIcon.vue'
import CircularLoader from '../../../components/ui/CircularLoader.vue'
import StaffSidebar from '../components/StaffSidebar.vue'
import PendingTasksNotification from '../components/PendingTasksNotification.vue'
import { useAuthStore } from '../../../stores/auth'
import { useStaffStore } from '../../../stores/staff'
import { useToastStore } from '../../../stores/toast'
import { useStaffNotificationsStore } from '../../../stores/staffNotifications'
import { navForRoles } from '../navConfig'
import logoIcon from '../../../assets/tesaliavet_isotype_transparent_background.png'

const MIN_LOADING_MS = 2000

const authStore = useAuthStore()
const staffStore = useStaffStore()
const toastStore = useToastStore()
const notificationsStore = useStaffNotificationsStore()
const router = useRouter()
const route = useRoute()

const navGroups = computed(() => navForRoles(authStore.user?.roles || []))
const unreadCount = computed(() => notificationsStore.summary?.unread || 0)

// "# de cosas por hacer" por módulo, pedido por Juan Manuel - reusa el
// mismo desglose por tipo que ya calculaba /staff/notifications/summary
// para el Centro de Notificaciones (decision 51), sin endpoint nuevo. Para
// una cuenta veterinario puro, byType.stock/pqrs/compra siempre da 0 (esas
// fuentes solo se calculan para admin) - inofensivo, esa cuenta tampoco ve
// esos items en el sidebar (navForRoles).
const moduleBadges = computed(() => {
  const byType = notificationsStore.summary?.byType || {}
  return {
    'staff-notifications': unreadCount.value,
    'staff-orders': (byType.compra || 0) + (byType.entrega || 0),
    'staff-pqrs': byType.pqrs || 0,
    'staff-stock-alerts': byType.stock || 0,
    'staff-appointments': byType.cita || 0,
    'staff-pets': byType.vacuna || 0,
  }
})

const userMenuOpen = ref(false)
const sidebarOpen = ref(false)
const entering = ref(true)
const leavingToPublic = ref(false)
const pendingNotifOpen = ref(false)

onMounted(async () => {
  const start = performance.now()
  await staffStore.fetchProfile()
  await notificationsStore.fetchSummary()
  await notificationsStore.fetchNotifications({ perPage: 5 })
  const remaining = MIN_LOADING_MS - (performance.now() - start)
  if (remaining > 0) await new Promise((resolve) => setTimeout(resolve, remaining))
  entering.value = false
  // Notificacion real de "cosas por hacer" pedida por Juan Manuel - solo al
  // entrar al panel (no en cada navegación interna, eso ya lo cubre el watch
  // de abajo sin volver a molestar). Usa el TOTAL de pendientes reales, no
  // solo "no leídas" - "cosas por hacer" son las que siguen sin resolverse
  // (ej. un pedido pagado sin entregar), independiente de si ya se marcaron
  // como leídas en el Centro de Notificaciones alguna vez. Un pequeño delay
  // despues de que ya se ve el Inicio - pedido explícito de Juan Manuel, para
  // que la notificación "suba" como algo aparte en vez de aparecer de la
  // nada al mismo tiempo que carga la página.
  if (notificationsStore.summary?.total > 0) {
    setTimeout(() => {
      pendingNotifOpen.value = true
    }, 700)
  }
})

// Los badges del sidebar (decision 93) antes solo se calculaban una vez al
// montar el panel - si el personal resolvía una PQRS o confirmaba una cita
// sin recargar la página, el número se quedaba viejo hasta refrescar a
// mano. Mismo patrón ya usado en el Navbar público (decision 76: refresca
// el carrito/notificaciones en cada navegación) - se refresca solo al
// cambiar de pantalla dentro del panel, no hace falta polling.
watch(
  () => route.fullPath,
  () => notificationsStore.fetchSummary()
)

function goToPublicSite() {
  userMenuOpen.value = false
  leavingToPublic.value = true
  setTimeout(() => router.push({ name: 'home' }), MIN_LOADING_MS)
}

async function handleLogout() {
  userMenuOpen.value = false
  await authStore.logout()
  toastStore.success('Cerrando sesión...')
  setTimeout(() => router.push({ name: 'home' }), 1000)
}
</script>

<template>
  <div v-if="entering || leavingToPublic" class="min-h-screen flex items-center justify-center bg-slate-50">
    <CircularLoader
      :label="leavingToPublic ? 'Sitio público' : 'Panel personal'"
      :icon="leavingToPublic ? 'home' : 'paw'"
      :duration="MIN_LOADING_MS"
    />
  </div>

  <div v-else class="min-h-screen flex flex-col bg-slate-50">
    <header class="bg-white border-b border-slate-200 h-20 flex items-center justify-between px-4 sm:px-6 sticky top-0 z-40">
      <div class="flex items-center gap-2 sm:gap-3 min-w-0">
        <button
          type="button"
          class="lg:hidden w-9 h-9 shrink-0 rounded-xl border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-emerald-700"
          @click="sidebarOpen = true"
        >
          <AppIcon name="menu" :size="18" />
        </button>
        <img :src="logoIcon" alt="TESALIAVET" class="w-12 h-12 shrink-0" />
        <span class="text-lg sm:text-xl font-extrabold text-slate-900 truncate hidden sm:inline">
          Panel de Personal
        </span>
      </div>

      <div class="flex items-center gap-2 sm:gap-3">
        <RouterLink
          :to="{ name: 'staff-notifications' }"
          class="relative w-9 h-9 rounded-xl border border-slate-200 flex items-center justify-center text-slate-500 hover:bg-slate-50 hover:text-emerald-700 transition"
        >
          <AppIcon name="bell" :size="18" />
          <span
            v-if="unreadCount > 0"
            class="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 rounded-full bg-red-600 text-white text-[10px] font-bold flex items-center justify-center animate-pulse"
          >
            {{ unreadCount > 9 ? '9+' : unreadCount }}
          </span>
        </RouterLink>

        <div class="relative">
          <button
            class="flex items-center gap-2 pl-2 pr-2 sm:pr-3 py-1.5 rounded-full border border-slate-200 hover:border-emerald-700 transition"
            @click="userMenuOpen = !userMenuOpen"
          >
            <div class="w-7 h-7 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold shrink-0">
              {{ authStore.user?.firstName?.[0] }}{{ authStore.user?.lastName?.[0] }}
            </div>
            <span class="text-sm font-semibold text-slate-700 hidden sm:inline">{{ authStore.user?.firstName }}</span>
            <AppIcon name="chevron-down" :size="14" />
          </button>

          <div
            v-if="userMenuOpen"
            class="absolute right-0 mt-2 w-52 bg-white border border-slate-200 rounded-xl shadow-lg py-2 z-50"
          >
            <button
              class="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-slate-700 hover:bg-emerald-50"
              @click="goToPublicSite"
            >
              <AppIcon name="home" :size="16" /> Ir al sitio público
            </button>
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
    </header>

    <div class="flex flex-1">
      <StaffSidebar
        :groups="navGroups"
        :badges="moduleBadges"
        :open="sidebarOpen"
        @close="sidebarOpen = false"
      />

      <main class="flex-1 min-w-0 px-4 sm:px-6 lg:px-8 py-6 lg:py-8 max-w-6xl w-full mx-auto">
        <RouterView :key="route.fullPath" />
      </main>
    </div>

    <PendingTasksNotification
      :open="pendingNotifOpen"
      :items="notificationsStore.items"
      :total="notificationsStore.summary?.total || 0"
      @close="pendingNotifOpen = false"
    />
  </div>
</template>
