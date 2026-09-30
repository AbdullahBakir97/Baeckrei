// Shared Three.js setup: renderer, warm studio lighting, a soft contact
// shadow and a render loop that pauses when the canvas is off screen.
import * as THREE from 'three'
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js'

export { webglAvailable } from './webgl'

export function createStage(container, { fov = 32, cameraZ = 6, shadow = true, exposure = 1, pixelRatio = 2 } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, pixelRatio))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  // Neutral tone mapping keeps the photo colours true (ACES washes them out).
  renderer.toneMapping = THREE.NeutralToneMapping
  renderer.toneMappingExposure = exposure
  renderer.shadowMap.enabled = shadow
  renderer.shadowMap.type = THREE.PCFShadowMap
  renderer.domElement.style.display = 'block'
  renderer.domElement.style.width = '100%'
  renderer.domElement.style.height = '100%'
  container.appendChild(renderer.domElement)

  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(fov, 1, 0.1, 100)
  camera.position.set(0, 0, cameraZ)

  // Neutral studio reflections, warmed up by the lights below.
  const pmrem = new THREE.PMREMGenerator(renderer)
  const envTexture = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
  scene.environment = envTexture
  scene.environmentIntensity = 0.45

  const key = new THREE.DirectionalLight('#ffd6a3', 1.7)
  key.position.set(3, 4, 5)
  key.castShadow = shadow
  key.shadow.mapSize.set(1024, 1024)
  key.shadow.camera.near = 1
  key.shadow.camera.far = 20
  key.shadow.radius = 8
  key.shadow.bias = -0.0005
  scene.add(key)

  const rim = new THREE.DirectionalLight('#ff9a5c', 1.4)
  rim.position.set(-4, 2, -3)
  scene.add(rim)

  scene.add(new THREE.HemisphereLight('#fff1e0', '#2a1a10', 0.5))

  let ground = null
  if (shadow) {
    ground = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.ShadowMaterial({ opacity: 0.28 }))
    ground.rotation.x = -Math.PI / 2
    ground.position.y = -1.25
    ground.receiveShadow = true
    scene.add(ground)
  }

  const timer = new THREE.Timer()
  const tickers = new Set()
  let visible = true
  let frame = null

  const render = () => {
    frame = null
    if (!visible || document.hidden) return
    timer.update()
    const delta = Math.min(timer.getDelta(), 0.05)
    const elapsed = timer.getElapsed()
    tickers.forEach((fn) => fn(delta, elapsed))
    renderer.render(scene, camera)
    frame = requestAnimationFrame(render)
  }
  const start = () => { if (!frame) { timer.update(); frame = requestAnimationFrame(render) } }

  const resize = () => {
    const { width, height } = container.getBoundingClientRect()
    if (!width || !height) return
    renderer.setSize(width, height, false)
    camera.aspect = width / height
    camera.updateProjectionMatrix()
    renderer.render(scene, camera)
  }
  const resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(container)

  // Stop drawing while scrolled out of view or in a background tab.
  const io = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting
    if (visible) start()
  })
  io.observe(container)
  const onVisibility = () => { if (!document.hidden) start() }
  document.addEventListener('visibilitychange', onVisibility)

  resize()
  start()

  return {
    THREE,
    renderer,
    scene,
    camera,
    ground,
    onTick: (fn) => { tickers.add(fn); return () => tickers.delete(fn) },
    renderOnce: () => renderer.render(scene, camera),
    dispose() {
      if (frame) cancelAnimationFrame(frame)
      resizeObserver.disconnect()
      io.disconnect()
      document.removeEventListener('visibilitychange', onVisibility)
      scene.traverse((obj) => obj.userData.dispose?.())
      envTexture.dispose()
      pmrem.dispose()
      renderer.dispose()
      renderer.domElement.remove()
    }
  }
}

// Scale and centre any object so its largest side is `size` units.
export function fitObject(object, size = 2) {
  const box = new THREE.Box3().setFromObject(object)
  const dims = box.getSize(new THREE.Vector3())
  const scale = size / Math.max(dims.x, dims.y, dims.z || 0.0001)
  object.scale.multiplyScalar(scale)
  const centred = new THREE.Box3().setFromObject(object)
  object.position.sub(centred.getCenter(new THREE.Vector3()))
  return object
}
