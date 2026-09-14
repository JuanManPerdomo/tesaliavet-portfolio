<script setup>
import { computed, onMounted, ref } from 'vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import KpiTile from '../components/KpiTile.vue'
import IncomeChart from '../components/IncomeChart.vue'
import PetPhoto from '../../client/components/PetPhoto.vue'
import { useAuthStore } from '../../../stores/auth'
import { useStaffStore } from '../../../stores/staff'
import { useAppointmentsStore } from '../../../stores/appointments'
import { useStaffClientsStore } from '../../../stores/staffClients'
import { useStockAlertsStore } from '../../../stores/stockAlerts'
import { useOrdersStore } from '../../../stores/orders'
import { useProductsStore } from '../../../stores/products'
import { useStaffNotificationsStore } from '../../../stores/staffNotifications'
import { useStaffPetsStore } from '../../../stores/staffPets'
import { NOTIFICATION_TYPE_META } from '../../../lib/notificationTypes'
import { formatCOP } from '../../../lib/pricing'

const ROLE_LABELS = {
  admin: 'Administrador',
  veterinario: 'Veterinario',
  bodeguero: 'Bodeguero',
}

const RANGE_OPTIONS = [
  { value: 'dia', label: 'Día' },
  { value: 'semana', label: 'Semana' },
  { value: 'mes', label: 'Mes' },
  { value: 'año', label: 'Año' },
]

// Texto especifico por pestaña en vez de un generico "periodo anterior" -
// pedido por Juan Manuel. "Mes" compara 6 meses contra los 6 anteriores (no
// 1 mes), por eso dice "semestre" y no "mes anterior" (decision 47). "Año"
// ahora muestra 5 años (no meses de este año, ver decision 97) y compara
// contra los 5 años previos a ese bloque, por eso "5 años anteriores" y no
// "año anterior" - seria enganoso decir un solo año.
const COMPARISON_LABELS = {
  dia: 'vs. ayer',
  semana: 'vs. semana anterior',
  mes: 'vs. semestre anterior',
  año: 'vs. 5 años anteriores',
}
// Misma idea pero para cuando no hay dato del periodo anterior con que
// comparar (ej. el negocio no tiene ventas tan atras todavia) - se muestra
// un texto real en vez de esconder la comparacion por completo, para que
// quede claro que la funcion existe (decision 7: nunca inventar un numero).
const NO_DATA_LABELS = {
  dia: 'Sin datos de ayer para comparar',
  semana: 'Sin datos de la semana anterior para comparar',
  mes: 'Sin datos del semestre anterior para comparar',
  año: 'Sin datos de años anteriores para comparar',
}
const comparisonLabel = computed(() => COMPARISON_LABELS[chartRange.value] || 'vs. período anterior')
const noDataLabel = computed(() => NO_DATA_LABELS[chartRange.value] || 'Sin datos del período anterior para comparar')

const authStore = useAuthStore()
const staffStore = useStaffStore()
const appointmentsStore = useAppointmentsStore()
const clientsStore = useStaffClientsStore()
const stockAlertsStore = useStockAlertsStore()
const ordersStore = useOrdersStore()
const productsStore = useProductsStore()
const staffNotificationsStore = useStaffNotificationsStore()
const staffPetsStore = useStaffPetsStore()

const isAdmin = computed(() => authStore.hasRole('admin'))
const isVet = computed(() => authStore.hasRole('veterinario'))
const isBodeguero = computed(() => authStore.hasRole('bodeguero'))
// Citas es terreno de admin/veterinario, nunca de Bodeguero (decision
// Bodeguero, 2026-09-02) - se usa para no pedir /appointments/staff (403
// para una cuenta bodeguero-pura, ver appointments/routes.py) ni mostrarle
// tarjetas de citas que no le aplican.
const canSeeAppointments = computed(() => isAdmin.value || isVet.value)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Buenos días'
  if (hour < 19) return 'Buenas tardes'
  return 'Buenas noches'
})

const displayName = computed(() => staffStore.profile?.firstName || authStore.user?.firstName)

const roleBadges = computed(() =>
  (authStore.user?.roles || []).map((r) => ROLE_LABELS[r] || r)
)

const todayLabel = computed(() => {
  const formatted = new Date().toLocaleDateString('es-CO', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
  return formatted.charAt(0).toUpperCase() + formatted.slice(1)
})

const chartRange = ref('semana')

// Pacientes recientes / vacunas por vencer - panel del veterinario, antes
// muy vacio (decision 18: solo tenia Inicio + Citas asignadas). Tambien se
// muestra para una cuenta admin+veterinario (decision 16), sumado a su
// vista admin completa.
const recentPatients = ref([])
const upcomingVaccines = ref([])

onMounted(() => {
  if (canSeeAppointments.value) {
    appointmentsStore.fetchStaffAppointments(undefined, !isAdmin.value)
  }
  staffNotificationsStore.fetchNotifications({ perPage: 5 })
  if (isAdmin.value || isBodeguero.value) {
    stockAlertsStore.fetchAlerts('Activa')
  }
  if (isVet.value) {
    staffPetsStore.fetchRecentPatients(6).then((data) => {
      recentPatients.value = data
    })
    staffPetsStore.fetchUpcomingVaccines(6).then((data) => {
      upcomingVaccines.value = data
    })
  }
  if (isAdmin.value) {
    clientsStore.fetchStats()
    ordersStore.fetchStaffOrders({ status: 'Pendiente' })
    ordersStore.fetchDashboardKpis()
    ordersStore.fetchIncomeChart(chartRange.value)
    ordersStore.fetchRecentPayments(6)
    productsStore.fetchFeaturedProducts(5)
  }
})

function handleRangeChange(range) {
  chartRange.value = range
  ordersStore.fetchIncomeChart(range)
}

const todayAppointments = computed(() => {
  // Fecha local (no UTC) - appointment_datetime viaja naive/local desde el
  // backend, toISOString() correria el dia cerca de medianoche.
  const now = new Date()
  const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  // Una cita Cancelada fechada hoy no es una cita que vaya a pasar hoy - no
  // debe contar en el KPI.
  return appointmentsStore.staffAppointments.filter(
    (a) => a.appointmentDatetime.startsWith(todayStr) && a.status !== 'Cancelada'
  )
})

const confirmedTodayCount = computed(
  () => todayAppointments.value.filter((a) => a.status === 'Confirmada').length
)

const criticalAlertsCount = computed(
  () => stockAlertsStore.alerts.filter((a) => a.currentStock <= 0).length
)

// Proximas citas: se derivan de lo que ya trae appointmentsStore (sin
// endpoint nuevo) - pendientes/confirmadas a partir de ahora, las 5 mas
// cercanas. Ya viene scopeado por rol desde fetchStaffAppointments (admin ve
// todas, veterinario solo las suyas).
const upcomingAppointments = computed(() => {
  const now = new Date()
  return appointmentsStore.staffAppointments
    .filter((a) => ['Pendiente', 'Confirmada'].includes(a.status) && new Date(a.appointmentDatetime) >= now)
    .sort((a, b) => new Date(a.appointmentDatetime) - new Date(b.appointmentDatetime))
    .slice(0, 5)
})

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(isoDate) {
  if (!isoDate) return '—'
  return new Date(isoDate + 'T00:00:00').toLocaleDateString('es-CO', { day: '2-digit', month: 'short' })
}

// Base de clientes por especie: Perro/Gato tienen datos reales, el resto
// (especies de Ganaderia, decision 20) se agrupan como "Otros".
const speciesBuckets = computed(() => {
  const rows = clientsStore.stats?.petsBySpecies || []
  const dogs = rows.find((r) => r.species === 'Perro')?.count || 0
  const cats = rows.find((r) => r.species === 'Gato')?.count || 0
  const total = rows.reduce((sum, r) => sum + r.count, 0)
  return [
    { label: 'Perros', count: dogs, color: '#047857' },
    { label: 'Gatos', count: cats, color: '#0ea5e9' },
    { label: 'Otros', count: Math.max(total - dogs - cats, 0), color: '#f59e0b' },
  ]
})

const donutSegments = computed(() => {
  const circumference = 2 * Math.PI * 50
  const total = clientsStore.stats?.totalActivePets || 0
  let cumulative = 0
  return speciesBuckets.value.map((b) => {
    const length = total > 0 ? (b.count / total) * circumference : 0
    const segment = { ...b, length, offset: -cumulative, circumference }
    cumulative += length
    return segment
  })
})

const kpiTiles = computed(() => {
  const tiles = []

  if (isAdmin.value && ordersStore.dashboardKpis) {
    tiles.push({
      icon: 'cash',
      label: 'Ingresos del día',
      value: formatCOP(ordersStore.dashboardKpis.incomeToday),
      iconBgClass: 'bg-emerald-50',
      iconColorClass: 'text-emerald-700',
    })
    tiles.push({
      icon: 'shopping-bag',
      label: 'Ventas realizadas',
      value: ordersStore.dashboardKpis.salesToday,
      iconBgClass: 'bg-cyan-50',
      iconColorClass: 'text-cyan-700',
    })
  }

  if (canSeeAppointments.value) {
    tiles.push({
      icon: 'calendar',
      label: isAdmin.value ? 'Citas hoy' : 'Mis citas hoy',
      value: todayAppointments.value.length,
      sub: `${confirmedTodayCount.value} confirmadas`,
      to: { name: isAdmin.value ? 'staff-appointments' : 'staff-appointments-mine' },
      iconBgClass: 'bg-sky-50',
      iconColorClass: 'text-sky-700',
    })
  }

  if (isAdmin.value || isBodeguero.value) {
    tiles.push({
      icon: 'alert-triangle',
      label: 'Alertas de stock',
      value: stockAlertsStore.alerts.length,
      sub: stockAlertsStore.alerts.length
        ? `${stockAlertsStore.alerts.length} producto(s) bajo el mínimo`
        : 'Todo el inventario está bien',
      badge: criticalAlertsCount.value ? 'Crítico' : '',
      to: { name: 'staff-stock-alerts' },
      iconBgClass: 'bg-amber-50',
      iconColorClass: 'text-amber-700',
    })
  }

  return tiles
})
</script>

<template>
  <div class="space-y-10">
    <!-- Welcome banner -->
    <div
      class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-700 via-emerald-600 to-teal-600 px-8 py-10"
    >
      <div
        class="pointer-events-none absolute -top-12 -right-12 w-56 h-56 bg-white/10 rounded-full blur-3xl"
      ></div>

      <div
        class="pointer-events-none absolute -bottom-16 -left-10 w-64 h-64 bg-white/5 rounded-full blur-3xl"
      ></div>

      <div class="relative text-white">
        <p class="text-sm font-semibold text-white/70">{{ todayLabel }}</p>

        <h1 class="mt-2 text-3xl md:text-4xl font-extrabold tracking-tight">
          {{ greeting }}, {{ displayName }}
        </h1>

        <p class="mt-2 text-white/80 max-w-xl">
          Bienvenido de vuelta al panel de personal de TesaliaVet.
        </p>

        <p v-if="staffStore.error" class="mt-4 text-sm text-red-100 bg-red-500/20 rounded-xl px-4 py-2 inline-block">
          {{ staffStore.error }}
        </p>

        <div v-else class="mt-5 flex flex-wrap gap-2">
          <span
            v-for="role in roleBadges"
            :key="role"
            class="inline-flex items-center gap-1.5 bg-white/15 backdrop-blur-sm px-3.5 py-1.5 rounded-full text-xs font-semibold"
          >
            <AppIcon name="shield-check" :size="14" />
            {{ role }}
          </span>
        </div>
      </div>
    </div>

    <!-- KPIs reales -->
    <div>
      <p class="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-5">
        Resumen de hoy
      </p>

      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiTile v-for="tile in kpiTiles" :key="tile.label" v-bind="tile" />
      </div>
    </div>

    <!-- Ingresos + Proximas citas: ninguna de las 2 aplica a Bodeguero -->
    <div v-if="isAdmin || isVet" class="grid lg:grid-cols-3 gap-6">
      <div v-if="isAdmin" class="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-1">
          <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <AppIcon name="chart-bar" :size="16" class="text-emerald-700" />
            Ingresos Generados
          </h3>
          <div class="flex gap-1 bg-slate-50 rounded-lg p-1">
            <button
              v-for="opt in RANGE_OPTIONS"
              :key="opt.value"
              type="button"
              class="px-3 py-1 rounded-md text-xs font-semibold transition"
              :class="chartRange === opt.value ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
              @click="handleRangeChange(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div v-if="ordersStore.incomeChart" class="flex items-baseline gap-2 mb-2">
          <p class="text-2xl font-extrabold text-slate-900">{{ formatCOP(ordersStore.incomeChart.total) }}</p>
          <span
            v-if="ordersStore.incomeChart.comparisonPercent !== null"
            class="text-xs font-bold"
            :class="ordersStore.incomeChart.comparisonPercent >= 0 ? 'text-emerald-700' : 'text-red-600'"
          >
            {{ ordersStore.incomeChart.comparisonPercent >= 0 ? '+' : '' }}{{ ordersStore.incomeChart.comparisonPercent.toFixed(1) }}%
            {{ comparisonLabel }}
          </span>
          <span v-else class="text-xs text-slate-400">{{ noDataLabel }}</span>
        </div>

        <IncomeChart :series="ordersStore.incomeChart?.series || []" :loading="ordersStore.dashboardLoading" />
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6" :class="isAdmin ? '' : 'lg:col-span-3'">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <AppIcon name="calendar" :size="16" class="text-emerald-700" />
            Próximas Citas
          </h3>
          <RouterLink
            :to="{ name: isAdmin ? 'staff-appointments' : 'staff-appointments-mine' }"
            class="text-xs font-semibold text-emerald-700 hover:underline"
          >
            Ver todas
          </RouterLink>
        </div>

        <div v-if="!upcomingAppointments.length" class="text-sm text-slate-400 text-center py-8">
          No hay citas próximas.
        </div>
        <div v-else class="space-y-1">
          <RouterLink
            v-for="appt in upcomingAppointments"
            :key="appt.id"
            :to="{ name: 'staff-appointment-detail', params: { id: appt.id } }"
            class="flex items-center gap-3 py-2.5 px-2 -mx-2 rounded-lg hover:bg-slate-50 transition"
          >
            <div class="w-10 h-10 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
              <PetPhoto :photo-url="appt.pet?.photoUrl" :icon-size="16" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-slate-900 truncate">{{ appt.pet?.name }}</p>
              <p class="text-xs text-slate-500 truncate">{{ appt.ownerName }} · {{ appt.reason }}</p>
            </div>
            <p class="text-xs font-semibold text-slate-600 shrink-0">{{ formatTime(appt.appointmentDatetime) }}</p>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Atencion Requerida: stock + PQRS + pedidos + vacunas (admin), solo
    stock (Bodeguero) o citas + vacunas de sus propios pacientes (veterinario
    puro) - mismas fuentes que ya calcula /staff/notifications (decision
    51/93/Bodeguero/vacunas). Visible para los 3 roles, a diferencia del
    resto de esta seccion que sigue siendo admin-only. -->
    <div class="bg-white rounded-2xl border border-slate-200 p-6">
      <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
        <AppIcon name="alert-triangle" :size="16" class="text-amber-600" />
        Atención Requerida
      </h3>
      <div v-if="!staffNotificationsStore.items.length" class="text-sm text-slate-400 text-center py-8">
        {{
          isAdmin
            ? 'Nada pendiente por revisar.'
            : isBodeguero
              ? 'No hay alertas de stock activas.'
              : 'No tienes citas ni vacunas por revisar.'
        }}
      </div>
      <div v-else class="space-y-1">
        <RouterLink
          v-for="n in staffNotificationsStore.items"
          :key="n.key"
          :to="n.action.to"
          class="flex items-center gap-3 py-2.5 px-2 -mx-2 rounded-lg hover:bg-slate-50 transition"
        >
          <div
            class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
            :class="[NOTIFICATION_TYPE_META[n.type]?.iconBgClass, NOTIFICATION_TYPE_META[n.type]?.iconColorClass]"
          >
            <AppIcon :name="NOTIFICATION_TYPE_META[n.type]?.icon || 'bell'" :size="16" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-semibold text-slate-800 truncate">{{ n.title }}</p>
            <p class="text-xs text-slate-400 truncate">{{ n.description }}</p>
          </div>
        </RouterLink>
      </div>
      <RouterLink
        :to="{ name: 'staff-notifications' }"
        class="mt-3 flex items-center justify-center gap-2 text-xs font-semibold text-emerald-700 hover:underline"
      >
        Ver todas las notificaciones
        <AppIcon name="chevron-right" :size="12" />
      </RouterLink>
    </div>

    <!-- Pacientes recientes + Vacunas por vencer: solo veterinario (panel
    del veterinario, antes muy vacio). Tambien se muestra en el combo
    admin+veterinario (decision 16), sumado a su vista admin completa. -->
    <div v-if="isVet" class="grid lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <AppIcon name="paw" :size="16" class="text-emerald-700" />
            Pacientes Recientes
          </h3>
          <RouterLink :to="{ name: 'staff-pets' }" class="text-xs font-semibold text-emerald-700 hover:underline">
            Ver todas
          </RouterLink>
        </div>
        <div v-if="!recentPatients.length" class="text-sm text-slate-400 text-center py-8">
          Todavía no has atendido ninguna mascota.
        </div>
        <div v-else class="space-y-1">
          <RouterLink
            v-for="pet in recentPatients"
            :key="pet.id"
            :to="{ name: 'staff-pet-detail', params: { id: pet.id } }"
            class="flex items-center gap-3 py-2.5 px-2 -mx-2 rounded-lg hover:bg-slate-50 transition"
          >
            <div class="w-10 h-10 rounded-full overflow-hidden bg-slate-100 flex-shrink-0">
              <PetPhoto :photo-url="pet.photoUrl" :icon-size="16" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-bold text-slate-900 truncate">{{ pet.name }}</p>
              <p class="text-xs text-slate-500 truncate">{{ pet.owner?.name }}</p>
            </div>
            <p class="text-xs font-semibold text-slate-600 shrink-0">{{ formatDate(pet.lastVisitDate) }}</p>
          </RouterLink>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="medical-cross" :size="16" class="text-amber-600" />
          Vacunas por Vencer
        </h3>
        <div v-if="!upcomingVaccines.length" class="text-sm text-slate-400 text-center py-8">
          Sin vacunas próximas a vencer entre tus pacientes.
        </div>
        <div v-else class="space-y-1">
          <RouterLink
            v-for="pet in upcomingVaccines"
            :key="pet.id"
            :to="{ name: 'staff-pet-detail', params: { id: pet.id } }"
            class="flex items-center justify-between gap-3 py-2.5 px-2 -mx-2 rounded-lg hover:bg-slate-50 transition"
          >
            <div class="min-w-0">
              <p class="text-sm font-semibold text-slate-800 truncate">
                {{ pet.name }} · {{ pet.nextVaccine.vaccineName }}
              </p>
              <p class="text-xs text-slate-400 truncate">{{ pet.owner?.name }}</p>
            </div>
            <span
              class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full shrink-0"
              :class="pet.nextVaccine.isOverdue ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-700'"
            >
              {{ pet.nextVaccine.isOverdue ? 'Vencida' : formatDate(pet.nextVaccine.nextDueDate) }}
            </span>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Base de clientes, actividad reciente -->
    <div v-if="isAdmin" class="grid lg:grid-cols-2 gap-6">
      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="users" :size="16" class="text-emerald-700" />
          Base de Mascotas
        </h3>
        <div class="flex items-center justify-between mb-5">
          <div>
            <p class="text-[11px] text-slate-400 uppercase font-bold">Totales</p>
            <p class="text-xl font-extrabold text-slate-900">{{ clientsStore.stats?.total ?? '—' }}</p>
          </div>
          <div class="text-right">
            <p class="text-[11px] text-slate-400 uppercase font-bold">Nuevos (mes)</p>
            <p class="text-xl font-extrabold text-emerald-700">+{{ clientsStore.stats?.newThisMonth ?? 0 }}</p>
          </div>
        </div>

        <div class="flex flex-col items-center">
          <svg viewBox="0 0 120 120" class="w-28 h-28">
            <circle cx="60" cy="60" r="50" fill="none" stroke="#e2e8f0" stroke-width="14" />
            <circle
              v-for="seg in donutSegments"
              :key="seg.label"
              cx="60"
              cy="60"
              r="50"
              fill="none"
              :stroke="seg.color"
              stroke-width="14"
              :stroke-dasharray="`${seg.length} ${seg.circumference}`"
              :stroke-dashoffset="seg.offset"
              transform="rotate(-90 60 60)"
            />
            <text x="60" y="56" text-anchor="middle" class="fill-slate-900 font-extrabold" style="font-size: 20px">
              {{ clientsStore.stats?.totalActivePets ?? 0 }}
            </text>
            <text x="60" y="74" text-anchor="middle" class="fill-slate-400" style="font-size: 10px">mascotas</text>
          </svg>
          <div class="flex flex-wrap justify-center gap-3 mt-3 text-xs">
            <span v-for="b in speciesBuckets" :key="b.label" class="flex items-center gap-1.5 text-slate-600">
              <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: b.color }"></span>
              {{ b.label }} ({{ b.count }})
            </span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
          <AppIcon name="cash" :size="16" class="text-emerald-700" />
          Actividad Reciente
        </h3>
        <div v-if="!ordersStore.recentPayments.length" class="text-sm text-slate-400 text-center py-8">
          Sin pagos registrados todavía.
        </div>
        <div v-else class="space-y-1">
          <RouterLink
            v-for="p in ordersStore.recentPayments"
            :key="p.id"
            :to="{ name: 'staff-order-detail', params: { id: p.orderId } }"
            class="flex items-center justify-between gap-3 py-2.5 px-2 -mx-2 rounded-lg hover:bg-slate-50 transition"
          >
            <div class="min-w-0">
              <p class="text-sm font-semibold text-slate-800 truncate">{{ p.customerName || 'Cliente' }}</p>
              <p class="text-xs text-slate-400">{{ p.invoiceNumber }} · {{ formatTime(p.paidAt) }} · {{ p.method }}</p>
            </div>
            <p class="text-sm font-bold text-emerald-700 shrink-0">{{ formatCOP(p.amount) }}</p>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Productos destacados: top 5 mas vendidos, sobre ventas reales -->
    <div v-if="isAdmin" class="bg-white rounded-2xl border border-slate-200 p-6">
      <div class="flex items-center justify-between mb-1">
        <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
          <AppIcon name="shopping-bag" :size="16" class="text-emerald-700" />
          Productos Destacados
        </h3>
        <RouterLink :to="{ name: 'staff-products' }" class="text-xs font-semibold text-emerald-700 hover:underline">
          Ver catálogo
        </RouterLink>
      </div>
      <p class="text-xs text-slate-400 mb-4">Los más vendidos, calculados sobre las ventas reales del negocio.</p>

      <div v-if="!productsStore.featuredProducts.length" class="text-sm text-slate-400 text-center py-8">
        Todavía no hay ventas registradas para calcular destacados.
      </div>
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <RouterLink
          v-for="product in productsStore.featuredProducts"
          :key="product.id"
          :to="{ name: 'staff-product-edit', params: { id: product.id } }"
          class="rounded-xl border border-slate-100 hover:border-emerald-300 hover:bg-emerald-50/40 transition p-3 flex flex-col"
        >
          <div class="w-full aspect-square rounded-lg overflow-hidden bg-slate-100 mb-2">
            <img
              v-if="product.image"
              :src="product.image"
              :alt="product.name"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-slate-300">
              <AppIcon name="paw" :size="24" />
            </div>
          </div>
          <p class="text-xs font-bold text-slate-900 line-clamp-2">{{ product.name }}</p>
          <p class="text-[11px] text-slate-400 mt-0.5">{{ product.unitsSold }} vendidos</p>
          <p class="text-sm font-bold text-emerald-700 mt-auto pt-1">{{ formatCOP(product.price) }}</p>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
