import { api } from '@/boot/axios'
import { useNotifications } from '@/composables/useNotifications'
import { ref } from 'vue'

export function useMyFIIs() {
  const fiis = ref([])
  const loading = ref(false)
  const { showError } = useNotifications()

  const fetchMyFIIs = async () => {
    try {
      loading.value = true
      const response = await api.get('/api/v1/myfiis')
      fiis.value = response.data
    } catch (error) {
      showError('Erro ao carregar FIIs: ' + error.message)
      throw error
    } finally {
      loading.value = false
    }
  }

  const addFIIToPortfolio = async (fiiData) => {
    try {
      loading.value = true
      const response = await api.post('/api/v1/myfiis', fiiData)
      fiis.value.push(response.data)
      return response.data
    } catch (error) {
      showError('Erro ao adicionar FII: ' + error.message)
      throw error
    } finally {
      loading.value = false
    }
  }

  const updateFII = async (id, fiiData) => {
    try {
      loading.value = true
      const response = await api.put(`/api/v1/myfiis/${id}`, fiiData)
      const index = fiis.value.findIndex(fii => fii.id === id)
      if (index !== -1) {
        fiis.value[index] = response.data
      }
      return response.data
    } catch (error) {
      showError('Erro ao atualizar FII: ' + error.message)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteFII = async (id) => {
    try {
      loading.value = true
      await api.delete(`/api/v1/myfiis/${id}`)
      fiis.value = fiis.value.filter(fii => fii.id !== id)
    } catch (error) {
      showError('Erro ao excluir FII: ' + error.message)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getFIIDetails = async (id) => {
    try {
      loading.value = true
      const response = await api.get(`/api/v1/myfiis/${id}`)
      return response.data
    } catch (error) {
      showError('Erro ao carregar detalhes do FII: ' + error.message)
      throw error
    } finally {
      loading.value = false
    }
  }

  const getAnalytics = async () => {
    try {
      loading.value = true
      const response = await api.get('/api/v1/myfiis/analytics')
      return response.data
    } catch (error) {
      showError('Erro ao carregar análises: ' + error.message)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    fiis,
    loading,
    fetchMyFIIs,
    addFIIToPortfolio,
    updateFII,
    deleteFII,
    getFIIDetails,
    getAnalytics
  }
} 