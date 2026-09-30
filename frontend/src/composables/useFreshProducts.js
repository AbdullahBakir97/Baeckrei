import { ref } from 'vue'
import axios from '@/plugins/axios'

// Wishlist and compare keep product snapshots in local storage. Reload them
// from the API so prices, stock and availability are current; products that
// no longer exist are reported as missing.
export function useFreshProducts() {
  const products = ref([])
  const missingIds = ref([])
  const loading = ref(false)

  const load = async (items) => {
    loading.value = true
    try {
      const results = await Promise.allSettled(
        items.map(item => axios.get(`/api/products/${item.id}/`))
      )
      products.value = results
        .map((result, index) => result.status === 'fulfilled' ? result.value.data : null)
        .filter(Boolean)
      missingIds.value = items
        .filter((item, index) => results[index].status === 'rejected')
        .map(item => item.id)
    } finally {
      loading.value = false
    }
  }

  return { products, missingIds, loading, load }
}
