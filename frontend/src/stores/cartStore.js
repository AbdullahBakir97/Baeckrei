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
          // Update cart state
          this.items = response.data.items || []
          this.subtotal = response.data.subtotal || '0.00'
          this.tax = response.data.tax || '0.00'
          this.total = response.data.total || '0.00'
          this.total_items = response.data.total_items || 0
          this.lastFetch = Date.now()
          
          console.log('Cart state updated:', {
            items: this.items,
            total_items: this.total_items,
            total: this.total
          })
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
          'X-CSRFToken': getCSRFToken()
        }
        
        if (authStore.isAuthenticated) {
          headers['Authorization'] = `Bearer ${authStore.token}`
        }

        // First check if item is already in cart
        const existingItem = this.items.find(item => item.product.id === validProductId)
        if (existingItem) {
          console.log('Item already in cart, updating quantity:', {
            productId: validProductId,
            currentQuantity: existingItem.quantity,
            addQuantity: quantity
          })
        }

        const response = await axios.post(`${BASE_URL}/add_item/`, {
          product_id: validProductId,
          quantity: quantity
        }, {
          withCredentials: true,
          headers
        })
        
        if (response.data) {
          // Check if it's an error response from backend
          if (response.data.status === 'error') {
            const errorDetail = response.data.detail
            let errorMessage = ''
            
            if (response.data.code === 'insufficient_stock') {
              errorMessage = `Not enough stock. Available: ${errorDetail.available_stock}`
            } else if (typeof errorDetail === 'object') {
              errorMessage = errorDetail.message || Object.entries(errorDetail)
                .map(([key, value]) => `${key}: ${value}`)
                .join(', ')
            } else {
              errorMessage = errorDetail
            }
            
            this.error = errorMessage
            throw new Error(errorMessage)
          }
          
          // Update cart state with response data
          const cartData = response.data.data || response.data
          this.items = cartData.items || []
          this.subtotal = cartData.subtotal || '0.00'
          this.tax = cartData.tax || '0.00'
          this.total = cartData.total || '0.00'
          this.total_items = cartData.total_items || 0
          
          console.log('Cart updated after adding item:', {
            items: this.items,
            total_items: this.total_items,
            total: this.total
          })
        }
        
        return response.data
      } catch (error) {
        console.error('Error adding item to cart:', {
          error: error.message,
          response: error.response?.data,
          status: error.response?.status
        })
        
        // Handle different types of errors
        let errorMessage = ''
        if (error.response?.data?.detail) {
          const detail = error.response.data.detail
          if (detail.message) {
            errorMessage = detail.message
          } else if (typeof detail === 'object') {
            errorMessage = Object.entries(detail)
              .map(([key, value]) => `${key}: ${value}`)
              .join(', ')
          } else {
            errorMessage = detail
          }
        } else {
          errorMessage = error.message || 'Error adding item to cart'
        }
        
        this.error = errorMessage
        throw error
      } finally {
        this.loading = false
      }
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

        const response = await axios.post(`${BASE_URL}/remove_item/`, {
          product_id: validProductId
        }, {
          withCredentials: true,
          headers
        })
        
        if (response.data) {
          this.items = response.data.items || []
          this.subtotal = response.data.subtotal || '0.00'
          this.tax = response.data.tax || '0.00'
          this.total = response.data.total || '0.00'
          this.total_items = response.data.total_items || 0
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

        const response = await axios.post(`${BASE_URL}/update_item/`, {
          product_id: validProductId,
          quantity: quantity
        }, {
          withCredentials: true,
          headers
        })
        
        if (response.data) {
          this.items = response.data.items || []
          this.subtotal = response.data.subtotal || '0.00'
          this.tax = response.data.tax || '0.00'
          this.total = response.data.total || '0.00'
          this.total_items = response.data.total_items || 0
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