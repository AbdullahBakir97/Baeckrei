<template>
  <div class="fixed inset-0 z-50 overflow-y-auto bg-oven-950/70" role="dialog" aria-modal="true" aria-labelledby="product-form-title" @click.self="$emit('close')">
    <div class="admin-panel mx-auto my-8 w-full max-w-2xl p-6 text-cream">
      <h2 id="product-form-title" class="text-lg font-semibold text-cream">{{ product ? $t('admin.productForm.editTitle') : $t('admin.productForm.newTitle') }}</h2>

      <form class="mt-4 grid sm:grid-cols-2 gap-4" @submit.prevent="handleSubmit">
        <div class="sm:col-span-2">
          <label for="pf-name" class="admin-label">{{ $t('admin.fields.name') }}</label>
          <input id="pf-name" v-model.trim="form.name" class="admin-input" required maxlength="200" aria-describedby="pf-german-hint" />
          <p v-if="errors.name" class="admin-error">{{ errors.name }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-description" class="admin-label">{{ $t('admin.fields.description') }}</label>
          <textarea id="pf-description" v-model.trim="form.description" rows="3" class="admin-input" required aria-describedby="pf-german-hint"></textarea>
          <p id="pf-german-hint" class="mt-1 text-xs text-cream-muted">{{ $t('admin.fields.germanHint') }}</p>
          <p v-if="errors.description" class="admin-error">{{ errors.description }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-name-en" class="admin-label">{{ $t('admin.fields.nameEn') }} <span class="font-normal text-cream-muted">({{ $t('common.optional') }})</span></label>
          <input id="pf-name-en" v-model.trim="form.name_en" lang="en" class="admin-input" maxlength="200" aria-describedby="pf-english-hint" />
          <p v-if="errors.name_en" class="admin-error">{{ errors.name_en }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-description-en" class="admin-label">{{ $t('admin.fields.descriptionEn') }} <span class="font-normal text-cream-muted">({{ $t('common.optional') }})</span></label>
          <textarea id="pf-description-en" v-model.trim="form.description_en" lang="en" rows="3" class="admin-input" aria-describedby="pf-english-hint"></textarea>
          <p id="pf-english-hint" class="mt-1 text-xs text-cream-muted">{{ $t('admin.fields.englishHint') }}</p>
          <p v-if="errors.description_en" class="admin-error">{{ errors.description_en }}</p>
        </div>

        <div>
          <label for="pf-category" class="admin-label">{{ $t('admin.fields.category') }}</label>
          <select id="pf-category" v-model="form.category" class="admin-input" required>
            <option disabled value="">{{ $t('admin.productForm.chooseCategory') }}</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">{{ categoryName(category) }}</option>
          </select>
          <p v-if="errors.category" class="admin-error">{{ errors.category }}</p>
        </div>

        <div>
          <label for="pf-status" class="admin-label">{{ $t('admin.fields.status') }}</label>
          <select id="pf-status" v-model="form.status" class="admin-input">
            <option value="draft">{{ $t('admin.productForm.draftOption') }}</option>
            <option value="active">{{ $t('admin.productStatus.active') }}</option>
            <option value="discontinued">{{ $t('admin.productStatus.discontinued') }}</option>
          </select>
        </div>

        <div>
          <label for="pf-price" class="admin-label">{{ $t('admin.productForm.price') }}</label>
          <input id="pf-price" v-model="form.price" type="number" min="0.01" step="0.01" class="admin-input" required />
          <p v-if="errors.price" class="admin-error">{{ errors.price }}</p>
        </div>

        <div>
          <label for="pf-stock" class="admin-label">{{ $t('admin.fields.stock') }}</label>
          <input id="pf-stock" v-model.number="form.stock" type="number" min="0" step="1" class="admin-input" required />
          <p v-if="errors.stock" class="admin-error">{{ errors.stock }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-image" class="admin-label">{{ $t('admin.productForm.photo') }} {{ product ? $t('admin.productForm.keepPhoto') : '' }}</label>
          <div class="mt-1 flex items-center gap-4">
            <img v-if="previewUrl" :src="previewUrl" alt="" class="h-16 w-16 rounded object-cover bg-cream/[0.05]" />
            <input id="pf-image" type="file" accept="image/jpeg,image/png,image/webp" class="text-sm text-cream/80" @change="onImage" />
          </div>
          <p class="mt-1 text-xs text-cream-muted">{{ $t('admin.productForm.photoHint') }}</p>
          <p v-if="errors.image" class="admin-error">{{ errors.image }}</p>
        </div>

        <div class="sm:col-span-2">
          <label for="pf-model" class="admin-label">{{ $t('admin.productForm.model') }} <span class="font-normal text-cream-muted">({{ $t('common.optional') }})</span></label>
          <p v-if="currentModel && !form.removeModel && !form.modelFile" class="mt-1 flex items-center gap-3 text-sm text-cream/80">
            <font-awesome-icon icon="cube" class="text-crust" />
            <a :href="currentModel" target="_blank" rel="noopener" class="underline truncate">{{ currentModel.split('/').pop() }}</a>
            <button type="button" class="text-red-300 hover:underline" @click="form.removeModel = true">{{ $t('common.remove') }}</button>
          </p>
          <p v-else-if="form.removeModel" class="mt-1 text-sm text-cream/80">
            {{ $t('admin.productForm.modelRemoved') }} <button type="button" class="text-crust hover:underline" @click="form.removeModel = false">{{ $t('admin.productForm.undo') }}</button>
          </p>
          <input id="pf-model" type="file" accept=".glb,model/gltf-binary" class="mt-1 text-sm text-cream/80" @change="onModel" />
          <p class="mt-1 text-xs text-cream-muted">{{ $t('admin.productForm.modelHint') }}</p>
          <p v-if="errors.model_3d" class="admin-error">{{ errors.model_3d }}</p>
        </div>

        <fieldset class="sm:col-span-2 flex flex-wrap gap-x-6 gap-y-2">
          <legend class="admin-label">{{ $t('admin.productForm.details') }}</legend>
          <label v-for="flag in flags" :key="flag.key" class="inline-flex items-center gap-2 text-sm text-cream/80">
            <input v-model="form[flag.key]" type="checkbox" class="rounded border-cream/15 text-crust" />
            {{ flag.label }}
          </label>
        </fieldset>

        <p v-if="errors.general" class="sm:col-span-2 rounded-md bg-red-400/10 p-3 text-sm text-red-300" role="alert">{{ errors.general }}</p>

        <div class="sm:col-span-2 flex justify-end gap-3">
          <button type="button" class="px-4 py-2 text-sm font-medium rounded-full text-cream/80 bg-cream/[0.05] hover:bg-cream/10" @click="$emit('close')">{{ $t('common.cancel') }}</button>
          <button type="submit" class="px-4 py-2 text-sm font-medium rounded-full text-oven-950 bg-crust hover:bg-crust-light" :disabled="saving">
            {{ saving ? $t('common.saving') : (product ? $t('admin.productForm.saveChanges') : $t('admin.productForm.create')) }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useProductStore } from '@/stores/productStore'
import { categoryName } from '@/i18n/catalog'

const props = defineProps({
  product: { type: Object, default: null },
  // Set by the parent while saving; field errors come back from the API.
  saving: { type: Boolean, default: false },
  serverErrors: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['close', 'save'])
const productStore = useProductStore()
const { t } = useI18n()
const categories = ref([])
const previewUrl = ref('')
const currentModel = ref('')
const errors = reactive({})

const flags = [
  { key: 'available', label: t('admin.productForm.available') },
  { key: 'is_seasonal', label: t('common.seasonal') },
  { key: 'is_vegan', label: t('common.vegan') },
  { key: 'is_vegetarian', label: t('common.vegetarian') },
  { key: 'is_gluten_free', label: t('common.glutenFree') }
]

const blank = () => ({
  name: '', name_en: '', description: '', description_en: '', category: '', price: '', stock: 0, status: 'active',
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
      name_en: product.name_en || '',
      description: product.description,
      description_en: product.description_en || '',
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
    if (['name', 'name_en', 'description', 'description_en', 'category', 'price', 'stock', 'image', 'model_3d'].includes(key)) errors[key] = message
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
    errors.image = t('admin.productForm.photoRequired')
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
  @apply block text-sm font-medium text-cream/80;
}

.admin-input {
  @apply mt-1 block w-full rounded-md border border-cream/15 px-3 py-2 shadow-sm sm:text-sm text-cream bg-oven-800 focus:border-crust focus:ring-crust;
}

.admin-error {
  @apply mt-1 text-sm text-red-300;
}
</style>
