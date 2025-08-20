import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { ref, computed } from 'vue'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_PATH = `${API_BASE}/api/orders`

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

      const response = await axios.get(API_PATH, {
        params: queryParams,
        withCredentials: true
      })

      if (response.data) {
        // Update pagination
        pagination.value = {
          count: response.data.count || 0,
          current_page: response.data.current_page || 1,
          total_pages: response.data.total_pages || 1,
          page_size: response.data.page_size || 10,
          has_next: response.data.has_next || false,
          has_previous: response.data.has_previous || false,
          page_range: response.data.page_range || [],
        }

        // Update orders with normalized data
        orders.value = (response.data.results || []).map(order => ({
          ...order,
          created_at: new Date(order.created_at),
          updated_at: new Date(order.updated_at),
          estimated_delivery_date: order.estimated_delivery_date ? 
            new Date(order.estimated_delivery_date) : null,
          total_price: parseFloat(order.total_price),
          order_items: (order.order_items || []).map(item => ({
            ...item,
            price_per_item: parseFloat(item.price_per_item),
            product: item.product ? {
              ...item.product,
              price: parseFloat(item.product.price),
              image: item.product.image_url || 
                    (item.product.image ? 
                      (item.product.image.startsWith('http') ? 
                        item.product.image : 
                        `${API_BASE}/media/${item.product.image}`)
                      : null)
            } : null
          }))
        }))

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
        currentOrder.value = {
          ...response.data,
          created_at: new Date(response.data.created_at),
          updated_at: new Date(response.data.updated_at),
          estimated_delivery_date: response.data.estimated_delivery_date ? 
            new Date(response.data.estimated_delivery_date) : null,
          total_price: parseFloat(response.data.total_price),
          order_items: (response.data.order_items || []).map(item => ({
            ...item,
            price_per_item: parseFloat(item.price_per_item),
            product: item.product ? {
              ...item.product,
              price: parseFloat(item.product.price),
              image: item.product.image_url || 
                    (item.product.image ? 
                      (item.product.image.startsWith('http') ? 
                        item.product.image : 
                        `${API_BASE}/media/${item.product.image}`)
                      : null)
            } : null
          }))
        }
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
        `${API_PATH}/${orderId}/update_status/`,
        { status: 'Canceled' },
        { withCredentials: true }
      )
      
      if (response.data) {
        // Update the order in the list
        const index = orders.value.findIndex(o => o.id === orderId)
        if (index !== -1) {
          orders.value[index] = {
            ...response.data,
            created_at: new Date(response.data.created_at),
            updated_at: new Date(response.data.updated_at)
          }
        }
        
        // Update current order if it's the same
        if (currentOrder.value?.id === orderId) {
          currentOrder.value = {
            ...response.data,
            created_at: new Date(response.data.created_at),
            updated_at: new Date(response.data.updated_at)
          }
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
          orders.value[index] = {
            ...response.data,
            created_at: new Date(response.data.created_at),
            updated_at: new Date(response.data.updated_at)
          }
        }
        
        // Update current order if it's the same
        if (currentOrder.value?.id === orderId) {
          currentOrder.value = {
            ...response.data,
            created_at: new Date(response.data.created_at),
            updated_at: new Date(response.data.updated_at)
          }
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
          orders.value[index] = {
            ...response.data,
            created_at: new Date(response.data.created_at),
            updated_at: new Date(response.data.updated_at)
          }
        }
        
        // Update current order if it's the same
        if (currentOrder.value?.id === orderId) {
          currentOrder.value = {
            ...response.data,
            created_at: new Date(response.data.created_at),
            updated_at: new Date(response.data.updated_at)
          }
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

    // Actions
    fetchOrders,
    fetchOrderById,
    cancelOrder,
    trackOrder,
    updateOrderStatus,
    addTrackingNumber
  }
})
