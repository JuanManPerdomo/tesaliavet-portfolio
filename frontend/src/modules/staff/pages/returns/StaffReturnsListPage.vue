<script setup>
import { ref, onMounted } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import NewReturnModal from './NewReturnModal.vue'
import { useReturnsStore } from '../../../../stores/returns'
import { useToastStore } from '../../../../stores/toast'
import { useCashRegisterStore } from '../../../../stores/cashRegister'

const returnsStore = useReturnsStore()
const toastStore = useToastStore()
const cashRegisterStore = useCashRegisterStore()

const search = ref('')
const showNewReturn = ref(false)
const creating = ref(false)
const createError = ref('')

function load() {
  returnsStore.fetchStaffReturns({ search: search.value || undefined })
}

onMounted(() => {
  load()
  cashRegisterStore.fetchCurrent()
})

function handleSearch() {
  load()
}

function openNewReturn() {
  if (!cashRegisterStore.current) return
  createError.value = ''
  showNewReturn.value = true
}

async function handleCreateReturn({ orderId, payload }) {
  creating.value = true
  createError.value = ''
  try {
    await returnsStore.createReturn(orderId, payload)
    toastStore.success('Devolución registrada.')
    showNewReturn.value = false
    load()
  } catch (err) {
    createError.value = err.response?.data?.message || 'No se pudo registrar la devolución.'
  } finally {
    creating.value = false
  }
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function firstItem(ret) {
  return ret.items?.[0]
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-1">
      <h1 class="text-2xl font-extrabold text-slate-900">Devoluciones</h1>
      <PrimaryButton class="gap-2" :disabled="!cashRegisterStore.current" @click="openNewReturn">
        <AppIcon name="plus" :size="16" />
        Nueva devolución
      </PrimaryButton>
    </div>
    <p class="text-sm text-slate-500" :class="cashRegisterStore.current ? 'mb-6' : 'mb-2'">
      Productos devueltos por los clientes.
    </p>
    <p v-if="!cashRegisterStore.current" class="flex items-center gap-2 text-sm text-amber-700 bg-amber-50 rounded-lg px-3 py-2 mb-6">
      <AppIcon name="alert-triangle" :size="14" class="shrink-0" />
      No hay una caja abierta — no se pueden registrar devoluciones.
      <RouterLink :to="{ name: 'staff-cash-register' }" class="font-semibold underline">Ir a Caja</RouterLink>
    </p>

    <div class="mb-4 flex flex-wrap gap-2">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por producto, cliente o # de pedido..."
        class="flex-1 min-w-[220px] border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
        @keyup.enter="handleSearch"
      />
      <button
        class="px-4 py-2.5 border border-slate-200 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50"
        @click="handleSearch"
      >
        Buscar
      </button>
    </div>

    <div v-if="returnsStore.loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="returnsStore.error" class="text-sm text-red-600">{{ returnsStore.error }}</div>
    <div
      v-else-if="!returnsStore.returns.length"
      class="bg-white rounded-2xl border border-slate-200 p-10 text-center text-sm text-slate-500"
    >
      No hay devoluciones registradas todavía.
    </div>

    <div v-else class="space-y-3">
      <RouterLink
        v-for="ret in returnsStore.returns"
        :key="ret.id"
        :to="{ name: 'staff-order-detail', params: { id: ret.orderId } }"
        class="flex items-center gap-4 bg-white rounded-2xl border border-slate-200 p-5 hover:border-emerald-300 transition"
      >
        <div class="w-10 h-10 rounded-xl bg-slate-50 text-slate-500 flex items-center justify-center shrink-0">
          <AppIcon name="arrow-back-up" :size="18" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-bold text-slate-900 truncate">
              Pedido #{{ ret.orderId }} — {{ firstItem(ret)?.productName }}
            </h3>
            <span v-if="ret.items.length > 1" class="text-[10px] font-bold text-slate-400 shrink-0">
              +{{ ret.items.length - 1 }}
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-0.5">
            {{ ret.orderCustomerName }} — {{ ret.reason }} — {{ formatDate(ret.createdAt) }}
          </p>
        </div>
        <p class="text-sm font-bold text-slate-900 shrink-0">$ {{ ret.refundAmount.toLocaleString() }}</p>
        <span class="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 shrink-0">
          {{ ret.refundMethod }}
        </span>
        <AppIcon name="chevron-right" :size="16" class="text-slate-300 shrink-0" />
      </RouterLink>
    </div>

    <NewReturnModal
      :open="showNewReturn"
      :saving="creating"
      :server-error="createError"
      @close="showNewReturn = false"
      @submit="handleCreateReturn"
    />
  </div>
</template>
