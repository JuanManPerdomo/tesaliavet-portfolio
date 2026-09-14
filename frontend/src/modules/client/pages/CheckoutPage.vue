<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../../public/components/Navbar.vue'
import Footer from '../../public/components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../components/ui/PrimaryButton.vue'
import DepartmentMunicipalitySelect from '../../../components/ui/DepartmentMunicipalitySelect.vue'
import api from '../../../lib/api'
import { useAuthStore } from '../../../stores/auth'
import { useCartStore } from '../../../stores/cart'
import { useToastStore } from '../../../stores/toast'

// Sin pasarela de pago online (decision 28 en CLAUDE.md) - solo metodos
// presenciales/manuales, verificados despues por el personal.
const PAYMENT_METHODS = [
  { value: 'Efectivo', icon: 'cash', label: 'Efectivo', desc: 'Pagas en efectivo al recoger' },
  { value: 'Transferencia', icon: 'send', label: 'Transferencia', desc: 'Transfieres por tu cuenta' },
]

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()
const toastStore = useToastStore()

const paymentMethod = ref('Efectivo')
const transferOption = ref('bank') // 'bank' | 'breb'
const bankInfo = ref(null)

const shippingName = ref(
  authStore.user ? `${authStore.user.firstName} ${authStore.user.lastName}` : ''
)
const shippingPhone = ref(authStore.user?.phone || '')
const shippingAddress = ref(authStore.user?.direccion || '')
const notes = ref('')
const pickupConfirmed = ref(false)

// Si el cliente no tiene departamento/municipio registrado en su perfil, el
// checkout se lo pide aca (decision 49) - mismo criterio que ya aplica a
// direccion (decision 48). No afecta el pedido en si (la recogida siempre
// es en Tesalia, decision 28), es solo para completar el perfil.
const needsLocation = computed(() => !authStore.user?.departamento)
const departamento = ref(authStore.user?.departamento || '')
const municipio = ref(authStore.user?.ciudad || '')

const submitting = ref(false)
const errorMessage = ref('')

function imageUrl(item) {
  return item.productImage ? `${api.defaults.baseURL}${item.productImage}` : null
}

const hasItems = computed(() => (cartStore.cart?.items?.length || 0) > 0)

onMounted(async () => {
  try {
    const { data } = await api.get('/payments/bank-transfer-info')
    bankInfo.value = data
  } catch {
    bankInfo.value = null
  }
  if (!cartStore.cart) await cartStore.fetchCart()
  if (!cartStore.cart?.items?.length) {
    router.replace({ name: 'cart' })
  }
})

async function handleSubmit() {
  errorMessage.value = ''

  if (!shippingName.value.trim() || !shippingAddress.value.trim()) {
    errorMessage.value = 'Completa nombre y dirección de facturación.'
    return
  }
  if (needsLocation.value && (!departamento.value || !municipio.value)) {
    errorMessage.value = 'Completa tu departamento y municipio.'
    return
  }
  if (!pickupConfirmed.value) {
    errorMessage.value = 'Confirma que entiendes que la recogida es solo en tienda.'
    return
  }

  const payload = {
    shippingName: shippingName.value.trim(),
    shippingPhone: shippingPhone.value.trim() || undefined,
    shippingAddress: shippingAddress.value.trim(),
    paymentMethod: paymentMethod.value,
    notes: notes.value.trim() || undefined,
  }
  if (needsLocation.value) {
    payload.departamento = departamento.value
    payload.ciudad = municipio.value
  }

  const hadNoAddress = !authStore.user?.direccion
  const hadNoLocation = needsLocation.value

  submitting.value = true
  try {
    const order = await cartStore.checkout(payload)
    // El backend guarda direccion/departamento/municipio en el perfil si el
    // cliente no los tenia registrados (decision 48/49) - resincroniza el
    // usuario en cache para que /mi-perfil y el proximo checkout ya los
    // muestren.
    if (hadNoAddress || hadNoLocation) await authStore.fetchMe()
    toastStore.success('¡Pedido realizado! Te avisaremos cuando lo confirmemos.')
    router.push({ name: 'order-detail', params: { id: order.id } })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo procesar el pedido.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen flex flex-col">
    <Navbar />

    <main class="flex-grow max-w-5xl mx-auto px-6 py-12 w-full">
      <RouterLink
        :to="{ name: 'cart' }"
        class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-6"
      >
        <AppIcon name="arrow-left" :size="16" />
        Volver al carrito
      </RouterLink>

      <div class="mb-8">
        <h1 class="text-2xl font-extrabold text-slate-900 mb-2">Finalizar pedido</h1>
        <p class="text-sm text-slate-500">
          Completa tus datos de facturación y elige cómo prefieres pagar.
        </p>
      </div>

      <div v-if="!hasItems" class="text-sm text-slate-500">Cargando...</div>

      <form v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start" @submit.prevent="handleSubmit">
        <div class="lg:col-span-8 flex flex-col gap-6">
          <!-- Método de pago -->
          <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
            <h2
              class="text-base font-bold text-slate-900 mb-6 pb-4 border-b border-slate-100 flex items-center gap-2.5"
            >
              <span
                class="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center"
              >
                <AppIcon name="cash" :size="18" />
              </span>
              Método de pago
            </h2>

            <div class="grid grid-cols-2 gap-3">
              <button
                v-for="method in PAYMENT_METHODS"
                :key="method.value"
                type="button"
                class="relative border-[1.5px] rounded-xl px-3.5 py-3 flex flex-col items-center text-center gap-2 transition-all"
                :class="
                  paymentMethod === method.value
                    ? 'border-emerald-700 bg-emerald-50 shadow-sm'
                    : 'border-slate-200 bg-white hover:border-emerald-700 hover:-translate-y-0.5'
                "
                @click="paymentMethod = method.value"
              >
                <span
                  class="w-9 h-9 rounded-lg flex items-center justify-center"
                  :class="paymentMethod === method.value ? 'bg-emerald-700 text-white' : 'bg-slate-100 text-slate-500'"
                >
                  <AppIcon :name="method.icon" :size="18" />
                </span>
                <span class="text-sm font-bold text-slate-900">{{ method.label }}</span>
                <span class="text-[11px] text-slate-500 leading-snug">{{ method.desc }}</span>
              </button>
            </div>

            <!-- Sub-selector de Transferencia -->
            <div v-if="paymentMethod === 'Transferencia'" class="mt-6 pt-6 border-t border-slate-100">
              <div class="flex gap-2 mb-4">
                <button
                  type="button"
                  class="px-4 py-2 rounded-full text-xs font-semibold border transition"
                  :class="
                    transferOption === 'bank'
                      ? 'bg-emerald-700 text-white border-emerald-700'
                      : 'border-slate-200 text-slate-600 hover:border-emerald-700'
                  "
                  @click="transferOption = 'bank'"
                >
                  Cuenta bancaria
                </button>
                <button
                  type="button"
                  class="px-4 py-2 rounded-full text-xs font-semibold border transition"
                  :class="
                    transferOption === 'breb'
                      ? 'bg-emerald-700 text-white border-emerald-700'
                      : 'border-slate-200 text-slate-600 hover:border-emerald-700'
                  "
                  @click="transferOption = 'breb'"
                >
                  Bre-B
                </button>
              </div>

              <!-- Cuenta bancaria -->
              <div v-if="transferOption === 'bank'">
                <div v-if="bankInfo?.bank?.available" class="bg-slate-50 rounded-xl p-4 space-y-1.5 text-sm">
                  <p><span class="text-slate-400">Titular:</span> <strong class="text-slate-800">{{ bankInfo.bank.accountHolder }}</strong></p>
                  <p><span class="text-slate-400">Banco:</span> <strong class="text-slate-800">{{ bankInfo.bank.bankName }}</strong></p>
                  <p><span class="text-slate-400">Tipo de cuenta:</span> <strong class="text-slate-800">{{ bankInfo.bank.accountType }}</strong></p>
                  <p><span class="text-slate-400">Número de cuenta:</span> <strong class="text-slate-800">{{ bankInfo.bank.accountNumber }}</strong></p>
                </div>
                <p v-else class="text-xs text-slate-400 bg-slate-50 rounded-xl p-4">
                  Próximamente. Por ahora elige Efectivo o transfiere por Bre-B.
                </p>
              </div>

              <!-- Bre-B -->
              <div v-else>
                <div v-if="bankInfo?.breb?.available" class="bg-slate-50 rounded-xl p-4 space-y-1.5 text-sm">
                  <p><span class="text-slate-400">Llave Bre-B:</span> <strong class="text-slate-800">{{ bankInfo.breb.key }}</strong></p>
                  <p><span class="text-slate-400">Banco:</span> <strong class="text-slate-800">{{ bankInfo.breb.bankName }}</strong></p>
                </div>
                <p v-else class="text-xs text-slate-400 bg-slate-50 rounded-xl p-4 flex items-center gap-1.5">
                  <AppIcon name="info" :size="13" />
                  Próximamente. Por ahora transfiere a la cuenta bancaria.
                </p>
              </div>

              <p class="mt-3 text-xs text-slate-400">
                Transfiere el total del pedido y guarda tu comprobante — lo confirmamos cuando pases
                a recoger.
              </p>
            </div>
          </div>

          <!-- Datos de facturación -->
          <div class="bg-white rounded-2xl border border-slate-200 p-6 md:p-8">
            <h2
              class="text-base font-bold text-slate-900 mb-6 pb-4 border-b border-slate-100 flex items-center gap-2.5"
            >
              <span
                class="w-9 h-9 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center"
              >
                <AppIcon name="user" :size="18" />
              </span>
              Datos de facturación
            </h2>

            <div class="space-y-5">
              <div class="grid sm:grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-medium text-slate-600 mb-2" for="shippingName">
                    Nombre completo *
                  </label>
                  <input
                    id="shippingName"
                    v-model="shippingName"
                    type="text"
                    placeholder="Tu nombre completo"
                    class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-slate-600 mb-2" for="shippingPhone">
                    Teléfono / Celular
                  </label>
                  <input
                    id="shippingPhone"
                    v-model="shippingPhone"
                    type="tel"
                    placeholder="300 000 0000"
                    class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-600 mb-2" for="shippingAddress">
                  Dirección *
                </label>
                <input
                  id="shippingAddress"
                  v-model="shippingAddress"
                  type="text"
                  placeholder="Calle, número, barrio"
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                />
              </div>

              <div v-if="needsLocation">
                <p class="text-sm text-slate-600 mb-3">
                  Nos falta tu departamento y municipio — complétalos para continuar.
                </p>
                <DepartmentMunicipalitySelect
                  :departamento="departamento"
                  :municipio="municipio"
                  @update:departamento="departamento = $event"
                  @update:municipio="municipio = $event"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-600 mb-2" for="notes">
                  Notas adicionales
                </label>
                <textarea
                  id="notes"
                  v-model="notes"
                  rows="3"
                  placeholder="Indicaciones para tu pedido, horario en el que pasas, etc."
                  class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                ></textarea>
              </div>

              <label class="flex items-start gap-3 bg-emerald-50 border border-emerald-100 rounded-lg px-4 py-3 text-sm text-emerald-800 cursor-pointer">
                <input v-model="pickupConfirmed" type="checkbox" class="mt-0.5 w-4 h-4 accent-emerald-700" />
                <span>
                  Este pedido se recoge únicamente en nuestra tienda física en
                  <strong>Tesalia, Huila</strong>. No hacemos envíos.
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- Resumen -->
        <div class="lg:col-span-4">
          <div class="bg-white rounded-2xl border border-slate-200 p-6 lg:sticky lg:top-24">
            <h3 class="text-sm font-bold text-slate-900 mb-5 pb-4 border-b border-slate-100">
              Resumen del pedido
            </h3>

            <div class="space-y-3 mb-5 max-h-64 overflow-y-auto">
              <div
                v-for="item in cartStore.cart.items"
                :key="item.id"
                class="flex items-center gap-3"
              >
                <div class="w-10 h-10 rounded-lg overflow-hidden bg-slate-100 flex-shrink-0">
                  <img
                    v-if="imageUrl(item)"
                    :src="imageUrl(item)"
                    :alt="item.productName"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-slate-300">
                    <AppIcon name="paw" :size="16" />
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-semibold text-slate-800 truncate">{{ item.productName }}</p>
                  <p class="text-[11px] text-slate-400">{{ item.quantity }} × $ {{ item.unitPrice.toLocaleString() }}</p>
                </div>
                <p class="text-xs font-bold text-slate-900">$ {{ item.total.toLocaleString() }}</p>
              </div>
            </div>

            <div class="space-y-2 text-sm mb-4 pt-4 border-t border-slate-100">
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

            <p v-if="errorMessage" class="text-sm text-red-600 mb-4">{{ errorMessage }}</p>

            <PrimaryButton
              type="submit"
              :loading="submitting"
              class="w-full justify-center gap-2"
            >
              <AppIcon name="check" :size="16" />
              Confirmar pedido
            </PrimaryButton>
          </div>
        </div>
      </form>
    </main>

    <Footer />
  </div>
</template>
