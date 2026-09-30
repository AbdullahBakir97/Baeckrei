import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { API_URL } from '@/config/api'


const BASE_URL = `${API_URL}/api/shopping-cart`

const mediaUrl = (path) => {
  if (!path) return null
  return path.startsWith('http') ? path : `${API_URL}${path}`
}

// The API returns the product as an id plus flat fields; the components
// expect a nested product object.
const normalizeItem = (item) => ({
  ...item,
  product: {
    id: item.product,
    name: item.product_name,
    name_en: item.product_name_en,
    price: parseFloat(item.product_price),
    stock: item.available_stock,
    image: mediaUrl(item.product_image)
  },
  unitPrice: item.unit_price,
  totalPrice: item.total_price,
  subtotal: item.total_price
})

// Turn an API error into a readable message.
const errorMessage = (error, fallback) => {
  const detail = error.response?.data?.detail
  if (detail?.message) return detail.message
  if (typeof detail === 'string') return detail
  return error.message || fallback
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

      const cleanId = String(productId).trim()
      const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

      if (!uuidPattern.test(cleanId)) {
        throw new Error(`Invalid product ID format: ${productId}. Must be a valid UUID.`)
      }

      return cleanId
    },

    applyCart(data) {
      this.items = (data?.items || []).map(normalizeItem)
      this.subtotal = data?.subtotal || '0.00'
      this.tax = data?.tax || '0.00'
      this.total = data?.total || '0.00'
      this.total_items = data?.total_items || 0
      this.lastFetch = Date.now()
    },

    // Run a cart request; every endpoint responds with the full cart.
    async request(method, path, body, fallbackError) {
      try {
        this.loading = true
        this.error = null
        const response = await axios({ method, url: `${BASE_URL}/${path}`, data: body })
        this.applyCart(response.data)
        return response.data
      } catch (error) {
        this.error = errorMessage(error, fallbackError)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchCart({ silent = false } = {}) {
      try {
        if (!silent) this.loading = true
        this.error = null
        const response = await axios.get(`${BASE_URL}/`)
        this.applyCart(response.data)
      } catch (error) {
        if (!silent) {
          console.error('Error fetching cart:', error)
          this.error = errorMessage(error, 'Error fetching cart')
        }
      } finally {
        if (!silent) this.loading = false
      }
    },

    async addItem(productId, quantity = 1) {
      const id = this.validateUUID(productId)
      return this.request('post', 'add/', { product_id: id, quantity }, 'Error adding item to cart')
    },

    async removeItem(productId) {
      const id = this.validateUUID(productId)
      return this.request('delete', `remove/${id}/`, undefined, 'Error removing item from cart')
    },

    async updateQuantity(productId, quantity) {
      const id = this.validateUUID(productId)
      if (quantity < 1) return this.removeItem(id)
      return this.request('put', `update/${id}/`, { quantity }, 'Error updating cart item')
    },

    async clearCart() {
      return this.request('post', 'clear/', {}, 'Error clearing cart')
    }
  }
})
