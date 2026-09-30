<template>
  <AuthCard :title="$t('auth.forgotTitle')" :subtitle="$t('auth.forgotSubtitle')">
    <p v-if="sentMessage" class="rounded-lg border border-green-500/30 bg-green-500/10 p-3 text-green-300" role="status">
      {{ sentMessage }}
    </p>
    <form v-else class="space-y-4" @submit.prevent="submit">
      <div>
        <label for="email" class="field-label">{{ $t('auth.email') }}</label>
        <input id="email" v-model.trim="email" type="email" class="field-input" autocomplete="email" required />
      </div>
      <p v-if="error" class="field-error" role="alert">{{ error }}</p>
      <button type="submit" class="btn-amber w-full" :disabled="sending">{{ sending ? $t('footer.sending') : $t('auth.sendLink') }}</button>
    </form>
    <p class="text-center text-sm text-gray-400">
      <router-link to="/login" class="text-amber-400 hover:text-amber-300">{{ $t('auth.backToSignIn') }}</router-link>
    </p>
  </AuthCard>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AuthCard from './AuthCard.vue'
import { useAuthStore } from '@/stores/authStore'

const { t } = useI18n()
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
      ? t('auth.tooMany')
      : t('auth.sendFailed')
  } finally {
    sending.value = false
  }
}
</script>
