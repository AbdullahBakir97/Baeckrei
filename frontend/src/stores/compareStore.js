import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCompareStore = defineStore('compare', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Load compare items from localStorage on initialization
  const initializeFromStorage = () => {
    const savedItems = localStorage.getItem('compare')
    if (savedItems) {
      items.value = JSON.parse(savedItems)
    }
  }

  // Save to localStorage whenever items change
  const saveToStorage = () => {
    localStorage.setItem('compare', JSON.stringify(items.value))
  }

  const fetchItems = () => {
    loading.value = true
    try {
      initializeFromStorage()
    } catch (err) {
      error.value = err.message
      console.error('Error fetching compare items:', err)
    } finally {
      loading.value = false
    }
  }

  const addItem = async (product) => {
    if (items.value.length >= 4) {
      throw new Error('Maximum 4 items can be compared')
    }
    if (!items.value.some(item => item.id === product.id)) {
      items.value.push(product)
      saveToStorage()
    }
  }

  const removeItem = async (productId) => {
    items.value = items.value.filter(item => item.id !== productId)
    saveToStorage()
  }

  const clearCompare = () => {
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
    clearCompare
  }
})
