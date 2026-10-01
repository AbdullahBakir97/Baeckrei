import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/plugins/axios'

const API_PATH = '/api/accounts/addresses/'

// The signed-in customer's saved delivery addresses.
export const useAddressStore = defineStore('addresses', () => {
  const addresses = ref([])
  const loading = ref(false)

  const fetchAddresses = async () => {
    loading.value = true
    try {
      const response = await axios.get(API_PATH)
      addresses.value = response.data
      return addresses.value
    } finally {
      loading.value = false
    }
  }

  const saveAddress = async (address) => {
    const response = address.id
      ? await axios.patch(`${API_PATH}${address.id}/`, address)
      : await axios.post(API_PATH, address)
    await fetchAddresses()
    return response.data
  }

  const deleteAddress = async (id) => {
    await axios.delete(`${API_PATH}${id}/`)
    addresses.value = addresses.value.filter(a => a.id !== id)
  }

  const reset = () => { addresses.value = [] }

  return { addresses, loading, fetchAddresses, saveAddress, deleteAddress, reset }
})
