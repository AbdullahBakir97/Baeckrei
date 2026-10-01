<template>
  <div ref="root" class="home">
    <!-- Hero -->
    <section ref="hero" class="hero">
      <div class="hero-stage">
        <SplineScene v-if="business.splineScene && !splineFailed" :scene="business.splineScene"
                     :label="$t('home.sceneLabel', { name: business.name })" @error="splineFailed = true" />
        <HeroScene v-else-if="use3d" @error="use3d = false" />
        <div v-else class="hero-fallback" aria-hidden="true">
          <img v-for="item in fallbackItems" :key="item.src" v-parallax="item.speed" :src="item.src" alt=""
               :style="item.style" />
        </div>
      </div>
      <div class="hero-shade" aria-hidden="true"></div>

      <div ref="heroContent" class="section hero-content">
        <p v-reveal="{ delay: 0.3 }" class="eyebrow">
          <span class="hero-live"></span> {{ $t('home.eyebrow', { street: business.street, city: business.city }) }}
        </p>
        <i18n-t v-split.load="{ delay: 0.35 }" keypath="home.heroTitle" tag="h1" class="display-title hero-title" scope="global">
          <template #loved><em>{{ $t('home.heroLoved') }}</em></template>
        </i18n-t>
        <p v-reveal="{ delay: 0.7 }" class="hero-lede">
          {{ $t('home.lede', { street: business.street, city: business.city }) }}
        </p>
        <div v-reveal="{ delay: 0.85 }" class="mt-10 flex flex-wrap gap-3">
          <router-link v-magnetic="0.25" to="/products" class="btn-amber">
            {{ $t('common.shopNow') }} <font-awesome-icon icon="arrow-right" />
          </router-link>
          <a href="#visit" class="btn-ghost">{{ $t('home.visitUs') }}</a>
        </div>
      </div>

      <div class="section hero-foot">
        <span class="hero-scroll"><span></span></span>
        <ul class="hero-facts">
          <li>{{ $t('home.factPickup', { street: business.street }) }}</li>
          <li>{{ $t('home.factDelivery', { city: business.city }) }}</li>
          <li>{{ $t('home.factPayment') }}</li>
        </ul>
      </div>
    </section>

    <!-- Marquee -->
    <section class="marquee" :aria-label="$t('home.marqueeLabel')">
      <div ref="marquee" class="marquee-track">
        <span v-for="n in 2" :key="n" class="marquee-row" :aria-hidden="n === 2">
          <template v-for="word in marqueeWords" :key="word">
            <span>{{ word }}</span><i aria-hidden="true">✦</i>
          </template>
        </span>
      </div>
    </section>

    <!-- Featured products: pinned horizontal scroll on desktop -->
    <section v-if="featured.length" ref="featuredEl" class="featured">
      <div class="featured-pin">
        <div class="section flex flex-wrap items-end justify-between gap-6">
          <div>
            <p v-reveal class="eyebrow">{{ $t('common.freshToday') }}</p>
            <h2 v-split class="display-title text-5xl sm:text-7xl mt-3">{{ $t('home.featuredTitle') }}</h2>
          </div>
          <router-link to="/products" class="btn-ghost">
            {{ $t('home.seeEverything') }} <font-awesome-icon icon="arrow-right" />
          </router-link>
        </div>
        <div ref="track" class="featured-track">
          <div v-for="product in featured" :key="product.id" class="featured-item">
            <ProductCard :product="product" />
          </div>
          <router-link to="/products" class="featured-more lux-card">
            <span class="display-title text-4xl">{{ $t('home.wholeCounter1') }}<br><em class="text-crust">{{ $t('home.wholeCounter2') }}</em></span>
            <span class="featured-more-arrow"><font-awesome-icon icon="arrow-right" /></span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Craft: scroll-driven steps with layered visual -->
    <section ref="craftEl" class="section craft">
      <div class="craft-visual">
        <div class="craft-orb">
          <svg viewBox="0 0 200 200" class="craft-ring" aria-hidden="true">
            <circle cx="100" cy="100" r="92" class="craft-ring-track" />
            <circle ref="ring" cx="100" cy="100" r="92" class="craft-ring-fill" pathLength="1" />
          </svg>
          <div class="craft-core" aria-hidden="true"></div>
          <transition name="swap" mode="out-in">
            <img :key="activeStep" :src="steps[activeStep].image" alt="" class="craft-img" />
          </transition>
          <p class="craft-num" aria-hidden="true">0{{ activeStep + 1 }}</p>
        </div>
        <img v-parallax="-0.6" :src="donutImg" alt="" class="craft-layer craft-layer-a" />
        <img v-parallax="0.5" :src="cookieImg" alt="" class="craft-layer craft-layer-b" />
      </div>

      <div class="craft-steps">
        <div class="craft-intro">
          <p v-reveal class="eyebrow">{{ $t('home.craftEyebrow') }}</p>
          <h2 v-split class="display-title text-5xl sm:text-7xl mt-3">{{ $t('home.craftTitle1') }}<br>{{ $t('home.craftTitle2') }}</h2>
        </div>
        <article v-for="(step, index) in steps" :key="step.title" class="craft-step"
                 :class="{ 'is-active': activeStep === index }">
          <span class="craft-step-num">0{{ index + 1 }}</span>
          <h3 class="display-title text-4xl sm:text-5xl">{{ step.title }}</h3>
          <p>{{ step.text }}</p>
        </article>
      </div>
    </section>

    <!-- Categories bento -->
    <section class="section mt-40">
      <p v-reveal class="eyebrow">{{ $t('home.counterEyebrow') }}</p>
      <h2 v-split class="display-title text-5xl sm:text-7xl mt-3 max-w-3xl">{{ $t('home.counterTitle') }}</h2>
      <div v-reveal.stagger class="bento">
        <router-link v-for="tile in tiles" :key="tile.slug" v-tilt="{ max: 6 }" :to="tile.to"
                     class="bento-tile lux-card" :class="tile.className">
          <span class="bento-glow" aria-hidden="true"></span>
          <img :src="tile.image" alt="" class="bento-img" data-depth="70" loading="lazy" />
          <span class="bento-text" data-depth="35">
            <span class="eyebrow !text-[0.65rem]">{{ tile.kicker }}</span>
            <span class="display-title bento-title">{{ tile.name }}</span>
          </span>
          <span class="bento-arrow" data-depth="45"><font-awesome-icon icon="arrow-right" /></span>
        </router-link>
      </div>
    </section>

    <!-- Visit -->
    <section id="visit" class="section visit">
      <div>
        <p v-reveal class="eyebrow">{{ $t('home.visitUs') }}</p>
        <h2 v-split class="display-title text-6xl sm:text-8xl mt-3">{{ $t('home.visitTitle', { street: business.street }) }}</h2>
        <div v-reveal="{ delay: 0.1 }" class="visit-info">
          <p class="text-lg text-cream">{{ business.name }}<br>{{ address }}</p>
          <p v-if="business.transit" class="flex items-center gap-3">
            <span class="ubahn" aria-hidden="true">U</span> {{ business.transit }}
          </p>
          <dl v-if="business.openingHours.length" class="grid grid-cols-2 gap-y-1 max-w-xs">
            <template v-for="row in business.openingHours" :key="row.days">
              <dt>{{ row.days }}</dt><dd class="tabular-nums text-cream">{{ row.hours }}</dd>
            </template>
          </dl>
        </div>
        <div v-reveal="{ delay: 0.2 }" class="mt-10 flex flex-wrap gap-3">
          <a v-magnetic="0.2" :href="mapUrl" target="_blank" rel="noopener" class="btn-amber">
            <font-awesome-icon icon="location-dot" /> {{ $t('home.directions') }}
          </a>
          <router-link to="/contact" class="btn-ghost">{{ $t('common.contactUs') }}</router-link>
        </div>
      </div>

      <a v-reveal="{ delay: 0.15 }" v-tilt="{ max: 5 }" :href="mapUrl" target="_blank" rel="noopener"
         class="visit-map lux-card" :aria-label="$t('home.openMap', { street: business.street })">
        <span class="visit-grid" aria-hidden="true"></span>
        <span class="visit-street" data-depth="20" aria-hidden="true">{{ business.street }}</span>
        <span class="visit-pin" data-depth="60" aria-hidden="true"><span></span></span>
        <span v-if="business.transit" class="visit-station" data-depth="40" aria-hidden="true">
          <span class="ubahn">U</span> {{ business.transit.replace(/^U-Bahn\s*/, '') }}
        </span>
      </a>
    </section>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { business, streetLine, cityLine } from '@/config/business'
import { gsap, ScrollTrigger, prefersReducedMotion } from '@/motion'
import { webglAvailable } from '@/three/webgl'
import HeroScene from '@/components/three/HeroScene.vue'
import SplineScene from '@/components/three/SplineScene.vue'
import ProductCard from '@/components/products/ProductCard.vue'
import croissantImg from '@/assets/bakery/croissant-butter.png'
import pretzelImg from '@/assets/bakery/pretzel.png'
import donutImg from '@/assets/bakery/donut.png'
import cupcakeImg from '@/assets/bakery/cupcake.png'
import cookieImg from '@/assets/bakery/cookie.png'
import macaronsImg from '@/assets/bakery/macarons.png'
import eclairImg from '@/assets/bakery/eclair.png'
import chocolateCroissantImg from '@/assets/bakery/croissant-chocolate.png'

const root = ref(null)
const hero = ref(null)
const heroContent = ref(null)
const marquee = ref(null)
const featuredEl = ref(null)
const track = ref(null)
const craftEl = ref(null)
const ring = ref(null)

const use3d = ref(webglAvailable())
const splineFailed = ref(false)
const featured = ref([])
const activeStep = ref(0)

const address = [streetLine(), cityLine()].filter(Boolean).join(', ')
const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent([business.name, address].join(', '))}`

const { t } = useI18n()
const marqueeWords = t('home.marquee').split(',')

const fallbackItems = [
  { src: croissantImg, speed: -0.2, style: 'right:8%;top:18%;width:min(40vw,520px)' },
  { src: pretzelImg, speed: -0.4, style: 'right:32%;bottom:8%;width:min(20vw,260px)' },
  { src: macaronsImg, speed: 0.2, style: 'right:2%;bottom:14%;width:min(16vw,200px);opacity:.7' }
]

// Copy for the craft section; adjust to match how the bakery works.
const steps = [
  { title: t('home.steps.mix.title'), image: pretzelImg, text: t('home.steps.mix.text') },
  { title: t('home.steps.rest.title'), image: eclairImg, text: t('home.steps.rest.text') },
  { title: t('home.steps.shape.title'), image: chocolateCroissantImg, text: t('home.steps.shape.text') },
  { title: t('home.steps.bake.title'), image: croissantImg, text: t('home.steps.bake.text', { street: business.street }) }
]

const tiles = [
  { slug: 'breads', image: pretzelImg, to: '/categories/breads', className: 'is-large' },
  { slug: 'pastries', image: croissantImg, to: '/categories/pastries', className: 'is-wide' },
  { slug: 'cakes', image: cupcakeImg, to: '/categories/cakes', className: '' },
  { slug: 'cookies', image: cookieImg, to: '/categories/cookies', className: '' },
  { slug: 'seasonal', image: macaronsImg, to: '/seasonal', className: 'is-banner' }
].map(tile => ({ ...tile, name: t(`categories.${tile.slug}`), kicker: t(`home.tiles.${tile.slug}`) }))

let ctx = null
let mm = null

function setupMotion() {
  ctx = gsap.context(() => {
    // Hero copy drifts up and fades as the page scrolls.
    gsap.to(heroContent.value, {
      yPercent: -25,
      opacity: 0,
      ease: 'none',
      scrollTrigger: { trigger: hero.value, start: 'top top', end: 'bottom top', scrub: true }
    })

    // Endless marquee that speeds up with the scroll.
    const loop = gsap.to(marquee.value, { xPercent: -50, duration: 40, ease: 'none', repeat: -1 })
    ScrollTrigger.create({
      trigger: marquee.value,
      start: 'top bottom',
      end: 'bottom top',
      onUpdate: (self) => {
        const boost = Math.min(6, 1 + Math.abs(self.getVelocity()) / 400)
        gsap.to(loop, {
          timeScale: boost,
          duration: 0.2,
          overwrite: true,
          onComplete: () => gsap.to(loop, { timeScale: 1, duration: 1.2 })
        })
      }
    })

    // Craft steps: the active step follows the scroll, the ring fills up.
    const stepEls = craftEl.value.querySelectorAll('.craft-step')
    stepEls.forEach((el, index) => {
      ScrollTrigger.create({
        trigger: el,
        start: 'top 60%',
        end: 'bottom 60%',
        onToggle: (self) => { if (self.isActive) activeStep.value = index }
      })
    })
    gsap.fromTo(ring.value, { strokeDashoffset: 1 }, {
      strokeDashoffset: 0,
      ease: 'none',
      scrollTrigger: { trigger: craftEl.value, start: 'top 60%', end: 'bottom 70%', scrub: true }
    })
  }, root.value)

  mm = gsap.matchMedia()
}

// Pin the product row and move it sideways while scrolling (desktop only).
function setupFeatured() {
  if (!mm || !track.value) return
  mm.add('(min-width: 1024px) and (prefers-reduced-motion: no-preference)', () => {
    const distance = () => Math.max(0, track.value.scrollWidth - window.innerWidth)
    gsap.to(track.value, {
      x: () => -distance(),
      ease: 'none',
      scrollTrigger: {
        trigger: featuredEl.value,
        start: 'top top',
        end: () => `+=${distance()}`,
        pin: true,
        scrub: 0.8,
        invalidateOnRefresh: true,
        // Measured first, so every trigger further down includes the
        // extra scroll distance the pin adds.
        refreshPriority: 1
      }
    })
  })
  ScrollTrigger.refresh()
}

async function loadFeatured() {
  try {
    const { data } = await axios.get('/api/products/', { params: { page_size: 8 } })
    // Show what can be ordered today first.
    const inStock = (p) => p.available !== false && p.stock > 0
    const products = data.results || data || []
    featured.value = [...products.filter(inStock), ...products.filter(p => !inStock(p))].slice(0, 8)
  } catch {
    featured.value = []
  }
}

onMounted(async () => {
  if (!prefersReducedMotion()) setupMotion()
  await loadFeatured()
  await nextTick()
  setupFeatured()
})

onBeforeUnmount(() => {
  mm?.revert()
  ctx?.revert()
})
</script>

<style scoped>
/* Hero */
.hero {
  position: relative;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
}

.hero-stage {
  position: absolute;
  inset: 0;
}

.hero-fallback img {
  position: absolute;
  object-fit: contain;
  filter: drop-shadow(0 40px 40px rgba(0, 0, 0, 0.5));
}

.hero-shade {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(14, 12, 10, 0.85) 0%, rgba(14, 12, 10, 0.35) 45%, transparent 70%),
    linear-gradient(0deg, #0e0c0a 0%, transparent 30%);
}

@media (max-width: 767px) {
  .hero-shade {
    background: linear-gradient(0deg, #0e0c0a 12%, rgba(14, 12, 10, 0.75) 45%, transparent 70%);
  }
}

.hero-content {
  position: relative;
  padding-top: 8rem;
  padding-bottom: 4rem;
}

@media (min-width: 768px) {
  .hero-content {
    padding-bottom: 7rem;
  }
}

.hero-title {
  margin-top: 1.25rem;
  max-width: 11ch;
  font-size: clamp(3.4rem, 8.4vw, 8.6rem);
  line-height: 0.9;
}

.hero-title em {
  font-style: italic;
  color: #e6a15a;
}

.hero-lede {
  margin-top: 1.75rem;
  max-width: 30rem;
  font-size: 1.1rem;
  line-height: 1.7;
  color: #d9cfc2;
}

.hero-live {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #9fd49a;
  box-shadow: 0 0 0 0 rgba(159, 212, 154, 0.6);
  animation: live 2s infinite;
}

@keyframes live {
  70% { box-shadow: 0 0 0 10px rgba(159, 212, 154, 0); }
  100% { box-shadow: 0 0 0 0 rgba(159, 212, 154, 0); }
}

.hero-foot {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 2rem;
}

.hero-scroll {
  position: relative;
  width: 1.5rem;
  height: 2.4rem;
  border-radius: 9999px;
  border: 1.5px solid rgba(244, 236, 225, 0.3);
}

.hero-scroll span {
  position: absolute;
  left: 50%;
  top: 0.45rem;
  width: 3px;
  height: 0.5rem;
  border-radius: 9999px;
  background: #e6a15a;
  transform: translateX(-50%);
  animation: wheel 1.8s var(--ease-out-expo) infinite;
}

@keyframes wheel {
  0% { transform: translate(-50%, 0); opacity: 1; }
  100% { transform: translate(-50%, 0.9rem); opacity: 0; }
}

.hero-facts {
  display: none;
  gap: 2rem;
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7d7061;
}

@media (min-width: 768px) {
  .hero-facts {
    display: flex;
  }
}

/* Marquee */
.marquee {
  overflow: hidden;
  padding: 1.6rem 0;
  border-block: 1px solid rgba(244, 236, 225, 0.07);
  background: rgba(21, 18, 15, 0.6);
}

.marquee-track {
  display: flex;
  width: max-content;
}

.marquee-row {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.marquee-row span {
  padding: 0 2rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 4rem);
  line-height: 1;
  color: #f4ece1;
  white-space: nowrap;
}

.marquee-row span:nth-child(4n + 3) {
  font-style: italic;
  color: #e6a15a;
}

.marquee-row i {
  font-style: normal;
  color: #d2603f;
  font-size: 1.25rem;
}

/* Featured */
.featured {
  padding-top: 8rem;
}

@media (min-width: 1024px) {
  .featured-pin {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 100vh;
  }
}

.featured-track {
  display: flex;
  gap: 1.5rem;
  margin-top: 3rem;
  padding: 1rem max(1rem, calc((100vw - 80rem) / 2 + 2rem)) 2rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
}

@media (min-width: 1024px) {
  .featured-track {
    overflow: visible;
    width: max-content;
  }
}

.featured-item {
  flex: 0 0 min(78vw, 22rem);
  scroll-snap-align: start;
}

.featured-more {
  flex: 0 0 min(78vw, 22rem);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 2rem;
  scroll-snap-align: start;
  color: #f4ece1;
}

.featured-more:hover {
  color: #f4ece1;
}

.featured-more-arrow {
  display: grid;
  place-items: center;
  width: 4rem;
  height: 4rem;
  border-radius: 9999px;
  color: #0e0c0a;
  background: #e6a15a;
  font-size: 1.25rem;
  transition: transform 0.5s var(--ease-out-expo);
}

.featured-more:hover .featured-more-arrow {
  transform: rotate(-45deg);
}

/* Craft */
.craft {
  display: grid;
  gap: 3rem;
  margin-top: 10rem;
}

@media (min-width: 1024px) {
  .craft {
    grid-template-columns: 1fr 1fr;
    gap: 5rem;
  }
}

.craft-visual {
  position: relative;
  display: none;
}

@media (min-width: 1024px) {
  .craft-visual {
    display: grid;
    place-items: center;
    position: sticky;
    top: 0;
    height: 100vh;
  }
}

.craft-orb {
  position: relative;
  display: grid;
  place-items: center;
  width: min(34vw, 30rem);
  aspect-ratio: 1;
}

.craft-ring {
  position: absolute;
  inset: 0;
  transform: rotate(-90deg);
}

.craft-ring-track,
.craft-ring-fill {
  fill: none;
  stroke-width: 1.2;
}

.craft-ring-track {
  stroke: rgba(244, 236, 225, 0.1);
}

.craft-ring-fill {
  stroke: #e6a15a;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  stroke-linecap: round;
}

.craft-core {
  position: absolute;
  inset: 14%;
  border-radius: 50%;
  background: radial-gradient(circle at 50% 60%, rgba(230, 161, 90, 0.35), rgba(210, 96, 63, 0.12) 45%, transparent 70%);
  filter: blur(6px);
}

.craft-img {
  position: relative;
  width: 62%;
  filter: drop-shadow(0 30px 30px rgba(0, 0, 0, 0.55));
}

.craft-num {
  position: absolute;
  right: -0.5rem;
  bottom: 0.5rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 5rem;
  line-height: 1;
  color: #f4ece1;
}

.craft-layer {
  position: absolute;
  pointer-events: none;
  filter: drop-shadow(0 20px 20px rgba(0, 0, 0, 0.5)) blur(1px);
  opacity: 0.55;
}

.craft-layer-a {
  width: 16%;
  left: 4%;
  top: 22%;
}

.craft-layer-b {
  width: 13%;
  right: 6%;
  bottom: 20%;
}

.craft-intro {
  padding-top: 0;
}

@media (min-width: 1024px) {
  .craft-intro {
    padding-top: 20vh;
  }
}

.craft-step {
  padding: 3rem 0;
  border-bottom: 1px solid rgba(244, 236, 225, 0.08);
  opacity: 0.35;
  transition: opacity 0.6s var(--ease-out-expo);
}

@media (min-width: 1024px) {
  .craft-step {
    min-height: 55vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

.craft-step.is-active,
.craft-step:only-child {
  opacity: 1;
}

@media (prefers-reduced-motion: reduce), (max-width: 1023px) {
  .craft-step {
    opacity: 1;
  }
}

.craft-step-num {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #e6a15a;
}

.craft-step h3 {
  margin-top: 0.75rem;
}

.craft-step p {
  margin-top: 1rem;
  max-width: 28rem;
  font-size: 1.1rem;
  line-height: 1.7;
}

.swap-enter-active,
.swap-leave-active {
  transition: opacity 0.4s, transform 0.6s var(--ease-out-expo);
}

.swap-enter-from {
  opacity: 0;
  transform: scale(0.8) rotate(-12deg);
}

.swap-leave-to {
  opacity: 0;
  transform: scale(1.1) rotate(12deg);
}

/* Bento */
.bento {
  display: grid;
  gap: 1rem;
  margin-top: 3rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (min-width: 1024px) {
  .bento {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    grid-auto-rows: 17rem;
  }
}

.bento-tile {
  position: relative;
  display: block;
  min-height: 14rem;
  overflow: visible;
  transform-style: preserve-3d;
  color: #f4ece1;
}

.bento-tile:hover {
  color: #f4ece1;
}

@media (min-width: 1024px) {
  .bento-tile.is-large {
    grid-column: span 2;
    grid-row: span 2;
  }

  .bento-tile.is-wide {
    grid-column: span 2;
  }
}

.bento-tile.is-banner {
  grid-column: 1 / -1;
  min-height: 12rem;
}

.bento-glow {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(70% 70% at 70% 60%, rgba(230, 161, 90, 0.2), transparent 70%);
}

.bento-img {
  position: absolute;
  right: 6%;
  bottom: 8%;
  width: 52%;
  max-height: 80%;
  object-fit: contain;
  filter: drop-shadow(0 30px 25px rgba(0, 0, 0, 0.5));
  transition: scale 0.8s var(--ease-out-expo), rotate 0.8s var(--ease-out-expo);
}

.is-large .bento-img {
  width: 70%;
}

.is-banner .bento-img {
  width: auto;
  height: 85%;
  right: 8%;
}

.bento-tile:hover .bento-img {
  scale: 1.08;
  rotate: -6deg;
}

.bento-text {
  position: absolute;
  left: 1.5rem;
  top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.bento-title {
  font-size: clamp(2.2rem, 4vw, 3.5rem);
}

.is-large .bento-title {
  font-size: clamp(3rem, 6vw, 5.5rem);
}

.bento-arrow {
  position: absolute;
  left: 1.5rem;
  bottom: 1.5rem;
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 9999px;
  border: 1px solid rgba(244, 236, 225, 0.2);
  transition: background 0.4s, color 0.4s, transform 0.5s var(--ease-out-expo);
}

.bento-tile:hover .bento-arrow {
  color: #0e0c0a;
  background: #e6a15a;
  border-color: transparent;
}

/* Visit */
.visit {
  display: grid;
  gap: 3rem;
  align-items: center;
  margin-top: 10rem;
  scroll-margin-top: 6rem;
}

@media (min-width: 1024px) {
  .visit {
    grid-template-columns: 1.1fr 1fr;
  }
}

.visit-info {
  display: grid;
  gap: 1.25rem;
  margin-top: 2.5rem;
  color: #b9ab98;
}

.ubahn {
  display: inline-grid;
  place-items: center;
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 0.3rem;
  background: #115d91;
  color: #fff;
  font-weight: 800;
  font-size: 0.9rem;
  font-family: 'Manrope Variable', system-ui, sans-serif;
}

.visit-map {
  position: relative;
  display: block;
  aspect-ratio: 4 / 3.4;
  overflow: visible;
  transform-style: preserve-3d;
  background:
    radial-gradient(50% 50% at 55% 50%, rgba(230, 161, 90, 0.18), transparent 70%),
    #15120f;
}

.visit-grid {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background-image:
    linear-gradient(rgba(244, 236, 225, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(244, 236, 225, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, transparent calc(55% - 1.1rem), rgba(244, 236, 225, 0.12) calc(55% - 1.1rem), rgba(244, 236, 225, 0.12) calc(55% + 1.1rem), transparent calc(55% + 1.1rem)),
    linear-gradient(transparent calc(30% - 0.6rem), rgba(244, 236, 225, 0.07) calc(30% - 0.6rem), rgba(244, 236, 225, 0.07) calc(30% + 0.6rem), transparent calc(30% + 0.6rem));
  background-size: 2.5rem 2.5rem, 2.5rem 2.5rem, 100% 100%, 100% 100%;
  mask-image: radial-gradient(ellipse at center, #000 45%, transparent 85%);
}

.visit-street {
  position: absolute;
  left: 55%;
  top: 72%;
  transform-origin: left center;
  translate: -50% 0;
  rotate: -90deg;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #7d7061;
  white-space: nowrap;
}

.visit-pin {
  position: absolute;
  left: 55%;
  top: 50%;
  width: 1.4rem;
  height: 1.4rem;
  margin: -0.7rem 0 0 -0.7rem;
  border-radius: 50%;
  background: #e6a15a;
  box-shadow: 0 0 0 6px rgba(230, 161, 90, 0.25), 0 20px 30px rgba(0, 0, 0, 0.5);
}

.visit-pin span {
  position: absolute;
  inset: -1rem;
  border-radius: 50%;
  border: 1px solid rgba(230, 161, 90, 0.6);
  animation: ripple 2.4s var(--ease-out-expo) infinite;
}

@keyframes ripple {
  from { transform: scale(0.4); opacity: 1; }
  to { transform: scale(2.6); opacity: 0; }
}

.visit-station {
  position: absolute;
  left: calc(55% + 1.8rem);
  top: 30%;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem 0.4rem 0.4rem;
  border-radius: 0.75rem;
  background: rgba(14, 12, 10, 0.8);
  border: 1px solid rgba(244, 236, 225, 0.1);
  font-size: 0.8rem;
  color: #f4ece1;
  translate: 0 -50%;
}
</style>
