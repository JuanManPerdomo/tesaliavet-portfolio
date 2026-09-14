<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import api from '../../../lib/api'
import AppIcon from '../../../components/ui/AppIcon.vue'

const props = defineProps({
  photoUrl: { type: String, default: null },
  iconSize: { type: [String, Number], default: 32 },
})

const objectUrl = ref('')

async function load(url) {
  if (objectUrl.value) {
    URL.revokeObjectURL(objectUrl.value)
    objectUrl.value = ''
  }
  if (!url) return
  try {
    const { data } = await api.get(url, { responseType: 'blob' })
    objectUrl.value = URL.createObjectURL(data)
  } catch {
    objectUrl.value = ''
  }
}

watch(() => props.photoUrl, load, { immediate: true })
onBeforeUnmount(() => {
  if (objectUrl.value) URL.revokeObjectURL(objectUrl.value)
})
</script>

<template>
  <img v-if="objectUrl" :src="objectUrl" class="w-full h-full object-cover" alt="" />
  <div v-else class="w-full h-full flex items-center justify-center bg-emerald-50 text-emerald-600">
    <AppIcon name="paw" :size="iconSize" />
  </div>
</template>
