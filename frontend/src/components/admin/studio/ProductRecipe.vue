<template>
  <section class="bg-[#1e1914] rounded-xl border border-cream/[0.07] overflow-hidden">
    <div class="p-6 border-b border-cream/[0.07] flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-lg font-bold text-white">{{ $t('admin.recipe.title') }}</h2>
        <p class="text-xs text-cream-faint">{{ $t('admin.recipe.hint') }}</p>
      </div>
      <router-link to="/admin/ingredients" class="st-link text-sm">{{ $t('admin.recipe.manage') }}</router-link>
    </div>
    <form class="p-6 st-grid" @submit.prevent="save">
      <p v-if="error" class="st-alert" role="alert">{{ error }}</p>
      <fieldset>
        <legend class="st-label">{{ $t('admin.recipe.ingredients') }}</legend>
        <input v-model="search" type="search" class="st-input mb-2" :placeholder="$t('admin.ingredients.search')" :aria-label="$t('admin.ingredients.search')" />
        <div class="picks">
          <label v-for="i in shown" :key="i.id" class="pick" :class="{ 'is-on': chosen.includes(i.id) }">
            <input v-model="chosen" type="checkbox" :value="i.id" /> {{ i.name }}
          </label>
          <p v-if="!all.length" class="text-sm text-cream-faint">{{ $t('admin.recipe.noIngredients') }}</p>
        </div>
      </fieldset>
      <p class="text-sm text-cream/80">
        <strong>{{ $t('admin.recipe.allergens') }}:</strong>
        <span v-if="!allergens.length" class="text-cream-faint"> {{ $t('admin.recipe.none') }}</span>
        <span v-for="a in allergens" :key="a" class="st-chip is-amber ml-1">{{ a }}</span>
      </p>
      <fieldset>
        <legend class="st-label">{{ $t('admin.recipe.nutrition') }}</legend>
        <label class="st-switch mb-3"><input v-model="hasNutrition" type="checkbox" /><i></i> {{ $t('admin.recipe.showNutrition') }}</label>
        <div v-if="hasNutrition" class="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div v-for="key in fields" :key="key">
            <label class="st-label" :for="`n-${key}`">{{ $t(`admin.nutrition.${key}`) }} <small>{{ key === 'calories' ? 'kcal' : 'g' }}</small></label>
            <input :id="`n-${key}`" v-model="nutrition[key]" type="number" min="0" step="0.1" class="st-input" required />
          </div>
        </div>
      </fieldset>
      <div class="flex items-center gap-3">
        <button type="submit" class="st-btn" :disabled="saving">{{ saving ? $t('admin.common.saving') : $t('admin.recipe.save') }}</button>
        <span v-if="done" class="text-sm text-emerald-300" role="status">{{ $t('admin.recipe.saved') }}</span>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { errorsFrom, listOf } from './api'

const props = defineProps({ productId: { type: String, required: true } })
const emit = defineEmits(['saved'])
const { t } = useI18n()
const fields = ['calories', 'proteins', 'carbohydrates', 'fats', 'fiber']
const all = ref([])
const chosen = ref([])
const allergens = ref([])
const search = ref('')
const hasNutrition = ref(false)
const nutrition = reactive({ calories: '', proteins: '', carbohydrates: '', fats: '', fiber: '' })
const saving = ref(false)
const done = ref(false)
const error = ref('')

const shown = computed(() => all.value.filter(i => (i.is_active || chosen.value.includes(i.id)) &&
  (!search.value || i.name.toLowerCase().includes(search.value.toLowerCase()))))

function fill(data) {
  chosen.value = data.ingredients
  allergens.value = data.allergens
  hasNutrition.value = Boolean(data.nutrition)
  if (data.nutrition) for (const key of fields) nutrition[key] = Number(data.nutrition[key])
}

onMounted(async () => {
  try {
    const [ingredients, recipe] = await Promise.all([
      axios.get('/api/studio/ingredients/'), axios.get(`/api/studio/products/${props.productId}/recipe/`)
    ])
    all.value = listOf(ingredients.data)
    fill(recipe.data)
  } catch {
    error.value = t('admin.common.loadError')
  }
})

async function save() {
  saving.value = true
  done.value = false
  error.value = ''
  try {
    const { data } = await axios.put(`/api/studio/products/${props.productId}/recipe/`, {
      ingredients: chosen.value,
      nutrition: hasNutrition.value ? { ...nutrition } : null
    })
    fill(data)
    done.value = true
    emit('saved')
  } catch (err) {
    const e = errorsFrom(err)
    error.value = e.message || Object.values(e.fields)[0] || t('admin.common.saveError')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.picks { display: flex; flex-wrap: wrap; gap: 0.4rem; max-height: 12rem; overflow-y: auto; }
.pick { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.82rem; color: #b9ab98; background: rgba(244, 236, 225, 0.05); cursor: pointer; }
.pick input { accent-color: #e6a15a; }
.pick.is-on { color: #0e0c0a; background: #f2c48d; }
</style>
