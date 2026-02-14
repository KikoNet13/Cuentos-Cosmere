<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  ApiError,
  getStory,
  patchStoryPage,
  setSlotActive,
  uploadAlternative,
} from '../api'
import CollapsiblePanel from '../components/CollapsiblePanel.vue'
import ImageModal from '../components/ImageModal.vue'
import ToastStack from '../components/ToastStack.vue'
import { useToasts } from '../composables/useToasts'

function normalizePathParam(value) {
  if (Array.isArray(value)) {
    return value.filter(Boolean).join('/')
  }
  return typeof value === 'string' ? value : ''
}

const route = useRoute()
const router = useRouter()
const toasts = useToasts()

const loading = ref(false)
const errorMessage = ref('')
const payload = ref(null)
const editorMode = ref(false)

const busy = reactive({
  save: false,
  uploadSlot: '',
  activate: '',
})

const panels = reactive({
  textOriginal: false,
  prompts: false,
  alternatives: true,
})

const draft = reactive({
  text_current: '',
  main_prompt_current: '',
  secondary_prompt_current: '',
})

const uploadForms = reactive({})

const modal = reactive({
  visible: false,
  title: '',
  imageUrl: '',
  notes: '',
})

const storyPath = computed(() => normalizePathParam(route.params.storyPath))
const page = computed(() => payload.value?.page || null)
const pagination = computed(() => payload.value?.pagination || null)
const breadcrumbs = computed(() => payload.value?.breadcrumbs || [])
const slots = computed(() => page.value?.slots || [])

const mainSlot = computed(() => slots.value.find((slot) => slot.slot_name === 'main') || null)

const definitiveImageUrl = computed(() => {
  if (mainSlot.value?.definitive_image_url) {
    return mainSlot.value.definitive_image_url
  }
  const fallback = slots.value.find((slot) => slot.definitive_image_url)
  return fallback?.definitive_image_url || null
})

const definitiveAltText = computed(() => {
  const storyTitle = payload.value?.story?.title || 'cuento'
  const pageNumber = page.value?.page_number || '-'
  return `${storyTitle} - pagina ${pageNumber}`
})

function syncDraft() {
  const currentPage = page.value
  if (!currentPage) return

  draft.text_current = currentPage.text.current || ''

  const main = slots.value.find((slot) => slot.slot_name === 'main')
  const secondary = slots.value.find((slot) => slot.slot_name === 'secondary')

  draft.main_prompt_current = main?.prompt?.current || ''
  draft.secondary_prompt_current = secondary?.prompt?.current || ''

  for (const slot of slots.value) {
    if (!uploadForms[slot.slot_name]) {
      uploadForms[slot.slot_name] = {
        file: null,
        slug: '',
        notes: '',
      }
    }
  }
}

async function loadStory() {
  loading.value = true
  errorMessage.value = ''
  try {
    payload.value = await getStory(storyPath.value, route.query.p)
    syncDraft()
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'No se pudo cargar el cuento.'
    errorMessage.value = message
    toasts.push(message, 'error')
  } finally {
    loading.value = false
  }
}

function goToPage(pageNumber) {
  if (!pageNumber) return
  router.replace({
    path: route.path,
    query: { p: String(pageNumber) },
  })
}

function onKeydown(event) {
  if (!pagination.value) return

  const tagName = event.target?.tagName?.toLowerCase() || ''
  if (tagName === 'input' || tagName === 'textarea' || tagName === 'select') {
    return
  }

  if (event.key === 'ArrowLeft' && pagination.value.prev_page) {
    event.preventDefault()
    goToPage(pagination.value.prev_page)
  }

  if (event.key === 'ArrowRight' && pagination.value.next_page) {
    event.preventDefault()
    goToPage(pagination.value.next_page)
  }
}

async function savePage() {
  if (!page.value) return

  busy.save = true
  try {
    payload.value = await patchStoryPage(storyPath.value, page.value.page_number, {
      text_current: draft.text_current,
      main_prompt_current: draft.main_prompt_current,
      secondary_prompt_current: draft.secondary_prompt_current,
    })
    syncDraft()
    toasts.push('Cambios de pagina guardados.', 'success')
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'No se pudo guardar la pagina.'
    toasts.push(message, 'error')
  } finally {
    busy.save = false
  }
}

function setUploadFile(slotName, event) {
  const file = event.target?.files?.[0] || null
  if (!uploadForms[slotName]) {
    uploadForms[slotName] = { file: null, slug: '', notes: '' }
  }
  uploadForms[slotName].file = file
}

async function submitAlternative(slotName) {
  if (!page.value) return

  const state = uploadForms[slotName]
  if (!state?.file) {
    toasts.push('Selecciona una imagen antes de subir.', 'error')
    return
  }

  const formData = new FormData()
  formData.append('image_file', state.file)
  formData.append('alt_slug', state.slug || '')
  formData.append('alt_notes', state.notes || '')

  busy.uploadSlot = slotName
  try {
    payload.value = await uploadAlternative(storyPath.value, page.value.page_number, slotName, formData)
    uploadForms[slotName] = { file: null, slug: '', notes: '' }
    syncDraft()
    toasts.push(`Nueva alternativa agregada en slot ${slotName}.`, 'success')
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'No se pudo subir la alternativa.'
    toasts.push(message, 'error')
  } finally {
    busy.uploadSlot = ''
  }
}

async function activateAlternative(slotName, alternativeId) {
  if (!page.value) return

  busy.activate = `${slotName}:${alternativeId}`
  try {
    payload.value = await setSlotActive(storyPath.value, page.value.page_number, slotName, alternativeId)
    syncDraft()
    toasts.push('Alternativa activa actualizada.', 'success')
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'No se pudo activar la alternativa.'
    toasts.push(message, 'error')
  } finally {
    busy.activate = ''
  }
}

function showImage(item, slotName) {
  modal.visible = true
  modal.title = `Slot ${slotName} - ${item.slug || item.id}`
  modal.imageUrl = item.image_url || ''
  modal.notes = item.notes || ''
}

function closeModal() {
  modal.visible = false
  modal.title = ''
  modal.imageUrl = ''
  modal.notes = ''
}

function openBreadcrumb(crumb) {
  if (!crumb.path) {
    router.push('/biblioteca')
    return
  }
  router.push(`/biblioteca/${crumb.path}`)
}

watch(
  () => route.fullPath,
  () => {
    loadStory()
  },
  { immediate: true },
)

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <section class="story-view">
    <nav class="crumbs" aria-label="breadcrumbs">
      <button v-for="crumb in breadcrumbs" :key="crumb.path || 'root'" type="button" class="crumb-btn" @click="openBreadcrumb(crumb)">
        {{ crumb.name }}
      </button>
    </nav>

    <header v-if="payload" class="museum-header">
      <p class="eyebrow">Cuento</p>
      <h1>{{ payload.story.title }}</h1>
      <p class="muted">
        {{ payload.story.story_rel_path }} | status {{ payload.story.status }}
      </p>

      <div class="story-actions">
        <button type="button" class="accent-btn" @click="editorMode = !editorMode">
          {{ editorMode ? 'Salir de modo editor' : 'Entrar a modo editor' }}
        </button>
      </div>
    </header>

    <section v-if="payload && pagination" class="museum-panel nav-panel">
      <button type="button" class="ghost-btn" :disabled="!pagination.prev_page" @click="goToPage(pagination.prev_page)">
        ← Pagina anterior
      </button>

      <label>
        Pagina
        <select :value="pagination.selected_page" @change="goToPage(Number($event.target.value))">
          <option v-for="number in pagination.page_numbers" :key="number" :value="number">{{ number }}</option>
        </select>
      </label>

      <button type="button" class="ghost-btn" :disabled="!pagination.next_page" @click="goToPage(pagination.next_page)">
        Pagina siguiente →
      </button>
    </section>

    <p v-if="pagination?.missing_pages?.length" class="warning-line">
      Paginas faltantes en secuencia: {{ pagination.missing_pages.join(', ') }}
    </p>

    <p v-if="loading" class="muted">Cargando cuento...</p>
    <p v-if="errorMessage" class="error-line">{{ errorMessage }}</p>

    <section v-if="page" class="story-grid">
      <article class="museum-panel picture-block">
        <h2>Imagen definitiva</h2>
        <img v-if="definitiveImageUrl" class="definitive-image" :src="definitiveImageUrl" :alt="definitiveAltText" />
        <p v-else class="muted">Sin imagen definitiva disponible para esta pagina.</p>
      </article>

      <article class="museum-panel text-block">
        <h2>Texto definitivo</h2>
        <pre>{{ page.text.current }}</pre>
      </article>
    </section>

    <section v-if="editorMode && page" class="museum-panel editor-panel">
      <h2>Edicion integrada</h2>
      <label>
        Texto current
        <textarea v-model="draft.text_current" rows="7"></textarea>
      </label>
      <label>
        Prompt main current
        <textarea v-model="draft.main_prompt_current" rows="5"></textarea>
      </label>
      <label>
        Prompt secondary current
        <textarea v-model="draft.secondary_prompt_current" rows="5"></textarea>
      </label>
      <button type="button" class="accent-btn" :disabled="busy.save" @click="savePage">
        {{ busy.save ? 'Guardando...' : 'Guardar pagina' }}
      </button>
    </section>

    <CollapsiblePanel title="Texto original" :open="panels.textOriginal" @toggle="panels.textOriginal = !panels.textOriginal">
      <pre v-if="page">{{ page.text.original }}</pre>
    </CollapsiblePanel>

    <CollapsiblePanel title="Prompts" :open="panels.prompts" @toggle="panels.prompts = !panels.prompts">
      <section class="slot-prompt-grid">
        <article v-for="slot in slots" :key="`prompt-${slot.slot_name}`" class="museum-panel slot-prompt-card">
          <h3>Slot {{ slot.slot_name }}</h3>
          <p class="muted">Prompt current</p>
          <pre>{{ slot.prompt.current }}</pre>
          <p class="muted">Prompt original</p>
          <pre>{{ slot.prompt.original }}</pre>
        </article>
      </section>
    </CollapsiblePanel>

    <CollapsiblePanel title="Alternativas de imagen" :open="panels.alternatives" @toggle="panels.alternatives = !panels.alternatives">
      <section class="slot-gallery-grid">
        <article v-for="slot in slots" :key="`gallery-${slot.slot_name}`" class="museum-panel slot-gallery-card">
          <h3>Slot {{ slot.slot_name }}</h3>
          <p class="muted">Activa: {{ slot.active_id || 'sin activa' }}</p>

          <div class="thumb-grid">
            <button
              v-for="item in slot.alternatives.filter((alt) => alt.image_exists)"
              :key="item.id"
              type="button"
              class="thumb-btn"
              :data-active="item.is_active ? '1' : '0'"
              @click="showImage(item, slot.slot_name)"
            >
              <img :src="item.image_url" :alt="item.slug || item.id" />
              <span>{{ item.slug || item.id }}</span>
            </button>
          </div>

          <ul class="metadata-list" v-if="slot.alternatives.length">
            <li v-for="item in slot.alternatives" :key="`meta-${slot.slot_name}-${item.id}`">
              <code>{{ item.id }}</code> · {{ item.status }}
              <span v-if="item.notes"> · {{ item.notes }}</span>
              <button
                v-if="editorMode && !item.is_active"
                type="button"
                class="ghost-btn mini"
                :disabled="busy.activate === `${slot.slot_name}:${item.id}`"
                @click="activateAlternative(slot.slot_name, item.id)"
              >
                Activar
              </button>
            </li>
          </ul>

          <p v-else class="muted">Sin alternativas para este slot.</p>

          <form v-if="editorMode" class="upload-form" @submit.prevent="submitAlternative(slot.slot_name)">
            <label>
              Subir imagen
              <input type="file" accept="image/png,image/jpeg,image/webp,image/gif" @change="setUploadFile(slot.slot_name, $event)" />
            </label>
            <label>
              Slug
              <input v-model="uploadForms[slot.slot_name].slug" type="text" placeholder="editorial" />
            </label>
            <label>
              Notas
              <textarea v-model="uploadForms[slot.slot_name].notes" rows="3"></textarea>
            </label>
            <button type="submit" class="accent-btn" :disabled="busy.uploadSlot === slot.slot_name">
              {{ busy.uploadSlot === slot.slot_name ? 'Subiendo...' : 'Agregar alternativa' }}
            </button>
          </form>
        </article>
      </section>
    </CollapsiblePanel>

    <ImageModal
      :visible="modal.visible"
      :title="modal.title"
      :image-url="modal.imageUrl"
      :notes="modal.notes"
      @close="closeModal"
    />

    <ToastStack :items="toasts.items" @close="toasts.dismiss" />
  </section>
</template>
