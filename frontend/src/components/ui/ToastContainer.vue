<script setup>
import { useToastStore } from '../../stores/toast'
import AppIcon from './AppIcon.vue'

const toastStore = useToastStore()
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed top-5 inset-x-0 z-[9999] flex flex-col items-center gap-2 px-4 pointer-events-none"
    >
      <TransitionGroup name="toast">
        <div
          v-for="t in toastStore.toasts"
          :key="t.id"
          class="pointer-events-auto flex items-center gap-3 rounded-xl border px-4 py-3 shadow-lg max-w-sm w-full"
          :class="{
            'bg-emerald-50 border-emerald-200 text-emerald-800': t.type === 'success',
            'bg-red-50 border-red-200 text-red-700': t.type === 'error',
            'bg-amber-50 border-amber-200 text-amber-800': t.type === 'info',
          }"
        >
          <AppIcon
            :name="t.type === 'success' ? 'check' : t.type === 'info' ? 'bell' : 'alert-triangle'"
            :size="18"
            class="flex-shrink-0"
          />
          <p class="text-sm font-medium flex-1">{{ t.message }}</p>
          <button
            type="button"
            class="text-current opacity-50 hover:opacity-100 transition flex-shrink-0"
            @click="toastStore.remove(t.id)"
          >
            <AppIcon name="x" :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
