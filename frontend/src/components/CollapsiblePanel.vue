<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  open: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['toggle'])

const expanded = computed(() => props.open)
</script>

<template>
  <section class="collapsible" :data-open="expanded ? '1' : '0'">
    <button type="button" class="collapsible-trigger" @click="emit('toggle')">
      <span>{{ title }}</span>
      <span>{{ expanded ? '−' : '+' }}</span>
    </button>
    <div v-show="expanded" class="collapsible-body">
      <slot />
    </div>
  </section>
</template>
