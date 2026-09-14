<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'

defineProps({
  name: { type: String, required: true },
  email: { type: String, required: true },
  phone: { type: String, required: true },
})
defineEmits(['update:name', 'update:email', 'update:phone'])
</script>

<template>
  <div class="mb-7">
    <div class="flex items-center gap-3 mb-3.5">
      <span class="text-xs font-bold text-slate-500 uppercase tracking-wide whitespace-nowrap">
        3. Datos del remitente
      </span>
      <span class="flex-1 h-px bg-slate-200"></span>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
      <div>
        <label class="block text-xs font-semibold text-slate-900 mb-1.5">
          Nombre completo <span class="text-red-600">*</span>
        </label>
        <div class="relative flex items-center">
          <AppIcon name="user" :size="16" class="absolute left-3 text-slate-400" />
          <input
            :value="name"
            type="text"
            placeholder="Tu nombre completo"
            class="w-full bg-white border border-slate-200 rounded-lg pl-10 pr-3 py-2.5 text-sm text-slate-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition"
            @input="$emit('update:name', $event.target.value)"
          />
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-900 mb-1.5">
          Correo electrónico <span class="text-red-600">*</span>
        </label>
        <div class="relative flex items-center">
          <AppIcon name="mail" :size="16" class="absolute left-3 text-slate-400" />
          <input
            :value="email"
            type="email"
            placeholder="tucorreo@ejemplo.com"
            class="w-full bg-white border border-slate-200 rounded-lg pl-10 pr-3 py-2.5 text-sm text-slate-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition"
            @input="$emit('update:email', $event.target.value)"
          />
        </div>
      </div>
    </div>

    <div>
      <label class="block text-xs font-semibold text-slate-900 mb-1.5"> Teléfono / Celular </label>
      <div class="relative flex items-center">
        <AppIcon name="phone" :size="16" class="absolute left-3 text-slate-400" />
        <input
          :value="phone"
          type="tel"
          placeholder="300 000 0000"
          class="w-full bg-white border border-slate-200 rounded-lg pl-10 pr-3 py-2.5 text-sm text-slate-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition"
          @input="$emit('update:phone', $event.target.value)"
        />
      </div>
    </div>
  </div>
</template>
