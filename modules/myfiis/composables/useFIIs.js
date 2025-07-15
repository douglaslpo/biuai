import { useApi } from '@/composables/useApi'
import { computed, ref } from 'vue'

export function useFIIs() {
  const { api } = useApi()
  
  // Estado
  const fiis = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Getters
  const totalInvestido = computed(() => {
    return fiis.value.reduce((total, fii) => total + (fii.quantidade * fii.preco_medio), 0)
  })
  
  const dyMedio = computed(() => {
    if (!fiis.value.length) return 0
    return fiis.value.reduce((total, fii) => total + fii.dividend_yield, 0) / fiis.value.length
  })
  
  const scoreMedio = computed(() => {
    if (!fiis.value.length) return 0
    return Math.round(fiis.value.reduce((total, fii) => total + fii.score, 0) / fiis.value.length)
  })
  
  // Actions
  const fetchFIIs = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/api/v1/myfiis')
      fiis.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erro ao carregar FIIs'
      console.error('Erro ao carregar FIIs:', err)
    } finally {
      loading.value = false
    }
  }
  
  const addFII = async (fiiData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/api/v1/myfiis', fiiData)
      fiis.value.push(response.data)
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erro ao adicionar FII'
      console.error('Erro ao adicionar FII:', err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  const updateFII = async (id, fiiData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.put(`/api/v1/myfiis/${id}`, fiiData)
      const index = fiis.value.findIndex(f => f.id === id)
      if (index !== -1) {
        fiis.value[index] = response.data
      }
      return { success: true, data: response.data }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erro ao atualizar FII'
      console.error('Erro ao atualizar FII:', err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  const deleteFII = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      await api.delete(`/api/v1/myfiis/${id}`)
      fiis.value = fiis.value.filter(f => f.id !== id)
      return { success: true }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Erro ao excluir FII'
      console.error('Erro ao excluir FII:', err)
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }
  
  const toggleFavorito = async (id) => {
    const fii = fiis.value.find(f => f.id === id)
    if (!fii) return
    
    try {
      const response = await api.patch(`/api/v1/myfiis/${id}/favorito`)
      const index = fiis.value.findIndex(f => f.id === id)
      if (index !== -1) {
        fiis.value[index] = { ...fiis.value[index], favorito: response.data.favorito }
      }
      return { success: true }
    } catch (err) {
      console.error('Erro ao alterar favorito:', err)
      return { success: false, error: err.response?.data?.detail || 'Erro ao alterar favorito' }
    }
  }
  
  return {
    // Estado
    fiis,
    loading,
    error,
    
    // Getters
    totalInvestido,
    dyMedio,
    scoreMedio,
    
    // Actions
    fetchFIIs,
    addFII,
    updateFII,
    deleteFII,
    toggleFavorito
  }
} 