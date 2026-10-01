<template>
  <div class="min-h-[60vh] flex items-center justify-center py-16 px-4">
    <div class="glass-panel max-w-lg w-full text-center">
      <p class="text-6xl font-extrabold text-amber-400">404</p>
      <h1 class="mt-4 text-2xl font-bold text-white">Page not found</h1>
      <p class="mt-2 text-gray-400">
        We couldn't find <span class="font-mono text-gray-300 break-all">{{ route.fullPath }}</span>.
        Maybe it was moved, or the link is out of date.
      </p>
      <form class="mt-6 flex gap-2" role="search" @submit.prevent="search">
        <label for="not-found-search" class="sr-only">Search products</label>
        <input id="not-found-search" v-model.trim="query" class="field-input" placeholder="Search products…" />
        <button type="submit" class="btn-amber px-4 py-2">Search</button>
      </form>
      <div class="mt-6 flex flex-wrap justify-center gap-3">
        <router-link to="/products" class="btn-ghost">Browse products</router-link>
        <router-link to="/contact" class="btn-ghost">Contact us</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const query = ref('')

const search = () => {
  if (query.value) router.push({ name: 'products', query: { search: query.value } })
}
</script>
