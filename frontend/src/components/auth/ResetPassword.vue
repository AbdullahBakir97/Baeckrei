<template>
  <AuthCard :title="$t('auth.resetTitle')">
    <template v-if="done">
      <p class="rounded-lg border border-green-500/30 bg-green-500/10 p-3 text-green-300" role="status">{{ done }}</p>
      <router-link to="/login" class="btn-amber w-full">{{ $t('nav.signIn') }}</router-link>
    </template>
    <form v-else class="space-y-4" @submit.prevent="submit">
      <div>
        <label for="new_password" class="field-label">{{ $t('account.newPassword') }}</label>
        <input id="new_password" v-model="password" type="password" class="field-input" autocomplete="new-password" required minlength="8" />
      </div>
      <div>
        <label for="confirm_password" class="field-label">{{ $t('account.repeatPassword') }}</label>
        <input id="confirm_password" v-model="confirm" type="password" class="field-input" autocomplete="new-password" required />
      </div>
      <p v-if="error" class="field-error" role="alert">{{ error }}</p>
      <button type="submit" class="btn-amber w-full" :disabled="saving">{{ saving ? $t('common.saving') : $t('auth.setPassword') }}</button>
      <p class="text-center text-sm text-gray-400">
        {{ $t('auth.linkExpired') }} <router-link to="/forgot-password" class="text-amber-400 hover:text-amber-300">{{ $t('auth.requestNew') }}</router-link>
      </p>
    </form>
  </AuthCard>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AuthCard from './AuthCard.vue'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const { t } = useI18n()
const authStore = useAuthStore()
const password = ref('')
const confirm = ref('')
const saving = ref(false)
const error = ref('')
const done = ref('')

async function submit() {
  error.value = ''
  if (password.value !== confirm.value) {
    error.value = t('auth.mismatch')
    return
  }
  saving.value = true
  try {
    done.value = await authStore.confirmPasswordReset({
      uid: route.params.uid,
      token: route.params.token,
      newPassword: password.value
    })
  } catch (err) {
    error.value = err.message
  } finally {
    saving.value = false
  }
}
</script>
