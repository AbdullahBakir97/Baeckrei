<template>
  <div class="viewer" :class="{ 'is-ready': status === 'ready' }" role="img" :aria-label="$t('viewer.label', { name: alt })">
    <!-- The photo stays visible until the 3D model is ready, and replaces it on failure. -->
    <img v-if="status !== 'ready'" :src="image || PLACEHOLDER_IMAGE" :alt="alt" class="viewer-fallback"
         :class="{ 'is-loading': status === 'loading' }" @error="applyImageFallback" />
    <div ref="container" class="viewer-canvas" aria-hidden="true"></div>

    <div v-if="status === 'loading'" class="viewer-status">
      <span class="viewer-spinner"></span> {{ $t('viewer.preparing') }}
    </div>
    <p v-if="status === 'ready' && showHint" class="viewer-hint">
      <font-awesome-icon icon="rotate" /> {{ $t('viewer.hint') }}
    </p>
    <button v-if="status === 'ready'" type="button" class="viewer-reset" :aria-label="$t('viewer.reset')" @click="resetView">
      <font-awesome-icon icon="rotate" />
    </button>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'
import { prefersReducedMotion } from '@/motion'
import { DRACO_PATH } from '@/three/draco'

const props = defineProps({
  image: { type: String, default: '' },
  // Optional real 3D model (.glb); used instead of the extruded photo.
  model: { type: String, default: '' },
  alt: { type: String, default: 'product' },
  autoRotate: { type: Boolean, default: true }
})
const emit = defineEmits(['ready', 'error'])

const container = ref(null)
const status = ref('loading')
const showHint = ref(true)
let stage = null
let controls = null
let object = null
let isModel = false

// Where the camera starts: a real model is seen a little from above, like a
// pastry on the counter; a photo silhouette faces the camera.
function homePosition() {
  const distance = 6.2
  const elevation = isModel ? 0.42 : 0
  return new stage.THREE.Vector3(0, Math.sin(elevation) * distance, Math.cos(elevation) * distance)
}

let disposed = false

async function build() {
  const [{ createStage, fitObject, webglAvailable }, { buildSilhouetteMesh }, { OrbitControls }] = await Promise.all([
    import('@/three/stage'),
    import('@/three/silhouette'),
    import('three/addons/controls/OrbitControls.js')
  ])
  if (disposed) return
  if (!webglAvailable()) throw new Error('WebGL is not available')

  stage = createStage(container.value, { fov: 30, cameraZ: 6.2 })
  const { THREE, scene, camera, renderer } = stage

  isModel = Boolean(props.model)
  if (isModel) {
    // Models optimized with `npm run optimize-model` use Draco compression;
    // the decoder is served by the shop itself (see vite.config.js).
    const [{ GLTFLoader }, { DRACOLoader }] = await Promise.all([
      import('three/addons/loaders/GLTFLoader.js'),
      import('three/addons/loaders/DRACOLoader.js')
    ])
    const draco = new DRACOLoader().setDecoderPath(DRACO_PATH)
    const gltf = await new GLTFLoader().setDRACOLoader(draco).loadAsync(props.model).finally(() => draco.dispose())
    object = new THREE.Group()
    gltf.scene.traverse((child) => { if (child.isMesh) child.castShadow = true })
    object.add(gltf.scene)
    fitObject(gltf.scene, 2.2)
  } else {
    object = new THREE.Group()
    const mesh = await buildSilhouetteMesh(props.image)
    mesh.scale.setScalar(1.05)
    object.add(mesh)
  }
  if (disposed) return
  scene.add(object)
  camera.position.copy(homePosition())

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08
  controls.enablePan = false
  controls.minDistance = 3.6
  controls.maxDistance = 9
  controls.minPolarAngle = Math.PI * 0.25
  controls.maxPolarAngle = Math.PI * 0.62
  if (!isModel) {
    // A photo has no back side worth showing; keep the turn in front.
    controls.minAzimuthAngle = -1.1
    controls.maxAzimuthAngle = 1.1
  }
  controls.autoRotate = isModel && props.autoRotate && !prefersReducedMotion()
  controls.autoRotateSpeed = 1.2

  let idleUntil = 0
  controls.addEventListener('start', () => {
    showHint.value = false
    idleUntil = Infinity
  })
  controls.addEventListener('end', () => { idleUntil = performance.now() + 3000 })

  const animate = !prefersReducedMotion() && props.autoRotate
  let sway = 0
  stage.onTick((delta, t) => {
    controls.update()
    if (!animate) return
    object.position.y = Math.sin(t * 1.3) * 0.06
    if (!isModel && performance.now() > idleUntil) {
      sway += delta
      object.rotation.y = Math.sin(sway * 0.7) * 0.5
      object.rotation.x = Math.sin(sway * 0.5) * 0.06
    }
  })

  status.value = 'ready'
  emit('ready')
}

function resetView() {
  if (!controls || !stage) return
  controls.reset()
  stage.camera.position.copy(homePosition())
  object?.rotation.set(0, 0, 0)
}

async function start() {
  status.value = 'loading'
  try {
    await build()
  } catch (err) {
    if (!disposed) {
      console.warn('3D view unavailable:', err.message)
      status.value = 'failed'
      emit('error', err)
    }
  }
}

function teardown() {
  controls?.dispose()
  stage?.dispose()
  controls = stage = object = null
}

onMounted(start)
onBeforeUnmount(() => {
  disposed = true
  teardown()
})

// Switching to another product reuses the component.
watch(() => [props.image, props.model], () => {
  teardown()
  disposed = false
  showHint.value = true
  start()
})
</script>

<style scoped>
.viewer {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 320px;
  overflow: hidden;
  border-radius: inherit;
  cursor: grab;
}

.viewer:active {
  cursor: grabbing;
}

.viewer-canvas {
  position: absolute;
  inset: 0;
}

.viewer-fallback {
  position: absolute;
  inset: 8%;
  width: 84%;
  height: 84%;
  object-fit: contain;
  transition: filter 0.4s, opacity 0.4s;
}

.viewer-fallback.is-loading {
  filter: blur(6px) saturate(0.8);
  opacity: 0.6;
}

.viewer-status,
.viewer-hint {
  position: absolute;
  inset-inline-end: 1rem;
  bottom: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.9rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  color: #f4ece1;
  background: rgba(14, 12, 10, 0.6);
  border: 1px solid rgba(244, 236, 225, 0.12);
  backdrop-filter: blur(10px);
  white-space: nowrap;
  pointer-events: none;
}

.viewer-hint {
  animation: hint-fade 6s forwards;
}

@media (max-width: 480px) {
  .viewer-hint {
    display: none;
  }
}

.viewer-spinner {
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 50%;
  border: 2px solid rgba(244, 236, 225, 0.25);
  border-top-color: #e6a15a;
  animation: spin 0.8s linear infinite;
}

.viewer-reset {
  position: absolute;
  top: 0.75rem;
  inset-inline-end: 0.75rem;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  color: #f4ece1;
  background: rgba(14, 12, 10, 0.55);
  border: 1px solid rgba(244, 236, 225, 0.12);
}

.viewer-reset:hover {
  background: rgba(14, 12, 10, 0.8);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes hint-fade {
  0%, 70% { opacity: 1; }
  100% { opacity: 0; }
}
</style>
