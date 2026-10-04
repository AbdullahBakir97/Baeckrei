import { onBeforeUnmount, onMounted, reactive } from 'vue'
import axios from '@/plugins/axios'

// Counts for the admin sidebar (unread messages, screens online), shared by
// every admin page and refreshed on navigation and once a minute.
const studio = reactive({ unread_messages: 0, subscribers: 0, scheduled_posts: 0, draft_posts: 0, screens: 0, screens_online: 0 })
let users = 0
let timer = null

export async function refreshStudio() {
  try {
    const { data } = await axios.get('/api/studio/summary/')
    Object.assign(studio, data)
  } catch { /* signed out or offline: keep the last counts */ }
}

export function useStudioSummary() {
  onMounted(() => {
    users += 1
    if (users === 1) {
      refreshStudio()
      timer = setInterval(refreshStudio, 60_000)
    }
  })
  onBeforeUnmount(() => {
    users -= 1
    if (!users) clearInterval(timer)
  })
  return { studio, refreshStudio }
}
