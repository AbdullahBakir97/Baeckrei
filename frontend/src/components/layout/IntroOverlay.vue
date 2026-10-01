<template>
  <div ref="root" class="intro" aria-hidden="true">
    <div class="intro-inner">
      <p ref="mark" class="intro-mark"><em>{{ business.name.charAt(0) }}</em>{{ business.name.slice(1) }}</p>
      <p class="intro-sub">{{ $t('intro.tagline', { street: business.street, city: business.city }) }}</p>
    </div>
    <div class="intro-foot">
      <span class="intro-count tabular-nums">{{ String(Math.round(progress.value)).padStart(3, '0') }}</span>
      <span class="intro-bar"><span ref="bar"></span></span>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { business } from '@/config/business'
import { gsap, SplitText, lockScroll } from '@/motion'

// First-visit intro: the name rises letter by letter while a counter follows
// the real loading (fonts, page), then the curtain lifts.
const emit = defineEmits(['done'])
const root = ref(null)
const mark = ref(null)
const bar = ref(null)
const progress = reactive({ value: 0 })

const loaded = () => new Promise((resolve) => {
  if (document.readyState === 'complete') resolve()
  else window.addEventListener('load', resolve, { once: true })
})

onMounted(async () => {
  lockScroll(true)
  await document.fonts?.ready
  const letters = SplitText.create(mark.value, { type: 'chars', mask: 'chars' })
  gsap.from(letters.chars, { yPercent: 110, duration: 1, ease: 'expo.out', stagger: 0.045 })

  // The counter runs to 70 on its own and completes once the page has loaded.
  const count = gsap.to(progress, { value: 70, duration: 1.2, ease: 'power2.out' })
  gsap.to(bar.value, { scaleX: 0.7, duration: 1.2, ease: 'power2.out' })
  await Promise.all([loaded(), new Promise(resolve => setTimeout(resolve, 1300))])
  count.kill()
  await gsap.timeline()
    .to(progress, { value: 100, duration: 0.5, ease: 'power2.inOut' })
    .to(bar.value, { scaleX: 1, duration: 0.5, ease: 'power2.inOut' }, '<')
    .to(letters.chars, { yPercent: -110, duration: 0.6, ease: 'expo.in', stagger: 0.02 }, '+=0.1')
    .to(root.value, { clipPath: 'inset(0 0 100% 0)', duration: 0.9, ease: 'expo.inOut' }, '-=0.2')
  lockScroll(false)
  emit('done')
})
</script>

<style scoped>
.intro {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background:
    radial-gradient(50% 50% at 50% 60%, rgba(230, 161, 90, 0.14), transparent 70%),
    #0e0c0a;
  clip-path: inset(0 0 0% 0);
}

.intro-inner {
  text-align: center;
}

.intro-mark {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: clamp(4.5rem, 16vw, 12rem);
  line-height: 1;
  letter-spacing: -0.03em;
  color: #f4ece1;
}

.intro-mark em {
  color: #e6a15a;
}

.intro-sub {
  margin-top: 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: #7d7061;
}

.intro-foot {
  position: absolute;
  left: 1.5rem;
  right: 1.5rem;
  bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.intro-count {
  font-size: 0.85rem;
  font-weight: 700;
  color: #e6a15a;
}

.intro-bar {
  flex: 1;
  height: 1px;
  background: rgba(244, 236, 225, 0.12);
}

.intro-bar span {
  display: block;
  height: 100%;
  background: #e6a15a;
  transform: scaleX(0);
  transform-origin: left;
}
</style>
