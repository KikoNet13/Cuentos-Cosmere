<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['close'])
</script>

<template>
  <div class="toast-stack" v-if="items.length">
    <article v-for="item in items" :key="item.id" class="toast" :data-tone="item.tone">
      <p>{{ item.message }}</p>
      <button type="button" class="ghost-btn" @click="emit('close', item.id)">Cerrar</button>
    </article>
  </div>
</template>
