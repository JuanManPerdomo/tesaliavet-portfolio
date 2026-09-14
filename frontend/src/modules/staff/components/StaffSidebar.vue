<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../components/ui/AppIcon.vue'

const props = defineProps({
  groups: { type: Array, required: true },
  badges: { type: Object, default: () => ({}) },
  open: { type: Boolean, default: false },
})

const emit = defineEmits(['close'])

const route = useRoute()

// Bug real de layout encontrado probando en mobile: con este <nav> como
// hijo directo del contenedor flex de StaffLayout, position:fixed + left
// quedaba mal calculado por el navegador (interaccion con el algoritmo de
// "static position" de items flex fuera de flujo) - el cajon se quedaba
// invisible fuera de pantalla aunque `left` estuviera puesto en 0.
// Teleport lo saca del arbol flex SOLO mientras esta en modo cajon (< lg);
// en escritorio (disabled=true) se queda en su lugar de siempre, como
// item flex normal junto a <main>.
const LG_BREAKPOINT = '(min-width: 1024px)'
const mediaQuery = window.matchMedia(LG_BREAKPOINT)
const isDesktop = ref(mediaQuery.matches)
function handleBreakpointChange(e) {
  isDesktop.value = e.matches
}
onMounted(() => mediaQuery.addEventListener('change', handleBreakpointChange))
onBeforeUnmount(() => mediaQuery.removeEventListener('change', handleBreakpointChange))

function isActive(entry) {
  if (!entry.to) return false
  if (entry.to.name === route.name) {
    if (entry.to.params?.slug) return entry.to.params.slug === route.params.slug
    return true
  }
  return (entry.children || []).some((child) => child.to?.name === route.name)
}
</script>

<template>
  <Teleport to="body" :disabled="isDesktop">
  <!-- Fondo oscuro solo en mobile mientras el cajon esta abierto -->
  <div
    v-if="props.open"
    class="fixed inset-0 bg-slate-900/50 z-40 lg:hidden"
    @click="emit('close')"
  ></div>

  <!-- En lg+ es la barra lateral fija de siempre; debajo de lg se vuelve un
  cajon que entra desde la izquierda (RNF15/19) -->
  <nav
    class="fixed inset-y-0 z-50 w-72 bg-white border-r border-slate-200 py-6 overflow-y-auto lg:static lg:z-auto lg:left-auto lg:w-60 lg:shrink-0 lg:sticky lg:top-20 lg:h-[calc(100vh-5rem)]"
    :class="props.open ? 'left-0' : '-left-72'"
  >
    <div class="flex items-center justify-between px-4 mb-2 lg:hidden">
      <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Menú</span>
      <button
        type="button"
        class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-slate-600"
        @click="emit('close')"
      >
        <AppIcon name="x" :size="16" />
      </button>
    </div>

    <div v-for="(group, gi) in groups" :key="gi" class="px-4 mb-2">
      <div v-if="group.label" class="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-3 py-2 mb-1">
        {{ group.label }}
      </div>

      <div v-for="entry in group.items" :key="entry.label" class="mb-0.5">
        <RouterLink
          :to="entry.to"
          class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition"
          :class="
            isActive(entry)
              ? 'bg-emerald-50 text-emerald-700 font-semibold'
              : 'text-slate-600 hover:bg-slate-50 hover:text-emerald-700'
          "
          @click="emit('close')"
        >
          <AppIcon :name="entry.icon" :size="18" class="shrink-0" />
          <span class="truncate">{{ entry.label }}</span>
          <span
            v-if="entry.to?.name && badges[entry.to.name] > 0"
            class="ml-auto min-w-[18px] h-[18px] px-1 rounded-full bg-red-600 text-white text-[10px] font-bold flex items-center justify-center animate-pulse"
          >
            {{ badges[entry.to.name] > 9 ? '9+' : badges[entry.to.name] }}
          </span>
        </RouterLink>

        <div v-if="entry.children" class="pl-8 mt-0.5 space-y-0.5">
          <RouterLink
            v-for="child in entry.children"
            :key="child.label"
            :to="child.to"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition"
            :class="
              child.to.name === route.name && (!child.to.params?.slug || child.to.params.slug === route.params.slug)
                ? 'text-emerald-700 font-semibold'
                : 'text-slate-500 hover:text-emerald-700 hover:bg-slate-50'
            "
            @click="emit('close')"
          >
            <span class="truncate">{{ child.label }}</span>
            <span
              v-if="child.to?.name && badges[child.to.name] > 0"
              class="ml-auto min-w-[16px] h-[16px] px-1 rounded-full bg-red-600 text-white text-[9px] font-bold flex items-center justify-center animate-pulse"
            >
              {{ badges[child.to.name] > 9 ? '9+' : badges[child.to.name] }}
            </span>
          </RouterLink>
        </div>
      </div>

      <div v-if="gi < groups.length - 1" class="h-px bg-slate-100 mx-1 mt-3"></div>
    </div>
  </nav>
  </Teleport>
</template>
