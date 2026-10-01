<template>
  <div v-if="enabled" class="cursor" aria-hidden="true">
    <div ref="ring" class="cursor-ring" :class="{ 'is-hover': hovering, 'has-label': label, 'is-down': pressed }">
      <span class="cursor-label">{{ label }}</span>
    </div>
    <div ref="dot" class="cursor-dot"></div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { gsap, isCoarsePointer, prefersReducedMotion } from '@/motion'

// A soft ring that trails the pointer. It grows over links and buttons, and
// shows a word over elements with data-cursor (e.g. data-cursor="view").
// The normal cursor stays visible; this only adds to it.
const { t } = useI18n()
const enabled = ref(false)
const ring = ref(null)
const dot = ref(null)
const hovering = ref(false)
const label = ref('')
const pressed = ref(false)

// A new page starts with a plain ring until the pointer moves again.
const route = useRoute()
watch(() => route.fullPath, () => { hovering.value = false; label.value = '' })

let ringX, ringY, dotX, dotY

const interactive = 'a, button, [role="button"], input, select, textarea, label, summary, [data-cursor]'

function onMove(event) {
  ringX(event.clientX)
  ringY(event.clientY)
  dotX(event.clientX)
  dotY(event.clientY)
  const target = event.target.closest?.(interactive)
  hovering.value = Boolean(target)
  const word = target?.closest('[data-cursor]')?.dataset.cursor
  label.value = word ? t(`cursor.${word}`) : ''
}

const onDown = () => { pressed.value = true }
const onUp = () => { pressed.value = false }
const onLeave = () => gsap.to([ring.value, dot.value], { opacity: 0, duration: 0.3 })
const onEnter = () => gsap.to([ring.value, dot.value], { opacity: 1, duration: 0.3 })

onMounted(async () => {
  if (isCoarsePointer() || prefersReducedMotion()) return
  enabled.value = true
  await nextTick()
  ringX = gsap.quickTo(ring.value, 'x', { duration: 0.45, ease: 'power3.out' })
  ringY = gsap.quickTo(ring.value, 'y', { duration: 0.45, ease: 'power3.out' })
  dotX = gsap.quickTo(dot.value, 'x', { duration: 0.08, ease: 'power3.out' })
  dotY = gsap.quickTo(dot.value, 'y', { duration: 0.08, ease: 'power3.out' })
  window.addEventListener('pointermove', onMove, { passive: true })
  window.addEventListener('pointerdown', onDown)
  window.addEventListener('pointerup', onUp)
  document.documentElement.addEventListener('pointerleave', onLeave)
  document.documentElement.addEventListener('pointerenter', onEnter)
})

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', onMove)
  window.removeEventListener('pointerdown', onDown)
  window.removeEventListener('pointerup', onUp)
  document.documentElement.removeEventListener('pointerleave', onLeave)
  document.documentElement.removeEventListener('pointerenter', onEnter)
})
</script>

<style scoped>
.cursor {
  position: fixed;
  inset: 0;
  z-index: 90;
  pointer-events: none;
}

.cursor-ring,
.cursor-dot {
  position: fixed;
  top: 0;
  left: 0;
  border-radius: 9999px;
  pointer-events: none;
}

.cursor-ring {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  margin: -1.125rem 0 0 -1.125rem;
  border: 1px solid rgba(242, 196, 141, 0.55);
  transition: width 0.35s var(--ease-out-expo), height 0.35s var(--ease-out-expo), margin 0.35s var(--ease-out-expo),
    background 0.3s, border-color 0.3s;
}

.cursor-ring.is-hover {
  width: 3.5rem;
  height: 3.5rem;
  margin: -1.75rem 0 0 -1.75rem;
  background: rgba(230, 161, 90, 0.08);
  border-color: rgba(242, 196, 141, 0.8);
}

.cursor-ring.has-label {
  width: 5.5rem;
  height: 5.5rem;
  margin: -2.75rem 0 0 -2.75rem;
  background: #e6a15a;
  border-color: transparent;
}

.cursor-ring.is-down {
  scale: 0.85;
}

.cursor-label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #0e0c0a;
  opacity: 0;
  transition: opacity 0.2s;
}

.has-label .cursor-label {
  opacity: 1;
}

.cursor-dot {
  width: 0.35rem;
  height: 0.35rem;
  margin: -0.175rem 0 0 -0.175rem;
  background: #e6a15a;
}

.has-label ~ .cursor-dot {
  opacity: 0;
}
</style>
