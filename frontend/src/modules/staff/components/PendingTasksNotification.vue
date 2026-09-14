<script setup>
import AppIcon from '../../../components/ui/AppIcon.vue'
import { NOTIFICATION_TYPE_META } from '../../../lib/notificationTypes'

defineProps({
  open: { type: Boolean, default: false },
  items: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
})

const emit = defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="rise-in fixed bottom-6 right-4 sm:right-6 z-[9997] w-[calc(100vw-2rem)] sm:w-96 max-h-[75vh] flex flex-col bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden"
    >
      <div class="flex items-start gap-3 p-5 pb-3 shrink-0">
        <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
          <AppIcon name="bell" :size="18" />
        </div>
        <div class="flex-1 min-w-0 pt-0.5">
          <h3 class="text-sm font-bold text-slate-900">
            {{ total === 1 ? 'Tienes 1 cosa pendiente' : `Tienes ${total} cosas pendientes` }}
          </h3>
          <p class="text-xs text-slate-500 mt-0.5">Esto es lo que necesita tu atención hoy.</p>
        </div>
        <button
          type="button"
          class="w-7 h-7 shrink-0 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
          @click="emit('close')"
        >
          <AppIcon name="x" :size="14" />
        </button>
      </div>

      <div class="overflow-y-auto px-3 pb-2 space-y-1 flex-1">
        <RouterLink
          v-for="item in items"
          :key="item.key"
          :to="item.action.to"
          class="flex items-start gap-3 py-2 px-2 rounded-lg hover:bg-slate-50 transition"
          @click="emit('close')"
        >
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
            :class="[NOTIFICATION_TYPE_META[item.type]?.iconBgClass, NOTIFICATION_TYPE_META[item.type]?.iconColorClass]"
          >
            <AppIcon :name="NOTIFICATION_TYPE_META[item.type]?.icon || 'bell'" :size="14" />
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold text-slate-800 leading-snug">{{ item.title }}</p>
            <p class="text-xs text-slate-400 truncate">{{ item.description }}</p>
          </div>
        </RouterLink>
        <p v-if="total > items.length" class="text-xs text-slate-400 text-center pt-1">
          y {{ total - items.length }} más...
        </p>
      </div>

      <RouterLink
        :to="{ name: 'staff-notifications' }"
        class="flex items-center justify-center gap-2 text-xs font-semibold text-emerald-700 hover:underline shrink-0 py-3 border-t border-slate-100"
        @click="emit('close')"
      >
        Ver todas las notificaciones
        <AppIcon name="chevron-right" :size="12" />
      </RouterLink>
    </div>
  </Teleport>
</template>

<style scoped>
/* Solo se anima la ENTRADA, con @keyframes CSS puro en vez de <Transition>
de Vue - a proposito. <Transition> depende de un swap de clases en dos
frames via requestAnimationFrame para la animacion de SALIDA; en un
entorno donde ese rAF no corre de forma confiable (ya documentado en este
proyecto, decision 66 del carrusel del Hero) el elemento se queda
atascado a mitad de "rise-leave-active" y nunca se remueve del DOM - bug
real encontrado probando el cierre de este mismo componente. Con
@keyframes aplicado directo al elemento (sin pasar por el ciclo
enter/leave de Vue) la entrada es igual de fluida y el cierre queda
instantaneo y 100% confiable (el div simplemente desaparece con el
v-if), que es todo lo que se pidio - nunca se pidio animar el cierre. */
.rise-in {
  animation: rise-in 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
