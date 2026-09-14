<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../../../../components/ui/AppIcon.vue'
import PrimaryButton from '../../../../components/ui/PrimaryButton.vue'
import { usePqrsStore } from '../../../../stores/pqrs'
import { useToastStore } from '../../../../stores/toast'
import api from '../../../../lib/api'

const STATUS_OPTIONS = ['Abierto', 'En Proceso', 'Resuelto', 'Cerrado']

const route = useRoute()
const pqrsStore = usePqrsStore()
const toastStore = useToastStore()

const pqrsId = computed(() => Number(route.params.id))
const item = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const responseText = ref('')
const status = ref('Resuelto')
const submitting = ref(false)
const reopening = ref(false)

onMounted(async () => {
  try {
    item.value = await pqrsStore.fetchOne(pqrsId.value)
    responseText.value = item.value.response || ''
    status.value = item.value.status === 'Abierto' ? 'Resuelto' : item.value.status
  } catch {
    errorMessage.value = 'No se pudo cargar la solicitud.'
  } finally {
    loading.value = false
  }
})

async function openAttachment() {
  try {
    const { data } = await api.get(item.value.attachmentUrl, { responseType: 'blob' })
    window.open(URL.createObjectURL(data), '_blank')
  } catch {
    toastStore.error('No se pudo abrir el adjunto.')
  }
}

async function handleRespond() {
  if (!responseText.value.trim()) {
    errorMessage.value = 'Escribe una respuesta antes de enviar.'
    return
  }
  submitting.value = true
  errorMessage.value = ''
  try {
    item.value = await pqrsStore.respond(pqrsId.value, { response: responseText.value, status: status.value })
    toastStore.success('Respuesta enviada.')
    // El botón queda al final del formulario, pero lo único que cambia (el
    // badge de estado y la caja "Respuesta enviada") aparece arriba - sin
    // esto, un admin que no hace scroll ve la misma pantalla y piensa que
    // no pasó nada, aunque sí se guardó (bug reportado por Juan Manuel).
    window.scrollTo({ top: 0, behavior: 'instant' })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo enviar la respuesta.'
  } finally {
    submitting.value = false
  }
}

async function handleReopen() {
  reopening.value = true
  errorMessage.value = ''
  try {
    item.value = await pqrsStore.reopen(pqrsId.value)
    responseText.value = item.value.response || ''
    status.value = item.value.status
    toastStore.success('PQRS reabierta.')
    window.scrollTo({ top: 0, behavior: 'instant' })
  } catch (err) {
    errorMessage.value = err.response?.data?.message || 'No se pudo reabrir la solicitud.'
  } finally {
    reopening.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl">
    <RouterLink
      :to="{ name: 'staff-pqrs' }"
      class="inline-flex items-center gap-2 text-emerald-700 text-sm font-semibold hover:underline mb-4"
    >
      <AppIcon name="arrow-left" :size="16" />
      Volver a PQRS
    </RouterLink>

    <div v-if="loading" class="text-sm text-slate-500">Cargando...</div>
    <div v-else-if="!item" class="text-sm text-red-600">{{ errorMessage }}</div>

    <template v-else>
      <div class="bg-white rounded-2xl border border-slate-200 p-6 mb-5">
        <div class="flex items-start justify-between mb-4">
          <div>
            <span class="text-[10px] font-bold text-slate-400 uppercase">{{ item.type }}</span>
            <h1 class="text-xl font-extrabold text-slate-900">{{ item.subject }}</h1>
          </div>
          <span class="text-[10px] font-bold uppercase px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
            {{ item.status }}
          </span>
        </div>

        <p class="text-sm text-slate-700 whitespace-pre-line mb-4">{{ item.message }}</p>

        <div class="border-t border-slate-100 pt-4 text-xs text-slate-500 space-y-1">
          <p><strong class="text-slate-700">{{ item.senderName }}</strong> — {{ item.senderEmail }}</p>
          <p v-if="item.senderPhone">{{ item.senderPhone }}</p>
          <button
            v-if="item.attachmentUrl"
            type="button"
            class="inline-flex items-center gap-1.5 text-emerald-700 font-semibold hover:underline mt-1"
            @click="openAttachment"
          >
            <AppIcon name="file-text" :size="14" /> Ver adjunto
          </button>
        </div>
      </div>

      <div v-if="item.response" class="bg-emerald-50 rounded-2xl border border-emerald-100 p-6 mb-5">
        <h3 class="text-sm font-bold text-emerald-900 mb-2">Respuesta enviada</h3>
        <p class="text-sm text-emerald-800 whitespace-pre-line">{{ item.response }}</p>
        <p class="text-xs text-emerald-600 mt-2">Por {{ item.respondedBy }}</p>
      </div>

      <div v-if="item.status !== 'Cerrado'" class="bg-white rounded-2xl border border-slate-200 p-6">
        <h3 class="text-sm font-bold text-slate-900 mb-4">{{ item.response ? 'Actualizar respuesta' : 'Responder' }}</h3>

        <textarea
          v-model="responseText"
          rows="5"
          placeholder="Escribe la respuesta para el cliente..."
          class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-800 resize-none focus:outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 mb-4"
        ></textarea>

        <div class="flex items-center justify-between gap-4 flex-wrap">
          <select
            v-model="status"
            class="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:border-emerald-700"
          >
            <option v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ s }}</option>
          </select>

          <PrimaryButton :loading="submitting" class="gap-2" @click="handleRespond">
            <AppIcon name="send" :size="14" />
            Enviar respuesta
          </PrimaryButton>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600 mt-4">{{ errorMessage }}</p>
      </div>

      <div v-else class="bg-slate-50 rounded-2xl border border-slate-200 p-6 flex items-start gap-4">
        <div class="w-10 h-10 rounded-xl bg-slate-100 text-slate-400 flex items-center justify-center shrink-0">
          <AppIcon name="archive" :size="18" />
        </div>
        <div class="flex-1">
          <h3 class="text-sm font-bold text-slate-900 mb-1">Esta solicitud está cerrada</h3>
          <p class="text-sm text-slate-500 mb-4">
            No se puede responder ni cambiar el estado mientras esté cerrada. Reábrela si necesitas seguir
            gestionándola.
          </p>
          <PrimaryButton :loading="reopening" class="gap-2" @click="handleReopen">
            <AppIcon name="refresh" :size="14" />
            Reabrir
          </PrimaryButton>
          <p v-if="errorMessage" class="text-sm text-red-600 mt-4">{{ errorMessage }}</p>
        </div>
      </div>
    </template>
  </div>
</template>
