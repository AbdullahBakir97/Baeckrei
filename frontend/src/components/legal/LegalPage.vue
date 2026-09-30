<template>
  <div class="min-h-screen py-12 px-4">
    <article class="max-w-3xl mx-auto glass-panel">
      <h1 class="display-title text-5xl sm:text-6xl">{{ title }}</h1>
      <p v-if="updated" class="mt-1 text-sm text-gray-500">Last updated: {{ updated }}</p>
      <div class="prose-dark mt-6">
        <slot />
      </div>
    </article>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  updated: { type: String, default: '' }
})
</script>
