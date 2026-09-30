<template>
  <header class="mb-10">
    <p v-if="eyebrow" v-reveal class="eyebrow mb-3">
      <font-awesome-icon v-if="icon" :icon="icon" />{{ eyebrow }}
    </p>
    <h1 v-split class="display-title text-5xl sm:text-6xl">
      <font-awesome-icon v-if="icon && !eyebrow" :icon="icon" class="mr-2 align-[-0.05em] text-[0.7em] text-crust" />{{ title }}
    </h1>
    <p v-if="subtitle" v-reveal="{ delay: 0.15 }" class="mt-4 max-w-2xl text-lg text-cream-muted">{{ subtitle }}</p>
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
