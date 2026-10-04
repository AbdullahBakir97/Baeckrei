<template>
  <transition name="announce">
    <div v-if="text && !dismissed" class="announce" role="status">
      <font-awesome-icon icon="bullhorn" class="announce-icon" aria-hidden="true" />
      <p>{{ text }}</p>
      <button type="button" class="announce-close" :aria-label="$t('common.close')" @click="dismiss">
        <font-awesome-icon icon="xmark" />
      </button>
    </div>
  </transition>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { business } from '@/config/business'

// The notice the bakery sets in the admin (Settings → Shop notice), e.g.
// holidays. Closing it hides this text for the rest of the visit.
const { locale } = useI18n()
const text = computed(() => (locale.value !== 'de' && business.announcementEn) || business.announcement)
const KEY = 'announcement-dismissed'
const dismissedText = ref((() => { try { return sessionStorage.getItem(KEY) } catch { return null } })())
const dismissed = computed(() => dismissedText.value === text.value)
function dismiss() {
  dismissedText.value = text.value
  try { sessionStorage.setItem(KEY, text.value) } catch { /* ignore */ }
}
</script>

<style scoped>
.announce {
  position: relative;
  z-index: 45;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.6rem 3rem;
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
  color: #14110e;
  background: linear-gradient(90deg, #e6a15a, #f2c48d, #e6a15a);
}
.announce-icon { flex: none; }
.announce-close {
  position: absolute;
  inset-inline-end: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  padding: 0.35rem 0.5rem;
  border-radius: 0.5rem;
  color: #14110e;
}
.announce-close:hover { background: rgba(20, 17, 14, 0.1); }
.announce-enter-active, .announce-leave-active { transition: opacity 0.3s, transform 0.4s; }
.announce-enter-from, .announce-leave-to { opacity: 0; transform: translateY(-100%); }
</style>
