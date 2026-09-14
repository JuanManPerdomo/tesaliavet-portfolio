<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import CardBase from '../../../../components/ui/CardBase.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { useAuthStore } from '../../../../stores/auth'
import { useCartStore } from '../../../../stores/cart'
import { useToastStore } from '../../../../stores/toast'

const props = defineProps({
  id: { type: Number, required: true },
  name: { type: String, required: true },
  category: { type: String, required: true },
  image: { type: String, default: null },
  price: { type: Number, required: true },
  unitLabel: { type: String, default: 'Unidad' },
  badge: { type: String, default: null },
  actionLabel: { type: String, default: 'Ver más' },
})

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()
const toastStore = useToastStore()

const adding = ref(false)

// Mismo patron que ProductDetailPage.vue: sin sesion, manda a iniciar sesion
// en vez de fallar en silencio contra el 401 del backend.
async function handleAddToCart() {
  if (!authStore.user) {
    router.push({ name: 'login' })
    return
  }
  adding.value = true
  try {
    await cartStore.addItem(props.id, 1)
    toastStore.success('Producto agregado al carrito.')
  } catch (err) {
    toastStore.error(err.response?.data?.message || 'No se pudo agregar al carrito.')
  } finally {
    adding.value = false
  }
}
</script>

<template>
  <CardBase class="group overflow-hidden">
    <div class="p-4 pb-0">
      <div class="relative rounded-2xl bg-slate-50 h-60 flex items-center justify-center overflow-hidden">
        <img
          v-if="image"
          :src="image"
          :alt="name"
          class="w-full h-full object-cover group-hover:scale-105 duration-300"
        />

        <AppIcon v-else name="paw" :size="44" class="text-slate-300" />

        <span
          v-if="badge"
          class="absolute top-3 left-3 bg-emerald-700 text-white px-3 py-1 rounded-full text-xs font-semibold"
        >
          {{ badge }}
        </span>
      </div>
    </div>

    <div class="p-5 flex-1 flex flex-col">
      <p class="text-xs text-emerald-700 font-bold uppercase tracking-wide">
        {{ category }}
      </p>

      <h3 class="mt-2 text-lg font-bold text-slate-900 line-clamp-2">
        {{ name }}
      </h3>

      <p class="mt-3 text-2xl font-extrabold text-emerald-700">
        $ {{ price.toLocaleString() }}
        <span v-if="unitLabel && unitLabel !== 'Unidad'" class="text-sm font-medium text-emerald-700/70">
          / {{ unitLabel }}
        </span>
      </p>

      <div class="mt-auto pt-5 flex flex-col gap-2.5">
        <PrimaryButton class="w-full justify-center gap-2" :loading="adding" @click="handleAddToCart">
          <AppIcon name="shopping-cart" :size="16" />
          Añadir
        </PrimaryButton>

        <RouterLink
          :to="{ name: 'product-detail', params: { id } }"
          class="w-full text-center border border-slate-200 hover:border-emerald-700 hover:text-emerald-700 text-slate-600 px-4 py-2.5 rounded-2xl font-semibold text-sm transition"
        >
          {{ actionLabel }}
        </RouterLink>
      </div>
    </div>
  </CardBase>
</template>
