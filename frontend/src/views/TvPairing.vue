<template>
  <div class="tv">
    <div class="tv-card">
      <p class="tv-logo"><em>{{ name.charAt(0) }}</em>{{ name.slice(1) }}</p>
      <template v-if="remembered && !changing">
        <h1>{{ tr('tv.remembered', { name: remembered.name, n: countdown }) }}</h1>
        <div class="tv-actions">
          <button type="button" class="tv-btn" autofocus @click="start(remembered)">{{ tr('tv.open') }}</button>
          <button type="button" class="tv-btn is-ghost" @click="changing = true">{{ tr('tv.change') }}</button>
        </div>
      </template>
      <form v-else @submit.prevent="pair">
        <h1>{{ tr('tv.title') }}</h1>
        <p class="tv-intro">{{ tr('tv.intro') }}</p>
        <label class="sr-only" for="tv-code">{{ tr('tv.code') }}</label>
        <input id="tv-code" ref="input" v-model="code" class="tv-code" inputmode="numeric" pattern="[0-9]{4}" maxlength="4"
               autocomplete="off" autofocus :placeholder="'0000'" @input="code = code.replace(/\\D/g, ''); code.length === 4 && pair()" />
        <p v-if="message" class="tv-message" role="alert">{{ message }}</p>
        <button type="submit" class="tv-btn" :disabled="code.length !== 4 || busy">{{ busy ? '…' : tr('tv.open') }}</button>
      </form>
      <p class="tv-tip">{{ tr('tv.tip') }}</p>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import { i18n } from '@/i18n'
import { business } from '@/config/business'

// /tv on the shop's TV: type the screen's 4-digit code with the remote once.
// The TV remembers it and opens that screen by itself after every restart
// (set the TV's or the kiosk app's start page to /tv).
const router = useRouter()
const KEY = 'menu-screen'
const name = business.name || 'Backlover'
const code = ref('')
const busy = ref(false)
const message = ref('')
const changing = ref(false)
const countdown = ref(8)
const input = ref(null)
const tr = (key, params) => i18n.global.t(`board.${key}`, params || {})
const remembered = ref((() => { try { return JSON.parse(localStorage.getItem(KEY) || 'null') } catch { return null } })())

function start(screen) {
  try { localStorage.setItem(KEY, JSON.stringify(screen)) } catch { /* private mode */ }
  router.replace(`/menu-board/${screen.slug}`)
}

async function pair() {
  if (code.value.length !== 4 || busy.value) return
  busy.value = true
  message.value = ''
  try {
    const { data } = await axios.get(`/api/menu-screens/pair/${code.value}/`)
    message.value = tr('tv.starting', { name: data.name })
    start(data)
  } catch (err) {
    message.value = err.response ? tr('tv.wrong') : tr('tv.offline')
    code.value = ''
    input.value?.focus()
  } finally {
    busy.value = false
  }
}

let timer = null
onMounted(() => {
  if (remembered.value) {
    timer = setInterval(() => {
      if (changing.value) return clearInterval(timer)
      countdown.value -= 1
      if (countdown.value <= 0) { clearInterval(timer); start(remembered.value) }
    }, 1000)
  }
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.tv { position: fixed; inset: 0; z-index: 50; display: grid; place-items: center; padding: 4vmin; font-size: min(1.6vw, 2.8vh);
  color: #f4ece1; background: radial-gradient(60% 60% at 50% 30%, rgba(230, 161, 90, 0.18), transparent 70%), #0e0c0a; }
.tv-card { width: min(100%, 42em); text-align: center; }
.tv-logo { font-family: 'Instrument Serif', Georgia, serif; font-size: 3.4em; line-height: 1; }
.tv-logo em { color: #e6a15a; font-style: normal; }
h1 { margin-top: 1.2em; font-family: 'Instrument Serif', Georgia, serif; font-size: 2.6em; font-weight: 400; line-height: 1.15; }
.tv-intro { margin: 0.8em auto 0; max-width: 30em; font-size: 1.1em; line-height: 1.5; color: #b9ab98; }
.tv-code { display: block; width: 6.2em; margin: 1em auto 0.6em; padding: 0.15em 0.3em; border-radius: 0.3em; font: 700 4em/1 'Manrope Variable', monospace;
  letter-spacing: 0.35em; text-align: center; text-indent: 0.35em; color: #f4ece1; background: rgba(244, 236, 225, 0.06); border: 2px solid rgba(244, 236, 225, 0.15); }
.tv-code:focus { outline: none; border-color: #e6a15a; box-shadow: 0 0 0 0.25em rgba(230, 161, 90, 0.25); }
.tv-message { margin-bottom: 0.8em; font-size: 1.05em; color: #f2c48d; }
.tv-actions { display: flex; justify-content: center; gap: 0.8em; margin-top: 1.5em; }
.tv-btn { padding: 0.75em 1.6em; border-radius: 9999px; font-size: 1.15em; font-weight: 700; color: #0e0c0a; background: #e6a15a; }
.tv-btn:focus-visible { outline: 0.2em solid #f4ece1; outline-offset: 0.2em; }
.tv-btn:disabled { opacity: 0.4; }
.tv-btn.is-ghost { color: #f4ece1; background: rgba(244, 236, 225, 0.1); }
.tv-tip { margin-top: 2em; font-size: 0.9em; color: #7d7061; }
</style>
