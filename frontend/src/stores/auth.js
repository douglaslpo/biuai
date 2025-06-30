import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/boot/axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isLoading = computed(() => loading.value)

  // Actions
  const login = async (email, password) => {
    loading.value = true
    error.value = null
    
    try {
      // Usar URLSearchParams para OAuth2PasswordRequestForm
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const response = await api.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      loading.value = false
      
      localStorage.setItem('token', access_token)
      localStorage.setItem('user', JSON.stringify(userData))
      
      return { success: true }
    } catch (error) {
      loading.value = false
      error.value = error.response?.data?.detail || 'Erro no login'
      return { success: false, error: error.value }
    }
  }

  const register = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/v1/auth/register', userData)
      
      // Após registro bem-sucedido, fazer login automaticamente
      const loginResult = await login(userData.email, userData.password)
      return loginResult
    } catch (error) {
      error.value = error.response?.data?.detail || 'Erro no registro'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    error.value = null
    
    user.value = null
    token.value = null
    
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    loading.value = false
    
    const router = useRouter()
    router.push('/login')
    
    return { success: true }
  }

  const checkAuth = async () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      
      try {
        // Verificar se o token ainda é válido
        await api.get('/api/v1/auth/me')
      } catch (error) {
        // Token inválido, fazer logout
        await logout()
      }
    }
  }

  const updateProfile = async (profileData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put('/api/v1/users/me', profileData)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      
      return { success: true, user: response.data }
    } catch (error) {
      error.value = error.response?.data?.detail || 'Erro ao atualizar perfil'
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  // Inicializar autenticação ao carregar a store
  const initAuth = async () => {
    await checkAuth()
  }

  return {
    // State
    user,
    token,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isLoading,
    
    // Actions
    login,
    register,
    logout,
    checkAuth,
    updateProfile,
    initAuth
  }
}) 