<template>
  <LegalPage :title="$t('legal.cookies.title')" :updated="$t('legal.updatedDate')">
    <p>{{ $t('legal.cookies.intro') }}</p>

    <h2>{{ $t('legal.cookies.cookies') }}</h2>
    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead>
          <tr>
            <th class="py-2 pr-4">{{ $t('common.name') }}</th>
            <th class="py-2 pr-4">{{ $t('legal.cookies.purpose') }}</th>
            <th class="py-2">{{ $t('legal.cookies.keptFor') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr><td class="py-2 pr-4 font-mono">sessionid</td><td class="py-2 pr-4">{{ $t('legal.cookies.session') }}</td><td class="py-2">{{ $t('legal.cookies.twoWeeks') }}</td></tr>
          <tr><td class="py-2 pr-4 font-mono">csrftoken</td><td class="py-2 pr-4">{{ $t('legal.cookies.csrf') }}</td><td class="py-2">{{ $t('legal.cookies.oneYear') }}</td></tr>
        </tbody>
      </table>
    </div>

    <h2>{{ $t('legal.cookies.local') }}</h2>
    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead><tr><th class="py-2 pr-4">{{ $t('common.name') }}</th><th class="py-2">{{ $t('legal.cookies.purpose') }}</th></tr></thead>
        <tbody>
          <tr><td class="py-2 pr-4 font-mono">token</td><td class="py-2">{{ $t('legal.cookies.token') }}</td></tr>
          <tr><td class="py-2 pr-4 font-mono">wishlist</td><td class="py-2">{{ $t('legal.cookies.wishlist') }}</td></tr>
          <tr><td class="py-2 pr-4 font-mono">compare</td><td class="py-2">{{ $t('legal.cookies.compare') }}</td></tr>
          <tr><td class="py-2 pr-4 font-mono">locale</td><td class="py-2">{{ $t('legal.cookies.locale') }}</td></tr>
          <tr><td class="py-2 pr-4 font-mono">intro-seen</td><td class="py-2">{{ $t('legal.cookies.introSeen') }}</td></tr>
        </tbody>
      </table>
    </div>
    <p>{{ $t('legal.cookies.delete') }}</p>
  </LegalPage>
</template>

<script setup>
import LegalPage from '@/components/legal/LegalPage.vue'
</script>
