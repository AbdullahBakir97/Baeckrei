import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
    subtotal: '0.00',
    tax: '0.00',
    total: '0.00',
    total_items: 0,
    dropdownVisible: false
  }),

  getters: {
    isLoading: (state) => state.loading,
    cartIsEmpty: (state) => !state.items?.length,
    itemCount: (state) => state.total_items || 0,
    subtotalAmount: (state) => Number(state.subtotal || 0),
    taxAmount: (state) => Number(state.tax || 0),
    totalAmount: (state) => Number(state.total || 0),
    displayedItems: (state) => state.items.slice(0, 3),
    isDropdownVisible: (state) => state.dropdownVisible
  },

  actions: {
    showDropdown() {
      this.dropdownVisible = true
    },

    hideDropdown() {
      this.dropdownVisible = false
    },

    resetError() {
      this.error = null
    },

    async fetchCart() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_URL}/api/shopping-cart/current/`, {
          withCredentials: true
        })
        
        this.items = response.data.items.map((item) => ({
          id: item.id,
          product: {
            id: item.product_id,
            name: item.product_name,
            image: item.product_image,
            price: parseFloat(item.product_price),
          },
          quantity: item.quantity,
          subtotal: parseFloat(item.subtotal),
        }));
        this.subtotal = response.data.subtotal || '0.00';
        this.tax = response.data.tax || '0.00';
        this.total = response.data.total || '0.00';
        this.total_items = response.data.total_items || 0;
    
        return response.data;
      } catch (error) {
        console.error('Error fetching cart:', error);
        this.error = error.response?.data?.message || 'Failed to load cart';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async addItem(productId, quantity = 1) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_URL}/api/shopping-cart/add_item/`, {
          product_id: productId,
          quantity
        }, {
          withCredentials: true
        })
        
        this.items = response.data.items || []
        this.subtotal = response.data.subtotal || '0.00'
        this.tax = response.data.tax || '0.00'
        this.total = response.data.total || '0.00'
        this.total_items = response.data.total_items || 0
        
        return response.data
      } catch (error) {
        console.error('Error adding item to cart:', error)
        this.error = error.response?.data?.message || 'Error adding item to cart'
        throw error
      } finally {
        this.loading = false
      }
    },

    async removeItem(productId) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_URL}/api/shopping-cart/remove_item/`, {
          product_id: productId
        }, {
          withCredentials: true
        })
        
        this.items = response.data.items || []
        this.subtotal = response.data.subtotal || '0.00'
        this.tax = response.data.tax || '0.00'
        this.total = response.data.total || '0.00'
        this.total_items = response.data.total_items || 0
        
        return response.data
      } catch (error) {
        console.error('Error removing item from cart:', error)
        this.error = error.response?.data?.message || 'Error removing item from cart'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateQuantity(productId, quantity) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_URL}/api/shopping-cart/update_item/`, {
          product_id: productId,
          quantity
        }, {
          withCredentials: true
        })
        
        this.items = response.data.items || []
        this.subtotal = response.data.subtotal || '0.00'
        this.tax = response.data.tax || '0.00'
        this.total = response.data.total || '0.00'
        this.total_items = response.data.total_items || 0
        
        return response.data
      } catch (error) {
        console.error('Error updating item quantity:', error)
        this.error = error.response?.data?.message || 'Error updating item quantity'
        throw error
      } finally {
        this.loading = false
      }
    },

    async clearCart() {
      this.loading = true
      this.error = null
      try {
        await axios.post(`${API_URL}/api/shopping-cart/clear/`, {}, {
          withCredentials: true
        })
        
        this.items = []
        this.subtotal = '0.00'
        this.tax = '0.00'
        this.total = '0.00'
        this.total_items = 0
        
        return true
      } catch (error) {
        console.error('Error clearing cart:', error)
        this.error = error.response?.data?.message || 'Error clearing cart'
        return false
      } finally {
        this.loading = false
      }
    }
  }
})