<template>
  <div class="mb-8">
    <h1 class="text-4xl font-extrabold text-white flex items-center gap-3">
      <font-awesome-icon v-if="icon" :icon="icon" class="text-amber-500/90" />
      {{ title }}
    </h1>
    <p v-if="subtitle" class="mt-2 text-gray-400">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  icon: { type: String, default: '' }
})
</script>
