<script setup>
import { ref, watch, nextTick } from 'vue'

const LENGTH = 6

const props = defineProps({
  modelValue: { type: String, default: '' },
  error: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'complete'])

const digits = ref(Array(LENGTH).fill(''))
const inputRefs = ref([])

watch(
  () => props.modelValue,
  (val) => {
    const chars = (val || '').split('').slice(0, LENGTH)
    digits.value = Array.from({ length: LENGTH }, (_, i) => chars[i] || '')
  }
)

function emitValue() {
  const value = digits.value.join('')
  emit('update:modelValue', value)
  if (value.length === LENGTH) emit('complete', value)
}

function handleInput(index, event) {
  const raw = event.target.value.replace(/\D/g, '')
  if (!raw) {
    digits.value[index] = ''
    emitValue()
    return
  }
  // Puede llegar mas de un digito si el usuario escribe rapido - se reparte
  // desde este casillero hacia adelante en vez de perder los extra.
  const chars = raw.split('')
  chars.forEach((ch, offset) => {
    const target = index + offset
    if (target < LENGTH) digits.value[target] = ch
  })
  emitValue()
  const nextIndex = Math.min(index + chars.length, LENGTH - 1)
  nextTick(() => inputRefs.value[nextIndex]?.focus())
}

function handleKeydown(index, event) {
  if (event.key === 'Backspace' && !digits.value[index] && index > 0) {
    inputRefs.value[index - 1]?.focus()
  } else if (event.key === 'ArrowLeft' && index > 0) {
    inputRefs.value[index - 1]?.focus()
  } else if (event.key === 'ArrowRight' && index < LENGTH - 1) {
    inputRefs.value[index + 1]?.focus()
  }
}

function handlePaste(event) {
  const pasted = (event.clipboardData?.getData('text') || '').replace(/\D/g, '').slice(0, LENGTH)
  if (!pasted) return
  event.preventDefault()
  digits.value = Array.from({ length: LENGTH }, (_, i) => pasted[i] || '')
  emitValue()
  const lastIndex = Math.max(Math.min(pasted.length, LENGTH) - 1, 0)
  nextTick(() => inputRefs.value[lastIndex]?.focus())
}
</script>

<template>
  <div class="flex gap-2 justify-center" @paste="handlePaste">
    <input
      v-for="(digit, i) in digits"
      :key="i"
      :ref="(el) => (inputRefs[i] = el)"
      :value="digit"
      type="text"
      inputmode="numeric"
      maxlength="1"
      autocomplete="one-time-code"
      class="w-12 h-14 text-center text-2xl font-bold bg-slate-50 border-2 rounded-xl outline-none transition-all focus:ring-2 focus:ring-emerald-600/20"
      :class="error ? 'border-red-400 text-red-600' : 'border-slate-200 text-slate-900 focus:border-emerald-700 focus:bg-white'"
      @input="handleInput(i, $event)"
      @keydown="handleKeydown(i, $event)"
    />
  </div>
</template>
