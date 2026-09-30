// Atmosphere for the 3D scenes: flour dust drifting in warm light, steam
// rising from fresh bakes, a soft glow behind objects, and a "bake" control
// that turns a product from pale dough to golden crust.
import * as THREE from 'three'

function softDot(size = 64) {
  const canvas = document.createElement('canvas')
  canvas.width = canvas.height = size
  const ctx = canvas.getContext('2d')
  const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2)
  gradient.addColorStop(0, 'rgba(255,255,255,1)')
  gradient.addColorStop(0.4, 'rgba(255,255,255,0.35)')
  gradient.addColorStop(1, 'rgba(255,255,255,0)')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, size, size)
  const texture = new THREE.CanvasTexture(canvas)
  texture.colorSpace = THREE.SRGBColorSpace
  return texture
}

/** Flour dust: specks drifting slowly upwards and sideways. */
export function createFlourDust({ count = 300, width = 16, height = 10, depth = 8 } = {}) {
  const positions = new Float32Array(count * 3)
  const seeds = new Float32Array(count)
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * width
    positions[i * 3 + 1] = (Math.random() - 0.5) * height
    positions[i * 3 + 2] = (Math.random() - 0.5) * depth - 1
    seeds[i] = Math.random() * 100
  }
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const texture = softDot()
  const material = new THREE.PointsMaterial({
    map: texture,
    size: 0.06,
    color: '#ffe2bd',
    transparent: true,
    opacity: 0.55,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    sizeAttenuation: true
  })
  const points = new THREE.Points(geometry, material)
  points.userData.dispose = () => { geometry.dispose(); material.dispose(); texture.dispose() }
  points.userData.update = (delta, time) => {
    const pos = geometry.attributes.position
    for (let i = 0; i < count; i++) {
      let y = pos.getY(i) + delta * (0.08 + (seeds[i] % 1) * 0.12)
      if (y > height / 2) y = -height / 2
      pos.setY(i, y)
      pos.setX(i, pos.getX(i) + Math.sin(time * 0.3 + seeds[i]) * delta * 0.05)
    }
    pos.needsUpdate = true
  }
  return points
}

const steamVertex = /* glsl */`
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`

const steamFragment = /* glsl */`
  uniform float uTime;
  uniform float uSeed;
  uniform float uStrength;
  varying vec2 vUv;

  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
  }
  float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.0; a *= 0.5; }
    return v;
  }

  void main() {
    vec2 uv = vUv;
    // Wisps sway as they rise and thin out towards the top.
    float sway = sin(uv.y * 4.0 + uTime * 0.8 + uSeed) * 0.08 * uv.y;
    float column = 1.0 - smoothstep(0.08, 0.45, abs(uv.x - 0.5 - sway));
    float wisp = fbm(vec2(uv.x * 3.0 + uSeed, uv.y * 2.5 - uTime * 0.35));
    float fade = smoothstep(0.0, 0.25, uv.y) * (1.0 - smoothstep(0.55, 1.0, uv.y));
    float alpha = column * smoothstep(0.35, 0.85, wisp) * fade * uStrength;
    gl_FragColor = vec4(vec3(1.0, 0.95, 0.88), alpha * 0.35);
  }
`

/** Steam: soft wisps rising from a point. Returns a group; set .userData.strength. */
export function createSteam({ width = 1.2, height = 2.4, wisps = 3 } = {}) {
  const group = new THREE.Group()
  const materials = []
  const geometry = new THREE.PlaneGeometry(width, height)
  geometry.translate(0, height / 2, 0)
  for (let i = 0; i < wisps; i++) {
    const material = new THREE.ShaderMaterial({
      vertexShader: steamVertex,
      fragmentShader: steamFragment,
      uniforms: { uTime: { value: 0 }, uSeed: { value: i * 3.7 }, uStrength: { value: 1 } },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    })
    const plane = new THREE.Mesh(geometry, material)
    plane.position.x = (i - (wisps - 1) / 2) * width * 0.35
    plane.scale.setScalar(0.8 + i * 0.15)
    group.add(plane)
    materials.push(material)
  }
  group.userData.strength = 1
  group.userData.update = (delta, time, camera) => {
    materials.forEach((m) => {
      m.uniforms.uTime.value = time
      m.uniforms.uStrength.value = group.userData.strength
    })
    // Always face the camera.
    if (camera) group.quaternion.copy(camera.quaternion)
  }
  group.userData.dispose = () => { geometry.dispose(); materials.forEach(m => m.dispose()) }
  return group
}

/** A warm glow sprite, drawn additively behind an object. */
export function createGlow({ color = '#ffb070', size = 4, opacity = 0.5 } = {}) {
  const texture = softDot(128)
  const material = new THREE.SpriteMaterial({
    map: texture, color, transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending
  })
  const sprite = new THREE.Sprite(material)
  sprite.scale.setScalar(size)
  sprite.userData.dispose = () => { material.dispose(); texture.dispose() }
  return sprite
}

/**
 * Lets a silhouette mesh (see silhouette.js) be "baked": at bake 0 it looks
 * like pale raw dough, at 1 it shows the real golden photo. Returns a setter.
 */
export function makeBakeable(mesh) {
  const uniforms = { uBake: { value: 1 } }
  mesh.material.onBeforeCompile = (shader) => {
    shader.uniforms.uBake = uniforms.uBake
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform float uBake;')
      .replace('#include <map_fragment>', `#include <map_fragment>
        float bakeLuma = dot(diffuseColor.rgb, vec3(0.299, 0.587, 0.114));
        vec3 dough = vec3(0.96, 0.88, 0.74) * (0.7 + 0.45 * bakeLuma);
        diffuseColor.rgb = mix(dough, diffuseColor.rgb, uBake);`)
  }
  mesh.material.needsUpdate = true
  return (value) => { uniforms.uBake.value = value }
}
