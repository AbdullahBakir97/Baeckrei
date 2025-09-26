import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { useAuthStore } from './authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const BASE_URL = `${API_URL}/api/shopping-cart`

// Get CSRF token from cookie
function getCSRFToken() {
  const name = 'csrftoken='
  const decodedCookie = decodeURIComponent(document.cookie)
  const cookieArray = decodedCookie.split(';')
  for (let cookie of cookieArray) {
    cookie = cookie.trim()
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length)
    }
  }
  return null
}

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    subtotal: '0.00',
    tax: '0.00',
    total: '0.00',
    total_items: 0,
    loading: false,
    error: null,
    dropdownVisible: false,
    lastFetch: null
  }),

  getters: {
    isLoading: state => state.loading,
    cartIsEmpty: state => state.items.length === 0,
    itemCount: state => state.total_items,
    subtotalAmount: state => state.subtotal,
    taxAmount: state => state.tax,
    totalAmount: state => state.total,
    displayedItems: state => state.items,
    isDropdownVisible: state => state.dropdownVisible
  },

  actions: {
    toggleDropdown() {
      this.dropdownVisible = !this.dropdownVisible
    },

    showDropdown() {
      this.dropdownVisible = true
    },

    hideDropdown() {
      this.dropdownVisible = false
    },

    resetError() {
      this.error = null
    },

    // UUID validation helper
    validateUUID(productId) {
      if (!productId) {
        throw new Error('Product ID is required')
      }

      // Convert to string and clean up any whitespace
      const cleanId = String(productId).trim()

      // UUID regex pattern
      const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

      if (!uuidPattern.test(cleanId)) {
        throw new Error(`Invalid product ID format: ${productId}. Must be a valid UUID.`)
      }

      return cleanId
    },

    async fetchCart({ silent = false } = {}) {
      const authStore = useAuthStore()
      
      try {
        if (!silent) {
          this.loading = true
        }
        this.error = null

        const headers = {
          'X-CSRFToken': getCSRFToken()
        }
        
        if (authStore.isAuthenticated) {
          headers['Authorization'] = `Bearer ${authStore.token}`
        }

        const response = await axios.get(`${BASE_URL}/current/`, {
          withCredentials: true,
          headers
        })

        if (response.data) {
          // Update cart state using _updateCartState to ensure proper processing
          this._updateCartState(response.data)
          this.lastFetch = Date.now()
        }
      } catch (error) {
        if (!silent) {
          console.error('Error fetching cart:', error)
          this.error = error.response?.data?.detail || 'Error fetching cart'
        }
      } finally {
        if (!silent) {
          this.loading = false
        }
      }
    },

    async addItem(productId, quantity = 1) {
      const authStore = useAuthStore()
      
      try {
        this.loading = true
        this.error = null
        
        const validProductId = this.validateUUID(productId)
        const headers = {
          'X-CSRFToken': getCSRFToken(),
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
        
        if (authStore.isAuthenticated) {
          headers['Authorization'] = `Bearer ${authStore.token}`
        }

        // First check if item is already in cart
        const existingItem = this.items.find(item => {
          const cartItemId = item.product?.id || item.product_id
          return cartItemId && String(cartItemId) === String(validProductId)
        })

        const response = await axios.post(`${BASE_URL}/add_item/`, {
          product_id: validProductId,
          quantity: quantity
        }, {
          withCredentials: true,
          headers
        })
        
        // Handle successful response
        if (response.data) {
          // Check if it's an error response from backend
          if (response.data.status === 'error') {
            return this._handleBackendError(response.data)
          }

          // Update cart state with response data when items are present
          const cartData = response.data.data || response.data
          if (cartData?.items) {
            this._updateCartState(cartData)
          } else {
            await this._refreshCartState()
          }
        } else {
          await this._refreshCartState()
        }
        
        return response.data
      } catch (error) {
        console.error('Error adding item to cart:', error)
        
        // Handle different types of errors
        if (error.response?.data) {
          this._handleBackendError(error.response.data, error)
        } else {
          this.error = error.message || 'Error adding item to cart'
        }
        
        throw error
      } finally {
        this.loading = false
      }
    },

    _handleBackendError(errorData, error) {
      const errorDetail = errorData.detail || errorData
      let errorMessage = ''
      
      if (errorData.code === 'insufficient_stock' || errorData.error_type === 'insufficient_stock') {
        const availableStock = errorData.extra_data?.available_stock || errorDetail.available_stock || 'unknown'
        errorMessage = `Not enough stock. Available: ${availableStock}`
      } else if (typeof errorDetail === 'object') {
        errorMessage = errorDetail.message || Object.entries(errorDetail)
          .filter(([key]) => key !== 'available_stock')
          .map(([key, value]) => `${key}: ${value}`)
          .join(', ')
      } else {
        errorMessage = errorDetail || 'An error occurred'
      }
      
      this.error = errorMessage
      throw new Error(errorMessage)
    },

    async _refreshCartState({ silent = true, fallbackRemoveProductId = null } = {}) {
      try {
        await this.fetchCart({ silent })
      } catch (fetchError) {
        console.error('Error refreshing cart state:', fetchError)
        if (!fallbackRemoveProductId) {
          throw fetchError
        }

        // Optimistically remove the item locally if the fetch fails
        const updatedItems = this.items.filter(item => {
          const cartItemId = item.product?.id || item.product_id
          return String(cartItemId) !== String(fallbackRemoveProductId)
        })

        if (updatedItems.length !== this.items.length) {
          this.items = updatedItems
          this.total_items = updatedItems.reduce((acc, it) => acc + (it.quantity || 1), 0)

          if (updatedItems.length === 0) {
            this.subtotal = '0.00'
            this.tax = '0.00'
            this.total = '0.00'
          }
        }
      }
    },

    _updateCartState(cartData) {
      // Handle both wrapped responses (with data property) and direct cart data
      const actualCartData = cartData.data || cartData
      const rawItems = actualCartData.items || []
      
      // Normalize keys to camelCase expected by components
      const processedItems = rawItems.map(it => {
        // Ensure product object exists and has proper structure
        const product = it.product || {}
        return {
          ...it,
          id: it.id,
          product: {
            ...product,
            id: product.id || it.product_id,
            name: product.name || it.product_name,
            price: product.price || it.product_price
          },
          unitPrice: it.unit_price ?? it.unitPrice ?? it.product_price,
          totalPrice: it.subtotal ?? it.totalPrice,
          quantity: it.quantity || 1
        }
      })
      
      // Replace the entire items array to ensure reactivity
      this.items = processedItems
      
      // Update other cart properties
      this.subtotal = actualCartData.subtotal || '0.00'
      this.tax = actualCartData.tax || '0.00'
      this.total = actualCartData.total || '0.00'
      this.total_items = actualCartData.total_items || processedItems.length
    },

    async removeItem(productId) {
      const authStore = useAuthStore()
      
      try {
        this.loading = true
        this.error = null
        
        const validProductId = this.validateUUID(productId)
        const headers = {
          'X-CSRFToken': getCSRFToken()
        }
        
        if (authStore.isAuthenticated) {
          headers['Authorization'] = `Bearer ${authStore.token}`
        }

        const response = await axios.delete(`${BASE_URL}/remove/${validProductId}/`, {
          withCredentials: true,
          headers
        })

        if (response.data) {
          const cartData = response.data.data || response.data
          if (cartData?.items) {
            this._updateCartState(cartData)
          } else {
            await this._refreshCartState({ fallbackRemoveProductId: validProductId })
          }
        } else {
          await this._refreshCartState({ fallbackRemoveProductId: validProductId })
        }
        
        return response.data
      } catch (error) {
        console.error('Error removing item from cart:', error)
        this.error = error.response?.data?.detail || 
                    error.response?.data?.error ||
                    error.message || 
                    'Error removing item from cart'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateQuantity(productId, quantity) {
      // If quantity is 0 or less, remove the item instead
      if (!quantity || quantity < 1) {
        return await this.removeItem(productId)
      }
      
      const authStore = useAuthStore()
      
      try {
        this.loading = true
        this.error = null
        
        const validProductId = this.validateUUID(productId)
        const headers = {
          'X-CSRFToken': getCSRFToken()
        }
        
        if (authStore.isAuthenticated) {
          headers['Authorization'] = `Bearer ${authStore.token}`
        }

        const response = await axios.put(`${BASE_URL}/update/${validProductId}/`, {
          quantity: quantity
        }, {
          withCredentials: true,
          headers
        })
        
        if (response.data) {
          // Update cart state using _updateCartState to ensure proper processing
          const cartData = response.data.data || response.data
          if (cartData?.items) {
            this._updateCartState(cartData)
          } else {
            await this._refreshCartState({ fallbackRemoveProductId: quantity < 1 ? validProductId : null })
          }
        } else {
          await this._refreshCartState({ fallbackRemoveProductId: quantity < 1 ? validProductId : null })
        }
        
        return response.data
      } catch (error) {
        console.error('Error updating cart item:', error)
        this.error = error.response?.data?.detail || 
                    error.response?.data?.error ||
                    error.message || 
                    'Error updating cart item'
        throw error
      } finally {
        this.loading = false
      }
    },

    async clearCart() {
      const authStore = useAuthStore()
      
      try {
        this.loading = true
        this.error = null
        
        const headers = {
          'X-CSRFToken': getCSRFToken()
        }
        
        if (authStore.isAuthenticated) {
          headers['Authorization'] = `Bearer ${authStore.token}`
        }

        const response = await axios.post(`${BASE_URL}/clear/`, {}, {
          withCredentials: true,
          headers
        })
        
        if (response.data) {
          this.items = []
          this.subtotal = '0.00'
          this.tax = '0.00'
          this.total = '0.00'
          this.total_items = 0
        }
        
        return response.data
      } catch (error) {
        console.error('Error clearing cart:', error)
        this.error = error.response?.data?.detail || 
                    error.response?.data?.error ||
                    error.message || 
                    'Error clearing cart'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})