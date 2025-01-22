import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { ref, computed } from 'vue'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PATH = `${API_BASE}/api/products`

export const useProductStore = defineStore('products', () => {
  const products = ref([])
  const product = ref(null)
  const categories = ref([])
  const ingredients = ref([])
  const allergens = ref([])
  const nutritionInfo = ref(null)
  const similarProducts = ref([])
  const relatedProducts = ref([])
  const categoriesLoading = ref(false)
  const relatedProductsLoading = ref(false)
  const totalItems = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(12)
  const loading = ref(false)
  const error = ref(null)

  const fetchProducts = async (filters = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const params = {
        page: filters.page || currentPage.value,
        page_size: filters.pageSize || pageSize.value,
        ordering: filters.sort === 'price_desc' ? '-price' : 
                 filters.sort === 'price_asc' ? 'price' : 
                 filters.sort === 'popularity' ? '-popularity' : 'name',
      }

      if (filters.categories?.length > 0) {
        params.category__in = filters.categories.join(',')
      }

      if (filters.price_min) params.price__gte = filters.price_min
      if (filters.price_max) params.price__lte = filters.price_max
      if (filters.isVegan) params.is_vegan = true
      if (filters.isVegetarian) params.is_vegetarian = true
      if (filters.isGlutenFree) params.is_gluten_free = true
      if (filters.search) params.search = filters.search

      const response = await axios.get(`${API_PATH}/`, {
        params,
        withCredentials: true
      })
      
      if (response.data.results) {
        // Log the first product for debugging
        console.log('Debug - Product data from API:', {
          id: response.data.results[0]?.id,
          image: response.data.results[0]?.image,
          image_url: response.data.results[0]?.image_url
        })

        // Store products with normalized image URLs
        products.value = response.data.results.map(product => ({
          ...product,
          // Use image_url if available, otherwise construct URL from image path
          image: product.image_url || 
                (product.image ? 
                  (product.image.startsWith('http') ? product.image : `/media/${product.image}`)
                  : null)
        }))
        totalItems.value = response.data.count || 0
      } else {
        products.value = []
        totalItems.value = 0
      }
    } catch (err) {
      error.value = 'Error fetching products'
      console.error('Error fetching products:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get('/api/products/categories/', {
        params: { page_size: 100 }
      })
      categories.value = response.data.results || []
      return categories.value
    } catch (err) {
      error.value = 'Error fetching categories'
      console.error('Error fetching categories:', err)
      // Return empty array instead of throwing
      categories.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  async function fetchProductById(id) {
    loading.value = true
    error.value = null
    
    try {
      console.log('Fetching product details for ID:', id)
      const response = await axios.get(`${API_PATH}/${id}/`, {
        withCredentials: true
      })
      
      if (response.data) {
        console.log('Product detail data:', response.data)
        product.value = {
          ...response.data,
          // Ensure image URLs are absolute
          image: response.data.image_url || 
                (response.data.image ? 
                  (response.data.image.startsWith('http') ? response.data.image : `/media/${response.data.image}`)
                  : null),
          images: response.data.images || []
        }
      } else {
        error.value = 'Product not found'
      }
    } catch (err) {
      console.error('Error fetching product:', err)
      error.value = err.response?.data?.message || 'Failed to fetch product details'
    } finally {
      loading.value = false
    }
  }

  const fetchIngredients = async () => {
    try {
      const response = await axios.get(`${API_PATH}/ingredients/`, {
        withCredentials: true
      })
      ingredients.value = response.data.results || []
      return ingredients.value
    } catch (err) {
      console.error('Error fetching ingredients:', err)
      throw err
    }
  }

  const fetchIngredientDetails = async (id) => {
    try {
      const response = await axios.get(`${API_PATH}/${id}/ingredient_details/`, {
        withCredentials: true
      })
      return response.data
    } catch (err) {
      console.error('Error fetching ingredient details:', err)
      throw err
    }
  }

  const fetchAllergens = async () => {
    try {
      const response = await axios.get(`${API_PATH}/allergens/`, {
        withCredentials: true
      })
      allergens.value = response.data.results || []
      return allergens.value
    } catch (err) {
      console.error('Error fetching allergens:', err)
      throw err
    }
  }

  const fetchProductAllergens = async (productId) => {
    try {
      const response = await axios.get(`${API_PATH}/${productId}/product_allergens/`, {
        withCredentials: true
      })
      return response.data
    } catch (err) {
      console.error('Error fetching product allergens:', err)
      throw err
    }
  }

  const fetchProductNutrition = async (productId) => {
    try {
      const response = await axios.get(`${API_PATH}/${productId}/product_nutrition/`, {
        withCredentials: true
      })
      nutritionInfo.value = response.data
      return response.data
    } catch (err) {
      console.error('Error fetching product nutrition:', err)
      throw err
    }
  }

  const fetchSimilarProducts = async (productId) => {
    try {
      const response = await axios.get(`${API_PATH}/${productId}/similar_products/`, {
        withCredentials: true
      })
      similarProducts.value = response.data.results || []
      return similarProducts.value
    } catch (err) {
      console.error('Error fetching similar products:', err)
      throw err
    }
  }

  const fetchRelatedProducts = async (productId) => {
    try {
      relatedProductsLoading.value = true
      error.value = null
      
      const response = await axios.get(`${API_PATH}/${productId}/related_products/`, {
        withCredentials: true
      })
      
      // Process and validate image paths
      relatedProducts.value = (response.data || []).map(product => {
        // Helper to validate image extensions
        const isValidImagePath = (path) => {
          if (!path) return false
          const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
          const ext = path.toLowerCase().split('.').pop()
          return validExtensions.includes(`.${ext}`)
        }

        // Process main image
        let mainImage = product.image_url || product.image
        if (!isValidImagePath(mainImage)) {
          mainImage = '/images/placeholder.png'
        }

        // Process image array
        const validImages = (product.images || [])
          .filter(isValidImagePath)
          .map(img => img.startsWith('http') ? img : `/media/${img}`)

        return {
          ...product,
          image: mainImage,
          images: validImages
        }
      })
    } catch (err) {
      console.error('Error fetching related products:', err)
      error.value = 'Failed to load related products'
    } finally {
      relatedProductsLoading.value = false
    }
  }

  const fetchReport = async (reportType = '') => {
    try {
      const response = await axios.get(`${API_PATH}/report/`, {
        params: { type: reportType },
        withCredentials: true
      })
      return response.data
    } catch (err) {
      console.error('Error fetching report:', err)
      throw err
    }
  }

  const fetchInventoryReport = async () => {
    try {
      const response = await axios.get(`${API_PATH}/inventory_report/`, {
        withCredentials: true
      })
      return response.data
    } catch (err) {
      console.error('Error fetching inventory report:', err)
      throw err
    }
  }

  const searchProducts = async (query) => {
    try {
      const response = await axios.get(`${API_PATH}/search/`, {
        params: { q: query },
        withCredentials: true
      })
      return response.data.results || []
    } catch (err) {
      console.error('Error searching products:', err)
      throw err
    }
  }

  const getImageUrl = (path) => {
    if (!path) return '/images/placeholder.png'
    
    // If it's already a full URL or the placeholder, return it
    if (path.startsWith('http') || path === '/images/placeholder.png') {
      return path
    }
  
    // Remove any duplicate /media/ prefixes first
    const cleanPath = path.replace(/\/media\/+/g, '/media/')
  
    // Construct the full URL, ensuring no duplicate /media/ prefixes
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const fullUrl = `${baseUrl}${cleanPath.startsWith('/') ? '' : '/'}${cleanPath}`
  
    return fullUrl
  }
  
  return {
    products,
    product,
    categories,
    ingredients,
    allergens,
    nutritionInfo,
    similarProducts,
    relatedProducts,
    relatedProductsLoading,
    categoriesLoading,
    totalItems,
    currentPage,
    pageSize,
    loading,
    error,
    fetchProducts,
    fetchCategories,
    fetchProductById,
    fetchIngredients,
    fetchIngredientDetails,
    fetchAllergens,
    fetchProductAllergens,
    fetchProductNutrition,
    fetchSimilarProducts,
    fetchRelatedProducts,
    fetchReport,
    fetchInventoryReport,
    searchProducts
  }
})
