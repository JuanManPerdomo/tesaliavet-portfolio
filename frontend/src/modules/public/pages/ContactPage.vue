<script setup>
import { ref, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import AppIcon from '../../../components/ui/AppIcon.vue'
import ContactPqrsTypeSelector from '../components/contact/ContactPqrsTypeSelector.vue'
import ContactPqrsSubjectSection from '../components/contact/ContactPqrsSubjectSection.vue'
import ContactPqrsSenderSection from '../components/contact/ContactPqrsSenderSection.vue'
import ContactPqrsMessageSection from '../components/contact/ContactPqrsMessageSection.vue'
import ContactPqrsSidebar from '../components/contact/ContactPqrsSidebar.vue'
import api from '../../../lib/api'
import { useAuthStore } from '../../../stores/auth'

const authStore = useAuthStore()

// PQRS solo para clientes con sesion iniciada - el backend tambien lo exige
// (@role_required('cliente')), esto es solo para no mostrar un formulario
// que de todas formas el servidor va a rechazar.
const canSubmitPqrs = computed(() => authStore.hasRole('cliente'))

// Estado del formulario PQRS
const selectedType = ref('peticion')
const subject = ref('')
const senderName = ref(
  authStore.user ? `${authStore.user.firstName} ${authStore.user.lastName}` : ''
)
const senderEmail = ref(authStore.user?.email ?? '')
const senderPhone = ref('')
const message = ref('')
const attachment = ref(null)

const submitting = ref(false)
const submitError = ref('')
const submitted = ref(false)

async function handleSubmit() {
  submitError.value = ''

  if (!subject.value || !message.value || !senderName.value || !senderEmail.value) {
    submitError.value = 'Completa asunto, mensaje, nombre y correo antes de enviar.'
    return
  }

  submitting.value = true
  try {
    let payload
    if (attachment.value) {
      payload = new FormData()
      payload.append('type', selectedType.value)
      payload.append('subject', subject.value)
      payload.append('message', message.value)
      payload.append('senderName', senderName.value)
      payload.append('senderEmail', senderEmail.value)
      if (senderPhone.value) payload.append('senderPhone', senderPhone.value)
      payload.append('attachment', attachment.value)
    } else {
      payload = {
        type: selectedType.value,
        subject: subject.value,
        message: message.value,
        senderName: senderName.value,
        senderEmail: senderEmail.value,
        senderPhone: senderPhone.value,
      }
    }

    await api.post('/pqrs', payload)
    submitted.value = true
  } catch (err) {
    submitError.value =
      err.response?.data?.message || 'No se pudo enviar la solicitud. Intenta de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <Navbar />

    <!-- Hero -->
    <section class="relative overflow-hidden bg-gradient-to-br from-emerald-900 to-emerald-700">
      <div
        class="pointer-events-none absolute -top-16 -right-16 w-72 h-72 bg-white/10 rounded-full blur-3xl"
      ></div>

      <div
        class="pointer-events-none absolute -bottom-24 left-1/3 w-80 h-80 bg-teal-400/10 rounded-full blur-3xl"
      ></div>

      <div class="relative max-w-7xl mx-auto px-6 pt-8 pb-20 md:pb-24">
        <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-10">
          <div v-reveal class="max-w-xl">
            <span
              class="inline-flex items-center gap-2 bg-white/15 backdrop-blur-sm text-white px-4 py-2 rounded-full text-sm font-semibold mb-5"
            >
              <AppIcon name="message-circle" :size="16" />
              Contáctanos
            </span>

            <h1 class="text-3xl sm:text-4xl font-extrabold text-white leading-tight tracking-tight">
              Hablemos. Estamos para ayudarte.
            </h1>

            <p class="mt-4 text-white/80 leading-relaxed">
              Peticiones, quejas, reclamos y sugerencias. Tu opinión nos ayuda a mejorar —
              respondemos en máximo 15 días hábiles.
            </p>
          </div>

          <div v-reveal="{ delay: 150 }" class="flex gap-4 shrink-0">
            <div
              class="bg-white/10 backdrop-blur border border-white/20 rounded-2xl p-5 text-center min-w-[110px]"
            >
              <div class="flex justify-center mb-2 text-emerald-200">
                <AppIcon name="clock" :size="22" />
              </div>
              <div class="text-xs font-medium text-white leading-snug">Lun–Sáb<br />7am–7pm</div>
            </div>

            <div
              class="bg-white/10 backdrop-blur border border-white/20 rounded-2xl p-5 text-center min-w-[110px]"
            >
              <div class="flex justify-center mb-2 text-emerald-200">
                <AppIcon name="map-pin" :size="22" />
              </div>
              <div class="text-xs font-medium text-white leading-snug">Tesalia<br />Huila</div>
            </div>

            <div
              class="bg-white/10 backdrop-blur border border-white/20 rounded-2xl p-5 text-center min-w-[110px]"
            >
              <div class="flex justify-center mb-2 text-emerald-200">
                <AppIcon name="phone" :size="22" />
              </div>
              <div class="text-xs font-medium text-white leading-snug">310<br />456 7890</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Form card -->
    <div class="relative z-10 max-w-7xl mx-auto px-6 -mt-12 md:-mt-14 pb-16">
      <div
        v-reveal="{ delay: 100 }"
        class="bg-white rounded-3xl shadow-xl border border-slate-100 overflow-hidden flex flex-col lg:flex-row"
      >
        <!-- Form panel -->
        <div class="flex-1 p-6 sm:p-8 lg:p-10 lg:border-r border-slate-100">
          <div
            class="flex items-center gap-2.5 text-xl font-extrabold text-slate-900 mb-2 tracking-tight"
          >
            <AppIcon name="file-text" :size="22" class="text-emerald-700" />
            PQRS — Recepción de solicitudes
          </div>
          <p class="text-sm text-slate-500 leading-relaxed mb-6 max-w-2xl">
            Completa el formulario y te responderemos al correo que nos indiques.
          </p>

          <div
            v-if="submitted"
            class="flex flex-col items-center text-center gap-4 py-16 max-w-md mx-auto"
          >
            <div class="relative">
              <span
                class="absolute inset-0 rounded-full bg-emerald-400/30 animate-ping"
              ></span>
              <div
                class="relative w-16 h-16 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center"
              >
                <AppIcon name="check" :size="30" />
              </div>
            </div>
            <h2 class="text-xl font-bold text-slate-900">Solicitud enviada</h2>
            <p class="text-sm text-slate-500">
              Recibimos tu {{ selectedType }}. Te responderemos a {{ senderEmail }} en máximo 15
              días hábiles.
            </p>
            <RouterLink
              to="/"
              class="mt-2 inline-flex items-center gap-2 text-emerald-700 font-semibold hover:gap-3 transition-all"
            >
              Volver al inicio →
            </RouterLink>
          </div>

          <div
            v-else-if="!canSubmitPqrs"
            class="flex flex-col items-center text-center gap-4 py-16 max-w-md mx-auto"
          >
            <div class="w-16 h-16 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <AppIcon name="user" :size="28" />
            </div>
            <h2 class="text-xl font-bold text-slate-900">Inicia sesión para escribirnos</h2>
            <p class="text-sm text-slate-500">
              Para llevar el registro y la respuesta de tu solicitud, enviar una PQRS requiere
              tener una cuenta de cliente e iniciar sesión.
            </p>
            <div class="flex gap-3 mt-2">
              <RouterLink
                to="/login"
                class="inline-flex items-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-5 py-2.5 rounded-lg font-semibold text-sm transition"
              >
                Iniciar sesión
              </RouterLink>
              <RouterLink
                to="/register"
                class="inline-flex items-center gap-2 border border-slate-200 hover:bg-slate-50 text-slate-700 px-5 py-2.5 rounded-lg font-semibold text-sm transition"
              >
                Registrarme
              </RouterLink>
            </div>
          </div>

          <template v-else>
            <ContactPqrsTypeSelector v-model="selectedType" />

            <ContactPqrsSubjectSection v-model:subject="subject" />

            <ContactPqrsSenderSection
              v-model:name="senderName"
              v-model:email="senderEmail"
              v-model:phone="senderPhone"
            />

            <p v-if="submitError" class="text-sm text-red-600 mb-4">{{ submitError }}</p>

            <ContactPqrsMessageSection
              v-model:message="message"
              v-model:file="attachment"
              :submitting="submitting"
              @submit="handleSubmit"
            />
          </template>
        </div>

        <!-- Sidebar -->
        <ContactPqrsSidebar />
      </div>
    </div>

    <Footer />
  </div>
</template>
