import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { SplitText } from 'gsap/SplitText'
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'

gsap.registerPlugin(ScrollTrigger, SplitText)

export { gsap, ScrollTrigger, SplitText }

export const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

export const isCoarsePointer = () =>
  typeof window !== 'undefined' && window.matchMedia('(pointer: coarse)').matches

let lenis = null

// The first-visit intro covers the page; entrance animations wait for it.
let finishIntro
const introDone = new Promise((resolve) => { finishIntro = resolve })
export const whenIntroDone = () => introDone
export const markIntroDone = () => finishIntro()

// Smooth scrolling driven by GSAP's ticker so ScrollTrigger stays in sync.
export function initSmoothScroll() {
  if (lenis || prefersReducedMotion()) return lenis
  lenis = new Lenis({
    duration: 1.1,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true
  })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add((time) => lenis.raf(time * 1000))
  gsap.ticker.lagSmoothing(0)
  return lenis
}

export const getLenis = () => lenis

export function scrollToTop() {
  if (lenis) lenis.scrollTo(0, { immediate: true })
  else window.scrollTo(0, 0)
}

// Modals and drawers should not scroll the page behind them.
export function lockScroll(locked) {
  document.documentElement.style.overflow = locked ? 'hidden' : ''
  if (lenis) locked ? lenis.stop() : lenis.start()
}
