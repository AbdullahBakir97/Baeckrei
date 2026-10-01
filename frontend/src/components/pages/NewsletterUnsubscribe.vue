<template>
  <div class="min-h-[60vh] flex items-center justify-center py-16 px-4">
    <div class="glass-panel max-w-md w-full text-center space-y-4">
      <h1 class="text-2xl font-bold text-white">Newsletter</h1>
      <p v-if="loading" class="text-gray-400">Unsubscribing…</p>
      <p v-else :class="ok ? 'text-green-300' : 'text-red-300'" role="status">{{ message }}</p>
      <router-link to="/products" class="btn-ghost">Back to the shop</router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/plugins/axios'

const route = useRoute()
const loading = ref(true)
const ok = ref(false)
const message = ref('')

onMounted(async () => {
  try {
    const response = await axios.post('/api/content/newsletter/unsubscribe/', { token: route.query.token })
    ok.value = true
    message.value = response.data.message
  } catch (err) {
    message.value = err.response?.data?.detail || 'This unsubscribe link is not valid.'
  } finally {
    loading.value = false
  }
})
</script>
