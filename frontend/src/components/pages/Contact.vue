<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Contact Us</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Contact Form -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Send us a message</h2>
        <form @submit.prevent="submitForm" class="space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              id="name"
              v-model="form.name"
              class="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
          </div>
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              id="email"
              v-model="form.email"
              class="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
          </div>
          
          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
            <input
              type="text"
              id="subject"
              v-model="form.subject"
              class="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
          </div>
          
          <div>
            <label for="message" class="block text-sm font-medium text-gray-700 mb-1">Message</label>
            <textarea
              id="message"
              v-model="form.message"
              rows="4"
              class="w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            ></textarea>
          </div>
          
          <button
            type="submit"
            class="btn btn-primary w-full"
            :disabled="loading"
          >
            {{ loading ? 'Sending...' : 'Send Message' }}
          </button>
        </form>
      </div>
      
      <!-- Contact Information -->
      <div class="space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">Contact Information</h2>
          <div class="space-y-4">
            <div class="flex items-start gap-4">
              <i class="fas fa-location-dot text-blue-600 mt-1"></i>
              <div>
                <h3 class="font-medium">Address</h3>
                <p class="text-gray-600">
                  123 Baker Street<br>
                  Cityville, ST 12345<br>
                  United States
                </p>
              </div>
            </div>
            
            <div class="flex items-start gap-4">
              <i class="fas fa-phone text-blue-600 mt-1"></i>
              <div>
                <h3 class="font-medium">Phone</h3>
                <p class="text-gray-600">
                  +1 (555) 123-4567
                </p>
              </div>
            </div>
            
            <div class="flex items-start gap-4">
              <i class="fas fa-envelope text-blue-600 mt-1"></i>
              <div>
                <h3 class="font-medium">Email</h3>
                <p class="text-gray-600">
                  info@beackrei.com
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">Business Hours</h2>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span>Monday - Friday</span>
              <span>7:00 AM - 7:00 PM</span>
            </div>
            <div class="flex justify-between">
              <span>Saturday</span>
              <span>8:00 AM - 6:00 PM</span>
            </div>
            <div class="flex justify-between">
              <span>Sunday</span>
              <span>9:00 AM - 4:00 PM</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const loading = ref(false)
const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const submitForm = async () => {
  loading.value = true
  try {
    // TODO: Implement form submission
    console.log('Form submitted:', form.value)
    // Reset form
    form.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
  } catch (error) {
    console.error('Failed to submit form:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50;
}
</style>
