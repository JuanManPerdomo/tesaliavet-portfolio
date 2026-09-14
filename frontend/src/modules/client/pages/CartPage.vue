<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import api from '../../../lib/api'
import { useCartStore } from '../../../stores/cart'
import { useToastStore } from '../../../stores/toast'

const cartStore = useCartStore()
const toastStore = useToastStore()
const router = useRouter()

const updatingId = ref(null)

function imageUrl(item) {
  return item.productImage ? `${api.defaults.baseURL}${item.productImage}` : null
}

async function changeQuantity(item, delta) {
  const next = item.quantity + delta
  if (next < 1) return
  if (next > item.stock) {
    toastStore.error(`Solo hay ${item.stock} unidades disponibles.`)
    return
  }
  updatingId.value = item.id
  try {
    await cartStore.updateItem(item.id, next)
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo actualizar la cantidad.')
  } finally {
    updatingId.value = null
  }
}

async function remove(item) {
  updatingId.value = item.id
  try {
    await cartStore.removeItem(item.id)
    toastStore.success('Producto eliminado del carrito.')
  } catch {
    toastStore.error('No se pudo eliminar el producto.')
  } finally {
    updatingId.value = null
  }
}

function goToCheckout() {
  router.push({ name: 'checkout' })
}

onMounted(() => {
  cartStore.fetchCart()
})
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-5xl mx-auto px-6 py-12 w-full">
      <div class="mb-8">
        <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Tu carrito</h1>
        <p class="text-sm text-slate-500">Revisa tus productos antes de pasar al pago.</p>
      </div>

      <p v-if="cartStore.error" class="text-sm text-red-600 mb-6">{{ cartStore.error }}</p>

      <div v-if="cartStore.loading && !cartStore.cart" class="text-sm text-slate-500">Cargando...</div>

      <div
        v-else-if="!cartStore.cart?.items?.length"
        class="bg-white border border-slate-200 rounded-2xl p-12 text-center"
      >
        <AppIcon name="shopping-cart" :size="28" class="text-slate-300 mx-auto mb-3" />
        <p class="text-sm text-slate-500 mb-4">Tu carrito está vacío.</p>
        <RouterLink
          to="/productos"
          class="inline-flex items-center gap-2 text-emerald-700 font-semibold hover:underline"
        >
          Ver catálogo
        </RouterLink>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div class="lg:col-span-8 flex flex-col gap-3">
          <div
            v-for="item in cartStore.cart.items"
            :key="item.id"
            class="bg-white rounded-2xl border border-slate-200 p-4 flex items-center gap-4"
            :class="{ 'opacity-50 pointer-events-none': updatingId === item.id }"
          >
            <div class="w-16 h-16 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0">
              <img
                v-if="imageUrl(item)"
                :src="imageUrl(item)"
                :alt="item.productName"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-slate-300">
                <AppIcon name="paw" :size="22" />
              </div>
            </div>

            <div class="flex-1 min-w-0">
              <RouterLink
                :to="{ name: 'product-detail', params: { id: item.productId } }"
                class="text-sm font-bold text-slate-900 truncate hover:text-emerald-700 transition block"
              >
                {{ item.productName }}
              </RouterLink>
              <p class="text-xs text-slate-500">$ {{ item.unitPrice.toLocaleString() }} c/u</p>
              <p v-if="!item.isActive" class="text-xs text-red-600 font-semibold mt-1">
                Este producto ya no está disponible
              </p>
            </div>

            <div class="flex items-center gap-2 border border-slate-200 rounded-xl px-1">
              <button
                type="button"
                class="w-7 h-7 flex items-center justify-center text-slate-500 hover:text-emerald-700 disabled:opacity-30"
                :disabled="item.quantity <= 1"
                @click="changeQuantity(item, -1)"
              >
                −
              </button>
              <span class="w-6 text-center text-sm font-semibold">{{ item.quantity }}</span>
              <button
                type="button"
                class="w-7 h-7 flex items-center justify-center text-slate-500 hover:text-emerald-700 disabled:opacity-30"
                :disabled="item.quantity >= item.stock"
                @click="changeQuantity(item, 1)"
              >
                +
              </button>
            </div>

            <p class="w-20 text-right text-sm font-bold text-slate-900">
              $ {{ item.total.toLocaleString() }}
            </p>

            <button
              type="button"
              class="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition"
              title="Eliminar"
              @click="remove(item)"
            >
              <AppIcon name="x" :size="16" />
            </button>
          </div>
        </div>

        <div class="lg:col-span-4">
          <div class="bg-white rounded-2xl border border-slate-200 p-6 lg:sticky lg:top-24">
            <h3 class="text-sm font-bold text-slate-900 mb-5 pb-4 border-b border-slate-100">
              Resumen
            </h3>

            <div class="space-y-2 text-sm mb-5">
              <div class="flex justify-between text-slate-500">
                <span>Subtotal</span>
                <span>$ {{ cartStore.cart.subtotal.toLocaleString() }}</span>
              </div>
              <div class="flex justify-between text-slate-500">
                <span>IVA</span>
                <span>$ {{ cartStore.cart.taxTotal.toLocaleString() }}</span>
              </div>
              <div class="flex justify-between text-base font-bold text-slate-900 pt-2 border-t border-slate-100">
                <span>Total</span>
                <span>$ {{ cartStore.cart.total.toLocaleString() }}</span>
              </div>
            </div>

            <PrimaryButton class="w-full justify-center gap-2" @click="goToCheckout">
              <AppIcon name="check" :size="16" />
              Proceder al pago
            </PrimaryButton>

            <div class="mt-4 flex items-center gap-2 text-xs text-slate-400">
              <AppIcon name="map-pin" :size="14" />
              Recoges tu pedido en nuestra tienda en {{ cartStore.cart.deliveryCity }}, Huila
            </div>
          </div>
        </div>
      </div>
    </main>

    <Footer />
  </div>
</template>
