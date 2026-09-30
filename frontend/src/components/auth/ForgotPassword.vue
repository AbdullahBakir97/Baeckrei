<template>
  <AuthCard title="Forgot your password?" subtitle="Enter your email and we'll send you a link to choose a new one.">
    <p v-if="sentMessage" class="rounded-lg border border-green-500/30 bg-green-500/10 p-3 text-green-300" role="status">
      {{ sentMessage }}
    </p>
    <form v-else class="space-y-4" @submit.prevent="submit">
      <div>
        <label for="email" class="field-label">Email address</label>
        <input id="email" v-model.trim="email" type="email" class="field-input" autocomplete="email" required />
      </div>
      <p v-if="error" class="field-error" role="alert">{{ error }}</p>
      <button type="submit" class="btn-amber w-full" :disabled="sending">{{ sending ? 'Sending…' : 'Send reset link' }}</button>
    </form>
    <p class="text-center text-sm text-gray-400">
      <router-link to="/login" class="text-amber-400 hover:text-amber-300">Back to sign in</router-link>
    </p>
  </AuthCard>
</template>

<script setup>
import { ref } from 'vue'
import AuthCard from './AuthCard.vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const email = ref('')
const sending = ref(false)
const sentMessage = ref('')
const error = ref('')

async function submit() {
  sending.value = true
  error.value = ''
  try {
    sentMessage.value = await authStore.requestPasswordReset(email.value)
  } catch (err) {
    error.value = err.response?.status === 429
      ? 'Too many requests. Please wait a while and try again.'
      : 'The reset link could not be sent. Please try again.'
  } finally {
    sending.value = false
  }
}
</script>
