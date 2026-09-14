<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import api from '../../../lib/api'
import { useProductsStore } from '../../../stores/products'
import { useAuthStore } from '../../../stores/auth'
import { useCartStore } from '../../../stores/cart'
import { useToastStore } from '../../../stores/toast'

const route = useRoute()
const router = useRouter()
const productsStore = useProductsStore()
const authStore = useAuthStore()
const cartStore = useCartStore()
const toastStore = useToastStore()

const productId = computed(() => Number(route.params.id))

const product = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const quantity = ref(1)
const addingToCart = ref(false)

const imageUrl = computed(() =>
  product.value?.image ? `${api.defaults.baseURL}${product.value.image}` : null
)

const inStock = computed(() => Number(product.value?.stock) > 0)

// Ficha técnica y "más información" - solo datos reales que ya trae el
// producto (SKU/marca/categoría/especie/unidad, decision 7: nunca inventar)
// - nunca proveedor ni precio de compra, esos son internos del negocio.
const activeTab = ref('detalles')

const unitDescription = computed(() => {
  if (!product.value) return ''
  const label = product.value.unitLabel || 'Unidad'
  if (!product.value.unitWeightKg) return label
  return `${label} (equivale a ${product.value.unitWeightKg} kg)`
})

async function load() {
  loading.value = true
  errorMessage.value = ''
  product.value = null
  quantity.value = 1
  try {
    product.value = await productsStore.fetchProduct(productId.value)
  } catch (err) {
    errorMessage.value =
      err.response?.status === 404
        ? 'No encontramos este producto. Puede que ya no esté disponible.'
        : 'No se pudo cargar el producto. Intenta de nuevo.'
  } finally {
    loading.value = false
  }
}

async function handleAddToCart() {
  if (!authStore.user) {
    router.push({ name: 'login' })
    return
  }
  addingToCart.value = true
  try {
    await cartStore.addItem(product.value.id, quantity.value)
    toastStore.success('Producto agregado al carrito.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo agregar al carrito.')
  } finally {
    addingToCart.value = false
  }
}

onMounted(load)
watch(productId, load)
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <Navbar />

    <section class="max-w-7xl mx-auto px-6 py-10 md:py-14">
      <!-- Loading -->
      <div v-if="loading" class="grid lg:grid-cols-2 gap-12 animate-pulse">
        <div class="bg-white border border-slate-100 rounded-3xl h-[420px]"></div>
        <div class="space-y-4">
          <div class="h-4 w-24 bg-slate-200 rounded"></div>
          <div class="h-9 w-3/4 bg-slate-200 rounded"></div>
          <div class="h-8 w-32 bg-slate-200 rounded"></div>
          <div class="h-24 w-full bg-slate-200 rounded"></div>
        </div>
      </div>

      <!-- Error -->
      <div
        v-else-if="errorMessage"
        class="flex flex-col items-center text-center gap-4 bg-white border border-red-100 rounded-2xl py-20 px-6"
      >
        <div class="w-14 h-14 rounded-full bg-red-50 text-red-600 flex items-center justify-center">
          <AppIcon name="alert-triangle" :size="26" />
        </div>
        <p class="text-red-600 font-medium">{{ errorMessage }}</p>
        <RouterLink
          to="/productos"
          class="inline-flex items-center gap-2 text-emerald-700 font-semibold hover:gap-3 transition-all"
        >
          <AppIcon name="arrow-left" :size="16" />
          Volver al catálogo
        </RouterLink>
      </div>

      <!-- Product -->
      <div v-else-if="product" class="grid lg:grid-cols-2 gap-12">
        <!-- Image -->
        <div
          v-reveal
          class="bg-white border border-slate-100 rounded-3xl shadow-sm p-6 flex items-center justify-center"
        >
          <img
            v-if="imageUrl"
            :src="imageUrl"
            :alt="product.name"
            class="w-full h-[420px] object-cover rounded-2xl"
          />
          <div
            v-else
            class="w-full h-[420px] bg-slate-100 rounded-2xl flex items-center justify-center text-slate-300"
          >
            <AppIcon name="paw" :size="64" />
          </div>
        </div>

        <!-- Info -->
        <div v-reveal="{ delay: 100 }">
          <div class="flex flex-wrap items-center gap-2 mb-4">
            <span
              v-if="product.category"
              class="inline-flex items-center gap-1.5 bg-emerald-100 text-emerald-700 px-3.5 py-1.5 rounded-full text-xs font-semibold"
            >
              <AppIcon name="tag" :size="13" />
              {{ product.category.name }}
            </span>

            <span
              v-if="product.species"
              class="inline-flex items-center gap-1.5 bg-slate-100 text-slate-600 px-3.5 py-1.5 rounded-full text-xs font-semibold"
            >
              <AppIcon name="paw" :size="13" />
              {{ product.species.name }}
            </span>

            <span
              :class="
                inStock
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'bg-red-50 text-red-600'
              "
              class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold"
            >
              <AppIcon :name="inStock ? 'check' : 'x'" :size="13" />
              {{ inStock ? 'Disponible' : 'Agotado' }}
            </span>
          </div>

          <h1 class="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight">
            {{ product.name }}
          </h1>

          <p v-if="product.brand" class="mt-2 text-slate-500">
            Marca: <span class="font-semibold text-slate-700">{{ product.brand }}</span>
          </p>

          <p class="mt-6 text-4xl font-extrabold text-emerald-700">
            $ {{ product.price.toLocaleString() }}
          </p>

          <p v-if="product.description" class="mt-6 text-slate-600 leading-relaxed">
            {{ product.description }}
          </p>

          <div v-if="inStock" class="mt-8 flex flex-wrap items-center gap-4">
            <div class="flex items-center gap-2 border border-slate-200 rounded-2xl px-2 py-1">
              <button
                type="button"
                class="w-9 h-9 flex items-center justify-center text-slate-500 hover:text-emerald-700 disabled:opacity-30"
                :disabled="quantity <= 1"
                @click="quantity--"
              >
                −
              </button>
              <span class="w-8 text-center font-semibold">{{ quantity }}</span>
              <button
                type="button"
                class="w-9 h-9 flex items-center justify-center text-slate-500 hover:text-emerald-700 disabled:opacity-30"
                :disabled="quantity >= product.stock"
                @click="quantity++"
              >
                +
              </button>
            </div>

            <button
              type="button"
              :disabled="addingToCart"
              class="inline-flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-6 py-3.5 rounded-2xl font-semibold shadow-md hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 transition disabled:opacity-60 disabled:pointer-events-none"
              @click="handleAddToCart"
            >
              <AppIcon name="shopping-cart" :size="16" />
              {{ addingToCart ? 'Agregando...' : 'Agregar al carrito' }}
            </button>

            <RouterLink
              to="/productos"
              class="inline-flex items-center justify-center gap-2 text-slate-500 hover:text-emerald-700 font-semibold transition"
            >
              <AppIcon name="arrow-left" :size="16" />
              Seguir viendo
            </RouterLink>
          </div>

          <div v-else class="mt-8 flex flex-wrap items-center gap-4">
            <span
              class="inline-flex items-center justify-center gap-2 bg-slate-100 text-slate-400 px-6 py-3.5 rounded-2xl font-semibold cursor-not-allowed"
            >
              <AppIcon name="x" :size="16" />
              Agotado
            </span>

            <RouterLink
              to="/productos"
              class="inline-flex items-center justify-center gap-2 border border-slate-300 hover:border-emerald-700 hover:text-emerald-700 text-slate-700 px-6 py-3.5 rounded-2xl font-semibold transition"
            >
              <AppIcon name="arrow-left" :size="16" />
              Volver al catálogo
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Detalles / Más información: debajo del detalle principal, pedido
           por Juan Manuel - solo datos reales (nunca proveedor/precio de
           compra, eso es interno). "Más información" surge reglas de
           negocio ya establecidas (decision 28/42 en CLAUDE.md) que hoy no
           aparecían en ningún lado del catálogo público. -->
      <div v-if="product" class="mt-16">
        <div class="flex gap-8 border-b border-slate-200 mb-8">
          <button
            type="button"
            :class="[
              'inline-flex items-center gap-2 py-4 font-semibold border-b-2 transition',
              activeTab === 'detalles'
                ? 'border-emerald-700 text-emerald-700'
                : 'border-transparent text-slate-500 hover:text-emerald-700',
            ]"
            @click="activeTab = 'detalles'"
          >
            Detalles
          </button>
          <button
            type="button"
            :class="[
              'inline-flex items-center gap-2 py-4 font-semibold border-b-2 transition',
              activeTab === 'info'
                ? 'border-emerald-700 text-emerald-700'
                : 'border-transparent text-slate-500 hover:text-emerald-700',
            ]"
            @click="activeTab = 'info'"
          >
            Más información
          </button>
        </div>

        <div v-if="activeTab === 'detalles'" class="bg-white rounded-2xl border border-slate-100 p-8">
          <dl class="grid sm:grid-cols-2 gap-x-10 gap-y-5">
            <div>
              <dt class="text-xs font-semibold text-slate-400 uppercase tracking-wide">SKU</dt>
              <dd class="mt-1 text-slate-800">{{ product.sku }}</dd>
            </div>
            <div v-if="product.brand">
              <dt class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Marca</dt>
              <dd class="mt-1 text-slate-800">{{ product.brand }}</dd>
            </div>
            <div v-if="product.category">
              <dt class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Categoría</dt>
              <dd class="mt-1 text-slate-800">
                <template v-if="product.category.parentName">{{ product.category.parentName }} / </template>
                {{ product.category.name }}
              </dd>
            </div>
            <div v-if="product.species">
              <dt class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Especie</dt>
              <dd class="mt-1 text-slate-800">{{ product.species.name }}</dd>
            </div>
            <div>
              <dt class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Unidad de medida</dt>
              <dd class="mt-1 text-slate-800">{{ unitDescription }}</dd>
            </div>
            <div v-if="product.barcode">
              <dt class="text-xs font-semibold text-slate-400 uppercase tracking-wide">Código de barras</dt>
              <dd class="mt-1 text-slate-800">{{ product.barcode }}</dd>
            </div>
          </dl>
        </div>

        <div v-else class="bg-white rounded-2xl border border-slate-100 p-8 space-y-6">
          <div class="flex gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0">
              <AppIcon name="map-pin" :size="18" />
            </div>
            <div>
              <p class="font-semibold text-slate-800">Recogida en tienda</p>
              <p class="mt-1 text-sm text-slate-600">
                Este producto se recoge únicamente en nuestra tienda física en Tesalia, Huila. No hacemos envíos.
              </p>
            </div>
          </div>

          <div class="flex gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0">
              <AppIcon name="cash" :size="18" />
            </div>
            <div>
              <p class="font-semibold text-slate-800">Métodos de pago</p>
              <p class="mt-1 text-sm text-slate-600">Efectivo o transferencia al recoger tu pedido.</p>
            </div>
          </div>

          <div class="flex gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0">
              <AppIcon name="arrow-back-up" :size="18" />
            </div>
            <div>
              <p class="font-semibold text-slate-800">Devoluciones</p>
              <p class="mt-1 text-sm text-slate-600">
                Puedes solicitar una devolución hasta 8 días después de recibir tu pedido.
              </p>
            </div>
          </div>

          <div class="flex gap-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0">
              <AppIcon name="file-text" :size="18" />
            </div>
            <div>
              <p class="font-semibold text-slate-800">IVA</p>
              <p class="mt-1 text-sm text-slate-600">
                <template v-if="product.taxRate > 0">El precio mostrado incluye IVA del {{ product.taxRate }}%.</template>
                <template v-else>Este producto está exento de IVA.</template>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <Footer />
  </div>
</template>
