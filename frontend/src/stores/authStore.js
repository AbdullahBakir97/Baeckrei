import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    isAdmin: (state) => state.user?.is_staff
  },

  actions: {
    async login(credentials) {
      try {
        this.loading = true
        this.error = null
        // First get the JWT token
        const tokenResponse = await axios.post('/api/token/', credentials)
        const token = tokenResponse.data.access
        
        // Set the token in localStorage and axios headers
        localStorage.setItem('token', token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        
        // Get user details
        const userResponse = await axios.get('/api/accounts/users/me/')
        this.user = userResponse.data
        
        // Return whether user is admin for navigation
        return this.user.is_staff ? 'admin' : 'customer'
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to login'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        this.loading = true
        this.error = null
        await axios.post('/api/accounts/users/logout/')
        this.user = null
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to logout'
      } finally {
        this.loading = false
      }
    },

    async register(userData) {
      try {
        this.loading = true
        this.error = null
        await axios.post('/api/accounts/users/register/', userData)
        // After registration, log the user in
        return await this.login({
          email: userData.email,
          password: userData.password
        })
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to register'
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchCurrentUser() {
      try {
        this.loading = true
        this.error = null
        const response = await axios.get('/api/accounts/users/me/')
        this.user = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch user'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateProfile(userData) {
      try {
        this.loading = true
        this.error = null
        const response = await axios.patch('/api/accounts/users/me/', userData)
        this.user = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to update profile'
        throw error
      } finally {
        this.loading = false
      }
    },

    async changePassword(passwords) {
      try {
        this.loading = true
        this.error = null
        await axios.post('/api/accounts/users/change_password/', passwords)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to change password'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
