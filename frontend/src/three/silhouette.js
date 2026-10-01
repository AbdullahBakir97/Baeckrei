// Turn a transparent product photo (PNG cut-out) into a real 3D object:
// trace the outline of the largest opaque shape (keeping holes such as the
// ones in a pretzel), extrude it with a soft bevel and project the photo
// onto the front. The sides pick up the colour of the photo's edge pixels,
// which reads as crust.
import * as THREE from 'three'

const MASK_SIZE = 256 // resolution used for tracing the outline
const TEXTURE_SIZE = 1024 // resolution of the colour texture

export function loadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error(`Could not load ${url}`))
    img.src = url
  })
}

function drawScaled(img, maxSize) {
  const scale = Math.min(1, maxSize / Math.max(img.naturalWidth, img.naturalHeight))
  const canvas = document.createElement('canvas')
  canvas.width = Math.max(1, Math.round(img.naturalWidth * scale))
  canvas.height = Math.max(1, Math.round(img.naturalHeight * scale))
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
  return { canvas, ctx }
}

// Label 4-connected regions where test(i) is true; returns labels + sizes.
function label(w, h, test) {
  const labels = new Int32Array(w * h).fill(-1)
  const sizes = []
  const queue = new Int32Array(w * h)
  for (let start = 0; start < w * h; start++) {
    if (labels[start] !== -1 || !test(start)) continue
    const id = sizes.length
    let head = 0
    let tail = 0
    queue[tail++] = start
    labels[start] = id
    let size = 0
    while (head < tail) {
      const i = queue[head++]
      size++
      const x = i % w
      const neighbours = [x > 0 ? i - 1 : -1, x < w - 1 ? i + 1 : -1, i - w, i + w]
      for (const n of neighbours) {
        if (n < 0 || n >= w * h || labels[n] !== -1 || !test(n)) continue
        labels[n] = id
        queue[tail++] = n
      }
    }
    sizes.push(size)
  }
  return { labels, sizes }
}

// Moore-neighbour boundary tracing of a filled region (pixel centres).
const DIRS = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]]
function traceBoundary(inside, w, h) {
  let start = -1
  for (let i = 0; i < w * h; i++) if (inside[i]) { start = i; break }
  if (start < 0) return []
  const at = (x, y) => x >= 0 && y >= 0 && x < w && y < h && inside[y * w + x]
  let cx = start % w
  let cy = Math.floor(start / w)
  const sx = cx
  const sy = cy
  let back = 4 // we arrived from the west (raster scan)
  const points = [[cx, cy]]
  const limit = w * h * 4
  for (let step = 0; step < limit; step++) {
    let moved = false
    for (let k = 1; k <= 8; k++) {
      const d = (back + k) % 8
      const nx = cx + DIRS[d][0]
      const ny = cy + DIRS[d][1]
      if (!at(nx, ny)) continue
      // Jacob's stopping criterion: the loop is closed once we leave the
      // start pixel the same way we did the first time.
      if (cx === sx && cy === sy && points.length > 1 && nx === points[1][0] && ny === points[1][1]) return points
      const p = (back + k - 1) % 8
      const px = cx + DIRS[p][0] - nx
      const py = cy + DIRS[p][1] - ny
      back = DIRS.findIndex(([dx, dy]) => dx === px && dy === py)
      cx = nx
      cy = ny
      moved = true
      break
    }
    if (!moved) break
    if (!(cx === sx && cy === sy)) points.push([cx, cy])
  }
  return points
}

// Ramer–Douglas–Peucker line simplification.
function simplify(points, epsilon) {
  if (points.length < 3) return points
  const keep = new Uint8Array(points.length)
  keep[0] = keep[points.length - 1] = 1
  const stack = [[0, points.length - 1]]
  while (stack.length) {
    const [a, b] = stack.pop()
    const [ax, ay] = points[a]
    const [bx, by] = points[b]
    const len = Math.hypot(bx - ax, by - ay) || 1
    let max = 0
    let index = -1
    for (let i = a + 1; i < b; i++) {
      const [px, py] = points[i]
      const dist = Math.abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / len
      if (dist > max) { max = dist; index = i }
    }
    if (max > epsilon && index > 0) {
      keep[index] = 1
      stack.push([a, index], [index, b])
    }
  }
  return points.filter((_, i) => keep[i])
}

// One round of Chaikin corner cutting for a smoother outline.
function smooth(points) {
  const out = []
  for (let i = 0; i < points.length; i++) {
    const [x0, y0] = points[i]
    const [x1, y1] = points[(i + 1) % points.length]
    out.push([0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1], [0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1])
  }
  return out
}

// Drop points that sit almost on top of their neighbour and needle-sharp
// spikes: the bevel pushes such corners far inwards, which tears the cap.
function clean(points, minDistance = 1.5) {
  let out = points.filter((p, i) => {
    if (i === 0) return true
    const q = points[i - 1]
    return Math.hypot(p[0] - q[0], p[1] - q[1]) >= minDistance
  })
  for (let pass = 0; pass < 3; pass++) {
    const n = out.length
    if (n < 4) break
    out = out.filter((p, i) => {
      const a = out[(i - 1 + n) % n]
      const b = out[(i + 1) % n]
      const ux = p[0] - a[0], uy = p[1] - a[1]
      const vx = b[0] - p[0], vy = b[1] - p[1]
      const cos = (ux * vx + uy * vy) / ((Math.hypot(ux, uy) * Math.hypot(vx, vy)) || 1)
      return cos > -0.85 // keep unless the outline nearly doubles back
    })
  }
  return out
}

const outlineFrom = (mask, w, h) => clean(smooth(simplify(traceBoundary(mask, w, h), 0.9)))

function traceOutline(ctx, w, h) {
  const { data } = ctx.getImageData(0, 0, w, h)
  const opaque = (i) => data[i * 4 + 3] > 128

  // Largest opaque shape (drops crumbs, steam and stray pixels).
  const parts = label(w, h, opaque)
  if (!parts.sizes.length) throw new Error('The image has no opaque shape')
  const main = parts.sizes.indexOf(Math.max(...parts.sizes))
  const inShape = (i) => parts.labels[i] === main

  // Background reachable from the border; everything else is shape or hole.
  const outside = label(w, h, (i) => !inShape(i))
  const borderIds = new Set()
  for (let x = 0; x < w; x++) { borderIds.add(outside.labels[x]); borderIds.add(outside.labels[(h - 1) * w + x]) }
  for (let y = 0; y < h; y++) { borderIds.add(outside.labels[y * w]); borderIds.add(outside.labels[y * w + w - 1]) }

  const filled = new Uint8Array(w * h)
  for (let i = 0; i < w * h; i++) filled[i] = inShape(i) || !borderIds.has(outside.labels[i]) ? 1 : 0

  const shapeArea = parts.sizes[main]
  const holes = []
  outside.sizes.forEach((size, id) => {
    if (borderIds.has(id) || size < shapeArea * 0.004) return
    const hole = new Uint8Array(w * h)
    for (let i = 0; i < w * h; i++) hole[i] = outside.labels[i] === id ? 1 : 0
    holes.push(hole)
  })

  // Average colour along the edge, used behind the texture so bevels and
  // sides never sample transparent pixels.
  let r = 0, g = 0, b = 0, n = 0
  for (let i = 0; i < w * h; i++) {
    if (!inShape(i)) continue
    const x = i % w
    const edge = !inShape(i - 1) || !inShape(i + 1) || (x === 0) || !inShape(i - w) || !inShape(i + w)
    if (!edge) continue
    r += data[i * 4]; g += data[i * 4 + 1]; b += data[i * 4 + 2]; n++
  }
  // Slightly darker than the edge itself, so the sides read as crust.
  const shade = (v) => Math.round((v / n) * 0.78)
  const edgeColor = n ? `rgb(${shade(r)},${shade(g)},${shade(b)})` : '#6e4622'

  let minX = w, minY = h, maxX = 0, maxY = 0
  for (let i = 0; i < w * h; i++) {
    if (!filled[i]) continue
    const x = i % w
    const y = (i / w) | 0
    if (x < minX) minX = x
    if (x > maxX) maxX = x
    if (y < minY) minY = y
    if (y > maxY) maxY = y
  }

  const outline = outlineFrom(filled, w, h)
  const holeOutlines = holes
    .map((hole) => outlineFrom(hole, w, h))
    .filter((pts) => pts.length >= 6)

  return { outline, holeOutlines, edgeColor, bounds: { minX, minY, maxX, maxY } }
}

/**
 * Build an extruded mesh from a cut-out image URL.
 * Resolves to a THREE.Mesh roughly 2 units across, centred at the origin.
 */
export async function buildSilhouetteMesh(url, { depth = 0.22, maskSize = MASK_SIZE, textureSize = TEXTURE_SIZE } = {}) {
  const img = await loadImage(url)
  const mask = drawScaled(img, maskSize)
  const { width: w, height: h } = mask.canvas
  const { outline, holeOutlines, edgeColor, bounds } = traceOutline(mask.ctx, w, h)
  if (outline.length < 6) throw new Error('Could not trace the product outline')

  const cx = (bounds.minX + bounds.maxX) / 2
  const cy = (bounds.minY + bounds.maxY) / 2
  const half = Math.max(bounds.maxX - bounds.minX, bounds.maxY - bounds.minY) / 2 || 1
  const toWorld = ([x, y]) => new THREE.Vector2((x - cx) / half, -(y - cy) / half)

  const shape = new THREE.Shape(outline.map(toWorld))
  holeOutlines.forEach((pts) => shape.holes.push(new THREE.Path(pts.map(toWorld))))

  const bevel = depth * 0.35
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth,
    curveSegments: 1,
    bevelEnabled: true,
    bevelThickness: bevel,
    bevelSize: bevel * 0.7,
    bevelOffset: -bevel * 0.7,
    bevelSegments: 5
  })
  geometry.translate(0, 0, -depth / 2)

  // Planar projection of the photo from the front: every vertex samples the
  // pixel it sits in front of, so the sides take on the edge colours.
  const pos = geometry.attributes.position
  const uv = geometry.attributes.uv
  for (let i = 0; i < pos.count; i++) {
    const px = pos.getX(i) * half + cx
    const py = -pos.getY(i) * half + cy
    uv.setXY(i, (px + 0.5) / w, 1 - (py + 0.5) / h)
  }
  uv.needsUpdate = true
  geometry.computeVertexNormals()

  const tex = drawScaled(img, textureSize)
  const painted = document.createElement('canvas')
  painted.width = tex.canvas.width
  painted.height = tex.canvas.height
  const pctx = painted.getContext('2d')
  pctx.fillStyle = edgeColor
  pctx.fillRect(0, 0, painted.width, painted.height)
  pctx.drawImage(tex.canvas, 0, 0)

  const map = new THREE.CanvasTexture(painted)
  map.colorSpace = THREE.SRGBColorSpace
  map.anisotropy = 8

  const material = new THREE.MeshPhysicalMaterial({
    map,
    bumpMap: map,
    bumpScale: 1.2,
    roughness: 0.55,
    metalness: 0,
    clearcoat: 0.2,
    clearcoatRoughness: 0.5,
    sheen: 0.4,
    sheenColor: new THREE.Color('#ffd9a8')
  })

  const mesh = new THREE.Mesh(geometry, material)
  mesh.castShadow = true
  mesh.receiveShadow = false
  mesh.userData.dispose = () => {
    geometry.dispose()
    material.dispose()
    map.dispose()
  }
  return mesh
}
