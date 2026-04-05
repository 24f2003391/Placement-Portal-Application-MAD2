import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useMessageStore = defineStore('messageStore', () => {
  const messages = ref({ text: '', type: '' })

  function updateMessages(text, type = 'success') {
    messages.value = { text, type }

    setTimeout(() => {
      messages.value = { text: '', type: '' }
    }, 5000)
  }

  return { messages, updateMessages }
})