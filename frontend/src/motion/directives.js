import { gsap, ScrollTrigger, SplitText, prefersReducedMotion, isCoarsePointer } from './index'

// Each directive keeps its GSAP objects on the element so they can be
// cleaned up when the component unmounts (route changes create and destroy
// many ScrollTriggers).
const store = (el, key, value) => { el.__motion = { ...(el.__motion || {}), [key]: value } }
const cleanup = (el) => {
  const m = el.__motion || {}
  m.tween?.scrollTrigger?.kill()
  m.tween?.kill()
  m.split?.revert()
  m.off?.()
  el.__motion = {}
}

/**
 * v-reveal: fade and rise into view on scroll.
 * v-reveal            -> the element itself
 * v-reveal.stagger    -> its children, one after another
 * v-reveal="{ y: 60, delay: 0.2 }"
 */
export const reveal = {
  mounted(el, binding) {
    if (prefersReducedMotion()) return
    const opts = binding.value || {}
    const targets = binding.modifiers.stagger ? Array.from(el.children) : el
    const tween = gsap.from(targets, {
      y: opts.y ?? 40,
      opacity: 0,
      duration: opts.duration ?? 1,
      delay: opts.delay ?? 0,
      ease: 'power3.out',
      stagger: binding.modifiers.stagger ? (opts.stagger ?? 0.08) : 0,
      clearProps: 'transform,opacity',
      scrollTrigger: { trigger: el, start: opts.start ?? 'top 88%', once: true }
    })
    store(el, 'tween', tween)
  },
  unmounted: cleanup
}

/**
 * v-split: headline that rises line by line (words masked by their line).
 * v-split.load plays immediately instead of on scroll.
 */
export const split = {
  mounted(el, binding) {
    if (prefersReducedMotion()) return
    const run = () => {
      const s = SplitText.create(el, { type: 'lines,words', mask: 'lines', linesClass: 'split-line' })
      const tween = gsap.from(s.words, {
        yPercent: 110,
        duration: 1.1,
        ease: 'expo.out',
        stagger: 0.035,
        delay: binding.value?.delay ?? 0,
        scrollTrigger: binding.modifiers.load ? undefined : { trigger: el, start: 'top 88%', once: true },
        onComplete: () => s.revert()
      })
      store(el, 'split', s)
      store(el, 'tween', tween)
    }
    // Wait for web fonts so lines are measured with the final font.
    document.fonts?.ready ? document.fonts.ready.then(run) : run()
  },
  unmounted: cleanup
}

/**
 * v-parallax="0.2": move at a different speed while scrolling
 * (positive = slower than the page, negative = faster).
 */
export const parallax = {
  mounted(el, binding) {
    if (prefersReducedMotion()) return
    const speed = Number(binding.value ?? 0.2)
    const tween = gsap.to(el, {
      yPercent: speed * 100,
      ease: 'none',
      scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: true }
    })
    store(el, 'tween', tween)
  },
  unmounted: cleanup
}

/**
 * v-tilt: 3D tilt that follows the pointer. Children with data-depth="40"
 * float above the surface by that many pixels, giving layered depth.
 */
export const tilt = {
  mounted(el, binding) {
    if (prefersReducedMotion() || isCoarsePointer()) return
    const max = binding.value?.max ?? 10
    el.style.transformStyle = 'preserve-3d'
    el.style.willChange = 'transform'
    el.querySelectorAll('[data-depth]').forEach((layer) => {
      layer.style.transform = `translateZ(${layer.dataset.depth}px)`
    })
    const rx = gsap.quickTo(el, 'rotationX', { duration: 0.6, ease: 'power3.out' })
    const ry = gsap.quickTo(el, 'rotationY', { duration: 0.6, ease: 'power3.out' })
    gsap.set(el, { transformPerspective: 900 })
    const move = (e) => {
      const r = el.getBoundingClientRect()
      const x = (e.clientX - r.left) / r.width - 0.5
      const y = (e.clientY - r.top) / r.height - 0.5
      ry(x * max * 2)
      rx(-y * max * 2)
      el.style.setProperty('--glare-x', `${(x + 0.5) * 100}%`)
      el.style.setProperty('--glare-y', `${(y + 0.5) * 100}%`)
    }
    const leave = () => { rx(0); ry(0) }
    el.addEventListener('pointermove', move)
    el.addEventListener('pointerleave', leave)
    store(el, 'off', () => {
      el.removeEventListener('pointermove', move)
      el.removeEventListener('pointerleave', leave)
    })
  },
  unmounted: cleanup
}

/** v-magnetic: the element leans toward the pointer while hovered. */
export const magnetic = {
  mounted(el, binding) {
    if (prefersReducedMotion() || isCoarsePointer()) return
    const strength = binding.value ?? 0.3
    const x = gsap.quickTo(el, 'x', { duration: 0.5, ease: 'power3.out' })
    const y = gsap.quickTo(el, 'y', { duration: 0.5, ease: 'power3.out' })
    const move = (e) => {
      const r = el.getBoundingClientRect()
      x((e.clientX - (r.left + r.width / 2)) * strength)
      y((e.clientY - (r.top + r.height / 2)) * strength)
    }
    const leave = () => { x(0); y(0) }
    el.addEventListener('pointermove', move)
    el.addEventListener('pointerleave', leave)
    store(el, 'off', () => {
      el.removeEventListener('pointermove', move)
      el.removeEventListener('pointerleave', leave)
    })
  },
  unmounted: cleanup
}

export function installMotion(app) {
  app.directive('reveal', reveal)
  app.directive('split', split)
  app.directive('parallax', parallax)
  app.directive('tilt', tilt)
  app.directive('magnetic', magnetic)
}

// Layout shifts after images/fonts load change trigger positions.
export const refreshScrollTriggers = () => ScrollTrigger.refresh()
