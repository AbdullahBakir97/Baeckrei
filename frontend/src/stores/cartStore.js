import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/plugins/axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useCartStore = defineStore('cart', () => {
  // State
  const state = ref({
    items: [],
    loading: false,
    error: null,
    subtotal: '0.00',
    tax: '0.00',
    total: '0.00',
    total_items: 0
  })

  // Computed
  const isLoading = computed(() => state.value.loading)
  const cartIsEmpty = computed(() => !state.value.items?.length)
  const items = computed(() => state.value.items || [])
  const subtotal = computed(() => Number(state.value.subtotal || 0))
  const tax = computed(() => Number(state.value.tax || 0))
  const total = computed(() => Number(state.value.total || 0))
  const itemCount = computed(() => state.value.total_items || 0)
  const error = computed(() => state.value.error)

  // Actions
  const resetError = () => {
    state.value.error = null
  }

  async function fetchCart() {
    state.value.loading = true
    state.value.error = null
    try {
      const response = await axios.get(`${API_URL}/api/shopping-cart/current/`, {
        withCredentials: true
      })
      
      state.value = {
        ...state.value,
        items: response.data.items || [],
        subtotal: response.data.subtotal || '0.00',
        tax: response.data.tax || '0.00',
        total: response.data.total || '0.00',
        total_items: response.data.total_items || 0,
        loading: false,
        error: null
      }
      return response.data
    } catch (error) {
      console.error('Error fetching cart:', error)
      state.value.error = error.response?.data?.message || 'Failed to load cart'
      throw error
    } finally {
      state.value.loading = false
    }
  }

  async function addItem(productId, quantity = 1) {
    state.value.loading = true
    state.value.error = null
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/shopping-cart/add_item/`, {
        product_id: productId,
        quantity
      }, {
        withCredentials: true
      })
      state.value.items = response.data.items || []
    } catch (error) {
      console.error('Error adding item to cart:', error)
      state.value.error = error.response?.data?.message || 'Error adding item to cart'
      throw error
    } finally {
      state.value.loading = false
    }
  }

  async function removeItem(productId) {
    state.value.loading = true
    state.value.error = null
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/shopping-cart/remove_item/`, {
        product_id: productId
      }, {
        withCredentials: true
      })
      state.value.items = response.data.items || []
    } catch (error) {
      console.error('Error removing item from cart:', error)
      state.value.error = error.response?.data?.message || 'Error removing item from cart'
      throw error
    } finally {
      state.value.loading = false
    }
  }

  async function updateQuantity(productId, quantity) {
    state.value.loading = true
    state.value.error = null
    try {
      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/shopping-cart/update_item/`, {
        product_id: productId,
        quantity
      }, {
        withCredentials: true
      })
      state.value.items = response.data.items || []
    } catch (error) {
      console.error('Error updating item quantity:', error)
      state.value.error = error.response?.data?.message || 'Error updating item quantity'
      throw error
    } finally {
      state.value.loading = false
    }
  }

  async function clearCart() {
    state.value.loading = true
    state.value.error = null
    try {
      const response = await axios.post(`${API_URL}/api/shopping-cart/clear/`, {}, {
        withCredentials: true
      })
      state.value.items = []
      return true
    } catch (error) {
      console.error('Error clearing cart:', error)
      state.value.error = error.response?.data?.message || 'Error clearing cart'
      return false
    } finally {
      state.value.loading = false
    }
  }

  // Initialize cart on store creation
  fetchCart()

  return {
    // State
    state,
    // Computed
    isLoading,
    cartIsEmpty,
    items,
    subtotal,
    tax,
    total,
    itemCount,
    error,
    // Actions
    fetchCart,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    resetError
  }
})
