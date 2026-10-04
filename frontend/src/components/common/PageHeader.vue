<template>
  <header class="mb-12">
    <p v-if="eyebrow || icon" v-reveal class="eyebrow mb-4">
      <font-awesome-icon v-if="icon" :icon="icon" />{{ eyebrow }}
    </p>
    <h1 v-split.load class="display-title text-6xl sm:text-8xl">{{ title }}</h1>
    <p v-if="subtitle" v-reveal="{ delay: 0.2 }" class="mt-5 max-w-2xl text-lg text-cream-muted text-auto">{{ subtitle }}</p>
  </header>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: '' },
  eyebrow: { type: String, default: '' }
})
</script>
