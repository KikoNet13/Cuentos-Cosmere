<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  imageUrl: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '',
  },
  notes: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['close'])
</script>

<template>
  <teleport to="body">
    <div v-if="visible" class="modal-backdrop" @click.self="emit('close')">
      <div class="modal-card">
        <div class="modal-head">
          <h3>{{ title }}</h3>
          <button type="button" class="ghost-btn" @click="emit('close')">Cerrar</button>
        </div>
        <div class="modal-body">
          <img :src="imageUrl" :alt="title" />
          <p v-if="notes" class="muted">{{ notes }}</p>
        </div>
      </div>
    </div>
  </teleport>
</template>
