<template>
  <LegalPage title="Impressum">
    <p>Information according to § 5 DDG (Digitale-Dienste-Gesetz).</p>

    <h2>Provider</h2>
    <p>
      <Fill :value="business.legalName || business.name" label="legal name" /><br>
      <Fill :value="streetLine()" label="street" /> <Fill v-if="!business.houseNumber" value="" label="house number" /><br>
      <Fill :value="business.postalCode" label="postal code" /> {{ business.city }}<br>
      {{ business.country }}
    </p>

    <h2>Represented by</h2>
    <p><Fill :value="business.owner" label="owner or managing director" /></p>

    <h2>Contact</h2>
    <p>
      Phone: <Fill :value="business.phone" label="phone number" /><br>
      Email: <Fill :value="business.email" label="email address" />
    </p>

    <template v-if="business.register">
      <h2>Commercial register</h2>
      <p>{{ business.register }}</p>
    </template>

    <h2>VAT ID</h2>
    <p>
      VAT identification number according to § 27a UStG:
      <Fill :value="business.vatId" label="VAT ID (if you have one)" />
    </p>

    <h2>Consumer dispute resolution</h2>
    <p>
      We are neither willing nor obliged to take part in dispute resolution proceedings before a consumer
      arbitration board.
    </p>
  </LegalPage>
</template>

<script setup>
import LegalPage from '@/components/legal/LegalPage.vue'
import Fill from '@/components/legal/Fill.vue'
import { business, streetLine } from '@/config/business'
</script>
