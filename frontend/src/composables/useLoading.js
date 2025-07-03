import { ref } from 'vue'

export function useLoading(initialState = false) {
  const loading = ref(initialState)
  
  const setLoading = (state) => {
    loading.value = state
  }
  
  const startLoading = () => {
    loading.value = true
  }
  
  const stopLoading = () => {
    loading.value = false
  }
  
  const withLoading = async (asyncFn) => {
    try {
      loading.value = true
      return await asyncFn()
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading,
    setLoading,
    startLoading,
    stopLoading,
    withLoading
  }
} 