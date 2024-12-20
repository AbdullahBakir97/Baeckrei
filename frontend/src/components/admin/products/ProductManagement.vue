<template>
  <div>
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-xl font-semibold text-gray-900">Products</h1>
        <p class="mt-2 text-sm text-gray-700">
          A list of all products in your store including their name, price, and status.
        </p>
      </div>
      <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
        <button
          @click="openCreateModal"
          class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
        >
          Add product
        </button>
      </div>
    </div>

    <div class="mt-8 flex flex-col">
      <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Price</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Stock</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="product in products" :key="product.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm sm:pl-6">
                    <div class="flex items-center">
                      <div class="h-10 w-10 flex-shrink-0">
                        <img :src="product.image" :alt="product.name" class="h-10 w-10 rounded-full object-cover" />
                      </div>
                      <div class="ml-4">
                        <div class="font-medium text-gray-900">{{ product.name }}</div>
                        <div class="text-gray-500">{{ product.sku }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ product.category }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">${{ product.price.toFixed(2) }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ product.stock }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <span
                      :class="[
                        product.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                        'inline-flex rounded-full px-2 text-xs font-semibold leading-5'
                      ]"
                    >
                      {{ product.status }}
                    </span>
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <button @click="editProduct(product)" class="text-indigo-600 hover:text-indigo-900 mr-4">Edit</button>
                    <button @click="deleteProduct(product)" class="text-red-600 hover:text-red-900">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <ProductFormModal
      v-if="showModal"
      :product="selectedProduct"
      @close="closeModal"
      @save="saveProduct"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProductStore } from '@/stores/productStore'
import ProductFormModal from './ProductFormModal.vue'

const productStore = useProductStore()
const products = ref([])
const showModal = ref(false)
const selectedProduct = ref(null)

const loadProducts = async () => {
  await productStore.fetchProducts()
  products.value = productStore.products
}

const openCreateModal = () => {
  selectedProduct.value = null
  showModal.value = true
}

const editProduct = (product) => {
  selectedProduct.value = { ...product }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedProduct.value = null
}

const saveProduct = async (productData) => {
  if (selectedProduct.value) {
    await productStore.updateProduct(productData)
  } else {
    await productStore.createProduct(productData)
  }
  await loadProducts()
  closeModal()
}

const deleteProduct = async (product) => {
  if (confirm('Are you sure you want to delete this product?')) {
    await productStore.deleteProduct(product.id)
    await loadProducts()
  }
}

onMounted(loadProducts)
</script>
