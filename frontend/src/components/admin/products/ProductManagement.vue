<template>
  <DashboardLayout>
    <template #title>Product Management</template>
    <template #actions>
      <button
        @click="openCreateModal"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <PlusIcon class="h-5 w-5 mr-2" />
        Add Product
      </button>
    </template>

    <div class="p-6">
      <!-- Stats Section -->
      <ProductStats @view-details="handleStatsDetail" class="mb-8" />

      <!-- Filters Section -->
      <ProductFilters @filter="handleFilter" class="mb-6" />

      <!-- Products Table -->
      <DataTable
        :items="products"
        :columns="columns"
        :total-items="totalItems"
        :loading="loading"
        @update:page="handlePageChange"
        @update:pageSize="handlePageSizeChange"
        @update:sort="handleSort"
        @search="handleSearch"
      >
        <template #image="{ item }">
          <div class="flex items-center">
            <img
              :src="item.image"
              :alt="item.name"
              class="h-10 w-10 rounded-full object-cover"
            />
          </div>
        </template>

        <template #name="{ item }">
          <div>
            <div class="font-medium text-gray-900">{{ item.name }}</div>
            <div class="text-gray-500 text-sm">SKU: {{ item.sku }}</div>
          </div>
        </template>

        <template #price="{ item }">
          ${{ item.price.toFixed(2) }}
        </template>

        <template #stock="{ item }">
          <div class="flex items-center">
            <span
              :class="[
                item.stock > 10 ? 'bg-green-100 text-green-800' :
                item.stock > 0 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800',
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
              ]"
            >
              {{ item.stock }} in stock
            </span>
          </div>
        </template>

        <template #status="{ item }">
          <span
            :class="[
              item.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
              'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
            ]"
          >
            {{ item.status }}
          </span>
        </template>

        <template #actions="{ item }">
          <div class="flex justify-end space-x-2">
            <button
              @click="viewProduct(item)"
              class="text-gray-400 hover:text-gray-500"
              title="View Details"
            >
              <EyeIcon class="h-5 w-5" />
            </button>
            <button
              @click="editProduct(item)"
              class="text-blue-400 hover:text-blue-500"
              title="Edit"
            >
              <PencilIcon class="h-5 w-5" />
            </button>
            <button
              @click="deleteProduct(item)"
              class="text-red-400 hover:text-red-500"
              title="Delete"
            >
              <TrashIcon class="h-5 w-5" />
            </button>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Modals -->
    <ProductFormModal
      v-if="showFormModal"
      :product="selectedProduct"
      @close="closeModal"
      @save="saveProduct"
    />

    <ProductDetailModal
      v-if="showDetailModal"
      :product="selectedProduct"
      @close="closeDetailModal"
    />
  </DashboardLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProductStore } from '@/stores/productStore'
import DashboardLayout from '@/components/admin/dashboard/AdminDashboard.vue'
import DataTable from '../common/DataTable.vue'
import ProductStats from './ProductStats.vue'
import ProductFilters from './ProductFilters.vue'
import ProductFormModal from './ProductFormModal.vue'
import ProductDetailModal from './ProductDetailModal.vue'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/vue/24/outline'

const productStore = useProductStore()
const products = ref([])
const totalItems = ref(0)
const loading = ref(false)
const showFormModal = ref(false)
const showDetailModal = ref(false)
const selectedProduct = ref(null)

const columns = [
  { key: 'image', label: '' },
  { key: 'name', label: 'Product' },
  { key: 'category', label: 'Category' },
  { key: 'price', label: 'Price' },
  { key: 'stock', label: 'Stock' },
  { key: 'status', label: 'Status' }
]

const currentFilters = ref({
  search: '',
  category: '',
  status: '',
  priceMin: null,
  priceMax: null,
  stockStatus: '',
  sort: '',
  page: 1,
  pageSize: 10
})

const loadProducts = async () => {
  loading.value = true
  try {
    await productStore.fetchProducts(currentFilters.value)
    products.value = productStore.products
    totalItems.value = productStore.totalItems
  } catch (error) {
    console.error('Error loading products:', error)
  } finally {
    loading.value = false
  }
}

const handleFilter = (filters) => {
  currentFilters.value = { ...currentFilters.value, ...filters, page: 1 }
  loadProducts()
}

const handleSearch = (query) => {
  currentFilters.value.search = query
  currentFilters.value.page = 1
  loadProducts()
}

const handlePageChange = (page) => {
  currentFilters.value.page = page
  loadProducts()
}

const handlePageSizeChange = (pageSize) => {
  currentFilters.value.pageSize = pageSize
  currentFilters.value.page = 1
  loadProducts()
}

const handleSort = ({ key, order }) => {
  currentFilters.value.sort = `${key}_${order}`
  loadProducts()
}

const handleStatsDetail = (type) => {
  switch (type) {
    case 'low_stock':
      currentFilters.value = {
        ...currentFilters.value,
        stockStatus: 'low_stock',
        page: 1
      }
      break
    case 'active':
      currentFilters.value = {
        ...currentFilters.value,
        status: 'active',
        page: 1
      }
      break
    // Add other cases as needed
  }
  loadProducts()
}

const openCreateModal = () => {
  selectedProduct.value = null
  showFormModal.value = true
}

const viewProduct = (product) => {
  selectedProduct.value = product
  showDetailModal.value = true
}

const editProduct = (product) => {
  selectedProduct.value = { ...product }
  showFormModal.value = true
}

const closeModal = () => {
  showFormModal.value = false
  selectedProduct.value = null
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedProduct.value = null
}

const saveProduct = async (productData) => {
  try {
    if (selectedProduct.value) {
      await productStore.updateProduct(productData)
    } else {
      await productStore.createProduct(productData)
    }
    await loadProducts()
    closeModal()
  } catch (error) {
    console.error('Error saving product:', error)
  }
}

const deleteProduct = async (product) => {
  if (confirm('Are you sure you want to delete this product?')) {
    try {
      await productStore.deleteProduct(product.id)
      await loadProducts()
    } catch (error) {
      console.error('Error deleting product:', error)
    }
  }
}

onMounted(loadProducts)
</script>
