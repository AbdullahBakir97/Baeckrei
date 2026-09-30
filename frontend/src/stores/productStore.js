import { defineStore } from 'pinia'
import { PLACEHOLDER_IMAGE } from '@/utils/imageFallback'
import axios from '@/plugins/axios'
import { ref, computed } from 'vue'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PATH = `${API_BASE}/api/products`

export const useProductStore = defineStore('products', () => {
  // State
  const products = ref([])
  const product = ref(null)
  const categories = ref([])
  const ingredients = ref([])
  const allergens = ref([])
  const nutritionInfo = ref(null)
  const similarProducts = ref([])
  const relatedProducts = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Pagination state
  const pagination = ref({
    count: 0,
    current_page: 1,
    total_pages: 1,
    page_size: 12,
    has_next: false,
    has_previous: false,
    page_range: [],
  })

  // Computed properties
  const hasProducts = computed(() => products.value.length > 0)
  const hasNextPage = computed(() => pagination.value.has_next)
  const hasPreviousPage = computed(() => pagination.value.has_previous)
  const totalItems = computed(() => pagination.value.count)

  // Convert the admin form to the API payload. A new image has to be sent
  // as multipart form data; everything else can be JSON.
  const toProductPayload = (data) => {
    const fields = {
      name: data.name,
      description: data.description,
      category: typeof data.category === 'object' ? data.category?.id : data.category,
      price: data.price,
      stock: data.stock,
      status: data.status,
      available: data.available,
      is_vegan: data.is_vegan ?? false,
      is_vegetarian: data.is_vegetarian ?? false,
      is_gluten_free: data.is_gluten_free ?? false,
      is_seasonal: data.is_seasonal ?? false
    }
    Object.keys(fields).forEach(key => fields[key] === undefined && delete fields[key])
    // modelFile: a new .glb to upload; removeModel: clear the current one.
    if (!data.imageFile && !data.modelFile && !data.removeModel) return fields
    const form = new FormData()
    Object.entries(fields).forEach(([key, value]) => form.append(key, value))
    if (data.imageFile) form.append('image', data.imageFile)
    if (data.modelFile) form.append('model_3d', data.modelFile)
    else if (data.removeModel) form.append('model_3d', '')
    return form
  }

  const createProduct = async (data) => {
    const response = await axios.post(`${API_PATH}/`, toProductPayload(data))
    return response.data
  }

  const updateProduct = async (data) => {
    const response = await axios.patch(`${API_PATH}/${data.id}/`, toProductPayload(data))
    return response.data
  }

  const deleteProduct = async (id) => {
    const response = await axios.delete(`${API_PATH}/${id}/`)
    products.value = products.value.filter(p => p.id !== id)
    return response.data || null
  }

  const fetchProducts = async (filters = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const params = new URLSearchParams()

      // Pagination params
      params.append('page', filters.page || pagination.value.current_page)
      params.append('page_size', filters.page_size || pagination.value.page_size)
      
      // View mode
      if (filters.view_mode) {
        params.append('view_mode', filters.view_mode)
      }

      // Ordering
      let ordering = 'name'
      if (filters.ordering) {
        if (filters.ordering === 'price_desc') ordering = '-price'
        else if (filters.ordering === 'price_asc') ordering = 'price'
        else if (filters.ordering === 'newest') ordering = '-created_at'
        else ordering = filters.ordering
      }
      params.append('ordering', ordering)

      // Admin product list: include drafts, hidden and unavailable products
      if (filters.include_all) params.append('include_all', 'true')
      if (filters.status) params.append('status', filters.status)
      if (filters.stock_status) params.append('stock_status', filters.stock_status)

      // Category page (slug) and seasonal page
      if (filters.category) params.append('category', filters.category)
      if (filters.seasonal) params.append('seasonal', true)

      // Category filter
      if (filters.categories?.length) {
        params.append('category_ids', filters.categories.join(','))
      }

      // Price range filter
      if (filters.price_min) params.append('price__gte', filters.price_min)
      if (filters.price_max) params.append('price__lte', filters.price_max)

      // Dietary preferences
      if (filters.is_vegan) params.append('is_vegan', true)
      if (filters.is_vegetarian) params.append('is_vegetarian', true)
      if (filters.is_gluten_free) params.append('is_gluten_free', true)

      // Stock filter
      if (filters.in_stock) params.append('in_stock', true)

      // Search
      if (filters.search) params.append('search', filters.search)

      const response = await axios.get(`${API_PATH}/`, {
        params: params,
        withCredentials: true
      }).catch(err => {
        console.error('Axios error:', {
          status: err.response?.status,
          statusText: err.response?.statusText,
          data: err.response?.data,
          config: {
            url: err.config?.url,
            params: err.config?.params,
            baseURL: err.config?.baseURL
          }
        })
        throw err
      })

      // Debug log for API request
      console.log('API Request:', {
        url: `${API_PATH}/`,
        params: Object.fromEntries(params.entries())
      })

      console.log('API Response:', {
        status: response.status,
        data: response.data,
        count: response.data?.count,
        results: response.data?.results?.length,
        pagination: {
          current_page: response.data?.current_page,
          total_pages: response.data?.total_pages,
          page_size: response.data?.page_size,
          has_next: response.data?.has_next,
          has_previous: response.data?.has_previous,
        }
      })

      if (response.data) {
        // Update pagination state
        pagination.value = {
          count: response.data.count || 0,
          current_page: response.data.current_page || 1,
          total_pages: response.data.total_pages || 1,
          page_size: response.data.page_size || 12,
          has_next: response.data.has_next || false,
          has_previous: response.data.has_previous || false,
          page_range: response.data.page_range || [],
        }

        console.log('Products before mapping:', response.data.results)

        // Update products with normalized image URLs
        products.value = (response.data.results || []).map(product => {
          console.log('Processing product:', product)
          const normalizedProduct = {
            ...product,
            id: product.id,
            name: product.name,
            slug: product.slug,
            description: product.description || '',
            price: parseFloat(product.price),
            stock: product.stock || 0,
            available: product.available ?? true,
            isNew: false, // You can set this based on your criteria
            image: product.image_url || 
                  (product.image ? 
                    (product.image.startsWith('http') ? product.image : `${API_BASE}/media/${product.image}`)
                    : null),
            category: product.category ? {
              ...product.category,
              name: product.category.name || '',
              image: product.category?.image_url || 
                    (product.category?.image ? 
                      (product.category.image.startsWith('http') ? product.category.image : `${API_BASE}/media/${product.category.image}`)
                      : null)
            } : null,
            is_vegan: product.is_vegan || false,
            is_vegetarian: product.is_vegetarian || false,
            is_gluten_free: product.is_gluten_free || false,
            status: product.status
          }
          console.log('Normalized product:', normalizedProduct)
          return normalizedProduct
        })

        console.log('Final products array:', products.value)

        return {
          results: products.value,
          pagination: pagination.value
        }
      }

      return {
        results: [],
        pagination: {
          count: 0,
          current_page: 1,
          total_pages: 1,
          page_size: 12,
          has_next: false,
          has_previous: false,
          page_range: [],
        }
      }
    } catch (err) {
      console.error('Error fetching products:', err)
      error.value = err.response?.data?.error || 'Error fetching products'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.get(`${API_PATH}/categories/`, {
        params: { page_size: 100 }
      })
      categories.value = response.data.results || []
      return categories.value
    } catch (err) {
      error.value = 'Error fetching categories'
      console.error('Error fetching categories:', err)
      categories.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  const fetchProductById = async (id) => {
    loading.value = true
    error.value = null
    product.value = null

    try {
      const response = await axios.get(`${API_PATH}/${id}/`, {
        withCredentials: true
      })
      
      if (response.data) {
        product.value = {
          ...response.data,
          // Ensure image URLs are absolute
          image: response.data.image_url || 
                (response.data.image ? 
                  (response.data.image.startsWith('http') ? response.data.image : `${API_BASE}/media/${response.data.image}`)
                  : null),
          images: response.data.images || []
        }
      } else {
        error.value = 'Product not found'
      }
    } catch (err) {
      console.error('Error fetching product:', err)
      error.value = err.response?.data?.message || 'Failed to fetch product details'
      // Don't keep showing the previously viewed product.
      product.value = null
    } finally {
      loading.value = false
    }
    return product.value
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
      const response = await axios.get(`${API_PATH}/${productId}/related_products/`, {
        withCredentials: true
      })
      relatedProducts.value = response.data.results || []
      return relatedProducts.value
    } catch (err) {
      console.error('Error fetching related products:', err)
      throw err
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
    if (!path) return PLACEHOLDER_IMAGE
    
    // If it's already a full URL or the placeholder, return it
    if (path.startsWith('http') || path === PLACEHOLDER_IMAGE) {
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
    // State
    products,
    product,
    categories,
    ingredients,
    allergens,
    nutritionInfo,
    similarProducts,
    relatedProducts,
    loading,
    error,
    pagination,

    // Computed properties
    hasProducts,
    hasNextPage,
    hasPreviousPage,
    totalItems,

    // Actions
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
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
    searchProducts,
    getImageUrl
  }
})
