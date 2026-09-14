<script setup>
import AppIcon from '../../../../components/ui/AppIcon.vue'
</script>

<template>
  <aside class="w-full lg:w-[320px] shrink-0 bg-slate-50 p-6 lg:p-8">
    <!-- Tiempos de respuesta -->
    <div class="mb-6">
      <div class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
        <AppIcon name="clock" :size="16" class="text-emerald-700" />
        Tiempos de respuesta
      </div>

      <div class="flex items-start gap-3 mb-3">
        <span
          class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0"
        >
          <AppIcon name="file-text" :size="16" />
        </span>
        <div>
          <div class="text-[13px] font-bold text-slate-900 leading-tight">Petición</div>
          <div class="text-xs text-slate-500">Máximo 15 días hábiles</div>
        </div>
      </div>

      <div class="flex items-start gap-3 mb-3">
        <span
          class="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center shrink-0"
        >
          <AppIcon name="alert-triangle" :size="16" />
        </span>
        <div>
          <div class="text-[13px] font-bold text-slate-900 leading-tight">Queja / Reclamo</div>
          <div class="text-xs text-slate-500">Máximo 15 días hábiles</div>
        </div>
      </div>

      <div class="flex items-start gap-3">
        <span
          class="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center shrink-0"
        >
          <AppIcon name="lightbulb" :size="16" />
        </span>
        <div>
          <div class="text-[13px] font-bold text-slate-900 leading-tight">Sugerencia</div>
          <div class="text-xs text-slate-500">Máximo 30 días hábiles</div>
        </div>
      </div>
    </div>

    <hr class="border-slate-200 my-5" />

    <!-- Estados de seguimiento -->
    <div class="mb-6">
      <div class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
        <AppIcon name="clipboard" :size="16" class="text-emerald-700" />
        Estados de seguimiento
      </div>

      <div class="flex flex-col gap-2 mb-3">
        <span
          class="inline-flex items-center gap-1.5 w-fit text-[11px] font-bold px-3 py-1 rounded-full bg-amber-100 text-amber-800"
        >
          <AppIcon name="clock" :size="12" /> Abierto
        </span>
        <span
          class="inline-flex items-center gap-1.5 w-fit text-[11px] font-bold px-3 py-1 rounded-full bg-blue-50 text-blue-700"
        >
          <AppIcon name="refresh" :size="12" /> En Proceso
        </span>
        <span
          class="inline-flex items-center gap-1.5 w-fit text-[11px] font-bold px-3 py-1 rounded-full bg-emerald-50 text-emerald-700"
        >
          <AppIcon name="check" :size="12" /> Resuelto
        </span>
        <span
          class="inline-flex items-center gap-1.5 w-fit text-[11px] font-bold px-3 py-1 rounded-full bg-white text-slate-500 border border-slate-200"
        >
          <AppIcon name="archive" :size="12" /> Cerrado
        </span>
      </div>

      <p class="text-[11px] text-slate-400 italic leading-relaxed">
        Puedes consultar el estado de tu solicitud iniciando sesión y revisando tus notificaciones.
      </p>
    </div>

    <hr class="border-slate-200 my-5" />

    <!-- Contacto directo -->
    <div>
      <div class="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
        <AppIcon name="headset" :size="16" class="text-emerald-700" />
        Contacto directo
      </div>

      <div class="flex items-start gap-3 mb-3">
        <span
          class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center shrink-0"
        >
          <AppIcon name="message-circle" :size="16" />
        </span>
        <div>
          <div class="text-[13px] font-bold text-slate-900 leading-tight">WhatsApp</div>
          <div class="text-xs text-slate-500">310 456 7890 — Lun–Sáb 7am–7pm</div>
        </div>
      </div>

      <div class="flex items-start gap-3 mb-3">
        <span
          class="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center shrink-0"
        >
          <AppIcon name="mail" :size="16" />
        </span>
        <div>
          <div class="text-[13px] font-bold text-slate-900 leading-tight">Correo</div>
          <div class="text-xs text-slate-500">contacto@tesaliavet.com</div>
        </div>
      </div>

      <div class="flex items-start gap-3">
        <span
          class="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 flex items-center justify-center shrink-0"
        >
          <AppIcon name="map-pin" :size="16" />
        </span>
        <div>
          <div class="text-[13px] font-bold text-slate-900 leading-tight">Presencial</div>
          <div class="text-xs text-slate-500">Tesalia, Huila - Colombia</div>
        </div>
      </div>
    </div>
  </aside>
</template>
