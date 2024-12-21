import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

export const useProductStore = defineStore('products', {
  state: () => ({
    products: [],
    totalItems: 0,
    currentPage: 1,
    pageSize: 12,
    loading: false,
    error: null,
  }),

  actions: {
    setPage(page) {
      this.currentPage = page
    },

    async fetchProducts(filters = {}) {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching products with filters:', filters)
        const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/products/products/`, {
          params: {
            page: this.currentPage,
            page_size: this.pageSize,
            ...filters
          },
          withCredentials: true
        })
        
        console.log('API Response:', response.data)
        
        if (response.data.results) {
          this.products = response.data.results
          this.totalItems = response.data.count || 0
          console.log('Products loaded:', this.products.length)
          console.log('Total items:', this.totalItems)
        } else {
          console.log('No results found in response')
          this.products = []
          this.totalItems = 0
        }
      } catch (error) {
        console.error('Error fetching products:', error)
        console.error('Error response:', error.response?.data)
        this.error = error.response?.data?.message || 'Error loading products'
        this.products = []
        this.totalItems = 0
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchProduct(id) {
      try {
        const response = await axios.get(`/api/products/products/${id}/`)
        return response.data
      } catch (error) {
        throw error
      }
    }
  },

  getters: {
    totalPages: (state) => Math.ceil(state.totalItems / state.pageSize),
    hasNextPage: (state) => state.currentPage < Math.ceil(state.totalItems / state.pageSize),
    hasPreviousPage: (state) => state.currentPage > 1
  }
})
