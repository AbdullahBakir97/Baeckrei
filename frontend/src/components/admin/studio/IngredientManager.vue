<template>
  <div class="st-page">
    <p class="st-intro">{{ $t('admin.ingredients.intro') }}</p>
    <p v-if="error" class="st-alert" role="alert">{{ error }}</p>

    <div class="ing-grid">
      <!-- Ingredients -->
      <section class="st-card !p-0 overflow-hidden">
        <div class="st-bar p-5 pb-4">
          <h2 class="st-card-title !mb-0">{{ $t('admin.ingredients.ingredients') }} <small>{{ $t('admin.ingredients.ingredientsHint') }}</small></h2>
          <div class="flex gap-2">
            <input v-model="search" type="search" class="st-input !w-48" :placeholder="$t('admin.ingredients.search')" :aria-label="$t('admin.ingredients.search')" />
            <button type="button" class="st-btn" @click="editIngredient()"><font-awesome-icon icon="plus" /> {{ $t('admin.ingredients.addIngredient') }}</button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="st-table">
            <thead><tr><th>{{ $t('admin.ingredients.name') }}</th><th>{{ $t('admin.ingredients.allergens') }}</th><th class="is-right">{{ $t('admin.ingredients.products') }}</th><th></th></tr></thead>
            <tbody>
              <tr v-if="!shownIngredients.length"><td colspan="4" class="st-empty">{{ $t('admin.ingredients.noIngredients') }}</td></tr>
              <tr v-for="i in shownIngredients" :key="i.id">
                <td><span class="font-medium text-cream">{{ i.name }}</span>
                  <span v-if="!i.is_active" class="st-chip ms-2">{{ $t('admin.ingredients.inactive') }}</span>
                  <span v-if="i.description" class="block text-xs text-cream-faint">{{ i.description }}</span></td>
                <td><span v-if="!i.allergen_names.length" class="text-cream-faint">–</span>
                  <span v-for="name in i.allergen_names" :key="name" class="st-chip is-amber me-1 mb-1">{{ name }}</span></td>
                <td class="is-right tabular-nums">{{ i.product_count }}</td>
                <td class="is-right whitespace-nowrap">
                  <button type="button" class="st-link text-sm me-3" @click="editIngredient(i)">{{ $t('admin.common.edit') }}</button>
                  <button type="button" class="text-sm text-red-300 disabled:opacity-40" :disabled="i.product_count > 0"
                          :title="i.product_count ? $t('admin.ingredients.inUse') : ''" @click="removeIngredient(i)">{{ $t('admin.common.delete') }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Allergens -->
      <section class="st-card st-grid content-start">
        <h2 class="st-card-title !mb-0">{{ $t('admin.ingredients.allergens') }} <small>{{ $t('admin.ingredients.allergensHint') }}</small></h2>
        <form class="flex gap-2" @submit.prevent="addAllergen">
          <input v-model.trim="newAllergen" class="st-input" required maxlength="100" :placeholder="$t('admin.ingredients.newAllergen')" :aria-label="$t('admin.ingredients.newAllergen')" />
          <button type="submit" class="st-btn" :aria-label="$t('admin.ingredients.addAllergen')"><font-awesome-icon icon="plus" /></button>
        </form>
        <button v-if="missingEu.length" type="button" class="st-btn st-btn-ghost st-btn-sm justify-self-start max-w-full !whitespace-normal text-start" :disabled="busy" @click="addEu">
          {{ $t('admin.ingredients.addEu', { n: missingEu.length }) }}
        </button>
        <ul class="allergen-list">
          <li v-for="a in allergens" :key="a.id">
            <template v-if="renaming === a.id">
              <input v-model.trim="renameValue" class="st-input !py-1" :aria-label="$t('admin.ingredients.name')" @keydown.enter.prevent="rename(a)" @keydown.esc="renaming = null" />
              <button type="button" class="st-link text-sm" @click="rename(a)">{{ $t('admin.common.save') }}</button>
            </template>
            <template v-else>
              <span class="flex-1">{{ a.name }} <small class="text-cream-faint">· {{ $t('admin.ingredients.usedIn', { n: a.ingredient_count }) }}</small></span>
              <button type="button" class="icon-btn" :aria-label="$t('admin.common.edit')" @click="renaming = a.id; renameValue = a.name"><font-awesome-icon icon="pen" /></button>
              <button type="button" class="icon-btn" :disabled="a.ingredient_count > 0" :aria-label="$t('admin.common.delete')" @click="removeAllergen(a)"><font-awesome-icon icon="trash" /></button>
            </template>
          </li>
        </ul>
      </section>
    </div>

    <!-- Ingredient form -->
    <div v-if="form" class="st-modal" role="dialog" aria-modal="true" @click.self="form = null">
      <form class="st-card st-modal-box st-grid" @submit.prevent="saveIngredient">
        <h2 class="st-card-title !mb-0">{{ form.id ? $t('admin.ingredients.editIngredient') : $t('admin.ingredients.addIngredient') }}</h2>
        <div>
          <label class="st-label" for="ing-name">{{ $t('admin.ingredients.name') }}</label>
          <input id="ing-name" v-model.trim="form.name" class="st-input" required maxlength="100" />
          <p v-if="fieldErrors.name" class="st-error">{{ fieldErrors.name }}</p>
        </div>
        <div>
          <label class="st-label" for="ing-desc">{{ $t('admin.ingredients.description') }} <small>({{ $t('admin.common.optional') }})</small></label>
          <input id="ing-desc" v-model.trim="form.description" class="st-input" />
        </div>
        <fieldset>
          <legend class="st-label">{{ $t('admin.ingredients.contains') }}</legend>
          <div class="allergen-picks">
            <label v-for="a in allergens" :key="a.id" class="pick" :class="{ 'is-on': form.allergens.includes(a.id) }">
              <input v-model="form.allergens" type="checkbox" :value="a.id" /> {{ a.name }}
            </label>
          </div>
        </fieldset>
        <label class="st-switch"><input v-model="form.is_active" type="checkbox" /><i></i> {{ $t('admin.ingredients.active') }}</label>
        <div class="flex justify-end gap-2">
          <button type="button" class="st-btn st-btn-ghost" @click="form = null">{{ $t('admin.common.cancel') }}</button>
          <button type="submit" class="st-btn" :disabled="busy">{{ $t('admin.common.save') }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from '@/plugins/axios'
import { errorsFrom, listOf } from './api'

// The 14 allergens that must be declared in the EU (LMIV, Annex II).
const EU_ALLERGENS = {
  de: ['Gluten', 'Krebstiere', 'Eier', 'Fisch', 'Erdnüsse', 'Soja', 'Milch', 'Schalenfrüchte', 'Sellerie', 'Senf', 'Sesam', 'Sulfite', 'Lupinen', 'Weichtiere'],
  en: ['Gluten', 'Crustaceans', 'Eggs', 'Fish', 'Peanuts', 'Soy', 'Milk', 'Tree nuts', 'Celery', 'Mustard', 'Sesame', 'Sulphites', 'Lupin', 'Molluscs']
}

const { t, locale } = useI18n()
const ingredients = ref([])
const allergens = ref([])
const search = ref('')
const newAllergen = ref('')
const renaming = ref(null)
const renameValue = ref('')
const form = ref(null)
const fieldErrors = reactive({})
const busy = ref(false)
const error = ref('')

const shownIngredients = computed(() => ingredients.value.filter(i => !search.value || i.name.toLowerCase().includes(search.value.toLowerCase())))
const missingEu = computed(() => {
  const have = new Set(allergens.value.map(a => a.name.toLowerCase()))
  return (EU_ALLERGENS[locale.value] || EU_ALLERGENS.de).filter(name => !have.has(name.toLowerCase()))
})

async function load() {
  try {
    const [i, a] = await Promise.all([axios.get('/api/studio/ingredients/'), axios.get('/api/studio/allergens/')])
    ingredients.value = listOf(i.data)
    allergens.value = listOf(a.data)
  } catch {
    error.value = t('admin.common.loadError')
  }
}
onMounted(load)

const fail = (err, fallback) => { const e = errorsFrom(err); error.value = e.message || Object.values(e.fields)[0] || fallback }

async function addAllergen() {
  try {
    const { data } = await axios.post('/api/studio/allergens/', { name: newAllergen.value })
    allergens.value = [...allergens.value, data].sort((x, y) => x.name.localeCompare(y.name))
    newAllergen.value = ''
    error.value = ''
  } catch (err) { fail(err, t('admin.common.saveError')) }
}

async function addEu() {
  busy.value = true
  try {
    for (const name of missingEu.value) await axios.post('/api/studio/allergens/', { name })
    await load()
  } catch (err) { fail(err, t('admin.common.saveError')) } finally { busy.value = false }
}

async function rename(a) {
  try {
    const { data } = await axios.patch(`/api/studio/allergens/${a.id}/`, { name: renameValue.value })
    Object.assign(a, data)
    renaming.value = null
    await load()
  } catch (err) { fail(err, t('admin.common.saveError')) }
}

async function removeAllergen(a) {
  try {
    await axios.delete(`/api/studio/allergens/${a.id}/`)
    allergens.value = allergens.value.filter(x => x.id !== a.id)
  } catch (err) { fail(err, t('admin.common.deleteError')) }
}

function editIngredient(i) {
  Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
  form.value = i
    ? { id: i.id, name: i.name, description: i.description, allergens: [...i.allergens], is_active: i.is_active }
    : { id: null, name: '', description: '', allergens: [], is_active: true }
}

async function saveIngredient() {
  busy.value = true
  Object.keys(fieldErrors).forEach(k => delete fieldErrors[k])
  const { id, ...payload } = form.value
  try {
    if (id) await axios.patch(`/api/studio/ingredients/${id}/`, payload)
    else await axios.post('/api/studio/ingredients/', payload)
    form.value = null
    await load()
  } catch (err) {
    Object.assign(fieldErrors, errorsFrom(err).fields)
    if (!Object.keys(fieldErrors).length) fail(err, t('admin.common.saveError'))
  } finally { busy.value = false }
}

async function removeIngredient(i) {
  try {
    await axios.delete(`/api/studio/ingredients/${i.id}/`)
    ingredients.value = ingredients.value.filter(x => x.id !== i.id)
    await load()
  } catch (err) { fail(err, t('admin.common.deleteError')) }
}
</script>

<style scoped>
.ing-grid { display: grid; gap: 1.5rem; align-items: start; }
@media (min-width: 1100px) { .ing-grid { grid-template-columns: minmax(0, 1fr) 21rem; } }
.allergen-list { display: grid; gap: 0.15rem; }
.allergen-list li { display: flex; align-items: center; gap: 0.5rem; padding: 0.45rem 0.6rem; border-radius: 0.75rem; font-size: 0.9rem; color: #f4ece1; }
.allergen-list li:hover { background: rgba(244, 236, 225, 0.04); }
.icon-btn { padding: 0.3rem 0.45rem; border-radius: 0.5rem; font-size: 0.8rem; color: #85766a; }
.icon-btn:hover:not(:disabled) { color: #f4ece1; background: rgba(244, 236, 225, 0.07); }
.icon-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.allergen-picks { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.pick { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.82rem; color: #b9ab98; background: rgba(244, 236, 225, 0.05); cursor: pointer; }
.pick input { accent-color: #e6a15a; }
.pick.is-on { color: #0e0c0a; background: #f2c48d; }
</style>
