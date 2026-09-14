<script setup>
import { computed, onMounted, ref } from 'vue'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import { usePqrsStore } from '../../../stores/pqrs'
import { useOrdersStore } from '../../../stores/orders'
import { useAppointmentsStore } from '../../../stores/appointments'
import { useNotificationsStore } from '../../../stores/notifications'

const PQRS_STATUS_BADGE = {
  Abierto: 'bg-amber-50 text-amber-700',
  'En Proceso': 'bg-sky-50 text-sky-700',
  Resuelto: 'bg-emerald-50 text-emerald-700',
  Cerrado: 'bg-slate-100 text-slate-600',
}

const ORDER_STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Pagado: 'bg-sky-50 text-sky-700',
  Entregado: 'bg-emerald-50 text-emerald-700',
  Cancelado: 'bg-red-50 text-red-600',
}

const APPOINTMENT_STATUS_BADGE = {
  Pendiente: 'bg-amber-50 text-amber-700',
  Confirmada: 'bg-emerald-50 text-emerald-700',
  Completada: 'bg-slate-100 text-slate-600',
  Cancelada: 'bg-red-50 text-red-600',
}

const pqrsStore = usePqrsStore()
const ordersStore = useOrdersStore()
const appointmentsStore = useAppointmentsStore()
const notificationsStore = useNotificationsStore()

// pqrsStore.fetchMine() ya existe en develop (decisión 34, /mi-perfil) y
// devuelve el arreglo directamente, sin trackear loading/error propios -
// se manejan aca con refs locales en vez de inventar campos en el store
// compartido con MyProfilePage.vue.
const myPqrs = ref([])
const pqrsLoading = ref(true)
const pqrsError = ref('')

onMounted(async () => {
  try {
    myPqrs.value = await pqrsStore.fetchMine()
  } catch {
    pqrsError.value = 'No se pudieron cargar tus solicitudes PQRS.'
  } finally {
    pqrsLoading.value = false
  }
  ordersStore.fetchOrders()
  appointmentsStore.fetchAppointments()
  notificationsStore.markAsRead()
})

const upcomingAppointments = computed(() =>
  appointmentsStore.appointments
    .filter((a) => a.status !== 'Cancelada' && new Date(a.appointmentDatetime) > new Date())
    .sort((a, b) => new Date(a.appointmentDatetime) - new Date(b.appointmentDatetime))
    .slice(0, 5)
)

const recentOrders = computed(() => ordersStore.orders.slice(0, 5))
const recentPqrs = computed(() => myPqrs.value.slice(0, 5))

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateTime(iso) {
  if (!iso) return '—'
  const dt = new Date(iso)
  return `${dt.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })} · ${dt.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })}`
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-3xl mx-auto px-6 py-12 w-full">
      <div class="mb-8">
        <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Notificaciones</h1>
        <p class="text-sm text-slate-500">
          Novedades de tus solicitudes, pedidos y próximas citas.
        </p>
      </div>

      <!-- PQRS -->
      <section class="mb-8">
        <h2 class="flex items-center gap-2 text-sm font-bold text-slate-900 mb-4">
          <AppIcon name="message-circle" :size="16" class="text-emerald-700" />
          Tus solicitudes (PQRS)
        </h2>

        <div v-if="pqrsLoading" class="text-sm text-slate-500">Cargando...</div>
        <p v-else-if="pqrsError" class="text-sm text-red-600">{{ pqrsError }}</p>
        <div
          v-else-if="!recentPqrs.length"
          class="bg-white border border-slate-200 rounded-2xl p-6 text-sm text-slate-500"
        >
          No has enviado ninguna PQRS todavía.
          <RouterLink to="/contacto" class="text-emerald-700 font-semibold hover:underline">
            Escríbenos
          </RouterLink>
        </div>

        <div v-else class="flex flex-col gap-3">
          <div
            v-for="item in recentPqrs"
            :key="item.id"
            class="bg-white rounded-2xl border border-slate-200 p-5"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="text-sm font-bold text-slate-900 truncate">{{ item.subject }}</p>
                <p class="text-xs text-slate-500 mt-0.5">{{ item.type }} · {{ formatDate(item.createdAt) }}</p>
              </div>
              <span
                class="shrink-0 text-[10px] font-bold uppercase px-2.5 py-1 rounded-full"
                :class="PQRS_STATUS_BADGE[item.status]"
              >
                {{ item.status }}
              </span>
            </div>

            <div
              v-if="item.response"
              class="mt-3 bg-emerald-50 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800"
            >
              <span class="font-bold">Respuesta:</span> {{ item.response }}
            </div>
            <p v-else class="mt-3 text-xs text-slate-400">Todavía sin respuesta.</p>
          </div>
        </div>
      </section>

      <!-- Pedidos -->
      <section class="mb-8">
        <h2 class="flex items-center gap-2 text-sm font-bold text-slate-900 mb-4">
          <AppIcon name="shopping-bag" :size="16" class="text-emerald-700" />
          Tus pedidos
        </h2>

        <div v-if="ordersStore.loading" class="text-sm text-slate-500">Cargando...</div>
        <p v-else-if="ordersStore.error" class="text-sm text-red-600">{{ ordersStore.error }}</p>
        <div
          v-else-if="!recentOrders.length"
          class="bg-white border border-slate-200 rounded-2xl p-6 text-sm text-slate-500"
        >
          No tienes pedidos todavía.
          <RouterLink to="/productos" class="text-emerald-700 font-semibold hover:underline">
            Ver catálogo
          </RouterLink>
        </div>

        <div v-else class="flex flex-col gap-3">
          <RouterLink
            v-for="order in recentOrders"
            :key="order.id"
            :to="{ name: 'order-detail', params: { id: order.id } }"
            class="flex items-center justify-between gap-3 bg-white rounded-2xl border border-slate-200 p-5 hover:border-emerald-300 transition"
          >
            <div class="min-w-0">
              <p class="text-sm font-bold text-slate-900">Pedido #{{ order.id }}</p>
              <p class="text-xs text-slate-500 mt-0.5">{{ formatDate(order.createdAt) }} · $ {{ order.total.toLocaleString() }}</p>
            </div>
            <span
              class="shrink-0 text-[10px] font-bold uppercase px-2.5 py-1 rounded-full"
              :class="ORDER_STATUS_BADGE[order.status]"
            >
              {{ order.status }}
            </span>
          </RouterLink>
        </div>
      </section>

      <!-- Citas -->
      <section>
        <h2 class="flex items-center gap-2 text-sm font-bold text-slate-900 mb-4">
          <AppIcon name="calendar" :size="16" class="text-emerald-700" />
          Tus próximas citas
        </h2>

        <div v-if="appointmentsStore.loading" class="text-sm text-slate-500">Cargando...</div>
        <p v-else-if="appointmentsStore.error" class="text-sm text-red-600">{{ appointmentsStore.error }}</p>
        <div
          v-else-if="!upcomingAppointments.length"
          class="bg-white border border-slate-200 rounded-2xl p-6 text-sm text-slate-500"
        >
          No tienes citas próximas.
          <RouterLink
            to="/mis-citas/agendar"
            class="text-emerald-700 font-semibold hover:underline"
          >
            Agendar una
          </RouterLink>
        </div>

        <div v-else class="flex flex-col gap-3">
          <RouterLink
            v-for="appt in upcomingAppointments"
            :key="appt.id"
            :to="{ name: 'appointment-detail', params: { id: appt.id } }"
            class="flex items-center justify-between gap-3 bg-white rounded-2xl border border-slate-200 p-5 hover:border-emerald-300 transition"
          >
            <div class="min-w-0">
              <p class="text-sm font-bold text-slate-900">{{ appt.pet?.name || 'Mascota' }} — {{ appt.reason }}</p>
              <p class="text-xs text-slate-500 mt-0.5">{{ formatDateTime(appt.appointmentDatetime) }}</p>
            </div>
            <span
              class="shrink-0 text-[10px] font-bold uppercase px-2.5 py-1 rounded-full"
              :class="APPOINTMENT_STATUS_BADGE[appt.status]"
            >
              {{ appt.status }}
            </span>
          </RouterLink>
        </div>
      </section>
    </main>

    <Footer />
  </div>
</template>
