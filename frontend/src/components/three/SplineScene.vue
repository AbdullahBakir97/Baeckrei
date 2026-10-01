<template>
  <div class="spline" :class="{ 'is-ready': ready }">
    <canvas ref="canvas" :aria-label="label" role="img"></canvas>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

// Renders a scene made in the Spline editor (Export > Code > .splinecode URL).
const props = defineProps({
  scene: { type: String, required: true },
  label: { type: String, default: '3D scene' }
})
const emit = defineEmits(['ready', 'error'])

const canvas = ref(null)
const ready = ref(false)
let app = null
let disposed = false

onMounted(async () => {
  try {
    const { Application } = await import('@splinetool/runtime')
    if (disposed) return
    app = new Application(canvas.value, { htmlContentMode: 'none' })
    await app.load(props.scene)
    if (disposed) return
    ready.value = true
    emit('ready', app)
  } catch (err) {
    if (!disposed) {
      console.warn('Spline scene unavailable:', err?.message || err)
      emit('error', err)
    }
  }
})

onBeforeUnmount(() => {
  disposed = true
  app?.dispose()
  app = null
})
</script>

<style scoped>
.spline {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 1s ease;
}

.spline.is-ready {
  opacity: 1;
}

.spline canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}
</style>
