<template>
  <div class="space-y-6">
    <form class="admin-panel flex flex-wrap items-end gap-3 p-4" role="search" @submit.prevent="load">
      <div class="flex-1 min-w-[16rem]">
        <label for="user-search" class="block text-sm font-medium text-cream/80">{{ $t('common.search') }}</label>
        <input id="user-search" v-model.trim="search" type="search" :placeholder="$t('admin.users.searchPlaceholder')"
               class="mt-1 block w-full rounded-md border border-cream/15 px-3 py-2 shadow-sm sm:text-sm text-cream bg-oven-800" />
      </div>
      <button type="submit" class="px-4 py-2 text-sm font-medium rounded-full text-oven-950 bg-crust hover:bg-crust-light">{{ $t('common.search') }}</button>
    </form>

    <p v-if="error" class="rounded-md bg-red-400/10 p-3 text-sm text-red-300" role="alert">{{ error }}</p>

    <div class="admin-panel overflow-x-auto">
      <table class="min-w-full divide-y divide-cream/10 admin-table">
        <thead>
          <tr>
            <th scope="col">{{ $t('common.name') }}</th>
            <th scope="col">{{ $t('common.email') }}</th>
            <th scope="col">{{ $t('admin.users.joined') }}</th>
            <th scope="col" class="text-end">{{ $t('admin.users.orders') }}</th>
            <th scope="col">{{ $t('admin.users.account') }}</th>
            <th scope="col"><span class="sr-only">{{ $t('admin.table.actions') }}</span></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-cream/10">
          <tr v-if="loading"><td colspan="6" class="text-center text-cream-muted">{{ $t('admin.users.loading') }}</td></tr>
          <tr v-else-if="!users.length"><td colspan="6" class="text-center text-cream-muted">{{ $t('admin.users.empty') }}</td></tr>
          <tr v-for="user in users" v-else :key="user.id">
            <td class="font-medium text-cream">{{ [user.first_name, user.last_name].filter(Boolean).join(' ') || '—' }}</td>
            <td class="max-w-[14rem] truncate" :title="user.email">{{ user.email }}</td>
            <td class="whitespace-nowrap" :title="$t('admin.users.lastSignIn', { date: user.last_login ? formatDate(user.last_login) : $t('admin.users.never') })">
              {{ formatDate(user.date_joined) }}
            </td>
            <td class="text-end tabular-nums">{{ user.order_count ?? 0 }}</td>
            <td>
              <div class="flex flex-col items-start gap-1">
                <span class="px-2 py-0.5 text-xs font-medium rounded-full" :class="user.is_staff ? 'bg-crust/15 text-crust-light' : 'bg-cream/[0.05] text-cream/80'">
                  {{ user.is_staff ? $t('admin.users.admin') : $t('admin.users.customer') }}
                </span>
                <span class="px-2 py-0.5 text-xs font-medium rounded-full" :class="user.is_active ? 'bg-emerald-400/10 text-emerald-300' : 'bg-red-400/10 text-red-300'">
                  {{ user.is_active ? $t('admin.users.active') : $t('admin.users.deactivated') }}
                </span>
              </div>
            </td>
            <td class="text-end whitespace-nowrap"><div class="flex flex-col items-end gap-1">
              <template v-if="user.id !== currentUserId">
                <template v-if="pending?.id === user.id">
                  <span class="text-cream-muted">{{ pending.question }}</span>
                  <button type="button" class="text-crust hover:text-crust-light bg-transparent font-medium" @click="confirmPending">{{ $t('admin.users.yes') }}</button>
                  <button type="button" class="text-cream-muted bg-transparent" @click="pending = null">{{ $t('admin.users.no') }}</button>
                </template>
                <template v-else>
                  <button type="button" class="text-cream/80 hover:text-cream bg-transparent"
                          @click="ask(user, { is_active: !user.is_active }, user.is_active ? $t('admin.users.deactivateQuestion') : $t('admin.users.reactivateQuestion'))">
                    {{ user.is_active ? $t('admin.users.deactivate') : $t('admin.users.reactivate') }}
                  </button>
                  <button type="button" class="text-crust hover:text-crust-light bg-transparent"
                          @click="ask(user, { is_staff: !user.is_staff }, user.is_staff ? $t('admin.users.removeAdminQuestion') : $t('admin.users.makeAdminQuestion'))">
                    {{ user.is_staff ? $t('admin.users.removeAdmin') : $t('admin.users.makeAdmin') }}
                  </button>
                </template>
              </template>
              <span v-else class="text-xs text-cream-faint">{{ $t('admin.users.you') }}</span>
            </div></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { formatDate } from '@/utils/money'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const { t } = useI18n()
const currentUserId = computed(() => authStore.user?.id)
const users = ref([])
const search = ref('')
const loading = ref(false)
const error = ref('')
const pending = ref(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/api/accounts/users/', { params: search.value ? { search: search.value } : {} })
    users.value = response.data
  } catch (err) {
    error.value = t('admin.users.loadError')
  } finally {
    loading.value = false
  }
}

function ask(user, changes, question) {
  pending.value = { id: user.id, changes, question }
}

async function confirmPending() {
  const { id, changes } = pending.value
  pending.value = null
  error.value = ''
  try {
    const response = await axios.patch(`/api/accounts/users/${id}/`, changes)
    const index = users.value.findIndex(u => u.id === id)
    if (index !== -1) users.value[index] = { ...users.value[index], ...response.data }
  } catch (err) {
    error.value = authStore.apiErrorMessage(err, t('admin.users.updateError'))
  }
}

onMounted(load)
</script>

<style scoped>
.admin-table {
  background: transparent;
}

.admin-table th {
  @apply px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-cream-muted bg-cream/[0.03];
  border-color: rgba(244, 236, 225, 0.08);
}

.admin-table td {
  @apply px-4 py-3 text-sm text-cream/80;
  background: transparent;
  border-color: rgba(244, 236, 225, 0.08);
}
</style>
