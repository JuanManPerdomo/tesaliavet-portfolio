<script setup>
import { useBackLink } from '../../../lib/useBackLink'

const { label: backLabel, goBack } = useBackLink({
  specialPath: '/register',
  specialLabel: 'Volver al registro',
  specialTo: { name: 'register' },
})

const sections = [
  {
    title: '1. Datos que recolectamos',
    body: 'Recolectamos tu nombre, apellidos, tipo y número de documento, correo electrónico, teléfono, y la información clínica de tus mascotas que registres en la plataforma.',
  },
  {
    title: '2. Finalidad del tratamiento',
    body: 'Usamos tus datos para gestionar tu cuenta, agendar citas, enviarte recordatorios de vacunas y citas, procesar compras, y mejorar nuestros servicios.',
  },
  {
    title: '3. Tratamiento conforme a la ley colombiana',
    body: 'Tus datos personales serán tratados conforme a la Ley 1581 de 2012 y el Decreto 1377 de 2013 de Colombia, que regulan la protección de datos personales.',
  },
  {
    title: '4. Tus derechos',
    body: 'Puedes conocer, actualizar, rectificar o solicitar la eliminación de tus datos personales en cualquier momento, escribiendo a nuestro correo de contacto.',
  },
  {
    title: '5. Seguridad de la información',
    body: 'Implementamos medidas técnicas y administrativas razonables para proteger tus datos personales contra acceso no autorizado, pérdida o alteración.',
  },
  {
    title: '6. Terceros',
    body: 'No compartimos tus datos personales con terceros para fines comerciales sin tu consentimiento explícito.',
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

      <h1 class="text-3xl font-bold text-slate-900 mb-2">Política de privacidad</h1>
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
