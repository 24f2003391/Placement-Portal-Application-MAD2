import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useMessageStore = defineStore('messageStore', () => {
  const messages = ref('')
  
  function updateMessages(message) {
    messages.value = message
    setTimeout(() => {
      messages.value = ''
    },5000)
  }

  return { messages, updateMessages }
})