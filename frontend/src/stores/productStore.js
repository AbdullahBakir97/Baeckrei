import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

export const useProductStore = defineStore('products', {
  state: () => ({
    products: [],
    product: null,
    categories: [],
    categoriesLoading: false,
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

    async fetchCategories() {
      this.categoriesLoading = true
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/products/categories/`, {
          withCredentials: true,
          params: {
            page_size: 100 // Get all categories at once
          }
        })
        if (response.data?.results) {
          this.categories = response.data.results
          return response.data.results
        }
        return []
      } catch (error) {
        console.error('Error fetching categories:', error)
        this.categories = []
        throw error
      } finally {
        this.categoriesLoading = false
      }
    },

    async fetchProducts(filters = {}) {
      this.loading = true
      this.error = null
      
      try {
        console.log('Fetching products with filters:', filters)
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ordering: filters.sort === 'price_desc' ? '-price' : 
                   filters.sort === 'price_asc' ? 'price' : 
                   filters.sort === 'popularity' ? '-popularity' : 'name',
        }

        // Add category filter if categories are selected
        if (filters.categories?.length > 0) {
          params.category__in = filters.categories.join(',')
        }

        // Add other filters
        if (filters.price_min) params.price__gte = filters.price_min
        if (filters.price_max) params.price__lte = filters.price_max
        if (filters.isVegan) params.is_vegan = true
        if (filters.isVegetarian) params.is_vegetarian = true
        if (filters.isGlutenFree) params.is_gluten_free = true

        const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/products/products/`, {
          params,
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

    async fetchProductById(id) {
      this.loading = true
      this.error = null
      this.product = null // Reset product before fetching
      
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/products/products/${id}/`, {
          withCredentials: true
        })
        if (response.data) {
          this.product = response.data
          return response.data
        } else {
          throw new Error('Product not found')
        }
      } catch (error) {
        console.error('Error fetching product:', error)
        this.error = error.response?.data?.message || error.message || 'Error loading product'
        throw error
      } finally {
        this.loading = false
      }
    }
  },

  getters: {
    totalPages: (state) => Math.ceil(state.totalItems / state.pageSize),
    hasNextPage: (state) => state.currentPage < Math.ceil(state.totalItems / state.pageSize),
    hasPreviousPage: (state) => state.currentPage > 1
  }
})
