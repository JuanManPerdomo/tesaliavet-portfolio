<script setup>
import { computed } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import { calcMargin, formatCOP, formatQuantity } from '../../../../lib/pricing'
import api from '../../../../lib/api'

const props = defineProps({
  open: { type: Boolean, default: false },
  product: { type: Object, default: null },
})

const emit = defineEmits(['close'])

const margin = computed(() =>
  props.product ? calcMargin(props.product.purchasePrice, props.product.price) : { amount: 0, percent: 0 }
)

const photoUrl = computed(() =>
  props.product?.image ? `${api.defaults.baseURL}${props.product.image}` : null
)
</script>

<template>
  <Teleport to="body">
    <div v-if="open && product" class="fixed inset-0 z-[9998] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50" @click="emit('close')"></div>

      <div class="relative bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          class="absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="16" />
        </button>

        <div class="flex items-start gap-4 mb-6">
          <div class="w-20 h-20 rounded-xl overflow-hidden bg-emerald-50 flex items-center justify-center flex-shrink-0">
            <img v-if="photoUrl" :src="photoUrl" class="w-full h-full object-cover" alt="" />
            <AppIcon v-else name="package" :size="28" class="text-emerald-600" />
          </div>
          <div class="min-w-0">
            <span
              class="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full"
              :class="product.isActive ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
            >
              {{ product.isActive ? 'Activo' : 'Inactivo' }}
            </span>
            <h3 class="text-lg font-bold text-slate-900 mt-1 truncate">{{ product.name }}</h3>
            <p class="text-xs text-slate-500">SKU {{ product.sku }}<span v-if="product.barcode"> · {{ product.barcode }}</span></p>
          </div>
        </div>

        <dl class="grid grid-cols-2 gap-x-4 gap-y-3 text-sm border-t border-slate-100 pt-4">
          <div>
            <dt class="text-xs text-slate-400">Categoría</dt>
            <dd class="text-slate-800 font-medium">
              {{ product.category?.parentName ? `${product.category.parentName} > ` : '' }}{{ product.category?.name || '—' }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Especie</dt>
            <dd class="text-slate-800 font-medium">{{ product.species?.name || 'Todas' }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Marca</dt>
            <dd class="text-slate-800 font-medium">{{ product.brand || '—' }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Precio de compra</dt>
            <dd class="text-slate-800 font-medium">{{ formatCOP(product.purchasePrice) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Precio de venta</dt>
            <dd class="text-emerald-700 font-bold">{{ formatCOP(product.price) }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">IVA</dt>
            <dd class="text-slate-800 font-medium">{{ product.taxRate }}%</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Margen bruto</dt>
            <dd class="text-slate-800 font-medium">
              {{ formatCOP(margin.amount) }} ({{ margin.percent.toFixed(0) }}%)
            </dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Stock actual</dt>
            <dd class="text-slate-800 font-medium">
              {{ formatQuantity(product.stock, product.unitLabel, product.unitWeightKg) }}
            </dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Stock mínimo</dt>
            <dd class="text-slate-800 font-medium">{{ product.minStock }} {{ product.unitLabel }}</dd>
          </div>
          <div class="col-span-2">
            <dt class="text-xs text-slate-400">Proveedor</dt>
            <dd class="text-slate-800 font-medium">{{ product.supplier?.name || 'Sin asignar' }}</dd>
          </div>
          <div v-if="product.description" class="col-span-2">
            <dt class="text-xs text-slate-400">Descripción</dt>
            <dd class="text-slate-700">{{ product.description }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </Teleport>
</template>
