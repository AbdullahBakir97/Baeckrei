<template>
  <div class="fixed inset-0 z-10 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex min-h-screen items-end justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>

      <span class="hidden sm:inline-block sm:h-screen sm:align-middle" aria-hidden="true">&#8203;</span>

      <div class="relative inline-block transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left align-bottom shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6 sm:align-middle">
        <div>
          <h3 class="text-lg font-medium leading-6 text-gray-900" id="modal-title">
            {{ product ? 'Edit Product' : 'Create New Product' }}
          </h3>
          <form @submit.prevent="handleSubmit" class="mt-4 space-y-4">
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                id="name"
                v-model="formData.name"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label for="description" class="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                id="description"
                v-model="formData.description"
                rows="3"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              ></textarea>
            </div>

            <div>
              <label for="category" class="block text-sm font-medium text-gray-700">Category</label>
              <select
                id="category"
                v-model="formData.category"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                required
              >
                <option v-for="category in categories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="price" class="block text-sm font-medium text-gray-700">Price</label>
                <div class="mt-1 relative rounded-md shadow-sm">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span class="text-gray-500 sm:text-sm">$</span>
                  </div>
                  <input
                    type="number"
                    id="price"
                    v-model="formData.price"
                    min="0"
                    step="0.01"
                    class="pl-7 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    required
                  />
                </div>
              </div>

              <div>
                <label for="stock" class="block text-sm font-medium text-gray-700">Stock</label>
                <input
                  type="number"
                  id="stock"
                  v-model="formData.stock"
                  min="0"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  required
                />
              </div>
            </div>

            <div>
              <label for="image" class="block text-sm font-medium text-gray-700">Image URL</label>
              <input
                type="url"
                id="image"
                v-model="formData.image"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              />
            </div>

            <div class="mt-4 space-x-3">
              <label class="inline-flex items-center">
                <input
                  type="checkbox"
                  v-model="formData.isVegan"
                  class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">Vegan</span>
              </label>

              <label class="inline-flex items-center">
                <input
                  type="checkbox"
                  v-model="formData.isVegetarian"
                  class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">Vegetarian</span>
              </label>

              <label class="inline-flex items-center">
                <input
                  type="checkbox"
                  v-model="formData.isGlutenFree"
                  class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm text-gray-700">Gluten Free</span>
              </label>
            </div>

            <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3">
              <button
                type="button"
                class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:text-sm"
                @click="$emit('close')"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
              >
                {{ product ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useProductStore } from '@/stores/productStore'

const props = defineProps({
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])
const productStore = useProductStore()
const categories = ref([])

const formData = ref({
  name: '',
  description: '',
  category: '',
  price: 0,
  stock: 0,
  image: '',
  isVegan: false,
  isVegetarian: false,
  isGlutenFree: false
})

const loadCategories = async () => {
  categories.value = await productStore.fetchCategories()
}

const handleSubmit = () => {
  emit('save', {
    ...formData.value,
    id: props.product?.id
  })
}

watch(() => props.product, (newProduct) => {
  if (newProduct) {
    formData.value = { ...newProduct }
  } else {
    formData.value = {
      name: '',
      description: '',
      category: '',
      price: 0,
      stock: 0,
      image: '',
      isVegan: false,
      isVegetarian: false,
      isGlutenFree: false
    }
  }
}, { immediate: true })

onMounted(loadCategories)
</script>
