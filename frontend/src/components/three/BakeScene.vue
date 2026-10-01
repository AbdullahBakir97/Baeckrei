<template>
  <div ref="container" class="bake-scene" aria-hidden="true"></div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import croissant from '@/assets/bakery/croissant-butter.png'
import { quality } from '@/three/quality'

// A croissant that goes through the bakery's steps as the page scrolls:
// pale dough (mix), rising (rest), turning (shape), turning golden with
// oven glow and steam (bake). `progress` runs from 0 to 1.
const props = defineProps({
  progress: { type: Number, default: 0 }
})
const emit = defineEmits(['ready', 'error'])

const container = ref(null)
let stage = null
let disposed = false
let target = 0

const clamp01 = (v) => Math.min(1, Math.max(0, v))
const phase = (p, from, to) => clamp01((p - from) / (to - from))
const smooth = (t) => t * t * (3 - 2 * t)

watch(() => props.progress, (value) => { target = value })

onMounted(async () => {
  target = props.progress
  try {
    const [{ createStage }, { buildSilhouetteMesh }, effects] = await Promise.all([
      import('@/three/stage'),
      import('@/three/silhouette'),
      import('@/three/effects')
    ])
    if (disposed) return
    const q = quality()
    stage = createStage(container.value, { fov: 30, cameraZ: 6.4, shadow: false, pixelRatio: q.pixelRatio })
    const { THREE, scene } = stage

    const glow = effects.createGlow({ color: '#ff9a4a', size: 5.5, opacity: 0 })
    glow.position.set(0, -0.2, -1.2)
    scene.add(glow)

    const mesh = await buildSilhouetteMesh(croissant, { depth: 0.34, maskSize: 220, textureSize: q.textureSize * 2 })
    if (disposed) return mesh.userData.dispose?.()
    const setBake = effects.makeBakeable(mesh)
    const holder = new THREE.Group()
    holder.add(mesh)
    scene.add(holder)

    const steam = q.steam ? effects.createSteam({ width: 1.3, height: 2.6 }) : null
    if (steam) {
      steam.position.set(0, 0.35, 0.2)
      scene.add(steam)
    }
    const dust = q.dust ? effects.createFlourDust({ count: Math.round(q.dust / 3), width: 6, height: 6, depth: 4 }) : null
    if (dust) scene.add(dust)

    // Warm oven light that rises during the bake step.
    const ovenLight = new THREE.PointLight('#ff8a3d', 0, 8)
    ovenLight.position.set(0, -1.6, 1.4)
    scene.add(ovenLight)

    let current = target
    stage.onTick((delta, time) => {
      current += (target - current) * (1 - Math.pow(0.0005, delta))
      const p = current
      const rise = smooth(phase(p, 0.2, 0.5))
      const turn = smooth(phase(p, 0.45, 0.75))
      const bake = smooth(phase(p, 0.68, 0.95))

      holder.scale.setScalar(0.72 + rise * 0.3)
      holder.position.y = Math.sin(time * 1.1) * 0.05 + rise * 0.05
      holder.rotation.set(
        -0.25 + Math.sin(time * 0.6) * 0.05,
        -0.9 + turn * 1.8 + Math.sin(time * 0.5) * 0.08,
        -0.12 + turn * 0.12
      )
      setBake(bake)
      glow.material.opacity = bake * 0.55
      glow.scale.setScalar(4.5 + bake * 1.5)
      ovenLight.intensity = bake * 18
      if (steam) steam.userData.strength = smooth(phase(p, 0.85, 1))
      steam?.userData.update(delta, time, stage.camera)
      dust?.userData.update(delta, time)
      if (dust) dust.material.opacity = 0.5 * (1 - bake)
    })
    emit('ready')
  } catch (err) {
    if (!disposed) emit('error', err)
  }
})

onBeforeUnmount(() => {
  disposed = true
  stage?.dispose()
  stage = null
})
</script>

<style scoped>
.bake-scene {
  position: absolute;
  inset: -12%;
}
</style>
