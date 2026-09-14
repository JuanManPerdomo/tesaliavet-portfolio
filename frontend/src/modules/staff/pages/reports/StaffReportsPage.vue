<script setup>
import { computed, ref } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import FinancialReportTab from './FinancialReportTab.vue'
import InventoryReportTab from './InventoryReportTab.vue'
import ClientsReportTab from './ClientsReportTab.vue'
import AppointmentsReportTab from './AppointmentsReportTab.vue'
import CashReportTab from './CashReportTab.vue'
import { useAuthStore } from '../../../../stores/auth'

const ALL_TABS = [
  { value: 'financiero', label: 'Financiero', icon: 'cash', component: FinancialReportTab },
  { value: 'inventario', label: 'Inventario', icon: 'package', component: InventoryReportTab },
  { value: 'clientes', label: 'Clientes', icon: 'users', component: ClientsReportTab },
  { value: 'citas', label: 'Citas', icon: 'calendar', component: AppointmentsReportTab },
  { value: 'caja', label: 'Caja', icon: 'cash', component: CashReportTab },
]

const authStore = useAuthStore()
// Bodeguero solo tiene permiso de verdad sobre /reports/inventory en el
// backend (decision Bodeguero, 2026-09-02) - mostrarle las otras 4 pestañas
// solo le pegaria contra endpoints que le devuelven 403.
const TABS = computed(() => (authStore.hasRole('admin') ? ALL_TABS : ALL_TABS.filter((t) => t.value === 'inventario')))

const activeTab = ref(authStore.hasRole('admin') ? 'financiero' : 'inventario')
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-extrabold text-slate-900">Reportes</h1>
      <p class="text-sm text-slate-500 mt-1">
        Financiero, inventario, clientes, citas y caja — todo calculado sobre datos reales del negocio.
      </p>
    </div>

    <div class="flex overflow-x-auto gap-6 border-b border-slate-200 mb-6">
      <button
        v-for="tab in TABS"
        :key="tab.value"
        type="button"
        class="pb-3 text-sm font-semibold whitespace-nowrap border-b-2 transition flex items-center gap-1.5"
        :class="
          activeTab === tab.value
            ? 'text-emerald-700 border-emerald-700'
            : 'text-slate-500 border-transparent hover:text-emerald-700'
        "
        @click="activeTab = tab.value"
      >
        <AppIcon :name="tab.icon" :size="15" />
        {{ tab.label }}
      </button>
    </div>

    <component :is="TABS.find((t) => t.value === activeTab).component" />
  </div>
</template>
