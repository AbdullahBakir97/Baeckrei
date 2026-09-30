<template>
  <span class="ar">
    <button type="button" class="ar-btn" :disabled="starting" @click="start">
      <font-awesome-icon :icon="starting ? 'spinner' : 'cube'" :spin="starting" />
      {{ $t('ar.view') }}
    </button>

    <Teleport to="body">
      <transition name="ar-fade">
        <div v-if="qr" class="ar-layer" role="dialog" aria-modal="true" :aria-label="$t('ar.view')" @click.self="close">
          <div class="ar-panel">
            <button ref="closeBtn" type="button" class="ar-close" :aria-label="$t('common.close')" @click="close">
              <font-awesome-icon icon="xmark" />
            </button>
            <p class="eyebrow">{{ $t('ar.eyebrow') }}</p>
            <h2 class="display-title text-4xl mt-2">{{ $t('ar.title', { name }) }}</h2>
            <img :src="qr" :alt="$t('ar.qrAlt')" class="ar-qr" width="220" height="220" />
            <p class="text-sm text-cream-muted">{{ $t(unsupported ? 'ar.unsupported' : 'ar.scan') }}</p>
          </div>
        </div>
      </transition>
    </Teleport>
  </span>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from 'vue'
import { isCoarsePointer } from '@/motion'
import { DRACO_PATH } from '@/three/draco'

// "View on your table": opens the product's .glb in augmented reality.
// Phones use their built-in viewer (Scene Viewer on Android, Quick Look on
// iPhone, via <model-viewer>); on a computer a QR code opens the page on a phone.
const props = defineProps({
  model: { type: String, required: true },
  name: { type: String, default: '' }
})

const starting = ref(false)
const qr = ref('')
const unsupported = ref(false)
const closeBtn = ref(null)
let viewer = null
let opener = null

const onKey = (e) => { if (e.key === 'Escape') close() }

function close() {
  qr.value = ''
  window.removeEventListener('keydown', onKey)
  opener?.focus()
}

async function showQr(notSupported = false) {
  const QRCode = await import('qrcode')
  unsupported.value = notSupported
  qr.value = await QRCode.toDataURL(window.location.href, {
    margin: 1,
    width: 440,
    color: { dark: '#0e0c0a', light: '#f4ece1' }
  })
  opener = document.activeElement
  window.addEventListener('keydown', onKey)
  await nextTick()
  closeBtn.value?.focus()
}

async function start() {
  if (!isCoarsePointer()) return showQr()
  starting.value = true
  try {
    // Decode Draco-compressed models with the shop's own copy of the decoder.
    window.ModelViewerElement = { ...window.ModelViewerElement, dracoDecoderLocation: DRACO_PATH }
    await import('@google/model-viewer')
    if (!viewer) {
      viewer = document.createElement('model-viewer')
      Object.assign(viewer, { src: props.model, alt: props.name })
      viewer.setAttribute('ar', '')
      viewer.setAttribute('ar-modes', 'webxr scene-viewer quick-look')
      viewer.setAttribute('ar-placement', 'floor')
      viewer.setAttribute('ar-scale', 'auto')
      viewer.setAttribute('aria-hidden', 'true')
      // It only needs to exist in the page to hand the model to the AR viewer.
      Object.assign(viewer.style, { position: 'fixed', width: '1px', height: '1px', opacity: '0', pointerEvents: 'none', bottom: '0' })
      document.body.appendChild(viewer)
      await new Promise((resolve, reject) => {
        viewer.addEventListener('load', resolve, { once: true })
        viewer.addEventListener('error', reject, { once: true })
        setTimeout(resolve, 8000)
      })
    }
    if (viewer.canActivateAR) viewer.activateAR()
    else await showQr(true)
  } catch {
    await showQr(true)
  } finally {
    starting.value = false
  }
}

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  viewer?.remove()
  viewer = null
})
</script>

<style scoped>
.ar {
  display: inline-block;
}

.ar-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #0e0c0a;
  background: #f4ece1;
  box-shadow: 0 12px 30px -12px rgba(0, 0, 0, 0.7);
  transition: background 0.3s, transform 0.4s var(--ease-out-expo);
}

.ar-btn:hover {
  background: #f2c48d;
  transform: translateY(-2px);
}

.ar-layer {
  position: fixed;
  inset: 0;
  z-index: 95;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(14, 12, 10, 0.7);
  backdrop-filter: blur(12px);
}

.ar-panel {
  position: relative;
  width: min(100%, 24rem);
  padding: 2rem;
  border-radius: 1.75rem;
  text-align: center;
  background: #1e1914;
  border: 1px solid rgba(244, 236, 225, 0.1);
  box-shadow: 0 40px 80px -30px rgba(0, 0, 0, 0.9);
}

.ar-panel .eyebrow {
  justify-content: center;
}

.ar-qr {
  width: 220px;
  height: 220px;
  margin: 1.5rem auto;
  border-radius: 1rem;
}

.ar-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  color: #b9ab98;
  background: rgba(244, 236, 225, 0.06);
}

.ar-fade-enter-active,
.ar-fade-leave-active {
  transition: opacity 0.3s;
}

.ar-fade-enter-from,
.ar-fade-leave-to {
  opacity: 0;
}
</style>
