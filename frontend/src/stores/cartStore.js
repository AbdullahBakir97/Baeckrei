import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useCartStore = defineStore('cart', () => {
  // State
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const cartTotal = computed(() => {
    if (!items.value?.length) return 0
    return items.value.reduce((total, item) => {
      return total + Number(item.total_price)
    }, 0)
  })

  const itemCount = computed(() => {
    if (!items.value?.length) return 0
    return items.value.reduce((total, item) => total + item.quantity, 0)
  })

  // Actions
  async function fetchCart() {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get(`${API_URL}/api/shopping-cart/current/`)
      items.value = response.data.items || []
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch cart'
      items.value = []
    } finally {
      loading.value = false
    }
  }

  async function addItem(productId, quantity = 1) {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_URL}/api/shopping-cart/add_item/`, {
        product_id: productId,
        quantity: quantity
      })
      items.value = response.data.items || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to add item to cart'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function removeItem(productId) {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_URL}/api/shopping-cart/remove_item/`, {
        product_id: productId
      })
      items.value = response.data.items || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to remove item from cart'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function updateItemQuantity(productId, quantity) {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_URL}/api/shopping-cart/update_item/`, {
        product_id: productId,
        quantity: quantity
      })
      items.value = response.data.items || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to update cart'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function clearCart() {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_URL}/api/shopping-cart/clear/`)
      items.value = []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to clear cart'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Initialize cart on store creation
  fetchCart()

  return {
    // State
    items,
    loading,
    error,
    // Computed
    cartTotal,
    itemCount,
    // Actions
    fetchCart,
    addItem,
    removeItem,
    updateItemQuantity,
    clearCart
  }
})
