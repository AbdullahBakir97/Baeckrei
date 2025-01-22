import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWishlistStore = defineStore('wishlist', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Load wishlist items from localStorage on initialization
  const initializeFromStorage = () => {
    const savedItems = localStorage.getItem('wishlist')
    if (savedItems) {
      items.value = JSON.parse(savedItems)
    }
  }

  // Save to localStorage whenever items change
  const saveToStorage = () => {
    localStorage.setItem('wishlist', JSON.stringify(items.value))
  }

  const fetchItems = () => {
    loading.value = true
    try {
      initializeFromStorage()
    } catch (err) {
      error.value = err.message
      console.error('Error fetching wishlist:', err)
    } finally {
      loading.value = false
    }
  }

  const addItem = async (product) => {
    if (!items.value.some(item => item.id === product.id)) {
      items.value.push(product)
      saveToStorage()
    }
  }

  const removeItem = async (productId) => {
    items.value = items.value.filter(item => item.id !== productId)
    saveToStorage()
  }

  const clearWishlist = () => {
    items.value = []
    saveToStorage()
  }

  // Initialize on store creation
  initializeFromStorage()

  return {
    items,
    loading,
    error,
    fetchItems,
    addItem,
    removeItem,
    clearWishlist
  }
})
