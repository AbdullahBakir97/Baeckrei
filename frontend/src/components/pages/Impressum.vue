<template>
  <LegalPage title="Impressum">
    <p>{{ $t('legal.impressum.basis') }}</p>

    <h2>{{ $t('legal.impressum.provider') }}</h2>
    <p>
      <Fill :value="business.legalName || business.name" :label="$t('legal.fields.legalName')" /><br>
      <Fill :value="streetLine()" :label="$t('legal.fields.street')" /> <Fill v-if="!business.houseNumber" value="" :label="$t('legal.fields.houseNumber')" /><br>
      <Fill :value="business.postalCode" :label="$t('legal.fields.postalCode')" /> {{ business.city }}<br>
      {{ business.country }}
    </p>

    <h2>{{ $t('legal.impressum.represented') }}</h2>
    <p><Fill :value="business.owner" :label="$t('legal.fields.owner')" /></p>

    <h2>{{ $t('legal.impressum.contact') }}</h2>
    <p>
      {{ $t('common.phone') }}: <Fill :value="business.phone" :label="$t('legal.fields.phone')" /><br>
      {{ $t('common.email') }}: <Fill :value="business.email" :label="$t('legal.fields.email')" />
    </p>

    <template v-if="business.register">
      <h2>{{ $t('legal.impressum.register') }}</h2>
      <p>{{ business.register }}</p>
    </template>

    <h2>{{ $t('legal.impressum.vat') }}</h2>
    <p>
      {{ $t('legal.impressum.vatText') }}
      <Fill :value="business.vatId" :label="$t('legal.fields.vatId')" />
    </p>

    <h2>{{ $t('legal.impressum.dispute') }}</h2>
    <p>{{ $t('legal.impressum.disputeText') }}</p>
  </LegalPage>
</template>

<script setup>
import LegalPage from '@/components/legal/LegalPage.vue'
import Fill from '@/components/legal/Fill.vue'
import { business, streetLine } from '@/config/business'
</script>
