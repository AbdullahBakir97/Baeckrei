<template>
  <div class="min-h-[70vh] flex items-center justify-center py-12 px-4">
    <div class="glass-panel w-full max-w-md space-y-6">
      <div class="text-center">
        <h1 class="display-title text-4xl sm:text-5xl">{{ title }}</h1>
        <p v-if="subtitle" class="mt-2 text-sm text-gray-400">{{ subtitle }}</p>
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
</script>
