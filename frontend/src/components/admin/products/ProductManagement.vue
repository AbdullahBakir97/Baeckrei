<template>
  <div>
    <div class="flex justify-end mb-6">
      <button
        @click="openCreateModal"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-full shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <PlusIcon class="h-5 w-5 mr-2" />
        Add Product
      </button>
    </div>

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
            <div class="font-medium text-cream">{{ item.name }}</div>
          </div>
        </template>

        <template #category="{ item }">
          {{ item.category?.name || '—' }}
        </template>

        <template #price="{ item }">
          {{ Number(item.price).toFixed(2) }} €
        </template>

        <template #stock="{ item }">
          <div class="flex items-center">
            <span
              :class="[
                item.stock > 10 ? 'bg-emerald-400/10 text-emerald-300' :
                item.stock > 0 ? 'bg-amber-300/10 text-amber-200' :
                'bg-red-400/10 text-red-300',
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
              ]"
            >
              {{ item.stock }} in stock
            </span>
          </div>
        </template>

        <template #status="{ item }">
          <span
            :class="[ item.status === 'active' ? 'bg-emerald-400/10 text-emerald-300' : 'bg-red-400/10 text-red-300', 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full' ]"
          >
            {{ item.status }}
          </span>
        </template>

        <template #actions="{ item }">
          <div class="flex justify-end space-x-2">
            <button
              @click="viewProduct(item)"
              class="text-cream-faint hover:text-cream-muted bg-transparent p-1"
              title="View Details"
            >
              <EyeIcon class="h-5 w-5" />
            </button>
            <button
              @click="editProduct(item)"
              class="text-blue-400 hover:text-blue-500 bg-transparent p-1"
              title="Edit"
            >
              <PencilIcon class="h-5 w-5" />
            </button>
            <button
              @click="deleteProduct(item)"
              class="text-red-400 hover:text-red-500 bg-transparent p-1"
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
      :saving="saving"
      :server-errors="formErrors"
      @close="closeModal"
      @save="saveProduct"
    />

    <ProductDetailModal
      v-if="showDetailModal"
      :product="selectedProduct"
      @close="closeDetailModal"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useProductStore } from '@/stores/productStore'
import { useToast } from '@/composables/useToast'
import { useRouter } from 'vue-router'
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
const { showToast } = useToast()
const router = useRouter()
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

// The API can order by name and price; other columns fall back to name.
const toOrdering = (sort) => {
  const [key, order] = (sort || '').split('_')
  if (!['name', 'price'].includes(key)) return 'name'
  return `${order === 'desc' ? '-' : ''}${key}`
}

const loadProducts = async () => {
  loading.value = true
  const f = currentFilters.value
  try {
    await productStore.fetchProducts({
      include_all: true,
      page: f.page,
      page_size: f.pageSize,
      search: f.search,
      categories: f.category ? [f.category] : [],
      status: f.status,
      stock_status: f.stockStatus,
      price_min: f.priceMin,
      price_max: f.priceMax,
      ordering: toOrdering(f.sort)
    })
    products.value = productStore.products
    totalItems.value = productStore.totalItems
  } catch (error) {
    showToast('Products could not be loaded', 'error')
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
  router.push({ name: 'admin-product-detail', params: { id: product.id } })
}

// List rows are a summary; load the full product (description etc.) to edit it.
const editProduct = async (product) => {
  formErrors.value = {}
  const full = await productStore.fetchProductById(product.id)
  if (!full) {
    showToast('The product could not be loaded', 'error')
    return
  }
  selectedProduct.value = full
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

const saving = ref(false)
const formErrors = ref({})

const saveProduct = async (productData) => {
  saving.value = true
  formErrors.value = {}
  try {
    if (selectedProduct.value) {
      await productStore.updateProduct(productData)
      showToast('Product saved')
    } else {
      await productStore.createProduct(productData)
      showToast('Product created')
    }
    await loadProducts()
    closeModal()
  } catch (error) {
    formErrors.value = error.response?.data || { general: 'The product could not be saved.' }
  } finally {
    saving.value = false
  }
}

const deleteProduct = async (product) => {
  if (!confirm(`Delete ${product.name}?`)) return
  try {
    const result = await productStore.deleteProduct(product.id)
    showToast(result?.discontinued ? 'Used in past orders, so it was marked discontinued' : 'Product deleted')
    await loadProducts()
  } catch (error) {
    showToast('The product could not be deleted', 'error')
  }
}

onMounted(loadProducts)
</script>
