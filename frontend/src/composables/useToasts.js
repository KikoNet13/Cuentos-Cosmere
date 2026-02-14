import { ref } from 'vue'

let currentId = 0

export function useToasts() {
  const items = ref([])

  function push(message, tone = 'info') {
    const id = ++currentId
    items.value.push({ id, message, tone })
    setTimeout(() => {
      dismiss(id)
    }, 3200)
  }

  function dismiss(id) {
    items.value = items.value.filter((item) => item.id !== id)
  }

  return {
    items,
    push,
    dismiss,
  }
}
