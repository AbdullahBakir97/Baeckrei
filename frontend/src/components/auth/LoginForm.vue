<template>
  <AuthCard title="Sign in to your account">
    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div>
        <label for="email" class="field-label">Email address</label>
        <input id="email" v-model.trim="form.email" type="email" class="field-input" autocomplete="email" required />
      </div>
      <div>
        <div class="flex items-center justify-between">
          <label for="password" class="field-label">Password</label>
          <router-link to="/forgot-password" class="text-sm text-amber-400 hover:text-amber-300">Forgot password?</router-link>
        </div>
        <input id="password" v-model="form.password" type="password" class="field-input" autocomplete="current-password" required />
      </div>
      <p v-if="authStore.error" class="field-error" role="alert">{{ authStore.error }}</p>
      <button type="submit" class="btn-amber w-full" :disabled="authStore.loading">
        {{ authStore.loading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>
    <p class="text-center text-sm text-gray-400">
      New here?
      <router-link :to="{ name: 'register', query: route.query }" class="text-amber-400 hover:text-amber-300">Create an account</router-link>
    </p>
  </AuthCard>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AuthCard from './AuthCard.vue'
import { useAuthStore } from '@/stores/authStore'
import { useCartStore } from '@/stores/cartStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const cartStore = useCartStore()

const form = ref({ email: '', password: '' })

const handleSubmit = async () => {
  try {
    await authStore.login(form.value)
    // The signed-in customer has their own cart.
    cartStore.fetchCart({ silent: true })
    const redirect = route.query.redirect
    if (redirect) router.push(redirect)
    else router.push(authStore.isAdmin ? { name: 'admin-dashboard' } : { name: 'products' })
  } catch (error) {
    // The store shows the message.
  }
}
</script>
