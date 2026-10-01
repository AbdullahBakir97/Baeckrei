<template>
  <div class="section max-w-3xl pb-10">
    <div class="space-y-6">
      <PageHeader :eyebrow="$t('account.eyebrow')" :title="$t('account.profileTitle')" :subtitle="memberSince" />

      <section class="glass-panel">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 class="display-title text-4xl">{{ fullName || $t('account.yourDetails') }}</h2>
            <p class="text-gray-400">{{ user?.email }}</p>
          </div>
          <span v-if="isAdmin" class="rounded-full bg-blue-500/20 px-3 py-1 text-sm text-blue-300">{{ $t('account.admin') }}</span>
        </div>

        <form v-if="editing" class="mt-6 grid sm:grid-cols-2 gap-4" @submit.prevent="save">
          <div>
            <label for="first_name" class="field-label">{{ $t('account.firstName') }}</label>
            <input id="first_name" v-model.trim="form.first_name" class="field-input" autocomplete="given-name" />
          </div>
          <div>
            <label for="last_name" class="field-label">{{ $t('account.lastName') }}</label>
            <input id="last_name" v-model.trim="form.last_name" class="field-input" autocomplete="family-name" />
          </div>
          <div class="sm:col-span-2">
            <label for="phone" class="field-label">{{ $t('common.phone') }} <span class="text-gray-500">({{ $t('common.optional') }})</span></label>
            <input id="phone" v-model.trim="form.phone" type="tel" class="field-input" autocomplete="tel" />
          </div>
          <p v-if="error" class="sm:col-span-2 field-error" role="alert">{{ error }}</p>
          <div class="sm:col-span-2 flex gap-3">
            <button type="submit" class="btn-amber" :disabled="saving">{{ saving ? $t('common.saving') : $t('account.saveChanges') }}</button>
            <button type="button" class="btn-ghost" @click="cancelEdit">{{ $t('common.cancel') }}</button>
          </div>
        </form>

        <template v-else>
          <dl class="mt-6 grid sm:grid-cols-2 gap-4">
            <div>
              <dt class="text-sm text-gray-500">{{ $t('common.name') }}</dt>
              <dd class="text-gray-200">{{ fullName || '—' }}</dd>
            </div>
            <div>
              <dt class="text-sm text-gray-500">{{ $t('common.phone') }}</dt>
              <dd class="text-gray-200">{{ user?.phone || '—' }}</dd>
            </div>
          </dl>
          <div class="mt-6 flex flex-wrap gap-3">
            <button type="button" class="btn-amber" @click="startEdit">{{ $t('account.editProfile') }}</button>
            <router-link to="/settings" class="btn-ghost">{{ $t('account.passwordAndAddresses') }}</router-link>
          </div>
        </template>
      </section>

      <section class="glass-panel grid sm:grid-cols-3 gap-3">
        <router-link to="/orders" class="choice-card">
          <font-awesome-icon icon="box-open" class="mt-1 text-amber-400" />
          <span><span class="block text-white font-medium">{{ $t('nav.orders') }}</span><span class="text-sm text-gray-400">{{ $t('account.ordersHint') }}</span></span>
        </router-link>
        <router-link to="/wishlist" class="choice-card">
          <font-awesome-icon icon="heart" class="mt-1 text-amber-400" />
          <span><span class="block text-white font-medium">{{ $t('nav.wishlist') }}</span><span class="text-sm text-gray-400">{{ $t('account.wishlistHint') }}</span></span>
        </router-link>
        <router-link v-if="isAdmin" to="/admin" class="choice-card">
          <font-awesome-icon icon="chart-pie" class="mt-1 text-amber-400" />
          <span><span class="block text-white font-medium">{{ $t('account.admin') }}</span><span class="text-sm text-gray-400">{{ $t('account.adminHint') }}</span></span>
        </router-link>
      </section>

      <button type="button" class="btn-ghost text-red-300" @click="handleLogout">{{ $t('nav.signOut') }}</button>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/common/PageHeader.vue'
import { useAuthStore } from '@/stores/authStore'
import { useToast } from '@/composables/useToast'
import { useI18n } from 'vue-i18n'
import { formatDate } from '@/utils/money'

const router = useRouter()
const authStore = useAuthStore()
const { showToast } = useToast()
const { t } = useI18n()

const user = computed(() => authStore.user)
const isAdmin = computed(() => authStore.isAdmin)
const fullName = computed(() => [user.value?.first_name, user.value?.last_name].filter(Boolean).join(' '))
const memberSince = computed(() => user.value?.date_joined
  ? t('account.memberSince', { date: formatDate(user.value.date_joined) })
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
    showToast(t('account.profileSaved'))
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
