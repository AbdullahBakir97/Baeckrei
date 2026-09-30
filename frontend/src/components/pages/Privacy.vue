<template>
  <LegalPage title="Privacy Policy" updated="September 2026">
    <h2>Who is responsible</h2>
    <p>
      {{ business.legalName || business.name }}, {{ address }}.
      Email: <Fill :value="business.email" label="email address" />.
      See the <router-link to="/impressum">Impressum</router-link> for full contact details.
    </p>

    <h2>What we collect and why</h2>
    <ul class="list-disc pl-6 space-y-2">
      <li>
        <strong class="text-white">Your account</strong>: email address, name, phone number (optional) and a
        securely hashed password, so you can sign in and see your orders (Art. 6(1)(b) GDPR).
      </li>
      <li>
        <strong class="text-white">Orders</strong>: the products you order, pickup or delivery choice,
        delivery address, preferred time, notes and payment method, so we can prepare and hand over your
        order and meet our bookkeeping obligations (Art. 6(1)(b) and (c) GDPR).
      </li>
      <li>
        <strong class="text-white">Saved addresses</strong>: delivery addresses you choose to keep in your
        account (Art. 6(1)(b) GDPR). You can delete them at any time in your settings.
      </li>
      <li>
        <strong class="text-white">Contact form and newsletter</strong>: your name, email address and message
        when you write to us, and your email address if you subscribe to our newsletter (Art. 6(1)(a) and (b)
        GDPR). You can unsubscribe at any time.
      </li>
      <li>
        <strong class="text-white">Technical data</strong>: the server logs the IP address and time of requests
        to keep the shop secure (Art. 6(1)(f) GDPR).
      </li>
    </ul>

    <h2>Payment</h2>
    <p>
      You pay in cash or by card when you pick up or receive your order. We do not store card details.
    </p>

    <h2>How long we keep data</h2>
    <p>
      Account data is kept until you delete your account. Order records are kept for as long as tax and
      commercial law requires (usually up to 10 years). Contact messages are deleted once they are dealt with.
    </p>

    <h2>Cookies and local storage</h2>
    <p>
      We only use what is needed for the shop to work. Details are in our
      <router-link to="/cookie-policy">cookie policy</router-link>.
    </p>

    <h2>Your rights</h2>
    <p>
      You have the right to access, correct and delete your data, to restrict or object to its processing,
      to data portability and to withdraw consent at any time. You can also complain to a data protection
      supervisory authority, for example the Berlin Commissioner for Data Protection and Freedom of Information.
    </p>
  </LegalPage>
</template>

<script setup>
import LegalPage from '@/components/legal/LegalPage.vue'
import Fill from '@/components/legal/Fill.vue'
import { business, streetLine, cityLine } from '@/config/business'

const address = [streetLine(), cityLine()].filter(Boolean).join(', ')
</script>
