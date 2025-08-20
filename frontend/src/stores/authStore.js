import { defineStore } from 'pinia'
import axios from '@/plugins/axios'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)
  const initialized = ref(false)
  const isAuthenticated = ref(!!token.value)

  const isAdmin = computed(() => {
    return user.value?.is_admin === true
  })

  const setAuthToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
      isAuthenticated.value = true
    } else {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      isAuthenticated.value = false
    }
  }

  const login = async (credentials) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.post('/api/token/', credentials)
      const tokenResponse = response.data.access
      setAuthToken(tokenResponse)
      await fetchCurrentUser()
      return isAdmin.value ? '/admin' : '/'
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to login'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      loading.value = true
      error.value = null
      if (token.value) {
        await axios.post('/api/accounts/users/logout/')
      }
    } catch (error) {
      console.error('Error during logout:', error)
    } finally {
      setAuthToken(null)
      user.value = null
      loading.value = false
    }
  }

  const fetchCurrentUser = async () => {
    try {
      if (!token.value) return null
      const response = await axios.get('/api/accounts/users/me/')
      user.value = response.data
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        setAuthToken(null)
        user.value = null
      }
      throw error
    }
  }

  const register = async (userData) => {
    try {
      loading.value = true
      error.value = null
      await axios.post('/api/accounts/users/register/', userData)
      // After registration, log the user in
      return await login({
        email: userData.email,
        password: userData.password
      })
    } catch (error) {
      error.value = error.response?.data?.detail || 'Failed to register'
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateProfile = async (userData) => {
    try {
      loading.value = true
      error.value = null
      const response = await axios.patch('/api/accounts/users/me/', userData)
      user.value = response.data
      return response.data
    } catch (error) {
      error.value = error.response?.data?.detail || 'Failed to update profile'
      throw error
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (passwords) => {
    try {
      loading.value = true
      error.value = null
      await axios.post('/api/accounts/users/change-password/', passwords)
      return true
    } catch (error) {
      error.value = error.response?.data?.detail || 'Failed to change password'
      throw error
    } finally {
      loading.value = false
    }
  }

  // Initialize auth state
  const initializeAuth = async () => {
    if (initialized.value) return
    if (token.value) {
      try {
        await fetchCurrentUser()
      } catch (error) {
        console.error('Error initializing auth:', error)
        setAuthToken(null)
      }
    }
    initialized.value = true
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    register,
    updateProfile,
    changePassword,
    initializeAuth,
    fetchCurrentUser
  }
})
