<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-3xl mx-auto space-y-6">
      <PageHeader eyebrow="Account" title="My profile" :subtitle="memberSince" icon="user" />

      <section class="glass-panel">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 class="text-xl font-semibold text-white">{{ fullName || 'Your details' }}</h2>
            <p class="text-gray-400">{{ user?.email }}</p>
          </div>
          <span v-if="isAdmin" class="rounded-full bg-blue-500/20 px-3 py-1 text-sm text-blue-300">Admin</span>
        </div>

        <form v-if="editing" class="mt-6 grid sm:grid-cols-2 gap-4" @submit.prevent="save">
          <div>
            <label for="first_name" class="field-label">First name</label>
            <input id="first_name" v-model.trim="form.first_name" class="field-input" autocomplete="given-name" />
          </div>
          <div>
            <label for="last_name" class="field-label">Last name</label>
            <input id="last_name" v-model.trim="form.last_name" class="field-input" autocomplete="family-name" />
          </div>
          <div class="sm:col-span-2">
            <label for="phone" class="field-label">Phone <span class="text-gray-500">(optional)</span></label>
            <input id="phone" v-model.trim="form.phone" type="tel" class="field-input" autocomplete="tel" />
          </div>
          <p v-if="error" class="sm:col-span-2 field-error" role="alert">{{ error }}</p>
          <div class="sm:col-span-2 flex gap-3">
            <button type="submit" class="btn-amber" :disabled="saving">{{ saving ? 'Saving…' : 'Save changes' }}</button>
            <button type="button" class="btn-ghost" @click="cancelEdit">Cancel</button>
          </div>
        </form>

        <template v-else>
          <dl class="mt-6 grid sm:grid-cols-2 gap-4">
            <div>
              <dt class="text-sm text-gray-500">Name</dt>
              <dd class="text-gray-200">{{ fullName || '—' }}</dd>
            </div>
            <div>
              <dt class="text-sm text-gray-500">Phone</dt>
              <dd class="text-gray-200">{{ user?.phone || '—' }}</dd>
            </div>
          </dl>
          <div class="mt-6 flex flex-wrap gap-3">
            <button type="button" class="btn-amber" @click="startEdit">Edit profile</button>
            <router-link to="/settings" class="btn-ghost">Password and addresses</router-link>
          </div>
        </template>
      </section>

      <section class="glass-panel grid sm:grid-cols-3 gap-3">
        <router-link to="/orders" class="choice-card">
          <font-awesome-icon icon="box-open" class="mt-1 text-amber-400" />
          <span><span class="block text-white font-medium">Orders</span><span class="text-sm text-gray-400">Track and cancel</span></span>
        </router-link>
        <router-link to="/wishlist" class="choice-card">
          <font-awesome-icon icon="heart" class="mt-1 text-amber-400" />
          <span><span class="block text-white font-medium">Wishlist</span><span class="text-sm text-gray-400">Saved products</span></span>
        </router-link>
        <router-link v-if="isAdmin" to="/admin" class="choice-card">
          <font-awesome-icon icon="chart-pie" class="mt-1 text-amber-400" />
          <span><span class="block text-white font-medium">Admin</span><span class="text-sm text-gray-400">Manage the shop</span></span>
        </router-link>
      </section>

      <button type="button" class="btn-ghost text-red-300" @click="handleLogout">Sign out</button>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/common/PageHeader.vue'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()

const user = computed(() => authStore.user)
const isAdmin = computed(() => authStore.isAdmin)
const fullName = computed(() => [user.value?.first_name, user.value?.last_name].filter(Boolean).join(' '))
const memberSince = computed(() => user.value?.date_joined
  ? `Member since ${new Date(user.value.date_joined).toLocaleDateString('en-GB', { year: 'numeric', month: 'long', day: 'numeric' })}`
  : '')

const editing = ref(false)
const saving = ref(false)
const error = ref('')
const form = reactive({ first_name: '', last_name: '', phone: '' })

function startEdit() {
  Object.assign(form, {
    first_name: user.value?.first_name || '',
    last_name: user.value?.last_name || '',
    phone: user.value?.phone || ''
  })
  error.value = ''
  editing.value = true
}

function cancelEdit() {
  editing.value = false
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    await authStore.updateProfile({ ...form })
    editing.value = false
    showToast('Profile saved')
  } catch (err) {
    error.value = authStore.error
  } finally {
    saving.value = false
  }
}

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>
