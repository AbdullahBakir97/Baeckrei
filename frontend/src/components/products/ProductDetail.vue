<template>
  <div class="container py-8">
    <!-- Loading State -->
    <div v-if="productStore.loading" class="grid place-items-center h-96">
      <div class="text-6xl text-primary-600">
        <font-awesome-icon icon="spinner" class="animate-spin" />
      </div>
      <p class="mt-4 text-gray-400">Loading product details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="productStore.error" class="text-center py-12">
      <font-awesome-icon icon="circle-xmark" class="text-4xl text-red-500 mb-4" />
      <p class="text-lg text-gray-600">{{ productStore.error }}</p>
      <button @click="loadProduct" class="btn btn-primary mt-4">
        <font-awesome-icon icon="rotate" class="mr-2" />
        Try Again
      </button>
    </div>

    <!-- Product Details -->
    <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column: Images -->
      <ProductImage 
      :product="product"
      :is-in-wishlist="isInWishlist"
      :is-in-compare="isInCompare"
      @toggle-wishlist="toggleWishlist"
      @toggle-compare="toggleCompare"
      @share-product="shareProduct"
    />

      <!-- Middle Column: Main Info -->
      <div class="lg:col-span-2">
        <div class="space-y-4">
          <!-- Basic Info Card -->
          <div class="info-card">
            <div class="card-header">
              <nav class="flex items-center space-x-2 text-sm text-gray-400">
                <router-link to="/" class="hover:text-amber-500 transition-colors">Home</router-link>
                <span>/</span>
                <router-link to="/products" class="hover:text-amber-500 transition-colors">Products</router-link>
                <span>/</span>
                <router-link
                  v-if="product?.category?.slug"
                  :to="{ name: 'category', params: { category: product.category.slug }}"
                  class="hover:text-amber-500 transition-colors"
                >
                  {{ product?.category?.name }}
                </router-link>
              </nav>
            </div>

            <div class="card-content">
              <h1 class="text-3xl font-bold bg-gradient-to-r from-amber-400 to-amber-600 
                         bg-clip-text text-transparent mb-4">
                {{ product.name }}
              </h1>

              <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div class="flex items-center gap-4">
                  <span class="text-3xl font-bold text-transparent bg-clip-text 
                             bg-gradient-to-r from-amber-400 to-amber-600">
                    {{ formatPrice(product.price) }} €
                  </span>
                  <span :class="[
                    'tag',
                    product.stock > 5 ? 'bg-green-500/20 text-green-300' :
                    product.stock > 0 ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-red-500/20 text-red-300'
                  ]">
                    {{ product.stock > 5 ? 'In Stock' :
                       product.stock > 0 ? `Only ${product.stock} left` :
                       'Out of Stock' }}
                  </span>
                </div>
                
                <div class="flex items-center gap-4">
                  <div class="quantity-controls">
                    <button @click="handleQuantityUpdate($event, quantity - 1)"
                            class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.02)] 
                                  hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-amber-600/20
                                  flex items-center justify-center 
                                  transition-all duration-300 group
                                  relative overflow-hidden"
                            :disabled="quantity <= 1">
                      <!-- Glass effect overlay -->
                      <div class="absolute inset-0 backdrop-blur-sm bg-gradient-to-br from-white/5 to-transparent"></div>
                      <font-awesome-icon icon="minus" 
                                      class="text-gray-400 group-hover:text-amber-500
                                              transition-colors duration-300 relative z-10" />
                    </button>
                    <span class="text-white font-medium w-6 text-center">{{ quantity }}</span>
                    <button @click="handleQuantityUpdate($event, quantity + 1)"
                            class="w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.02)]
                                  hover:bg-gradient-to-r hover:from-amber-500/20 hover:to-amber-600/20
                                  flex items-center justify-center
                                  transition-all duration-300 group
                                  relative overflow-hidden"
                            :disabled="quantity >= product.stock">
                      <!-- Glass effect overlay -->
                      <div class="absolute inset-0 backdrop-blur-sm bg-gradient-to-br from-white/5 to-transparent"></div>
                      <font-awesome-icon icon="plus"
                                      class="text-gray-400 group-hover:text-amber-500
                                              transition-colors duration-300 relative z-10" />
                    </button>
                  </div>
                  <div class="flex items-center gap-2">
                    <button v-if="!isInCart"
                            v-show="product.available"
                            @click="addToCart(product)"
                            class="px-4 py-2 rounded-lg text-white font-medium
                                  bg-gradient-to-r from-amber-500/90 to-amber-600/90
                                  hover:from-amber-500 hover:to-amber-600
                                  transform hover:-translate-y-0.5 transition-all duration-300
                                  shadow-lg hover:shadow-amber-500/25">
                      Add to Cart
                    </button>
                    
                    <button v-else-if="product.available"
                            @click="removeFromCart(product.id)"
                            class="w-10 h-10 rounded-lg bg-[rgba(255,255,255,0.05)]
                                  hover:bg-red-500/20 active:bg-red-500/30
                                  flex items-center justify-center
                                  transition-all duration-300 ease-in-out
                                  group/trash relative overflow-hidden">
                      <!-- Glass effect overlay -->
                      <div class="absolute inset-0 backdrop-blur-sm bg-gradient-to-br from-white/5 to-transparent"></div>
                      <font-awesome-icon icon="trash"
                                        class="text-gray-400 group-hover/trash:text-red-400
                                              transition-colors duration-300 relative z-10" />
                    </button>
                    
                    <button v-else
                            disabled
                            class="px-4 py-2 rounded-lg text-gray-400 font-medium
                                  bg-[rgba(255,255,255,0.03)]
                                  cursor-not-allowed opacity-50">
                      Out of Stock
                    </button>
                  </div>
                </div>
              </div>

              <div class="prose prose-invert max-w-none mb-6">
                <p class="text-gray-300">{{ product.description }}</p>
              </div>

              <div class="flex flex-wrap gap-3">
                <span v-if="product.is_vegan" class="tag bg-green-500/20 text-green-300">
                  <font-awesome-icon icon="leaf" class="mr-1" /> Vegan
                </span>
                <span v-if="product.is_vegetarian" class="tag bg-green-500/20 text-green-300">
                  <font-awesome-icon icon="seedling" class="mr-1" /> Vegetarian
                </span>
                <span v-if="product.is_gluten_free" class="tag bg-yellow-500/20 text-yellow-300">
                  <font-awesome-icon icon="wheat-alt" class="mr-1" /> Gluten Free
                </span>
              </div>
            </div>
          </div>

          <!-- Detailed Info Grid -->
          <div class="info-grid">
            <!-- Ingredients Card -->
            <div class="info-card">
              <div class="card-header">
                <h2 class="text-lg font-semibold text-gray-200">
                  <font-awesome-icon icon="mortar-pestle" class="mr-2 text-amber-500" />
                  Ingredients
                </h2>
                <span class="text-sm text-gray-400">{{ product.ingredients?.length || 0 }} items</span>
              </div>
              <div class="card-content">
                <table class="info-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Type</th>
                      <th>Origin</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ingredient in product.ingredients" :key="ingredient.id">
                      <td>{{ ingredient.name }}</td>
                      <td>{{ ingredient.type || 'N/A' }}</td>
                      <td>{{ ingredient.origin || 'N/A' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Allergens Card -->
            <div class="info-card">
              <div class="card-header">
                <h2 class="text-lg font-semibold text-gray-200">
                  <font-awesome-icon icon="triangle-exclamation" class="mr-2 text-amber-500" />
                  Allergens
                </h2>
                <span class="text-sm text-gray-400">{{ product.allergens?.length || 0 }} items</span>
              </div>
              <div class="card-content">
                <div class="grid gap-2">
                  <div v-for="allergen in product.allergens" 
                       :key="allergen.id"
                       class="flex items-center gap-3 p-2 bg-[rgba(255,255,255,0.02)] rounded-lg">
                    <div class="p-2 bg-red-500/20 rounded-lg">
                      <img v-if="allergen.icon && allergen.icon.startsWith('http')"
                           :src="allergen.icon"
                           :alt="allergen.name"
                           class="w-6 h-6 object-contain"
                           @error="handleImageError" />
                      <font-awesome-icon v-else 
                                       icon="triangle-exclamation"
                                       class="text-red-400" />
                    </div>
                    <div>
                      <h3 class="font-medium text-gray-200">{{ allergen.name }}</h3>
                      <p class="text-sm text-gray-400">{{ allergen.description || 'No description available' }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Nutrition Card -->
            <div v-if="product.nutrition_info" class="info-card col-span-2">
              <div class="card-header">
                <h2 class="text-lg font-semibold text-gray-200">
                  <font-awesome-icon icon="chart-pie" class="mr-2 text-amber-500" />
                  Nutrition Information
                </h2>
                <span class="text-sm text-gray-400">per 100g</span>
              </div>
              <div class="card-content">
                <div class="grid gap-4">
                  <!-- Main Nutrients -->
                  <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg text-center">
                      <div class="flex items-center justify-center gap-2 mb-1">
                        <font-awesome-icon icon="bolt" class="text-amber-500" />
                        <span class="text-sm text-gray-400">Calories</span>
                      </div>
                      <span class="text-lg font-medium text-gray-200">
                        {{ product.nutrition_info.calories }} kcal
                      </span>
                    </div>
                    <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg text-center">
                      <div class="flex items-center justify-center gap-2 mb-1">
                        <font-awesome-icon icon="dumbbell" class="text-amber-500" />
                        <span class="text-sm text-gray-400">Proteins</span>
                      </div>
                      <span class="text-lg font-medium text-gray-200">
                        {{ product.nutrition_info.proteins }}g
                      </span>
                    </div>
                    <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg text-center">
                      <div class="flex items-center justify-center gap-2 mb-1">
                        <font-awesome-icon icon="bread-slice" class="text-amber-500" />
                        <span class="text-sm text-gray-400">Carbs</span>
                      </div>
                      <span class="text-lg font-medium text-gray-200">
                        {{ product.nutrition_info.carbohydrates }}g
                      </span>
                    </div>
                    <div class="bg-[rgba(255,255,255,0.02)] p-3 rounded-lg text-center">
                      <div class="flex items-center justify-center gap-2 mb-1">
                        <font-awesome-icon icon="oil-can" class="text-amber-500" />
                        <span class="text-sm text-gray-400">Fats</span>
                      </div>
                      <span class="text-lg font-medium text-gray-200">
                        {{ product.nutrition_info.fats }}g
                      </span>
                    </div>
                  </div>

                  <!-- Detailed Nutrition Table -->
                  <table class="info-table">
                    <thead>
                      <tr>
                        <th>Nutrient</th>
                        <th>Amount</th>
                        <th>% Daily Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Total Fat</td>
                        <td>{{ product.nutrition_info.fats }}g</td>
                        <td>{{ Math.round((product.nutrition_info.fats / 65) * 100) }}%</td>
                      </tr>
                      <tr>
                        <td>Saturated Fat</td>
                        <td>{{ product.nutrition_info.saturated_fats || 0 }}g</td>
                        <td>{{ Math.round(((product.nutrition_info.saturated_fats || 0) / 20) * 100) }}%</td>
                      </tr>
                      <tr>
                        <td>Total Carbohydrates</td>
                        <td>{{ product.nutrition_info.carbohydrates }}g</td>
                        <td>{{ Math.round((product.nutrition_info.carbohydrates / 300) * 100) }}%</td>
                      </tr>
                      <tr>
                        <td>Dietary Fiber</td>
                        <td>{{ product.nutrition_info.fiber || 0 }}g</td>
                        <td>{{ Math.round(((product.nutrition_info.fiber || 0) / 25) * 100) }}%</td>
                      </tr>
                      <tr>
                        <td>Sugars</td>
                        <td>{{ product.nutrition_info.sugars || 0 }}g</td>
                        <td>-</td>
                      </tr>
                      <tr>
                        <td>Protein</td>
                        <td>{{ product.nutrition_info.proteins }}g</td>
                        <td>{{ Math.round((product.nutrition_info.proteins / 50) * 100) }}%</td>
                      </tr>
                      <tr>
                        <td>Sodium</td>
                        <td>{{ product.nutrition_info.sodium || 0 }}mg</td>
                        <td>{{ Math.round(((product.nutrition_info.sodium || 0) / 2400) * 100) }}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Related Products -->
    <div v-if="productStore.relatedProducts.length > 0" 
         class="mt-16 bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] border border-white/10 
                hover:border-white/20 hover:shadow-red-500/10 transition-all duration-300 p-6 rounded-lg">
      <h2 class="text-2xl font-bold mb-6 bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
        Related Products
      </h2>
      
      <!-- Loading State -->
      <div v-if="productStore.relatedProductsLoading" class="flex justify-center py-8">
        <font-awesome-icon icon="spinner" class="text-3xl text-primary-600 animate-spin" />
      </div>
      
      <!-- Products Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
        <router-link
          v-for="relatedProduct in productStore.relatedProducts"
          :key="relatedProduct.id"
          :to="{ name: 'product-detail', params: { id: relatedProduct.id }}"
          class="group"
        >
          <div class="bg-[rgba(255,255,255,0.02)] rounded-lg p-4 transition-all duration-300 
                      hover:bg-[rgba(255,255,255,0.05)] hover:shadow-lg">
            <!-- Product Image -->
            <div class="aspect-square rounded-lg overflow-hidden bg-transparent mb-4">
              <img
                :src="getImageUrl(relatedProduct.image)"
                :alt="relatedProduct.name"
                class="w-full h-full object-contain mix-blend-normal transform transition-transform 
                       duration-500 group-hover:scale-110"
              >
            </div>
            
            <!-- Product Info -->
            <h3 class="text-lg font-semibold text-gray-200 mb-2 truncate">{{ relatedProduct.name }}</h3>
            <p class="text-amber-500 font-bold">{{ formatPrice(relatedProduct.price) }} €</p>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/productStore'
import { useCartStore } from '@/stores/cartStore'
import { useWishlistStore } from '@/stores/wishlistStore'
import { useCompareStore } from '@/stores/compareStore'
import { useToast } from '@/composables/useToast'
import { useModalStore } from '@/stores/modalStore'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import ImageZoomModal from '@/components/common/ImageZoomModal.vue'
import ProductImage from './ProductImage.vue'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const compareStore = useCompareStore()
const { showToast } = useToast()
const modalStore = useModalStore()

// Constants
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const defaultImage = ref('/assets/images/placeholder.jpg')

// State
const quantity = ref(1)
const selectedImage = ref(null)
const loading = ref(false)

// Computed
const product = computed(() => productStore.product)
const cartItem = computed(() => 
  cartStore.items.find(item => item.product.id === product.value?.id)
)

const isInWishlist = computed(() => 
  wishlistStore.items.some(item => item.id === product.value?.id)
)

const isInCompare = computed(() => 
  compareStore.items.some(item => item.id === product.value?.id)
)

const isInCart = computed(() => {
  return cartStore.items.some(item => item.product?.id === product.value?.id)
})


const currentQuantity = computed(() => cartItem.value?.quantity || quantity.value)

const relatedProducts = computed(() => {
  if (!product.value) return []
  return productStore.products.filter(p => 
    p.category?.id === product.value.category?.id && 
    p.id !== product.value.id
  ).slice(0, 4)
})

// Methods
const openImageModal = () => {
  if (!product.value) return
  
  // Filter out invalid images and get URLs
  const allImages = [product.value.image, ...(product.value.images || [])]
  const validImages = allImages
    .filter(img => {
      const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
      return imageExtensions.some(ext => img.toLowerCase().endsWith(ext))
    })
    .map(img => getImageUrl(img))
  
  if (validImages.length === 0) {
    console.warn('No valid images found for the modal')
    return
  }

  const initialIndex = selectedImage.value 
    ? allImages.findIndex(img => img === selectedImage.value)
    : 0

  modalStore.openModal({
    component: ImageZoomModal,
    props: {
      images: validImages,
      initialIndex: Math.max(0, initialIndex),
      productName: product.value.name
    }
  })
}

const shareProduct = async () => {
  try {
    if (navigator.share) {
      await navigator.share({
        title: product.value.name,
        text: product.value.description,
        url: window.location.href
      })
      showToast('Product shared successfully', 'success')
    } else {
      await navigator.clipboard.writeText(window.location.href)
      showToast('Link copied to clipboard', 'success')
    }
  } catch (error) {
    console.error('Error sharing:', error)
    showToast('Failed to share product', 'error')
  }
}

const toggleWishlist = async () => {
  try {
    if (isInWishlist.value) {
      await wishlistStore.removeItem(product.value.id)
      showToast('Removed from wishlist', 'success')
    } else {
      await wishlistStore.addItem(product.value)
      showToast('Added to wishlist', 'success')
    }
  } catch (error) {
    console.error('Wishlist error:', error)
    showToast('Failed to update wishlist', 'error')
  }
}

const toggleCompare = async () => {
  try {
    if (isInCompare.value) {
      await compareStore.removeItem(product.value.id)
      showToast('Removed from compare', 'success')
    } else {
      if (compareStore.items.length >= 4) {
        showToast('Maximum 4 items can be compared', 'warning')
        return
      }
      await compareStore.addItem(product.value)
      showToast('Added to compare', 'success')
    }
  } catch (error) {
    console.error('Compare error:', error)
    showToast('Failed to update compare list', 'error')
  }
}

const getImageUrl = (path) => {
  if (!path) return '/images/placeholder.png'
  
  // If it's already a full URL or the placeholder, return it
  if (path.startsWith('http') || path === '/images/placeholder.png') {
    return path
  }

  // Check if the path ends with a non-image extension
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
  const extension = path.toLowerCase().split('.').pop()
  const hasValidExtension = extension && imageExtensions.includes(`.${extension}`)
  
  if (!hasValidExtension) {
    console.warn(`Invalid image extension for path: ${path}`)
    return '/images/placeholder.png'
  }

  // Construct the full URL, ensuring no duplicate /media/ prefixes
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const cleanPath = path.replace(/^\/media\/+/, '/media/')
  return `${baseUrl}${cleanPath.startsWith('/') ? '' : '/'}${cleanPath}`
}

const handleImageError = (event) => {
  console.warn('Image failed to load:', event.target.src)
  event.target.src = '/images/placeholder.png'
}

async function loadProduct() {
  if (!route.params.id) {
    showToast('Invalid product ID', 'error')
    router.push('/products')
    return
  }

  try {
    await productStore.fetchProductById(route.params.id)
    await productStore.fetchRelatedProducts(route.params.id)
    
    if (!productStore.product) {
      showToast('Product not found', 'error')
      router.push('/products')
    }
    
    // Update quantity if item is in cart
    const item = cartStore.items.find(item => item.product.id === route.params.id)
    if (item) {
      quantity.value = item.quantity
    } else {
      quantity.value = 1
    }
  } catch (error) {
    console.error('Error loading product:', error)
    showToast('Failed to load product details', 'error')
    router.push('/products')
  }
}

const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

const handleQuantityUpdate = async (_, newQuantity) => {
  if (!product.value?.id) return
  
  try {
    loading.value = true
    if (cartItem.value) {
      await cartStore.updateQuantity(product.value.id, newQuantity)
    } else {
      await cartStore.addItem(product.value.id, newQuantity)
    }
    quantity.value = newQuantity
    showToast('Cart updated successfully')
  } catch (error) {
    console.error('Failed to update cart:', error)
    showToast('Failed to update cart', 'error')
  } finally {
    loading.value = false
  }
}

const addToCart = async (product) => {
  try {
    await cartStore.addItem(product.id, 1)
  } catch (error) {
    console.error('Failed to add item:', error)
  }
}

const removeFromCart = async (productId) => {
  try {
    await cartStore.removeItem(productId)
  } catch (error) {
    console.error('Failed to remove item:', error)
  }
}



const previousImage = () => {
  if (!product.value.images || product.value.images.length === 0) return
  const currentIndex = product.value.images.indexOf(selectedImage.value)
  if (currentIndex === -1) {
    selectedImage.value = product.value.images[0]
  } else {
    selectedImage.value = product.value.images[(currentIndex - 1 + product.value.images.length) % product.value.images.length]
  }
}

const nextImage = () => {
  if (!product.value.images || product.value.images.length === 0) return
  const currentIndex = product.value.images.indexOf(selectedImage.value)
  if (currentIndex === -1) {
    selectedImage.value = product.value.images[0]
  } else {
    selectedImage.value = product.value.images[(currentIndex + 1) % product.value.images.length]
  }
}

// Lifecycle
onMounted(() => {
  loadProduct()
  cartStore.fetchCart()
  wishlistStore.fetchItems()
  compareStore.fetchItems()
})

// Watch for route changes
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      selectedImage.value = null
      await loadProduct()
      await productStore.fetchRelatedProducts(newId)
    }
  },
  { immediate: true }
)

// Clean up
onUnmounted(() => {
  // Clean up any modal or state if needed
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(251, 191, 36, 0.5) rgba(255, 255, 255, 0.1);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(251, 191, 36, 0.5);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(251, 191, 36, 0.7);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.quantity-controls {
  @apply flex items-center gap-2 rounded-lg px-2 py-1 relative;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(4px);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
  transition: all 500ms ease-in-out;
}

.info-card:hover .quantity-controls {
  box-shadow: 
    0 0 20px 0 rgba(245, 158, 11, 0.1),
    inset 0 0 0 1px rgba(245, 158, 11, 0.2);
}

.quantity-controls button {
  @apply w-8 h-8 rounded-lg bg-[rgba(255,255,255,0.02)]
         flex items-center justify-center 
         transition-all duration-500 ease-in-out
         relative overflow-hidden;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
}

.info-card:hover .quantity-controls button {
  box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.2);
}

.info-card:hover .quantity-controls button:hover {
  @apply bg-gradient-to-r from-amber-500/20 to-amber-600/20;
  box-shadow: 
    0 0 15px 0 rgba(245, 158, 11, 0.2),
    inset 0 0 0 1px rgba(245, 158, 11, 0.3);
}

/* Disabled state styles */
button:disabled {
  @apply opacity-50 cursor-not-allowed;
  background: rgba(255, 255, 255, 0.02) !important;
  box-shadow: none !important;
}

.info-card {
  @apply bg-[rgba(23,23,23,0.7)] backdrop-blur-[10px] 
         border border-white/10 rounded-xl p-6 
         transition-all duration-500 ease-in-out;
  
  /* Add glow effect */
  box-shadow: 0 0 20px 0 rgba(0, 0, 0, 0.5),
              inset 0 0 0 1px rgba(255, 255, 255, 0.1);

  /* Hover effects */
  &:hover {
    @apply border-amber-500/30;
    box-shadow: 
      0 8px 32px rgba(0, 0, 0, 0.1),
      0 4px 8px rgba(245, 158, 11, 0.2);
    
    /* Keep the subtle gradient on hover */
    background: linear-gradient(
      to bottom right,
      rgba(23, 23, 23, 0.8),
      rgba(23, 23, 23, 0.7)
    );
  }
}

.card-header {
  @apply flex items-center justify-between p-4 border-b border-white/10 bg-[rgba(255,255,255,0.02)];
}

.card-content {
  @apply p-4 max-h-[300px] overflow-y-auto custom-scrollbar;
}

.tag {
  @apply px-3 py-1 rounded-full text-sm font-medium transition-all duration-300 
         hover:scale-105 cursor-default;
}

.info-table {
  @apply w-full border-collapse;
}

.info-table th {
  @apply text-left p-2 text-gray-400 font-medium bg-[rgba(255,255,255,0.02)];
}

.info-table td {
  @apply p-2 border-t border-white/5;
}

.info-table tr:hover {
  @apply bg-[rgba(255,255,255,0.02)];
}
</style>
