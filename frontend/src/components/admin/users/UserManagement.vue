<template>
  <div class="space-y-6">
    <form class="flex flex-wrap items-end gap-3 bg-white rounded-lg shadow p-4" role="search" @submit.prevent="load">
      <div class="flex-1 min-w-[16rem]">
        <label for="user-search" class="block text-sm font-medium text-gray-700">Search</label>
        <input id="user-search" v-model.trim="search" type="search" placeholder="Name or email"
               class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white" />
      </div>
      <button type="submit" class="px-4 py-2 text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">Search</button>
    </form>

    <p v-if="error" class="rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{{ error }}</p>

    <div class="bg-white rounded-lg shadow overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 admin-table">
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">Email</th>
            <th scope="col">Joined</th>
            <th scope="col" class="text-right">Orders</th>
            <th scope="col">Account</th>
            <th scope="col"><span class="sr-only">Actions</span></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="loading"><td colspan="6" class="text-center text-gray-500">Loading users…</td></tr>
          <tr v-else-if="!users.length"><td colspan="6" class="text-center text-gray-500">No users found.</td></tr>
          <tr v-for="user in users" v-else :key="user.id">
            <td class="font-medium text-gray-900">{{ [user.first_name, user.last_name].filter(Boolean).join(' ') || '—' }}</td>
            <td class="max-w-[14rem] truncate" :title="user.email">{{ user.email }}</td>
            <td class="whitespace-nowrap" :title="`Last sign-in: ${user.last_login ? formatDate(user.last_login) : 'never'}`">
              {{ formatDate(user.date_joined) }}
            </td>
            <td class="text-right tabular-nums">{{ user.order_count ?? 0 }}</td>
            <td>
              <div class="flex flex-col items-start gap-1">
                <span class="px-2 py-0.5 text-xs font-medium rounded-full" :class="user.is_staff ? 'bg-indigo-100 text-indigo-800' : 'bg-gray-100 text-gray-700'">
                  {{ user.is_staff ? 'Admin' : 'Customer' }}
                </span>
                <span class="px-2 py-0.5 text-xs font-medium rounded-full" :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ user.is_active ? 'Active' : 'Deactivated' }}
                </span>
              </div>
            </td>
            <td class="text-right whitespace-nowrap"><div class="flex flex-col items-end gap-1">
              <template v-if="user.id !== currentUserId">
                <template v-if="pending?.id === user.id">
                  <span class="text-gray-600">{{ pending.question }}</span>
                  <button type="button" class="text-indigo-600 hover:text-indigo-900 bg-transparent font-medium" @click="confirmPending">Yes</button>
                  <button type="button" class="text-gray-600 bg-transparent" @click="pending = null">No</button>
                </template>
                <template v-else>
                  <button type="button" class="text-gray-700 hover:text-gray-900 bg-transparent"
                          @click="ask(user, { is_active: !user.is_active }, user.is_active ? 'Deactivate?' : 'Reactivate?')">
                    {{ user.is_active ? 'Deactivate' : 'Reactivate' }}
                  </button>
                  <button type="button" class="text-indigo-600 hover:text-indigo-900 bg-transparent"
                          @click="ask(user, { is_staff: !user.is_staff }, user.is_staff ? 'Remove admin rights?' : 'Make admin?')">
                    {{ user.is_staff ? 'Remove admin' : 'Make admin' }}
                  </button>
                </template>
              </template>
              <span v-else class="text-xs text-gray-400">You</span>
            </div></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '@/plugins/axios'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)
const users = ref([])
const search = ref('')
const loading = ref(false)
const error = ref('')
const pending = ref(null)

const formatDate = (value) => new Date(value).toLocaleDateString('de-DE')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/api/accounts/users/', { params: search.value ? { search: search.value } : {} })
    users.value = response.data
  } catch (err) {
    error.value = 'Users could not be loaded.'
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
    error.value = authStore.apiErrorMessage(err, 'The user could not be updated.')
  }
}

onMounted(load)
</script>

<style scoped>
.admin-table {
  background: white;
}

.admin-table th {
  @apply px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-600 bg-gray-50;
  border-color: #e5e7eb;
}

.admin-table td {
  @apply px-4 py-3 text-sm text-gray-700;
  background: white;
  border-color: #e5e7eb;
}
</style>
