<template>
  <div ref="container" class="hero-scene" aria-hidden="true"></div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { gsap, ScrollTrigger, prefersReducedMotion, isCoarsePointer } from '@/motion'
import croissant from '@/assets/bakery/croissant-butter.png'
import pretzel from '@/assets/bakery/pretzel.png'
import donut from '@/assets/bakery/donut.png'
import macarons from '@/assets/bakery/macarons.png'
import cupcake from '@/assets/bakery/cupcake.png'
import cookie from '@/assets/bakery/cookie.png'
import eclair from '@/assets/bakery/eclair.png'

// Floating bakes in three depth layers. fx/fy place each one as a fraction
// of the visible half-width/half-height at its depth, so the composition
// holds at any screen size. `wide` is used for landscape screens,
// `tall` for phones.
const ITEMS = [
  { src: croissant, size: 2.6, z: 0.6, tilt: -0.25, wide: [0.42, 0.1], tall: [0.02, 0.5] },
  { src: pretzel, size: 1.7, z: -0.8, tilt: 0.2, wide: [0.8, -0.5], tall: [0.62, 0.62] },
  { src: donut, size: 1.35, z: 1.4, tilt: 0.35, wide: [0.18, -0.62], tall: [-0.64, 0.4] },
  { src: macarons, size: 1.5, z: -2.2, tilt: -0.1, wide: [0.86, 0.62], tall: [0.8, 0.32] },
  { src: cupcake, size: 1.2, z: -1.6, tilt: 0.12, wide: [0.14, 0.6], tall: [-0.72, 0.74] },
  { src: cookie, size: 1.1, z: -3.2, tilt: 0.4, wide: [-0.97, -0.9], tall: [-0.95, -0.95] },
  { src: eclair, size: 1.2, z: -3.8, tilt: -0.5, wide: [-0.98, 0.5], tall: [1, -0.72] }
]

const emit = defineEmits(['ready', 'error'])
const container = ref(null)

let stage = null
let trigger = null
let disposed = false
const items = []
const pointer = { x: 0, y: 0, sx: 0, sy: 0 }
let scroll = 0
let scrollSmooth = 0

const onPointer = (event) => {
  pointer.x = (event.clientX / window.innerWidth) * 2 - 1
  pointer.y = -((event.clientY / window.innerHeight) * 2 - 1)
}

function layout(item) {
  const { camera } = stage
  const tall = camera.aspect < 1.1
  const [fx, fy] = tall ? item.def.tall : item.def.wide
  const halfHeight = Math.tan((camera.fov * Math.PI) / 360) * (camera.position.z - item.def.z)
  const halfWidth = halfHeight * camera.aspect
  item.base.set(fx * halfWidth, fy * halfHeight, item.def.z)
  // Smaller bakes on phones so they frame the text instead of covering it.
  item.scale = (item.def.size / 2) * (tall ? 0.5 : 1)
}

async function build() {
  const [{ createStage }, { buildSilhouetteMesh }] = await Promise.all([
    import('@/three/stage'),
    import('@/three/silhouette')
  ])
  if (disposed) return
  stage = createStage(container.value, { fov: 35, cameraZ: 9, shadow: false, exposure: 1 })
  const { THREE, scene, camera } = stage
  const reduced = prefersReducedMotion()

  // Re-place the bakes when the canvas changes shape.
  let lastAspect = 0

  stage.onTick((delta, t) => {
    if (camera.aspect !== lastAspect) {
      lastAspect = camera.aspect
      items.forEach(layout)
    }
    const ease = 1 - Math.pow(0.001, delta)
    pointer.sx += (pointer.x - pointer.sx) * ease * 0.6
    pointer.sy += (pointer.y - pointer.sy) * ease * 0.6
    scrollSmooth += (scroll - scrollSmooth) * ease

    if (!reduced) {
      camera.position.x = pointer.sx * 0.45
      camera.position.y = pointer.sy * 0.3
      camera.lookAt(0, 0, 0)
    }

    for (const item of items) {
      const { mesh, base, phase } = item
      const bob = reduced ? 0 : Math.sin(t * 0.8 + phase) * 0.12
      // Scroll pushes every bake outwards and towards the viewer.
      const s = reduced ? 0 : scrollSmooth
      mesh.position.set(
        base.x + item.dir.x * s * 3,
        base.y + bob + item.dir.y * s * 3 + s * 1.5,
        base.z + s * 2.5
      )
      const intro = item.intro
      const sway = reduced ? 0 : Math.sin(t * 0.45 + phase) * 0.45
      mesh.rotation.set(
        (reduced ? 0 : Math.sin(t * 0.35 + phase) * 0.12) - pointer.sy * 0.25 + s * 0.8,
        sway + pointer.sx * 0.4 + (1 - intro) * 2.4 + s * 1.6 * item.dir.x,
        item.def.tilt + (reduced ? 0 : Math.sin(t * 0.25 + phase) * 0.06)
      )
      mesh.scale.setScalar(item.scale * (0.4 + 0.6 * intro) * Math.max(0.0001, intro))
    }
  })

  // Build one bake at a time so the page stays responsive.
  for (const [index, def] of ITEMS.entries()) {
    let mesh
    try {
      mesh = await buildSilhouetteMesh(def.src, { depth: 0.26, maskSize: 200, textureSize: 512 })
    } catch (err) {
      console.warn('Skipping hero item:', err.message)
      continue
    }
    if (disposed) {
      mesh.userData.dispose?.()
      return
    }
    mesh.castShadow = false
    const item = {
      def,
      mesh,
      base: new THREE.Vector3(),
      dir: new THREE.Vector2(),
      scale: 1,
      phase: index * 1.7,
      intro: reduced ? 1 : 0
    }
    layout(item)
    item.dir.set(item.base.x || 0.001, item.base.y || 0.001).normalize()
    scene.add(mesh)
    items.push(item)
    if (!reduced) gsap.to(item, { intro: 1, duration: 1.8, ease: 'expo.out' })
    if (items.length === 1) emit('ready')
    await new Promise((resolve) => setTimeout(resolve, 0))
  }
  if (!items.length) throw new Error('No hero items could be built')
}

onMounted(async () => {
  if (!prefersReducedMotion()) {
    if (!isCoarsePointer()) window.addEventListener('pointermove', onPointer, { passive: true })
    trigger = ScrollTrigger.create({
      trigger: container.value,
      start: 'top top',
      end: 'bottom top',
      onUpdate: (self) => { scroll = self.progress }
    })
  }
  try {
    await build()
  } catch (err) {
    if (!disposed) {
      console.warn('Hero 3D scene unavailable:', err.message)
      emit('error', err)
    }
  }
})

onBeforeUnmount(() => {
  disposed = true
  window.removeEventListener('pointermove', onPointer)
  trigger?.kill()
  gsap.killTweensOf(items)
  stage?.dispose()
  stage = null
  items.length = 0
})
</script>

<style scoped>
.hero-scene {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
</style>
