import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { ref, computed } from 'vue'
import { API_URL } from '@/config/api'

const API_BASE = API_URL
const API_PATH = `${API_BASE}/api/orders/orders`

const mediaUrl = (path) => {
  if (!path) return null
  return path.startsWith('http') ? path : `${API_BASE}${path.startsWith('/') ? '' : '/media/'}${path}`
}

// Map the backend's order shape onto what the views render.
const normalizeOrder = (order) => ({
  ...order,
  created_at: new Date(order.created_at),
  updated_at: new Date(order.updated_at),
  estimated_delivery_date: order.estimated_delivery_date ?
    new Date(order.estimated_delivery_date) : null,
  total_price: parseFloat(order.total_price),
  order_items: (order.items || []).map(item => ({
    ...item,
    price_per_item: parseFloat(item.price_per_item),
    product: {
      id: item.product,
      name: item.product_name,
      name_en: item.product_name_en,
      image: mediaUrl(item.product_image)
    }
  }))
})

export const useOrderStore = defineStore('orders', () => {
  // State
  const orders = ref([])
  const currentOrder = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Pagination state
  const pagination = ref({
    count: 0,
    current_page: 1,
    total_pages: 1,
    page_size: 10,
    has_next: false,
    has_previous: false,
    page_range: [],
  })

  // Computed
  const hasOrders = computed(() => orders.value.length > 0)
  const pendingOrders = computed(() => 
    orders.value.filter(order => order.status === 'Pending')
  )
  const processingOrders = computed(() => 
    orders.value.filter(order => order.status === 'Processing')
  )
  const completedOrders = computed(() => 
    orders.value.filter(order => order.status === 'Completed')
  )
  const canceledOrders = computed(() => 
    orders.value.filter(order => order.status === 'Canceled')
  )

  // Actions
  const fetchOrders = async (params = {}) => {
    try {
      loading.value = true
      error.value = null

      const queryParams = new URLSearchParams()
      
      // Pagination
      queryParams.append('page', params.page || pagination.value.current_page)
      queryParams.append('page_size', params.page_size || pagination.value.page_size)
      
      // Filters
      if (params.status) queryParams.append('status', params.status)
      if (params.start_date) queryParams.append('start_date', params.start_date)
      if (params.end_date) queryParams.append('end_date', params.end_date)
      if (params.search) queryParams.append('search', params.search)

      // Ordering
      if (params.ordering) queryParams.append('ordering', params.ordering)

      const response = await axios.get(`${API_PATH}/`, {
        params: queryParams,
        withCredentials: true
      })

      if (response.data) {
        // The endpoint may return a plain list or a paginated object.
        const data = Array.isArray(response.data)
          ? { results: response.data, count: response.data.length }
          : response.data

        pagination.value = {
          count: data.count || 0,
          current_page: data.current_page || 1,
          total_pages: data.total_pages || 1,
          page_size: data.page_size || 10,
          has_next: data.has_next || false,
          has_previous: data.has_previous || false,
          page_range: data.page_range || [],
        }

        orders.value = (data.results || []).map(normalizeOrder)

        return {
          results: orders.value,
          pagination: pagination.value
        }
      }

      return {
        results: [],
        pagination: {
          count: 0,
          current_page: 1,
          total_pages: 1,
          page_size: 10,
          has_next: false,
          has_previous: false,
          page_range: [],
        }
      }
    } catch (err) {
      console.error('Error fetching orders:', err)
      error.value = err.response?.data?.error || 'Error fetching orders'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchOrderById = async (orderId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get(`${API_PATH}/${orderId}/`, {
        withCredentials: true
      })
      
      if (response.data) {
        currentOrder.value = normalizeOrder(response.data)
        return currentOrder.value
      }
      return null
    } catch (err) {
      console.error('Error fetching order:', err)
      error.value = err.response?.data?.error || 'Error fetching order'
      throw err
    } finally {
      loading.value = false
    }
  }

  const cancelOrder = async (orderId) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_PATH}/${orderId}/cancel/`,
        {},
        { withCredentials: true }
      )
      
      if (response.data) {
        // Update the order in the list
        const index = orders.value.findIndex(o => o.id === orderId)
        if (index !== -1) {
          orders.value[index] = normalizeOrder(response.data)
        }
        
        // Update current order if it's the same
        if (currentOrder.value?.id === orderId) {
          currentOrder.value = normalizeOrder(response.data)
        }
        
        return response.data
      }
      return null
    } catch (err) {
      console.error('Error canceling order:', err)
      error.value = err.response?.data?.error || 'Error canceling order'
      throw err
    } finally {
      loading.value = false
    }
  }

  const trackOrder = async (trackingNumber) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get(`${API_PATH}/track/${trackingNumber}/`, {
        withCredentials: true
      })
      
      return response.data
    } catch (err) {
      console.error('Error tracking order:', err)
      error.value = err.response?.data?.error || 'Error tracking order'
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkoutOptions = ref(null)

  const fetchCheckoutOptions = async () => {
    const response = await axios.get(`${API_PATH}/checkout_options/`)
    checkoutOptions.value = response.data
    return response.data
  }

  // Place an order from the current cart. Errors are returned as a readable
  // message plus field errors so the checkout form can show them inline.
  const placeOrder = async (payload) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.post(`${API_PATH}/checkout/`, payload)
      const order = normalizeOrder(response.data)
      currentOrder.value = order
      return order
    } catch (err) {
      const data = err.response?.data || {}
      error.value = data.detail?.message ||
        (typeof data.detail === 'string' ? data.detail : null) ||
        'Your order could not be placed. Please try again.'
      err.fieldErrors = data.detail ? {} : data
      throw err
    } finally {
      loading.value = false
    }
  }

  // Open (or reopen) the online payment page for an unpaid order.
  const payOrder = async (orderId) => {
    const response = await axios.post(`${API_PATH}/${orderId}/pay/`)
    return response.data.payment_url
  }

  // Admin actions
  const updateOrderStatus = async (orderId, status) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_PATH}/${orderId}/update_status/`,
        { status },
        { withCredentials: true }
      )
      
      if (response.data) {
        // Update the order in the list
        const index = orders.value.findIndex(o => o.id === orderId)
        if (index !== -1) {
          orders.value[index] = normalizeOrder(response.data)
        }
        
        // Update current order if it's the same
        if (currentOrder.value?.id === orderId) {
          currentOrder.value = normalizeOrder(response.data)
        }
        
        return response.data
      }
      return null
    } catch (err) {
      console.error('Error updating order status:', err)
      error.value = err.response?.data?.error || 'Error updating order status'
      throw err
    } finally {
      loading.value = false
    }
  }

  const addTrackingNumber = async (orderId, trackingNumber) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.post(
        `${API_PATH}/${orderId}/add_tracking/`,
        { tracking_number: trackingNumber },
        { withCredentials: true }
      )
      
      if (response.data) {
        // Update the order in the list
        const index = orders.value.findIndex(o => o.id === orderId)
        if (index !== -1) {
          orders.value[index] = normalizeOrder(response.data)
        }
        
        // Update current order if it's the same
        if (currentOrder.value?.id === orderId) {
          currentOrder.value = normalizeOrder(response.data)
        }
        
        return response.data
      }
      return null
    } catch (err) {
      console.error('Error adding tracking number:', err)
      error.value = err.response?.data?.error || 'Error adding tracking number'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    orders,
    currentOrder,
    loading,
    error,
    pagination,

    // Computed
    hasOrders,
    pendingOrders,
    processingOrders,
    completedOrders,
    canceledOrders,

    checkoutOptions,

    // Actions
    fetchOrders,
    fetchCheckoutOptions,
    placeOrder,
    payOrder,
    fetchOrderById,
    cancelOrder,
    trackOrder,
    updateOrderStatus,
    addTrackingNumber
  }
})
