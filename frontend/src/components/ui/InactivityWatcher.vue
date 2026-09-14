<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useToastStore } from '../../stores/toast'
import AppIcon from './AppIcon.vue'
import PrimaryButton from './PrimaryButton.vue'

// RNF07: cierre de sesion tras 15 minutos de inactividad. Se avisa 1 minuto
// antes con un modal y cuenta regresiva - si nadie interactua, se cierra
// sola la sesion (mismo patron de toast + redirect que ya usa el logout
// manual en Navbar.vue/StaffLayout.vue).
const INACTIVITY_LIMIT_MS = 15 * 60 * 1000
const WARNING_LEAD_MS = 60 * 1000
const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart']
const RESET_THROTTLE_MS = 1000

const authStore = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()

const showWarning = ref(false)
const secondsLeft = ref(0)

let warningTimer = null
let logoutTimer = null
let countdownInterval = null
let lastReset = 0

function clearTimers() {
  clearTimeout(warningTimer)
  clearTimeout(logoutTimer)
  clearInterval(countdownInterval)
}

function scheduleTimers() {
  clearTimers()
  showWarning.value = false
  warningTimer = setTimeout(startWarning, INACTIVITY_LIMIT_MS - WARNING_LEAD_MS)
}

function startWarning() {
  showWarning.value = true
  secondsLeft.value = Math.round(WARNING_LEAD_MS / 1000)
  countdownInterval = setInterval(() => {
    secondsLeft.value -= 1
    if (secondsLeft.value <= 0) clearInterval(countdownInterval)
  }, 1000)
  logoutTimer = setTimeout(doLogout, WARNING_LEAD_MS)
}

async function doLogout() {
  clearTimers()
  showWarning.value = false
  stopListening()
  await authStore.logout()
  toastStore.success('Tu sesión se cerró por inactividad.')
  router.push({ name: 'home' })
}

function handleActivity() {
  // Mientras el aviso esta abierto, solo el boton "Seguir conectado" lo
  // reinicia - un movimiento de mouse sin querer no deberia descartarlo en
  // silencio.
  if (showWarning.value) return
  const now = Date.now()
  if (now - lastReset < RESET_THROTTLE_MS) return
  lastReset = now
  scheduleTimers()
}

function stayConnected() {
  scheduleTimers()
}

function startListening() {
  ACTIVITY_EVENTS.forEach((event) => window.addEventListener(event, handleActivity, { passive: true }))
  scheduleTimers()
}

function stopListening() {
  ACTIVITY_EVENTS.forEach((event) => window.removeEventListener(event, handleActivity))
  clearTimers()
}

watch(
  () => authStore.token,
  (token) => {
    if (token) startListening()
    else stopListening()
  },
  { immediate: true }
)

onBeforeUnmount(stopListening)
</script>

<template>
  <Teleport to="body">
    <div v-if="showWarning" class="fixed inset-0 z-[9999] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 text-center">
        <div class="w-14 h-14 mx-auto bg-amber-50 rounded-full flex items-center justify-center mb-4">
          <AppIcon name="clock" :size="26" class="text-amber-600" />
        </div>

        <h3 class="text-lg font-bold text-slate-900 mb-1">¿Sigues ahí?</h3>
        <p class="text-sm text-slate-500 mb-5">
          Tu sesión se cerrará por inactividad en
          <strong class="text-slate-900">{{ secondsLeft }} segundos</strong>.
        </p>

        <div class="flex flex-col gap-2.5">
          <PrimaryButton class="w-full justify-center" @click="stayConnected">Seguir conectado</PrimaryButton>
          <button
            type="button"
            class="w-full px-4 py-2 text-slate-500 text-sm font-semibold rounded-lg hover:bg-slate-50 transition"
            @click="doLogout"
          >
            Cerrar sesión ahora
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
