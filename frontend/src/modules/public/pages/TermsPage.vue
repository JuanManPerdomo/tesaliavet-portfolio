<script setup>
import { useBackLink } from '../../../lib/useBackLink'

const { label: backLabel, goBack } = useBackLink({
  specialPath: '/register',
  specialLabel: 'Volver al registro',
  specialTo: { name: 'register' },
})

const sections = [
  {
    title: '1. Aceptación de los términos',
    body: 'Al registrarte y usar TesaliaVet, aceptas estos términos y condiciones en su totalidad. Si no estás de acuerdo con alguna parte, no debes usar la plataforma.',
  },
  {
    title: '2. Descripción del servicio',
    body: 'TesaliaVet es una plataforma en línea que permite agendar citas veterinarias, consultar el historial clínico de tus mascotas y comprar productos relacionados con su cuidado.',
  },
  {
    title: '3. Registro de cuenta',
    body: 'Eres responsable de mantener la confidencialidad de tu contraseña y de toda actividad realizada desde tu cuenta. La información proporcionada durante el registro debe ser veraz y estar actualizada.',
  },
  {
    title: '4. Uso adecuado',
    body: 'Te comprometes a usar la plataforma únicamente para fines lícitos relacionados con el cuidado de tus mascotas, sin afectar el funcionamiento del servicio ni los derechos de otros usuarios.',
  },
  {
    title: '5. Modificaciones',
    body: 'TesaliaVet puede actualizar estos términos en cualquier momento. Notificaremos los cambios relevantes a través de la plataforma o por correo electrónico.',
  },
]
</script>

<template>
  <div class="min-h-screen bg-slate-50 py-12 px-4 md:px-8">
    <div
      class="max-w-3xl mx-auto bg-white rounded-xl shadow-sm border border-slate-200 p-8 md:p-12"
    >
      <button
        type="button"
        class="inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:underline mb-8"
        @click="goBack"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        {{ backLabel }}
      </button>

      <h1 class="text-3xl font-bold text-slate-900 mb-2">Términos y condiciones</h1>
      <p class="text-sm text-slate-500 mb-10">Última actualización: julio de 2026</p>

      <div class="space-y-8">
        <section v-for="section in sections" :key="section.title">
          <h2 class="text-lg font-semibold text-slate-900 mb-2">{{ section.title }}</h2>
          <p class="text-sm text-slate-600 leading-relaxed">{{ section.body }}</p>
        </section>
      </div>
    </div>
  </div>
</template>
