<script setup>
import { ref, onMounted } from 'vue'

const message = ref('loading...')

onMounted(async () => {
  const res = await fetch('/api/hello')
  const text = await res.text()   // ← json() じゃなくて text()
  message.value = text
})
</script>

<template>
  <h1>Static Web Apps + Vue + Functions</h1>
  <p>API says: {{ message }}</p>
</template>