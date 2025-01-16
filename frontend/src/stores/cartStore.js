import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import axios from '@/plugins/axios'

export const useCartStore = defineStore('cart', () => {
  // State
  const state = ref({
    items: [],
    loading: false,
    error: null,
    subtotal: '0.00',
    tax: '0.00',
    total: '0.00',
    total_items: 0,
    lastSuccessfulState: null,
    initialized: false,
    operationInProgress: false
  })

  // Load persisted state on initialization
  const loadPersistedState = () => {
    try {
      const savedState = localStorage.getItem('cart-state')
      if (savedState) {
        const parsedState = JSON.parse(savedState)
        state.value = {
          ...parsedState,
          loading: false,
          error: null,
          initialized: false
        }
      }
    } catch (error) {
      console.error('Error loading persisted state:', error)
    }
  }

  // Watch for cart changes and sync with localStorage
  watch(
    () => ({
      items: state.value.items,
      subtotal: state.value.subtotal,
      tax: state.value.tax,
      total: state.value.total,
      total_items: state.value.total_items
    }),
    async (newState) => {
      try {
        // Only save to localStorage if we have valid data
        if (newState.items && !state.value.loading) {
          localStorage.setItem('cart-state', JSON.stringify(newState))
          
          // Verify cart state with backend periodically
          if (!state.value.operationInProgress) {
            const lastSync = localStorage.getItem('last-cart-sync')
            const now = Date.now()
            if (!lastSync || now - parseInt(lastSync) > 60000) { // Sync every minute
              await fetchCart()
              localStorage.setItem('last-cart-sync', now.toString())
            }
          }
        }
      } catch (error) {
        console.error('Error syncing cart state:', error)
      }
    },
    { deep: true }
  )

  // Computed
  const isLoading = computed(() => state.value.loading)
  const cartIsEmpty = computed(() => !state.value.items?.length)
  const items = computed(() => state.value.items || [])
  const subtotal = computed(() => Number(state.value.subtotal || 0))
  const tax = computed(() => Number(state.value.tax || 0))
  const total = computed(() => Number(state.value.total || 0))
  const itemCount = computed(() => state.value.total_items || 0)
  const error = computed(() => state.value.error)
  const isInitialized = computed(() => state.value.initialized)

  // Actions
  const resetError = () => {
    state.value.error = null
  }

  async function fetchCart() {
    if (state.value.loading) return
    
    state.value.loading = true
    state.value.error = null
    
    try {
      const response = await axios.get('/api/shopping-cart/current/')
      updateCartState(response.data)
      state.value.initialized = true
      console.log('Cart data fetched:', response.data)
      return response.data
    } catch (error) {
      handleError('Error fetching cart', error)
      throw error
    } finally {
      state.value.loading = false
    }
  }

  // Helper function to handle cart operations with retry
  async function executeCartOperation(operation, errorMessage, maxRetries = 2) {
    if (state.value.operationInProgress) {
      console.log('Operation in progress, skipping...')
      return
    }

    let retryCount = 0
    saveCurrentState()
    state.value.loading = true
    state.value.operationInProgress = true
    state.value.error = null

    while (retryCount <= maxRetries) {
      try {
        const response = await operation()
        if (response?.data) {
          updateCartState(response.data)
          return response.data
        }
        return null
      } catch (error) {
        console.error(`Attempt ${retryCount + 1} failed:`, error)
        if (retryCount === maxRetries) {
          handleError(errorMessage, error)
          restoreLastState()
          throw error
        }
        retryCount++
        await new Promise(resolve => setTimeout(resolve, 1000 * retryCount)) // Exponential backoff
      }
    }
  }

  async function addItem(productId, quantity = 1) {
    return executeCartOperation(
      async () => {
        const response = await axios.post('/api/shopping-cart/add/', {
          product_id: productId,
          quantity: quantity
        })
        return response
      },
      'Failed to add item to cart'
    )
  }

  async function updateQuantity(productId, quantity) {
    if (quantity < 1) {
      return removeItem(productId)
    }
    return executeCartOperation(
      async () => {
        const response = await axios.put('/api/shopping-cart/update/', {
          product_id: productId,
          quantity: quantity
        })
        return response
      },
      'Failed to update cart quantity'
    )
  }

  async function removeItem(productId) {
    return executeCartOperation(
      async () => {
        const response = await axios.delete('/api/shopping-cart/remove/', {
          data: { product_id: productId }
        })
        return response
      },
      'Failed to remove item from cart'
    )
  }

  async function clearCart() {
    return executeCartOperation(
      () => axios.post('/api/shopping-cart/clear/'),
      'Error clearing cart'
    )
  }

  // Helper function to save current state
  function saveCurrentState() {
    state.value.lastSuccessfulState = JSON.parse(JSON.stringify({
      items: state.value.items,
      subtotal: state.value.subtotal,
      tax: state.value.tax,
      total: state.value.total,
      total_items: state.value.total_items
    }))
  }

  // Helper function to restore last successful state
  function restoreLastState() {
    if (state.value.lastSuccessfulState) {
      const restoredState = state.value.lastSuccessfulState
      state.value = {
        ...state.value,
        items: restoredState.items,
        subtotal: restoredState.subtotal,
        tax: restoredState.tax,
        total: restoredState.total,
        total_items: restoredState.total_items,
        loading: false
      }
    }
  }

  // Helper function to handle errors
  function handleError(message, error) {
    console.error(message + ':', error)
    state.value.error = error.response?.data?.detail || error.message || message
  }

  // Helper function to update cart state
  function updateCartState(data) {
    if (!data) return

    try {
      state.value = {
        ...state.value,
        items: data.items || [],
        subtotal: data.subtotal || '0.00',
        tax: data.tax || '0.00',
        total: data.total || '0.00',
        total_items: data.total_items || 0,
        error: null,
        initialized: true
      }
      state.value.lastSuccessfulState = { ...state.value }
    } catch (error) {
      console.error('Error updating cart state:', error)
      handleError('Failed to update cart state', error)
    }
  }

  // Initialize cart on store creation
  const initializeCart = async () => {
    try {
      loadPersistedState()
      await fetchCart() // Always fetch from backend to ensure consistency
    } catch (error) {
      console.error('Error initializing cart:', error)
      // If backend fetch fails, we still have local state as fallback
    }
  }

  initializeCart()

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
    isInitialized,
    // Actions
    fetchCart,
    addItem,
    removeItem,
    updateQuantity,
    clearCart,
    resetError
  }
})
