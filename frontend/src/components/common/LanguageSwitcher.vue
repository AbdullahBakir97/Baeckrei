<template>
  <!-- Buttons side by side (mobile menu, admin) -->
  <div v-if="inline" class="lang-inline" role="group" :aria-label="$t('nav.language')">
    <button v-for="l in LOCALES" :key="l.code" type="button" class="lang-chip" :class="{ 'is-on': l.code === locale }"
            :lang="l.code" :aria-pressed="l.code === locale" @click="choose(l.code)">
      {{ l.label }}
    </button>
  </div>

  <!-- Menu (navbar) -->
  <div v-else ref="root" class="lang-menu" @keydown.escape="close">
    <button ref="trigger" type="button" class="lang-trigger" aria-haspopup="menu" :aria-expanded="open"
            :aria-label="`${$t('nav.language')}: ${current.label}`" @click="open = !open">
      <font-awesome-icon icon="globe" />
      <span class="lang-code">{{ current.code.toUpperCase() }}</span>
    </button>
    <transition name="lang-pop">
      <ul v-if="open" class="lang-pop" role="menu">
        <li v-for="l in LOCALES" :key="l.code" role="none">
          <button type="button" role="menuitemradio" :aria-checked="l.code === locale" :lang="l.code" :dir="l.dir || 'ltr'"
                  class="lang-option" :class="{ 'is-on': l.code === locale }" @click="choose(l.code)">
            <span>{{ l.label }}</span>
            <font-awesome-icon v-if="l.code === locale" icon="check" />
          </button>
        </li>
      </ul>
    </transition>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { LOCALES, setLocale } from '@/i18n'

// Switches the whole site between German, English and Arabic (right to left).
defineProps({ inline: { type: Boolean, default: false } })
const emit = defineEmits(['changed'])
const { locale } = useI18n()
const open = ref(false)
const root = ref(null)
const trigger = ref(null)
const current = computed(() => LOCALES.find(l => l.code === locale.value) || LOCALES[0])

function choose(code) {
  setLocale(code)
  open.value = false
  emit('changed', code)
}
function close() {
  if (!open.value) return
  open.value = false
  trigger.value?.focus()
}
const onOutside = (event) => { if (open.value && root.value && !root.value.contains(event.target)) open.value = false }
onMounted(() => document.addEventListener('pointerdown', onOutside))
onBeforeUnmount(() => document.removeEventListener('pointerdown', onOutside))
</script>

<style scoped>
.lang-menu { position: relative; }
.lang-trigger { display: inline-flex; align-items: center; gap: 0.4rem; height: 2.5rem; padding: 0 0.75rem; border-radius: 9999px;
  font-size: 0.75rem; font-weight: 800; letter-spacing: 0.08em; color: #d9cfc2; transition: background 0.25s, color 0.25s; }
.lang-trigger:hover, .lang-trigger[aria-expanded='true'] { color: #f4ece1; background: rgba(244, 236, 225, 0.07); }
.lang-pop { position: absolute; top: calc(100% + 0.5rem); inset-inline-end: 0; z-index: 60; min-width: 10rem; padding: 0.35rem;
  border-radius: 1rem; background: rgba(30, 25, 20, 0.97); border: 1px solid rgba(244, 236, 225, 0.1); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(12px); }
.lang-option { display: flex; align-items: center; justify-content: space-between; gap: 1rem; width: 100%; padding: 0.55rem 0.8rem;
  border-radius: 0.7rem; font-size: 0.9rem; color: #d9cfc2; text-align: start; }
.lang-option:hover { color: #f4ece1; background: rgba(244, 236, 225, 0.06); }
.lang-option.is-on { color: #e6a15a; font-weight: 700; }
.lang-option[lang='ar'] { font-size: 1rem; }
.lang-pop-enter-active, .lang-pop-leave-active { transition: opacity 0.18s, transform 0.25s cubic-bezier(0.16, 1, 0.3, 1); }
.lang-pop-enter-from, .lang-pop-leave-to { opacity: 0; transform: translateY(-6px) scale(0.98); }
.lang-inline { display: inline-flex; flex-wrap: wrap; gap: 0.35rem; padding: 0.25rem; border-radius: 9999px; background: rgba(244, 236, 225, 0.05); }
.lang-chip { padding: 0.4rem 0.9rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; color: #b9ab98; transition: background 0.2s, color 0.2s; }
.lang-chip:hover { color: #f4ece1; }
.lang-chip.is-on { color: #0e0c0a; background: #f4ece1; }
</style>
