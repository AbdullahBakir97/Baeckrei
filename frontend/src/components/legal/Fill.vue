<template>
  <span v-if="value">{{ value }}</span>
  <span v-else class="rounded bg-amber-500/15 px-1.5 py-0.5 text-amber-300 text-sm" :title="$t('legal.fillHint', { label })">
    {{ $t('legal.missing', { label }) }}
  </span>
</template>

<script setup>
// Shows a business detail, or a visible marker while it is still missing.
defineProps({
  value: { type: String, default: '' },
  label: { type: String, required: true }
})
</script>
