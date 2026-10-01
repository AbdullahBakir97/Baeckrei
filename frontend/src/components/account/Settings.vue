<template>
  <div class="section max-w-3xl pb-10">
    <div class="space-y-6">
      <PageHeader :eyebrow="$t('account.eyebrow')" :title="$t('account.settingsTitle')" :subtitle="$t('account.settingsSubtitle')" />

      <!-- Password -->
      <section class="glass-panel">
        <h2 class="display-title text-3xl">{{ $t('account.changePassword') }}</h2>
        <form class="mt-4 grid gap-4" @submit.prevent="changePassword">
          <div>
            <label for="old_password" class="field-label">{{ $t('account.currentPassword') }}</label>
            <input id="old_password" v-model="passwords.old_password" type="password" class="field-input" autocomplete="current-password" required />
          </div>
          <div class="grid sm:grid-cols-2 gap-4">
            <div>
              <label for="new_password" class="field-label">{{ $t('account.newPassword') }}</label>
              <input id="new_password" v-model="passwords.new_password" type="password" class="field-input" autocomplete="new-password" required minlength="8" />
            </div>
            <div>
              <label for="confirm_password" class="field-label">{{ $t('account.repeatPassword') }}</label>
              <input id="confirm_password" v-model="passwords.confirm" type="password" class="field-input" autocomplete="new-password" required />
            </div>
          </div>
          <p class="text-sm text-gray-500">{{ $t('auth.passwordRules') }}</p>
          <p v-if="passwordError" class="field-error" role="alert">{{ passwordError }}</p>
          <div>
            <button type="submit" class="btn-amber" :disabled="changingPassword">
              {{ changingPassword ? $t('common.saving') : $t('account.changePassword') }}
            </button>
          </div>
        </form>
      </section>

      <!-- Addresses -->
      <section class="glass-panel">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <h2 class="display-title text-3xl">{{ $t('account.savedAddresses') }}</h2>
          <button v-if="!editingAddress" type="button" class="btn-ghost" @click="editAddress()">
            <font-awesome-icon icon="plus" /> {{ $t('account.addAddress') }}
          </button>
        </div>

        <form v-if="editingAddress" class="mt-4 grid sm:grid-cols-6 gap-4" @submit.prevent="saveAddress">
          <div class="sm:col-span-6">
            <label for="addr_line_1" class="field-label">{{ $t('address.street') }}</label>
            <input id="addr_line_1" v-model.trim="editingAddress.address_line_1" class="field-input" autocomplete="address-line1" required />
          </div>
          <div class="sm:col-span-6">
            <label for="addr_line_2" class="field-label">{{ $t('address.line2') }} <span class="text-gray-500">({{ $t('common.optional') }})</span></label>
            <input id="addr_line_2" v-model.trim="editingAddress.address_line_2" class="field-input" autocomplete="address-line2" />
          </div>
          <div class="sm:col-span-2">
            <label for="addr_postal" class="field-label">{{ $t('address.postalCode') }}</label>
            <input id="addr_postal" v-model.trim="editingAddress.postal_code" class="field-input" autocomplete="postal-code" required />
          </div>
          <div class="sm:col-span-4">
            <label for="addr_city" class="field-label">{{ $t('address.city') }}</label>
            <input id="addr_city" v-model.trim="editingAddress.city" class="field-input" autocomplete="address-level2" required />
          </div>
          <p v-if="addressError" class="sm:col-span-6 field-error" role="alert">{{ addressError }}</p>
          <div class="sm:col-span-6 flex gap-3">
            <button type="submit" class="btn-amber" :disabled="savingAddress">{{ savingAddress ? $t('common.saving') : $t('account.saveAddress') }}</button>
            <button type="button" class="btn-ghost" @click="editingAddress = null">{{ $t('common.cancel') }}</button>
          </div>
        </form>

        <p v-if="!addressStore.addresses.length && !editingAddress" class="mt-4 text-gray-400">
          {{ $t('account.noAddresses') }}
        </p>
        <ul class="mt-4 grid gap-3">
          <li v-for="address in addressStore.addresses" :key="address.id"
              class="flex flex-wrap items-start justify-between gap-3 rounded-xl border border-white/10 p-4">
            <p class="text-gray-200">
              {{ address.address_line_1 }}<br>
              <template v-if="address.address_line_2">{{ address.address_line_2 }}<br></template>
              {{ address.postal_code }} {{ address.city }}
            </p>
            <div class="flex gap-2">
              <template v-if="confirmDeleteId === address.id">
                <button type="button" class="btn-ghost text-red-300" @click="removeAddress(address.id)">{{ $t('common.delete') }}</button>
                <button type="button" class="btn-ghost" @click="confirmDeleteId = null">{{ $t('account.keep') }}</button>
              </template>
              <template v-else>
                <button type="button" class="btn-ghost" @click="editAddress(address)">{{ $t('common.edit') }}</button>
                <button type="button" class="btn-ghost text-red-300" @click="confirmDeleteId = address.id">{{ $t('common.delete') }}</button>
              </template>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useAuthStore } from '@/stores/authStore'
import { useAddressStore } from '@/stores/addressStore'
import { useToast } from '@/composables/useToast'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const addressStore = useAddressStore()
const { showToast } = useToast()
const { t } = useI18n()

const passwords = reactive({ old_password: '', new_password: '', confirm: '' })
const passwordError = ref('')
const changingPassword = ref(false)

async function changePassword() {
  passwordError.value = ''
  if (passwords.new_password !== passwords.confirm) {
    passwordError.value = t('account.passwordMismatch')
    return
  }
  changingPassword.value = true
  try {
    await authStore.changePassword({ old_password: passwords.old_password, new_password: passwords.new_password })
    Object.assign(passwords, { old_password: '', new_password: '', confirm: '' })
    showToast(t('account.passwordChanged'))
  } catch (err) {
    passwordError.value = authStore.error
  } finally {
    changingPassword.value = false
  }
}

const editingAddress = ref(null)
const addressError = ref('')
const savingAddress = ref(false)
const confirmDeleteId = ref(null)

function editAddress(address) {
  addressError.value = ''
  editingAddress.value = address
    ? { ...address }
    : { address_line_1: '', address_line_2: '', postal_code: '', city: 'Berlin', country: 'DE' }
}

async function saveAddress() {
  savingAddress.value = true
  addressError.value = ''
  try {
    await addressStore.saveAddress(editingAddress.value)
    editingAddress.value = null
    showToast(t('account.addressSaved'))
  } catch (err) {
    addressError.value = authStore.apiErrorMessage(err, t('account.addressSaveFailed'))
  } finally {
    savingAddress.value = false
  }
}

async function removeAddress(id) {
  try {
    await addressStore.deleteAddress(id)
    showToast(t('account.addressDeleted'))
  } catch (err) {
    showToast(t('account.addressDeleteFailed'), 'error')
  } finally {
    confirmDeleteId.value = null
  }
}

onMounted(() => {
  addressStore.fetchAddresses().catch(() => showToast(t('account.addressesLoadFailed'), 'error'))
})
</script>
