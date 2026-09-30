<template>
  <LegalPage title="Cookie Policy" updated="September 2026">
    <p>
      We do not use tracking or advertising cookies. We only store what the shop needs to work, so no
      consent banner is required.
    </p>

    <h2>Cookies</h2>
    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead><tr><th class="py-2 pr-4">Name</th><th class="py-2 pr-4">Purpose</th><th class="py-2">Kept for</th></tr></thead>
        <tbody>
          <tr><td class="py-2 pr-4 font-mono">sessionid</td><td class="py-2 pr-4">Remembers your shopping cart before you sign in</td><td class="py-2">2 weeks</td></tr>
          <tr><td class="py-2 pr-4 font-mono">csrftoken</td><td class="py-2 pr-4">Protects forms against cross-site request forgery</td><td class="py-2">1 year</td></tr>
        </tbody>
      </table>
    </div>

    <h2>Local storage in your browser</h2>
    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead><tr><th class="py-2 pr-4">Name</th><th class="py-2">Purpose</th></tr></thead>
        <tbody>
          <tr><td class="py-2 pr-4 font-mono">token</td><td class="py-2">Keeps you signed in; removed when you sign out</td></tr>
          <tr><td class="py-2 pr-4 font-mono">wishlist</td><td class="py-2">Products you saved to your wishlist</td></tr>
          <tr><td class="py-2 pr-4 font-mono">compare</td><td class="py-2">Products you chose to compare</td></tr>
        </tbody>
      </table>
    </div>

    <p>You can delete all of these at any time in your browser settings.</p>
  </LegalPage>
</template>

<script setup>
import LegalPage from '@/components/legal/LegalPage.vue'
</script>
