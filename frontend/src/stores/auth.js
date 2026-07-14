import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('authStore', () => {
  // Safely initialize state
  const auth_token = ref(localStorage.getItem('auth_token') || null)
  
  // Safe JSON parsing wrapper
  const getStoredUser = () => {
    const stored = localStorage.getItem('user')
    try {
      return stored ? JSON.parse(stored) : null
    } catch (error) {
      console.error(error)
      localStorage.removeItem('user') // Clear corrupted data
      return null
    }
  }
  const user = ref(getStoredUser())

  // --- REACTIVE GETTERS (Computed Properties) ---
  const isAuthenticated = computed(() => auth_token.value !== null)
  
  const token = computed(() => auth_token.value)
  
  const userId = computed(() => user.value ? user.value.id : null)
  
  // Changed to a computed property so it's fully reactive
  const userRoles = computed(() => {
    if (!user.value) return []
    // Ensure it always returns an array even if the backend sent a single string
    return Array.isArray(user.value.roles) ? user.value.roles : [user.value.roles]
  })

  // --- ACTIONS ---
  function setUserCred(tokenValue, userData) {
    localStorage.setItem('auth_token', tokenValue)
    localStorage.setItem('user', JSON.stringify(userData))
    auth_token.value = tokenValue
    user.value = userData
  }

  function clearAuthToken() {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    auth_token.value = null
    user.value = null
  }

  return {
    // State / Getters
    isAuthenticated, 
    token, 
    userId, 
    userRoles, 
    user,
    // Actions
    setUserCred, 
    clearAuthToken
  }
})
