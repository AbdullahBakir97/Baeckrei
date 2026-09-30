<template>
  <LegalPage title="Terms and Conditions" updated="September 2026">
    <h2>1. Scope</h2>
    <p>
      These terms apply to all orders placed in the online shop of {{ business.legalName || business.name }},
      {{ address }} ("we").
    </p>

    <h2>2. Placing an order</h2>
    <p>
      Products in the shop are an invitation to order. By clicking "Place order" you make a binding offer.
      The contract is formed when we confirm the order, at the latest when we hand over the goods.
    </p>

    <h2>3. Prices</h2>
    <p>All prices are in euros and include the statutory VAT. A delivery fee is shown at checkout before you order.</p>

    <h2>4. Pickup and delivery</h2>
    <p>
      You can pick up your order at our shop ({{ address }}, {{ business.transit }}) or have it delivered.
      A requested time is a preference; we will contact you if we cannot meet it.
    </p>

    <h2>5. Payment</h2>
    <p>You pay in cash or by card when you pick up or receive the order.</p>

    <h2 id="withdrawal">6. Cancellation and right of withdrawal</h2>
    <p>
      You can cancel an order free of charge in your account as long as it has not been prepared.
      Our products are fresh baked goods that spoil quickly; the statutory right of withdrawal therefore
      does not apply (§ 312g (2) no. 2 BGB).
    </p>

    <h2>7. Allergens</h2>
    <p>
      Ingredients and allergens are listed on each product page. If you have an allergy, please contact us
      before ordering.
    </p>

    <h2>8. Warranty</h2>
    <p>The statutory warranty rights apply. Please tell us about any problem with your order as soon as possible.</p>
  </LegalPage>
</template>

<script setup>
import LegalPage from '@/components/legal/LegalPage.vue'
import { business, streetLine, cityLine } from '@/config/business'

const address = [streetLine(), cityLine()].filter(Boolean).join(', ')
</script>
