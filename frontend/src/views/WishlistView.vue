<template>
  <div class="section pb-10">
    <PageHeader :eyebrow="$t('wishlist.eyebrow')" :title="$t('wishlist.title')" :subtitle="$t('wishlist.subtitle')" />

    <div v-if="loading" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4" aria-busy="true">
      <div v-for="n in 4" :key="n" class="skeleton aspect-[3/4] rounded-3xl"></div>
    </div>

    <div v-else-if="!products.length" class="empty lux-card">
      <span class="empty-heart" aria-hidden="true"><font-awesome-icon icon="heart" /></span>
      <h2 class="display-title text-5xl">{{ $t('wishlist.emptyTitle') }}</h2>
      <p class="mt-3 text-cream-muted">{{ $t('wishlist.emptyText') }}</p>
      <router-link to="/products" class="btn-amber mt-8">{{ $t('common.browseProducts') }}</router-link>
    </div>

    <template v-else>
      <div v-reveal.stagger class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="product in products" :key="product.id" class="relative">
          <ProductCard :product="product" />
          <button type="button" class="unsave" :aria-label="$t('wishlist.remove', { name: localized(product, 'name') })"
                  @click="remove(product.id)">
            <font-awesome-icon icon="xmark" />
          </button>
        </div>
      </div>
      <p v-if="missingIds.length" class="mt-6 text-sm text-cream-muted">
        {{ $t('wishlist.missing', missingIds.length) }}
      </p>
    </template>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import ProductCard from '@/components/products/ProductCard.vue'
import { useWishlistStore } from '@/stores/wishlistStore'
import { useFreshProducts } from '@/composables/useFreshProducts'
import { localized } from '@/i18n/catalog'

const wishlistStore = useWishlistStore()
const { products, missingIds, loading, load } = useFreshProducts()

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

<style scoped>
.unsave {
  position: absolute;
  top: 1.35rem;
  right: 1.35rem;
  z-index: 2;
  display: grid;
  place-items: center;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 9999px;
  color: #f4ece1;
  background: rgba(14, 12, 10, 0.6);
  border: 1px solid rgba(244, 236, 225, 0.14);
  backdrop-filter: blur(8px);
  transition: background 0.25s, color 0.25s;
}

.unsave:hover {
  color: #0e0c0a;
  background: #f08f79;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem 1.5rem 3.5rem;
  text-align: center;
}

.empty-heart {
  display: grid;
  place-items: center;
  width: 5rem;
  height: 5rem;
  margin-bottom: 1.5rem;
  border-radius: 9999px;
  font-size: 1.8rem;
  color: #e6a15a;
  background: rgba(230, 161, 90, 0.12);
  animation: beat 2.4s ease-in-out infinite;
}

@keyframes beat {
  0%, 60%, 100% { transform: scale(1); }
  30% { transform: scale(1.12); }
}

@media (prefers-reduced-motion: reduce) {
  .empty-heart {
    animation: none;
  }
}

.skeleton {
  background: linear-gradient(100deg, rgba(244, 236, 225, 0.04) 30%, rgba(244, 236, 225, 0.09) 50%, rgba(244, 236, 225, 0.04) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}
</style>
