<template>
  <div ref="root" class="about">
    <!-- Statement: words light up as you scroll -->
    <section class="section pt-10">
      <p v-reveal class="eyebrow">{{ $t('about.eyebrow') }}</p>
      <p ref="statement" class="statement">{{ $t('about.statement', { name: business.name, street: business.street }) }}</p>
    </section>

    <!-- Story with layered collage -->
    <section class="section story">
      <div v-mask class="collage" aria-hidden="true">
        <span class="collage-glow"></span>
        <img v-parallax="-0.15" :src="croissantImg" alt="" class="collage-a" />
        <img v-parallax="-0.45" :src="pretzelImg" alt="" class="collage-b" />
        <img v-parallax="0.25" :src="macaronsImg" alt="" class="collage-c" />
      </div>
      <div>
        <h2 v-split class="display-title text-5xl sm:text-7xl">{{ $t('about.storyTitle') }}</h2>
        <p v-reveal class="story-text">{{ $t('about.story1', { name: business.name }) }}</p>
        <p v-reveal class="story-text">
          {{ business.transit ? $t('about.story2Transit', { street: business.street, city: business.city, transit: business.transit }) : $t('about.story2', { street: business.street, city: business.city }) }}
        </p>
      </div>
    </section>

    <!-- Values -->
    <section class="section mt-32">
      <p v-reveal class="eyebrow">{{ $t('about.valuesEyebrow') }}</p>
      <h2 v-split class="display-title text-5xl sm:text-7xl mt-3 max-w-3xl">{{ $t('about.valuesTitle') }}</h2>
      <div v-reveal.stagger class="values">
        <article v-for="(value, index) in values" :key="value.title" v-tilt="{ max: 6 }" class="value lux-card">
          <span class="value-num" data-depth="30">0{{ index + 1 }}</span>
          <font-awesome-icon :icon="value.icon" class="value-icon" data-depth="50" />
          <h3 class="value-title" data-depth="25">{{ value.title }}</h3>
          <p data-depth="15">{{ value.text }}</p>
        </article>
      </div>
    </section>

    <!-- Promise -->
    <section class="section promise">
      <p v-reveal class="eyebrow justify-center">{{ $t('about.promiseEyebrow') }}</p>
      <h2 v-split class="display-title text-5xl sm:text-7xl mt-4">
        {{ $t('about.promise1') }} <em>{{ $t('about.promise2') }}</em>
      </h2>
      <p v-reveal class="mx-auto mt-6 max-w-xl text-lg text-cream-muted">{{ $t('about.promiseText') }}</p>
      <div v-reveal class="mt-10 flex flex-wrap justify-center gap-3">
        <router-link v-magnetic="0.2" to="/products" class="btn-amber">{{ $t('common.shopNow') }} <font-awesome-icon icon="arrow-right" /></router-link>
        <router-link to="/contact" class="btn-ghost">{{ $t('about.getInTouch') }}</router-link>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { business } from '@/config/business'
import { useI18n } from 'vue-i18n'
import { gsap, SplitText, prefersReducedMotion } from '@/motion'
import croissantImg from '@/assets/bakery/croissant-butter.png'
import pretzelImg from '@/assets/bakery/pretzel.png'
import macaronsImg from '@/assets/bakery/macarons.png'

const root = ref(null)
const statement = ref(null)

const { t } = useI18n()
const values = ['ingredients', 'methods', 'waste', 'neighbourhood'].map((key, index) => ({
  icon: ['wheat-awn', 'fire', 'leaf', 'store'][index],
  title: t(`about.values.${key}.title`),
  text: t(`about.values.${key}.text`)
}))

let ctx = null
let split = null

onMounted(async () => {
  if (prefersReducedMotion()) return
  await document.fonts?.ready
  ctx = gsap.context(() => {
    split = SplitText.create(statement.value, { type: 'words' })
    gsap.fromTo(split.words, { opacity: 0.15 }, {
      opacity: 1,
      stagger: 0.1,
      ease: 'none',
      scrollTrigger: { trigger: statement.value, start: 'top 80%', end: 'bottom 50%', scrub: true }
    })
  }, root.value)
})

onBeforeUnmount(() => {
  ctx?.revert()
  split?.revert()
})
</script>

<style scoped>
.statement {
  margin-top: 1.5rem;
  max-width: 64rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: clamp(2.2rem, 5vw, 4.5rem);
  line-height: 1.08;
  letter-spacing: -0.015em;
  color: #f4ece1;
}

.story {
  display: grid;
  gap: 3rem;
  align-items: center;
  margin-top: 8rem;
}

@media (min-width: 1024px) {
  .story {
    grid-template-columns: 1fr 1fr;
    gap: 5rem;
  }
}

.collage {
  position: relative;
  aspect-ratio: 1;
  border-radius: 2rem;
  background: linear-gradient(180deg, #1e1914, #15120f);
  border: 1px solid rgba(244, 236, 225, 0.07);
  overflow: hidden;
}

.collage-glow {
  position: absolute;
  inset: 15%;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(230, 161, 90, 0.3), transparent);
  filter: blur(20px);
}

.collage img {
  position: absolute;
  filter: drop-shadow(0 30px 30px rgba(0, 0, 0, 0.55));
}

.collage-a {
  width: 66%;
  left: 17%;
  top: 22%;
}

.collage-b {
  width: 34%;
  right: 6%;
  top: 6%;
}

.collage-c {
  width: 26%;
  left: 6%;
  bottom: 6%;
}

.story-text {
  margin-top: 1.5rem;
  max-width: 32rem;
  font-size: 1.1rem;
  line-height: 1.75;
}

.values {
  display: grid;
  gap: 1rem;
  margin-top: 3rem;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 15rem), 1fr));
}

.value {
  position: relative;
  min-height: 17rem;
  padding: 1.75rem;
  overflow: visible;
  transform-style: preserve-3d;
}

.value-num {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #7d7061;
}

.value-icon {
  display: block;
  margin-top: 2.5rem;
  font-size: 1.6rem;
  color: #e6a15a;
}

.value-title {
  margin-top: 1rem;
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 2rem;
  font-weight: 400;
  line-height: 1.05;
}

.value p {
  margin-top: 0.6rem;
  color: #b9ab98;
}

.promise {
  margin-top: 10rem;
  text-align: center;
}

.promise h2 {
  max-width: 56rem;
  margin-left: auto;
  margin-right: auto;
}

.promise em {
  color: #e6a15a;
}
</style>
