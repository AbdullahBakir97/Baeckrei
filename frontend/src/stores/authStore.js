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
      // Don't show the previous user's cart or addresses to the next person.
      const [{ useCartStore }, { useAddressStore }] = await Promise.all([
        import('./cartStore'), import('./addressStore')
      ])
      useCartStore().$reset()
      useAddressStore().reset()
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

  // Turn a DRF error response into one readable sentence.
  const apiErrorMessage = (err, fallback) => {
    const data = err.response?.data
    if (!data) return fallback
    if (typeof data === 'string') return fallback
    if (data.detail) return data.detail
    if (data.error) return data.error
    const first = Object.values(data)[0]
    return Array.isArray(first) ? first[0] : (first || fallback)
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
    } catch (err) {
      error.value = apiErrorMessage(err, 'Registration failed. Please check your details.')
      throw err
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
    } catch (err) {
      error.value = apiErrorMessage(err, 'Your profile could not be saved.')
      throw err
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (passwords) => {
    try {
      loading.value = true
      error.value = null
      await axios.post('/api/accounts/users/change_password/', passwords)
      return true
    } catch (err) {
      error.value = apiErrorMessage(err, 'Your password could not be changed.')
      throw err
    } finally {
      loading.value = false
    }
  }

  const requestPasswordReset = async (email) => {
    const response = await axios.post('/api/accounts/password-reset/', { email })
    return response.data.message
  }

  const confirmPasswordReset = async ({ uid, token, newPassword }) => {
    try {
      const response = await axios.post('/api/accounts/password-reset/confirm/', {
        uid, token, new_password: newPassword
      })
      return response.data.message
    } catch (err) {
      throw new Error(apiErrorMessage(err, 'Your password could not be reset.'))
    }
  }

  // Initialize auth state once; concurrent callers share the same request.
  let initPromise = null
  const initializeAuth = () => {
    if (!initPromise) {
      initPromise = (async () => {
        if (token.value) {
          try {
            await fetchCurrentUser()
          } catch (error) {
            console.error('Error initializing auth:', error)
            setAuthToken(null)
          }
        }
        initialized.value = true
      })()
    }
    return initPromise
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
    requestPasswordReset,
    confirmPasswordReset,
    apiErrorMessage,
    initializeAuth,
    fetchCurrentUser
  }
})
