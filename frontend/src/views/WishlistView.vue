<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <PageHeader title="Wishlist" subtitle="Products you saved for later" icon="heart" />

      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white/20"></div>
      </div>

      <div v-else-if="!products.length" class="glass-panel text-center py-12">
        <p class="text-lg text-white font-medium">Your wishlist is empty</p>
        <p class="mt-2 text-gray-400">Tap the heart on a product to save it here.</p>
        <router-link to="/products" class="btn-amber mt-6">Browse products</router-link>
      </div>

      <template v-else>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <article v-for="product in products" :key="product.id" class="glass-panel flex flex-col gap-4">
            <router-link :to="{ name: 'product-detail', params: { id: product.id } }" class="block">
              <img :src="product.image_url || product.image || PLACEHOLDER_IMAGE" :alt="product.name"
                   class="h-48 w-full rounded-xl object-contain bg-white/5" @error="applyImageFallback" />
            </router-link>
            <div class="flex-1">
              <router-link :to="{ name: 'product-detail', params: { id: product.id } }"
                           class="text-lg font-semibold text-white hover:text-amber-300">{{ product.name }}</router-link>
              <p class="text-amber-400 font-bold">{{ Number(product.price).toFixed(2) }} €</p>
              <p v-if="!product.available || product.stock < 1" class="text-sm text-red-300">Currently unavailable</p>
            </div>
            <div class="flex gap-2">
              <button type="button" class="btn-amber flex-1 py-2" :disabled="!product.available || product.stock < 1 || busyId === product.id"
                      @click="addToCart(product)">
                <font-awesome-icon icon="cart-plus" /> Add to cart
              </button>
              <button type="button" class="btn-ghost" :aria-label="`Remove ${product.name} from wishlist`" @click="remove(product.id)">
                <font-awesome-icon icon="trash" />
              </button>
            </div>
          </article>
        </div>
        <p v-if="missingIds.length" class="mt-6 text-sm text-gray-400">
          {{ missingIds.length }} saved product(s) are no longer in the shop and were removed.
        </p>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useWishlistStore } from '@/stores/wishlistStore'
import { useCartStore } from '@/stores/cartStore'
import { useToast } from '@/composables/useToast'
import { useFreshProducts } from '@/composables/useFreshProducts'
import { PLACEHOLDER_IMAGE, applyImageFallback } from '@/utils/imageFallback'

const wishlistStore = useWishlistStore()
const cartStore = useCartStore()
const { showToast } = useToast()
const { products, missingIds, loading, load } = useFreshProducts()
const busyId = ref(null)

async function addToCart(product) {
  busyId.value = product.id
  try {
    await cartStore.addItem(product.id, 1)
    showToast(`${product.name} added to your cart`)
  } catch (err) {
    showToast(cartStore.error || 'Could not add to cart', 'error')
  } finally {
    busyId.value = null
  }
}

function remove(id) {
  wishlistStore.removeItem(id)
  products.value = products.value.filter(p => p.id !== id)
}

onMounted(async () => {
  wishlistStore.fetchItems()
  await load(wishlistStore.items)
  missingIds.value.forEach(id => wishlistStore.removeItem(id))
})
</script>
