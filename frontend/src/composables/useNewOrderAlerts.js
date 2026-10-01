import { onBeforeUnmount, onMounted, ref } from 'vue'
import axios from '@/plugins/axios'
import { useToast } from '@/composables/useToast'
import { t } from '@/i18n'

// Tells whoever has the admin open that an order came in: a toast, a soft
// chime, a count in the browser tab and on "Orders", and (if allowed) a
// desktop notification. Checks every 30 seconds while the tab is visible.
const INTERVAL = 30_000
const unseen = ref(0)
const notificationsOn = ref(typeof Notification !== 'undefined' && Notification.permission === 'granted')

function chime() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext
    const ctx = new AudioContext()
    ;[880, 1320].forEach((frequency, index) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      const start = ctx.currentTime + index * 0.16
      osc.frequency.value = frequency
      gain.gain.setValueAtTime(0.0001, start)
      gain.gain.exponentialRampToValueAtTime(0.15, start + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.5)
      osc.connect(gain).connect(ctx.destination)
      osc.start(start)
      osc.stop(start + 0.55)
    })
    setTimeout(() => ctx.close(), 1200)
  } catch {
    // Sound is a bonus; browsers may block it until the page is clicked.
  }
}

export async function enableOrderNotifications() {
  if (typeof Notification === 'undefined') return false
  notificationsOn.value = (await Notification.requestPermission()) === 'granted'
  return notificationsOn.value
}

export function markOrdersSeen() {
  unseen.value = 0
}

export function useNewOrderAlerts() {
  const { showToast } = useToast()
  const baseTitle = document.title.replace(/^\(\d+\) /, '')
  let known = null
  let timer = null

  const setTitle = () => {
    const title = document.title.replace(/^\(\d+\) /, '') || baseTitle
    document.title = unseen.value ? `(${unseen.value}) ${title}` : title
  }

  async function check() {
    if (document.hidden) return
    try {
      const { data } = await axios.get('/api/orders/orders/recent_orders/')
      const ids = data.map(order => order.id)
      if (known) {
        const fresh = data.filter(order => !known.has(order.id))
        if (fresh.length) {
          unseen.value += fresh.length
          const newest = fresh[0]
          showToast(t('admin.alerts.newOrder', { number: newest.order_number }), 'success', 8000)
          chime()
          if (notificationsOn.value) {
            new Notification(t('admin.alerts.newOrderTitle'), { body: newest.order_number, tag: 'new-order' })
          }
          window.dispatchEvent(new CustomEvent('admin:new-orders'))
        }
      }
      known = new Set([...(known || []), ...ids])
      setTitle()
    } catch {
      // Offline or signed out; try again on the next round.
    }
  }

  const onVisible = () => { if (!document.hidden) check() }

  onMounted(() => {
    check()
    timer = setInterval(check, INTERVAL)
    document.addEventListener('visibilitychange', onVisible)
  })

  onBeforeUnmount(() => {
    clearInterval(timer)
    document.removeEventListener('visibilitychange', onVisible)
    unseen.value = 0
    setTitle()
  })

  return { unseen, notificationsOn, setTitle }
}
