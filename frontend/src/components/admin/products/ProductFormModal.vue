<template>
  <div class="fixed inset-0 z-50 overflow-y-auto bg-gray-900/50" role="dialog" aria-modal="true" aria-labelledby="product-form-title" @click.self="$emit('close')">
    <div class="mx-auto my-8 w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl text-gray-800">
      <h2 id="product-form-title" class="text-lg font-semibold text-gray-900">{{ product ? 'Edit product' : 'New product' }}</h2>

      <form class="mt-4 grid sm:grid-cols-2 gap-4" @submit.prevent="handleSubmit">
        <div class="sm:col-span-2">
          <label for="pf-name" class="admin-label">Name</label>
          <input id="pf-name" v-model.trim="form.name" class="admin-input" required maxlength="200" />
          <p v-if="errors.name" class="admin-error">{{ errors.name }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-description" class="admin-label">Description</label>
          <textarea id="pf-description" v-model.trim="form.description" rows="3" class="admin-input" required></textarea>
          <p v-if="errors.description" class="admin-error">{{ errors.description }}</p>
        </div>

        <div>
          <label for="pf-category" class="admin-label">Category</label>
          <select id="pf-category" v-model="form.category" class="admin-input" required>
            <option disabled value="">Choose a category</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option>
          </select>
          <p v-if="errors.category" class="admin-error">{{ errors.category }}</p>
        </div>

        <div>
          <label for="pf-status" class="admin-label">Status</label>
          <select id="pf-status" v-model="form.status" class="admin-input">
            <option value="draft">Draft (not in the shop)</option>
            <option value="active">Active</option>
            <option value="discontinued">Discontinued</option>
          </select>
        </div>

        <div>
          <label for="pf-price" class="admin-label">Price (€, incl. VAT)</label>
          <input id="pf-price" v-model="form.price" type="number" min="0.01" step="0.01" class="admin-input" required />
          <p v-if="errors.price" class="admin-error">{{ errors.price }}</p>
        </div>

        <div>
          <label for="pf-stock" class="admin-label">Stock</label>
          <input id="pf-stock" v-model.number="form.stock" type="number" min="0" step="1" class="admin-input" required />
          <p v-if="errors.stock" class="admin-error">{{ errors.stock }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-image" class="admin-label">Photo {{ product ? '(leave empty to keep the current one)' : '' }}</label>
          <div class="mt-1 flex items-center gap-4">
            <img v-if="previewUrl" :src="previewUrl" alt="" class="h-16 w-16 rounded object-cover bg-gray-100" />
            <input id="pf-image" type="file" accept="image/jpeg,image/png,image/webp" class="text-sm text-gray-700" @change="onImage" />
          </div>
          <p class="mt-1 text-xs text-gray-500">JPG, PNG or WebP, up to 5 MB.</p>
          <p v-if="errors.image" class="admin-error">{{ errors.image }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-model" class="admin-label">3D model <span class="font-normal text-gray-500">(optional)</span></label>
          <p v-if="currentModel && !form.removeModel && !form.modelFile" class="mt-1 flex items-center gap-3 text-sm text-gray-700">
            <font-awesome-icon icon="cube" class="text-indigo-600" />
            <a :href="currentModel" target="_blank" rel="noopener" class="underline truncate">{{ currentModel.split('/').pop() }}</a>
            <button type="button" class="text-red-600 hover:underline" @click="form.removeModel = true">Remove</button>
          </p>
          <p v-else-if="form.removeModel" class="mt-1 text-sm text-gray-700">
            The 3D model will be removed. <button type="button" class="text-indigo-600 hover:underline" @click="form.removeModel = false">Undo</button>
          </p>
          <input id="pf-model" type="file" accept=".glb,model/gltf-binary" class="mt-1 text-sm text-gray-700" @change="onModel" />
          <p class="mt-1 text-xs text-gray-500">A .glb file up to 20 MB. Without one, the storefront builds a 3D view from the photo (works best with a transparent PNG).</p>
          <p v-if="errors.model_3d" class="admin-error">{{ errors.model_3d }}</p>
        </div>

        <fieldset class="sm:col-span-2 flex flex-wrap gap-x-6 gap-y-2">
          <legend class="admin-label">Details</legend>
          <label v-for="flag in flags" :key="flag.key" class="inline-flex items-center gap-2 text-sm text-gray-700">
            <input v-model="form[flag.key]" type="checkbox" class="rounded border-gray-300 text-indigo-600" />
            {{ flag.label }}
          </label>
        </fieldset>

        <p v-if="errors.general" class="sm:col-span-2 rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{{ errors.general }}</p>

        <div class="sm:col-span-2 flex justify-end gap-3">
          <button type="button" class="px-4 py-2 text-sm font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200" @click="$emit('close')">Cancel</button>
          <button type="submit" class="px-4 py-2 text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700" :disabled="saving">
            {{ saving ? 'Saving…' : (product ? 'Save changes' : 'Create product') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useProductStore } from '@/stores/productStore'

const props = defineProps({
  product: { type: Object, default: null },
  // Set by the parent while saving; field errors come back from the API.
  saving: { type: Boolean, default: false },
  serverErrors: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['close', 'save'])
const productStore = useProductStore()
const categories = ref([])
const previewUrl = ref('')
const currentModel = ref('')
const errors = reactive({})

const flags = [
  { key: 'available', label: 'Available to order' },
  { key: 'is_seasonal', label: 'Seasonal' },
  { key: 'is_vegan', label: 'Vegan' },
  { key: 'is_vegetarian', label: 'Vegetarian' },
  { key: 'is_gluten_free', label: 'Gluten free' }
]

const blank = () => ({
  name: '', description: '', category: '', price: '', stock: 0, status: 'active',
  available: true, is_seasonal: false, is_vegan: false, is_vegetarian: false, is_gluten_free: false,
  imageFile: null,
  modelFile: null,
  removeModel: false
})
const form = reactive(blank())

watch(() => props.product, (product) => {
  Object.assign(form, blank())
  previewUrl.value = ''
  currentModel.value = product?.model_3d || product?.model_3d_url || ''
  if (product) {
    Object.assign(form, {
      name: product.name,
      description: product.description,
      category: typeof product.category === 'object' ? product.category?.id : product.category,
      price: product.price,
      stock: product.stock,
      status: product.status || 'active',
      available: product.available ?? true,
      is_seasonal: !!product.is_seasonal,
      is_vegan: !!product.is_vegan,
      is_vegetarian: !!product.is_vegetarian,
      is_gluten_free: !!product.is_gluten_free
    })
    previewUrl.value = product.image || product.image_url || ''
  }
}, { immediate: true })

watch(() => props.serverErrors, (serverErrors) => {
  Object.keys(errors).forEach(key => delete errors[key])
  for (const [key, value] of Object.entries(serverErrors || {})) {
    const message = [].concat(value)[0]
    if (['name', 'description', 'category', 'price', 'stock', 'image', 'model_3d'].includes(key)) errors[key] = message
    else errors.general = message
  }
})

function onImage(event) {
  const file = event.target.files?.[0]
  form.imageFile = file || null
  if (previewUrl.value.startsWith('blob:')) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = file ? URL.createObjectURL(file) : (props.product?.image || '')
}

function onModel(event) {
  form.modelFile = event.target.files?.[0] || null
  if (form.modelFile) form.removeModel = false
}

function handleSubmit() {
  Object.keys(errors).forEach(key => delete errors[key])
  if (!props.product && !form.imageFile) {
    errors.image = 'Add a photo of the product.'
    return
  }
  emit('save', { ...form, id: props.product?.id })
}

onMounted(async () => {
  categories.value = await productStore.fetchCategories()
})

onBeforeUnmount(() => {
  if (previewUrl.value.startsWith('blob:')) URL.revokeObjectURL(previewUrl.value)
})
</script>

<style scoped>
.admin-label {
  @apply block text-sm font-medium text-gray-700;
}

.admin-input {
  @apply mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm sm:text-sm text-gray-900 bg-white focus:border-indigo-500 focus:ring-indigo-500;
}

.admin-error {
  @apply mt-1 text-sm text-red-600;
}
</style>
