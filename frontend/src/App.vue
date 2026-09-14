<script setup>
import ToastContainer from './components/ui/ToastContainer.vue'
import InactivityWatcher from './components/ui/InactivityWatcher.vue'
</script>

<template>
  <RouterView />
  <ToastContainer />
  <InactivityWatcher />
</template>
