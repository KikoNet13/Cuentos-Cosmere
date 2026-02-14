<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { ApiError, getLibraryNode } from '../api'
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
const nodeData = ref(null)

const filters = reactive({
  q: '',
  kind: 'all',
  status: 'all',
})

const nodePath = computed(() => normalizePathParam(route.params.nodePath))

const breadcrumbs = computed(() => nodeData.value?.breadcrumbs || [])
const children = computed(() => nodeData.value?.children || [])
const counts = computed(() => nodeData.value?.counts || null)
const nodeTitle = computed(() => nodeData.value?.node?.name || 'biblioteca')

async function loadNode() {
  filters.q = typeof route.query.q === 'string' ? route.query.q : ''
  filters.kind = typeof route.query.kind === 'string' ? route.query.kind : 'all'
  filters.status = typeof route.query.status === 'string' ? route.query.status : 'all'

  loading.value = true
  errorMessage.value = ''

  try {
    nodeData.value = await getLibraryNode({
      path: nodePath.value,
      q: filters.q,
      kind: filters.kind,
      status: filters.status,
    })
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'No se pudo cargar la biblioteca.'
    errorMessage.value = message
    toasts.push(message, 'error')
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  const query = {}
  if (filters.q) query.q = filters.q
  if (filters.kind !== 'all') query.kind = filters.kind
  if (filters.status !== 'all') query.status = filters.status
  router.replace({ path: route.path, query })
}

function openItem(item) {
  if (item.node_type === 'story') {
    router.push(`/cuento/${item.path_rel}`)
    return
  }

  if (!item.path_rel) {
    router.push('/biblioteca')
    return
  }
  router.push(`/biblioteca/${item.path_rel}`)
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
    loadNode()
  },
  { immediate: true },
)
</script>

<template>
  <section class="library-view">
    <header class="museum-header">
      <p class="eyebrow">Navegacion por nodos</p>
      <h1>{{ nodeTitle }}</h1>
      <p class="muted">Explora la biblioteca paso a paso hasta llegar a cada cuento.</p>
    </header>

    <nav class="crumbs" aria-label="breadcrumbs">
      <button v-for="crumb in breadcrumbs" :key="crumb.path || 'root'" type="button" class="crumb-btn" @click="openBreadcrumb(crumb)">
        {{ crumb.name }}
      </button>
    </nav>

    <section class="museum-panel filter-panel">
      <label>
        Buscar en este nodo
        <input v-model="filters.q" type="search" placeholder="nombre, ruta, estado" />
      </label>

      <label>
        Tipo
        <select v-model="filters.kind">
          <option value="all">Todos</option>
          <option value="node">Nodo</option>
          <option value="book">Libro</option>
          <option value="story">Cuento</option>
        </select>
      </label>

      <label>
        Estado
        <select v-model="filters.status">
          <option value="all">Todos</option>
          <option value="draft">draft</option>
          <option value="text_reviewed">text_reviewed</option>
          <option value="text_blocked">text_blocked</option>
          <option value="prompt_reviewed">prompt_reviewed</option>
          <option value="prompt_blocked">prompt_blocked</option>
          <option value="ready">ready</option>
        </select>
      </label>

      <button type="button" class="accent-btn" @click="applyFilters">Aplicar filtros</button>
    </section>

    <section v-if="counts" class="museum-panel stat-panel">
      <article>
        <strong>{{ counts.nodes }}</strong>
        <span>Nodos</span>
      </article>
      <article>
        <strong>{{ counts.stories }}</strong>
        <span>Cuentos</span>
      </article>
      <article>
        <strong>{{ counts.pages }}</strong>
        <span>Paginas</span>
      </article>
      <article>
        <strong>{{ counts.alternatives }}</strong>
        <span>Alternativas</span>
      </article>
    </section>

    <p v-if="loading" class="muted">Cargando nodo...</p>
    <p v-if="errorMessage" class="error-line">{{ errorMessage }}</p>

    <transition-group name="fade-rise" tag="section" class="card-grid">
      <article v-for="item in children" :key="item.path_rel + item.node_type" class="museum-card" :data-type="item.node_type">
        <button type="button" class="card-hit" @click="openItem(item)">
          <p class="eyebrow">{{ item.node_type }}</p>
          <h2>{{ item.name }}</h2>
          <p class="muted path-line">{{ item.path_rel || 'library' }}</p>
          <template v-if="item.story">
            <p class="story-line"><span>Status:</span> {{ item.story.status }}</p>
            <p class="story-line"><span>Paginas:</span> {{ item.story.pages }}</p>
          </template>
        </button>
      </article>
    </transition-group>

    <p v-if="!loading && !children.length" class="muted">No hay elementos para estos filtros en el nodo actual.</p>

    <ToastStack :items="toasts.items" @close="toasts.dismiss" />
  </section>
</template>
