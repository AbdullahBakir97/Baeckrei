<template>
  <AuthCard :title="$t('auth.registerTitle')" :subtitle="$t('auth.registerSubtitle')">
    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="first_name" class="field-label">{{ $t('account.firstName') }}</label>
          <input id="first_name" v-model.trim="form.first_name" class="field-input" autocomplete="given-name" required />
        </div>
        <div>
          <label for="last_name" class="field-label">{{ $t('account.lastName') }}</label>
          <input id="last_name" v-model.trim="form.last_name" class="field-input" autocomplete="family-name" required />
        </div>
      </div>
      <div>
        <label for="email" class="field-label">{{ $t('auth.email') }}</label>
        <input id="email" v-model.trim="form.email" type="email" class="field-input" autocomplete="email" required />
      </div>
      <div>
        <label for="password" class="field-label">{{ $t('common.password') }}</label>
        <input id="password" v-model="form.password" type="password" class="field-input" autocomplete="new-password" required minlength="8" />
      </div>
      <div>
        <label for="password2" class="field-label">{{ $t('auth.repeatPassword') }}</label>
        <input id="password2" v-model="form.password2" type="password" class="field-input" autocomplete="new-password" required />
      </div>
      <p class="text-sm text-gray-500">{{ $t('auth.passwordRules') }}</p>
      <p v-if="localError || authStore.error" class="field-error" role="alert">{{ localError || authStore.error }}</p>
      <button type="submit" class="btn-amber w-full" :disabled="authStore.loading">
        {{ authStore.loading ? $t('auth.creating') : $t('auth.createAccount') }}
      </button>
    </form>
    <p class="text-center text-sm text-gray-400">
      {{ $t('auth.haveAccount') }}
      <router-link :to="{ name: 'login', query: route.query }" class="text-amber-400 hover:text-amber-300">{{ $t('nav.signIn') }}</router-link>
    </p>
  </AuthCard>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import AuthCard from './AuthCard.vue'
import { useAuthStore } from '@/stores/authStore'
import { useCartStore } from '@/stores/cartStore'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const authStore = useAuthStore()
const cartStore = useCartStore()
const localError = ref('')

const form = ref({ first_name: '', last_name: '', email: '', password: '', password2: '' })

const handleSubmit = async () => {
  localError.value = ''
  if (form.value.password !== form.value.password2) {
    localError.value = t('auth.mismatch')
    return
  }
  try {
    await authStore.register(form.value)
    cartStore.fetchCart({ silent: true })
    router.push(route.query.redirect || { name: 'products' })
  } catch (error) {
    // The store shows the message.
  }
}
</script>
