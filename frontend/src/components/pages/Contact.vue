<template>
  <div class="section pb-10">
    <div>
      <PageHeader :eyebrow="$t('contact.eyebrow')" :title="$t('contact.title')" :subtitle="$t('contact.subtitle')" />

      <div class="grid lg:grid-cols-5 gap-6">
        <section class="glass-panel lg:col-span-3">
          <p v-if="sent" class="rounded-lg border border-green-500/30 bg-green-500/10 p-4 text-green-300" role="status">
            {{ sent }}
          </p>
          <form v-else class="grid sm:grid-cols-2 gap-4" novalidate @submit.prevent="submitForm">
            <div>
              <label for="contact-name" class="field-label">{{ $t('common.name') }}</label>
              <input id="contact-name" v-model.trim="form.name" class="field-input" autocomplete="name" required maxlength="100" />
              <p v-if="errors.name" class="field-error">{{ errors.name }}</p>
            </div>
            <div>
              <label for="contact-email" class="field-label">{{ $t('common.email') }}</label>
              <input id="contact-email" v-model.trim="form.email" type="email" class="field-input" autocomplete="email" required />
              <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
            </div>
            <div class="sm:col-span-2">
              <label for="contact-subject" class="field-label">{{ $t('contact.subject') }} <span class="text-gray-500">({{ $t('common.optional') }})</span></label>
              <input id="contact-subject" v-model.trim="form.subject" class="field-input" maxlength="150" />
            </div>
            <div class="sm:col-span-2">
              <label for="contact-message" class="field-label">{{ $t('contact.message') }}</label>
              <textarea id="contact-message" v-model.trim="form.message" rows="6" class="field-input" required maxlength="5000"></textarea>
              <p v-if="errors.message" class="field-error">{{ errors.message }}</p>
            </div>
            <!-- Hidden from people; bots tend to fill it in -->
            <div class="hidden" aria-hidden="true">
              <label for="contact-website">{{ $t('contact.website') }}</label>
              <input id="contact-website" v-model="form.website" tabindex="-1" autocomplete="off" />
            </div>
            <p v-if="errors.general" class="sm:col-span-2 field-error" role="alert">{{ errors.general }}</p>
            <div class="sm:col-span-2">
              <button type="submit" class="btn-amber" :disabled="sending">{{ sending ? $t('footer.sending') : $t('contact.send') }}</button>
            </div>
            <p class="sm:col-span-2 text-xs text-gray-500">
              {{ $t('contact.privacyNote') }} <router-link to="/privacy" class="underline hover:text-gray-300">{{ $t('footer.privacyPolicy') }}</router-link>.
            </p>
          </form>
        </section>

        <aside class="glass-panel lg:col-span-2 space-y-4 text-gray-300">
          <h2 class="display-title text-3xl">{{ $t('home.visitUs') }}</h2>
          <p class="flex gap-3">
            <font-awesome-icon icon="store" class="mt-1 text-amber-400" />
            <span>{{ business.name }}<br>{{ streetLine() }}<br>{{ cityLine() }}</span>
          </p>
          <p v-if="business.transit" class="flex gap-3">
            <font-awesome-icon icon="train-subway" class="mt-1 text-amber-400" />
            <span>{{ business.transit }}</span>
          </p>
          <p v-if="business.phone" class="flex gap-3">
            <font-awesome-icon icon="phone" class="mt-1 text-amber-400" />
            <span class="select-all">{{ business.phone }}</span>
          </p>
          <p v-if="business.email" class="flex gap-3">
            <font-awesome-icon icon="envelope" class="mt-1 text-amber-400" />
            <span class="select-all">{{ business.email }}</span>
          </p>
          <div v-if="business.openingHours.length">
            <h3 class="font-semibold text-white">{{ $t('contact.openingHours') }}</h3>
            <dl class="mt-2 grid grid-cols-2 gap-y-1">
              <template v-for="row in business.openingHours" :key="row.days">
                <dt>{{ row.days }}</dt><dd class="tabular-nums">{{ row.hours }}</dd>
              </template>
            </dl>
          </div>
          <a :href="mapUrl" target="_blank" rel="noopener" class="btn-ghost w-full">
            <font-awesome-icon icon="location-dot" /> {{ $t('contact.openMaps') }}
          </a>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from '@/plugins/axios'
import PageHeader from '@/components/common/PageHeader.vue'
import { business, streetLine, cityLine } from '@/config/business'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const form = reactive({ name: '', email: '', subject: '', message: '', website: '' })
const errors = reactive({})
const sending = ref(false)
const sent = ref('')

const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
  [business.name, streetLine(), cityLine()].filter(Boolean).join(', ')
)}`

function validate() {
  Object.keys(errors).forEach(key => delete errors[key])
  if (!form.name) errors.name = t('contact.errors.name')
  if (!/^\S+@\S+\.\S+$/.test(form.email)) errors.email = t('contact.errors.email')
  if (!form.message) errors.message = t('contact.errors.message')
  return !Object.keys(errors).length
}

async function submitForm() {
  if (!validate()) return
  sending.value = true
  try {
    const response = await axios.post('/api/content/contact/', { ...form })
    sent.value = response.data.message || t('contact.thanks')
  } catch (err) {
    const data = err.response?.data || {}
    if (err.response?.status === 429) errors.general = t('contact.tooMany')
    for (const key of ['name', 'email', 'message']) if (data[key]) errors[key] = [].concat(data[key])[0]
    if (!Object.keys(errors).length) errors.general = t('contact.failed')
  } finally {
    sending.value = false
  }
}
</script>
