<script setup>
import { ref } from 'vue'
import AppIcon from '../../../../components/ui/AppIcon.vue'

defineProps({
  message: { type: String, required: true },
  submitting: { type: Boolean, default: false },
})
const emit = defineEmits(['update:message', 'update:file', 'submit'])

const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png']
const MAX_SIZE = 5 * 1024 * 1024 // 5MB

const fileName = ref('')
const fileError = ref('')

function handleFileChange(event) {
  const file = event.target.files?.[0]
  fileError.value = ''
  fileName.value = ''

  if (!file) {
    emit('update:file', null)
    return
  }

  if (!ALLOWED_TYPES.includes(file.type)) {
    fileError.value = 'Formato no permitido. Solo se aceptan PDF, JPG o PNG.'
    event.target.value = ''
    emit('update:file', null)
    return
  }

  if (file.size > MAX_SIZE) {
    fileError.value = 'El archivo supera el máximo de 5MB.'
    event.target.value = ''
    emit('update:file', null)
    return
  }

  fileName.value = file.name
  emit('update:file', file)
}
</script>

<template>
  <div>
    <div class="mb-7">
      <div class="flex items-center gap-3 mb-3.5">
        <span class="text-xs font-bold text-slate-500 uppercase tracking-wide whitespace-nowrap">
          4. Descripción y soporte
        </span>
        <span class="flex-1 h-px bg-slate-200"></span>
      </div>

      <div class="mb-4">
        <label class="block text-xs font-semibold text-slate-900 mb-1.5">
          Mensaje detallado <span class="text-red-600">*</span>
        </label>
        <textarea
          :value="message"
          placeholder="Cuéntanos con detalle tu solicitud…"
          class="w-full h-[110px] bg-white border border-slate-200 rounded-lg p-3 text-sm text-slate-900 outline-none resize-none leading-relaxed focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 transition"
          @input="$emit('update:message', $event.target.value)"
        ></textarea>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-900 mb-1.5">
          Adjuntar archivo <span class="font-normal text-slate-400 text-[11px]">(opcional)</span>
        </label>
        <label
          class="block bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-6 text-center cursor-pointer hover:border-emerald-700 hover:bg-emerald-50 transition"
        >
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            class="hidden"
            @change="handleFileChange"
          />
          <div class="flex justify-center text-slate-400 mb-2">
            <AppIcon name="cloud" :size="28" />
          </div>
          <div v-if="fileName" class="text-[13px] text-emerald-700 font-semibold">
            {{ fileName }}
          </div>
          <div v-else class="text-[13px] text-slate-500">
            <span class="text-emerald-700 font-bold">Haz clic para seleccionar</span> o arrastra un
            archivo aquí
          </div>
          <div class="text-[11px] text-slate-400 mt-1">PDF, JPG, PNG — Máximo 5MB</div>
        </label>
        <p v-if="fileError" class="text-[11px] text-red-600 mt-1.5">{{ fileError }}</p>
      </div>
    </div>

    <button
      type="button"
      :disabled="submitting"
      class="w-full bg-emerald-700 text-white rounded-xl py-3.5 text-[15px] font-bold flex items-center justify-center gap-2 shadow-lg shadow-emerald-700/20 hover:bg-emerald-800 hover:-translate-y-0.5 transition-all disabled:opacity-60 disabled:pointer-events-none"
      @click="$emit('submit')"
    >
      <AppIcon name="send" :size="18" />
      {{ submitting ? 'Enviando...' : 'Enviar solicitud' }}
    </button>
  </div>
</template>
