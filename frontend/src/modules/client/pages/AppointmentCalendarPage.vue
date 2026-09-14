<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import { useAppointmentsStore } from '../../../stores/appointments'

const route = useRoute()
const router = useRouter()
const appointmentsStore = useAppointmentsStore()

const WEEKDAY_LABELS = ['DOM', 'LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB']
const MONTH_LABELS = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

function pad2(n) {
  return String(n).padStart(2, '0')
}
function isoDate(year, month, day) {
  return `${year}-${pad2(month + 1)}-${pad2(day)}`
}

const today = new Date()
const todayIso = isoDate(today.getFullYear(), today.getMonth(), today.getDate())

const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth())

const selectedDate = ref(todayIso)
const selectedSlot = ref(null)

const monthSummary = ref({})
const daySlots = ref([])
const summaryLoading = ref(false)
const slotsLoading = ref(false)
const errorMessage = ref('')

const isViewingCurrentMonth = computed(
  () => viewYear.value === today.getFullYear() && viewMonth.value === today.getMonth()
)

const calendarCells = computed(() => {
  const firstWeekday = new Date(viewYear.value, viewMonth.value, 1).getDay()
  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  const daysInPrevMonth = new Date(viewYear.value, viewMonth.value, 0).getDate()

  const cells = []
  for (let i = firstWeekday - 1; i >= 0; i--) {
    cells.push({ day: daysInPrevMonth - i, inMonth: false })
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const iso = isoDate(viewYear.value, viewMonth.value, d)
    cells.push({
      day: d,
      inMonth: true,
      iso,
      isPast: iso < todayIso,
      isToday: iso === todayIso,
      isSelected: iso === selectedDate.value,
      hasAvailability: monthSummary.value[iso] ?? false,
    })
  }
  let nextDay = 1
  while (cells.length % 7 !== 0) {
    cells.push({ day: nextDay++, inMonth: false })
  }
  return cells
})

const selectedDateLabel = computed(() => {
  if (!selectedDate.value) return ''
  const label = new Date(`${selectedDate.value}T00:00:00`).toLocaleDateString('es-CO', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  })
  return label.charAt(0).toUpperCase() + label.slice(1)
})

function formatSlotLabel(time24) {
  const [h] = time24.split(':').map(Number)
  const period = h >= 12 ? 'PM' : 'AM'
  const hour12 = h % 12 === 0 ? 12 : h % 12
  return `${pad2(hour12)}:00 ${period}`
}

async function loadMonthSummary() {
  summaryLoading.value = true
  try {
    const monthStr = `${viewYear.value}-${pad2(viewMonth.value + 1)}`
    const { days } = await appointmentsStore.fetchAvailabilitySummary(monthStr)
    monthSummary.value = Object.fromEntries(days.map((d) => [d.date, d.hasAvailability]))
  } catch {
    monthSummary.value = {}
  } finally {
    summaryLoading.value = false
  }
}

async function loadDaySlots() {
  if (!selectedDate.value) return
  slotsLoading.value = true
  selectedSlot.value = null
  try {
    const { slots } = await appointmentsStore.fetchAvailability(selectedDate.value)
    daySlots.value = slots
  } catch {
    daySlots.value = []
  } finally {
    slotsLoading.value = false
  }
}

function selectDay(cell) {
  if (!cell.inMonth || cell.isPast) return
  selectedDate.value = cell.iso
}

function selectSlot(slot) {
  if (!slot.available) return
  selectedSlot.value = slot.time
}

function prevMonth() {
  if (isViewingCurrentMonth.value) return
  if (viewMonth.value === 0) {
    viewMonth.value = 11
    viewYear.value -= 1
  } else {
    viewMonth.value -= 1
  }
}

function nextMonth() {
  if (viewMonth.value === 11) {
    viewMonth.value = 0
    viewYear.value += 1
  } else {
    viewMonth.value += 1
  }
}

function handleContinue() {
  if (!selectedDate.value || !selectedSlot.value) return
  router.push({
    name: 'appointment-new',
    query: {
      date: selectedDate.value,
      time: selectedSlot.value,
      petId: route.query.petId,
    },
  })
}

watch([viewYear, viewMonth], loadMonthSummary)
watch(selectedDate, loadDaySlots)

onMounted(() => {
  loadMonthSummary()
  loadDaySlots()
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-6xl mx-auto px-6 py-12 w-full">
      <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Agendar Cita</h1>
      <p class="text-sm text-slate-500 mb-8 max-w-2xl">
        Selecciona la fecha y hora que mejor se adapte a ti. Nuestro equipo está listo para
        atender a tu mascota.
      </p>

      <p v-if="errorMessage" class="text-sm text-red-600 mb-6">{{ errorMessage }}</p>

      <div class="flex flex-col lg:flex-row gap-8 items-start">
        <!-- Calendar -->
        <div class="w-full lg:w-2/3 bg-white rounded-2xl border border-slate-200 p-6 lg:p-8">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-bold text-slate-900">
              {{ MONTH_LABELS[viewMonth] }} {{ viewYear }}
            </h2>
            <div class="flex gap-1">
              <button
                type="button"
                :disabled="isViewingCurrentMonth"
                class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-slate-100 text-slate-500 disabled:opacity-30 disabled:pointer-events-none transition"
                @click="prevMonth"
              >
                <AppIcon name="chevron-left" :size="18" />
              </button>
              <button
                type="button"
                class="w-8 h-8 rounded-full flex items-center justify-center hover:bg-slate-100 text-slate-500 transition"
                @click="nextMonth"
              >
                <AppIcon name="chevron-right" :size="18" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-7 gap-1 mb-2">
            <div
              v-for="label in WEEKDAY_LABELS"
              :key="label"
              class="text-center text-[11px] font-semibold text-slate-400 uppercase py-2"
            >
              {{ label }}
            </div>
          </div>

          <div class="grid grid-cols-7 gap-1 sm:gap-2">
            <button
              v-for="(cell, index) in calendarCells"
              :key="index"
              type="button"
              :disabled="!cell.inMonth || cell.isPast"
              class="aspect-square flex flex-col items-center justify-center rounded-lg text-sm transition relative"
              :class="[
                !cell.inMonth ? 'opacity-0 pointer-events-none' : '',
                cell.inMonth && cell.isPast ? 'text-slate-300 cursor-not-allowed' : '',
                cell.inMonth && !cell.isPast && !cell.isSelected
                  ? 'text-slate-700 hover:bg-slate-100 border border-transparent hover:border-slate-200'
                  : '',
                cell.isSelected ? 'bg-emerald-700 text-white font-bold shadow-sm' : '',
              ]"
              @click="selectDay(cell)"
            >
              <span>{{ cell.day }}</span>
              <div
                v-if="cell.inMonth && !cell.isPast && !cell.isSelected && cell.hasAvailability"
                class="w-1.5 h-1.5 rounded-full bg-emerald-400 absolute bottom-1.5"
              ></div>
            </button>
          </div>

          <div class="flex flex-wrap justify-center gap-6 mt-6 pt-6 border-t border-slate-100">
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 rounded-full bg-emerald-400"></div>
              <span class="text-xs text-slate-500">Disponible</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 rounded-full bg-emerald-700"></div>
              <span class="text-xs text-slate-500">Seleccionado</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 rounded-full border border-dashed border-slate-300"></div>
              <span class="text-xs text-slate-500">No disponible</span>
            </div>
          </div>
        </div>

        <!-- Time slots + summary -->
        <div class="w-full lg:w-1/3 flex flex-col gap-6">
          <div class="bg-white rounded-2xl border border-slate-200 p-6">
            <h4 class="text-xs font-semibold text-slate-400 uppercase mb-1">Fecha seleccionada</h4>
            <p class="text-lg font-bold text-emerald-700 mb-5">{{ selectedDateLabel }}</p>

            <h5 class="text-sm font-semibold text-slate-800 mb-3 flex items-center gap-2">
              <AppIcon name="clock" :size="16" />
              Horarios disponibles
            </h5>

            <div v-if="slotsLoading" class="text-sm text-slate-400">Cargando horarios...</div>
            <div
              v-else-if="daySlots.length === 0"
              class="text-sm text-slate-400"
            >
              No hay horarios de atención ese día.
            </div>
            <div v-else class="grid grid-cols-2 gap-2.5 max-h-72 overflow-y-auto pr-1">
              <button
                v-for="slot in daySlots"
                :key="slot.time"
                type="button"
                :disabled="!slot.available"
                class="py-2.5 px-2 rounded-lg border text-center text-sm transition"
                :class="[
                  !slot.available
                    ? 'border-dashed border-slate-200 bg-slate-50 text-slate-300 line-through cursor-not-allowed'
                    : selectedSlot === slot.time
                      ? 'border-2 border-emerald-700 bg-emerald-50 text-emerald-700 font-bold'
                      : 'border-slate-200 text-slate-700 hover:border-emerald-700 hover:bg-emerald-50/50',
                ]"
                @click="selectSlot(slot)"
              >
                {{ formatSlotLabel(slot.time) }}
              </button>
            </div>
          </div>

          <div class="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col gap-4">
            <div class="flex justify-between items-center pb-4 border-b border-slate-100">
              <span class="text-sm text-slate-500">Cita seleccionada:</span>
              <span class="text-sm font-semibold text-slate-800">
                {{ selectedSlot ? `${selectedDateLabel} · ${formatSlotLabel(selectedSlot)}` : '—' }}
              </span>
            </div>
            <PrimaryButton
              :disabled="!selectedSlot"
              class="w-full justify-center gap-2"
              @click="handleContinue"
            >
              Continuar
              <AppIcon name="chevron-right" :size="16" />
            </PrimaryButton>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>
