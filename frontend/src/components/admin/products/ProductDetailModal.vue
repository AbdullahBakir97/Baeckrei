<template>
  <TransitionRoot appear :show="true" as="template">
    <Dialog as="div" class="relative z-10" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-3xl transform overflow-hidden rounded-2xl bg-oven-800 p-6 text-start align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-cream mb-4">
                {{ $t('admin.productDetail.title') }}
              </DialogTitle>

              <div v-if="loading" class="flex justify-center items-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>

              <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Product Image -->
                <div class="aspect-w-4 aspect-h-3">
                  <img
                    :src="product.image"
                    :alt="product.name"
                    class="object-cover rounded-lg shadow-lg"
                  />
                </div>

                <!-- Product Information -->
                <div class="space-y-4">
                  <div>
                    <h4 class="text-sm font-medium text-cream-muted">{{ $t('admin.productDetail.productName') }}</h4>
                    <p class="mt-1 text-lg font-semibold text-cream">{{ product.name }}</p>
                  </div>

                  <div>
                    <h4 class="text-sm font-medium text-cream-muted">{{ $t('admin.fields.sku') }}</h4>
                    <p class="mt-1 text-cream">{{ product.sku }}</p>
                  </div>

                  <div>
                    <h4 class="text-sm font-medium text-cream-muted">{{ $t('admin.fields.category') }}</h4>
                    <p class="mt-1 text-cream">{{ typeof product.category === 'object' ? categoryName(product.category) : product.category }}</p>
                  </div>

                  <div>
                    <h4 class="text-sm font-medium text-cream-muted">{{ $t('admin.fields.price') }}</h4>
                    <p class="mt-1 text-cream">{{ formatEuro(product.price) }}</p>
                  </div>

                  <div>
                    <h4 class="text-sm font-medium text-cream-muted">{{ $t('admin.fields.stock') }}</h4>
                    <div class="mt-1 flex items-center">
                      <span
                        :class="[
                          product.stock > 10 ? 'bg-emerald-400/10 text-emerald-300' :
                          product.stock > 0 ? 'bg-amber-300/10 text-amber-200' :
                          'bg-red-400/10 text-red-300',
                          'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
                        ]"
                      >
                        {{ $t('admin.inStock', { n: product.stock }) }}
                      </span>
                    </div>
                  </div>

                  <div>
                    <h4 class="text-sm font-medium text-cream-muted">{{ $t('admin.fields.status') }}</h4>
                    <span
                      :class="[ product.status === 'active' ? 'bg-emerald-400/10 text-emerald-300' : 'bg-red-400/10 text-red-300', 'mt-1 px-2 inline-flex text-xs leading-5 font-semibold rounded-full' ]"
                    >
                      {{ $te(`admin.productStatus.${product.status}`) ? $t(`admin.productStatus.${product.status}`) : product.status }}
                    </span>
                  </div>

                  <div v-if="product.description">
                    <h4 class="text-sm font-medium text-cream-muted">{{ $t('admin.fields.description') }}</h4>
                    <p class="mt-1 text-cream">{{ product.description }}</p>
                  </div>
                </div>

                <!-- Additional Information -->
                <div class="col-span-1 md:col-span-2 space-y-4">
                  <!-- Nutrition Information -->
                  <div v-if="nutritionInfo" class="border-t pt-4">
                    <h4 class="text-sm font-medium text-cream-muted mb-2">{{ $t('admin.productDetail.nutrition') }}</h4>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <div v-for="(value, key) in nutritionInfo" :key="key" class="bg-cream/[0.03] p-3 rounded-lg">
                        <div class="text-xs text-cream-muted">{{ $te(`admin.nutrition.${key}`) ? $t(`admin.nutrition.${key}`) : key }}</div>
                        <div class="text-sm font-medium text-cream">{{ value }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- Allergens -->
                  <div v-if="allergens.length" class="border-t pt-4">
                    <h4 class="text-sm font-medium text-cream-muted mb-2">{{ $t('admin.productDetail.allergens') }}</h4>
                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="allergen in allergens"
                        :key="allergen.id"
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-400/10 text-red-300"
                      >
                        {{ allergen.name }}
                      </span>
                    </div>
                  </div>

                  <!-- Similar Products -->
                  <div v-if="similarProducts.length" class="border-t pt-4">
                    <h4 class="text-sm font-medium text-cream-muted mb-2">{{ $t('admin.productDetail.similar') }}</h4>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <div
                        v-for="similar in similarProducts"
                        :key="similar.id"
                        class="group relative"
                      >
                        <div class="aspect-w-4 aspect-h-3 rounded-lg overflow-hidden">
                          <img
                            :src="similar.image"
                            :alt="similar.name"
                            class="object-cover group-hover:opacity-75"
                          />
                        </div>
                        <p class="mt-2 text-sm font-medium text-cream">{{ similar.name }}</p>
                        <p class="text-sm text-cream-muted">{{ formatEuro(similar.price) }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-6 flex justify-end space-x-3 rtl:space-x-reverse">
                <button
                  @click="$emit('close')"
                  class="admin-panel inline-flex justify-center border border-cream/15 px-4 py-2 text-sm font-medium text-cream/80 hover:bg-cream/[0.03] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                >
                  {{ $t('common.close') }}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { useProductStore } from '@/stores/productStore'
import { formatEuro } from '@/utils/money'
import { categoryName } from '@/i18n/catalog'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])
const productStore = useProductStore()
const loading = ref(true)
const nutritionInfo = ref(null)
const allergens = ref([])
const similarProducts = ref([])

const loadProductDetails = async () => {
  try {
    const [nutritionData, allergensData, similarData] = await Promise.all([
      productStore.fetchProductNutrition(props.product.id),
      productStore.fetchProductAllergens(props.product.id),
      productStore.fetchSimilarProducts(props.product.id)
    ])

    nutritionInfo.value = nutritionData
    allergens.value = allergensData
    similarProducts.value = similarData
  } catch (error) {
    console.error('Error loading product details:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadProductDetails)
</script>
