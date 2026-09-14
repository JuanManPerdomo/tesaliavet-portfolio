<script setup>
defineProps({
  eyebrowIcon: { type: String, default: 'heart' }, // 'heart' | 'user-plus'
  eyebrowText: { type: String, default: '' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  widthClass: { type: String, default: 'md:w-[42%]' },
})

const icons = {
  paw: 'M12 4a2 2 0 100 4 2 2 0 000-4zM7 8a1.6 1.6 0 100 3.2A1.6 1.6 0 007 8zm10 0a1.6 1.6 0 100 3.2A1.6 1.6 0 0017 8zM9 12a2 2 0 00-2 2v1a4 4 0 004 4h2a4 4 0 004-4v-1a2 2 0 00-2-2H9z',
  heart: 'M12 21s-7-4.5-9.5-9A5.5 5.5 0 0112 6a5.5 5.5 0 019.5 6c-2.5 4.5-9.5 9-9.5 9z',
  'user-plus': 'M8 11a4 4 0 100-8 4 4 0 000 8zM2 21v-1a6 6 0 016-6h1M18 8v6M15 11h6',
}
</script>

<template>
  <div
    :class="widthClass"
    class="w-full p-10 flex flex-col justify-between relative overflow-hidden text-white bg-gradient-to-br from-emerald-900 via-emerald-800 to-emerald-700"
  >
    <div class="absolute w-64 h-64 -top-24 -right-24 rounded-full bg-white/10 blur-2xl"></div>
    <div class="absolute w-80 h-80 -bottom-32 -left-16 rounded-full bg-white/5 blur-2xl"></div>

    <div class="relative z-10 flex items-center gap-3 font-semibold text-xl tracking-tight">
      <div
        class="w-10 h-10 bg-white/20 backdrop-blur-md border border-white/30 rounded-xl flex items-center justify-center"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path :d="icons.paw" /></svg>
      </div>
      TesaliaVet
    </div>

    <div class="relative z-10 space-y-6 my-10">
      <div
        class="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-[11px] font-semibold tracking-wider uppercase border border-white/10"
      >
        <svg
          class="w-3.5 h-3.5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="icons[eyebrowIcon]" />
        </svg>
        {{ eyebrowText }}
      </div>
      <h1 class="text-4xl font-bold leading-[1.1] tracking-tight">{{ title }}</h1>
      <p class="text-white/70 text-sm leading-relaxed max-w-xs">{{ subtitle }}</p>

      <div class="space-y-4 pt-4">
        <slot />
      </div>
    </div>

    <div class="relative z-10 mt-auto">
      <slot name="footer" />
    </div>
  </div>
</template>
