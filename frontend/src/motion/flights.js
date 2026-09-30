import { gsap, prefersReducedMotion } from './index'

// Small "flying image" effects: a picture leaves one place on the page and
// lands in another. Each flight is a fixed-position copy of the image, so
// the real layout never moves.

function makeClone(img, rect) {
  const clone = img.cloneNode(false)
  clone.removeAttribute('id')
  clone.removeAttribute('loading')
  clone.setAttribute('aria-hidden', 'true')
  Object.assign(clone.style, {
    position: 'fixed',
    left: `${rect.left}px`,
    top: `${rect.top}px`,
    width: `${rect.width}px`,
    height: `${rect.height}px`,
    margin: '0',
    objectFit: 'contain',
    zIndex: '80',
    pointerEvents: 'none',
    transform: 'none',
    willChange: 'transform, opacity',
    filter: 'drop-shadow(0 30px 30px rgba(0, 0, 0, 0.5))'
  })
  document.body.appendChild(clone)
  return clone
}

/* ----------------------------------------------------------------------
 * Product card -> product page: the photo carries over between pages.
 * ------------------------------------------------------------------- */
let pending = null

/** Call on the card's click: the photo lifts off and waits for the next page. */
export function launchShared(key, img) {
  if (prefersReducedMotion() || !img?.complete) return
  const rect = img.getBoundingClientRect()
  if (!rect.width || rect.bottom < 0 || rect.top > window.innerHeight) return
  pending?.clone.remove()
  const clone = makeClone(img, rect)
  gsap.to(clone, { scale: 1.06, duration: 0.35, ease: 'power2.out' })
  // Give up if the next page never claims it.
  const timeout = setTimeout(() => dropShared(), 2500)
  pending = { key, clone, timeout }
}

/** Call on the new page once its target is in place; resolves when landed. */
export function landShared(key, target) {
  return new Promise((resolve) => {
    if (!pending || pending.key !== key || !target) {
      dropShared()
      return resolve(false)
    }
    const { clone, timeout } = pending
    clearTimeout(timeout)
    pending = null
    const to = target.getBoundingClientRect()
    const from = clone.getBoundingClientRect()
    // Fit the clone inside the target box, keeping its proportions.
    const scale = Math.min(to.width / from.width, to.height / from.height) * 0.8
    gsap.to(clone, {
      x: to.left + to.width / 2 - (from.left + from.width / 2),
      y: to.top + to.height / 2 - (from.top + from.height / 2),
      scale,
      duration: 0.9,
      ease: 'expo.inOut',
      onComplete: () => {
        gsap.to(clone, { opacity: 0, duration: 0.5, delay: 0.2, onComplete: () => clone.remove() })
        resolve(true)
      }
    })
  })
}

export function dropShared() {
  if (!pending) return
  const { clone, timeout } = pending
  clearTimeout(timeout)
  pending = null
  gsap.to(clone, { opacity: 0, duration: 0.3, onComplete: () => clone.remove() })
}

/* ----------------------------------------------------------------------
 * Add to cart: the product arcs into the cart button, which bumps.
 * ------------------------------------------------------------------- */
// `source` is the product image, or any element to start from together with
// the image's `src` (e.g. the 3D stage).
export function flyToCart(source, src) {
  const cart = document.getElementById('nav-cart')
  if (!cart) return
  const bump = () => gsap.fromTo(cart, { scale: 1 }, { scale: 1.18, duration: 0.18, yoyo: true, repeat: 1, ease: 'power2.out' })
  if (prefersReducedMotion() || !source) return bump()
  let img = source
  if (source.tagName !== 'IMG') {
    if (!src) return bump()
    img = new Image()
    img.src = src
  }
  const from = source.getBoundingClientRect()
  const to = cart.getBoundingClientRect()
  if (!from.width) return bump()
  const size = Math.min(from.width, 160)
  const start = { left: from.left + (from.width - size) / 2, top: from.top + (from.height - size) / 2, width: size, height: size }
  const clone = makeClone(img, start)
  const dx = to.left + to.width / 2 - (start.left + size / 2)
  const dy = to.top + to.height / 2 - (start.top + size / 2)
  // Horizontal and vertical move on different eases make a curved path.
  const tl = gsap.timeline({ onComplete: () => { clone.remove(); bump() } })
  tl.to(clone, { x: dx, duration: 0.8, ease: 'power1.inOut' }, 0)
    .to(clone, { y: dy, duration: 0.8, ease: 'back.in(1.6)' }, 0)
    .to(clone, { scale: 0.12, rotation: 25, duration: 0.8, ease: 'power2.in' }, 0)
    .to(clone, { opacity: 0.2, duration: 0.2 }, 0.6)
}
