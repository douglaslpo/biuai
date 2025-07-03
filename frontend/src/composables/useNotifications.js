import { ref } from 'vue'
import { useNotificationStore } from '@/stores/notifications'

export function useNotifications() {
  const notificationsStore = useNotificationStore()
  
  // Local state for component-specific notifications
  const localNotifications = ref([])
  
  // Methods
  const showSuccess = (message, options = {}) => {
    return notificationsStore.add({
      type: 'success',
      message,
      duration: 5000,
      ...options
    })
  }
  
  const showError = (message, options = {}) => {
    return notificationsStore.add({
      type: 'error',
      message,
      duration: 8000,
      ...options
    })
  }
  
  const showWarning = (message, options = {}) => {
    return notificationsStore.add({
      type: 'warning',
      message,
      duration: 6000,
      ...options
    })
  }
  
  const showInfo = (message, options = {}) => {
    return notificationsStore.add({
      type: 'info',
      message,
      duration: 5000,
      ...options
    })
  }
  
  const showLoading = (message, options = {}) => {
    return notificationsStore.add({
      type: 'loading',
      message,
      persistent: true,
      ...options
    })
  }
  
  const dismiss = (id) => {
    notificationsStore.remove(id)
  }
  
  const dismissAll = () => {
    notificationsStore.clear()
  }
  
  // Specialized notification methods
  const showActionSuccess = (action, entity) => {
    const messages = {
      create: `${entity} criado com sucesso!`,
      update: `${entity} atualizado com sucesso!`,
      delete: `${entity} excluído com sucesso!`,
      save: `${entity} salvo com sucesso!`
    }
    
    return showSuccess(messages[action] || `${action} realizado com sucesso!`)
  }
  
  const showActionError = (action, entity, error = null) => {
    const messages = {
      create: `Erro ao criar ${entity}`,
      update: `Erro ao atualizar ${entity}`,
      delete: `Erro ao excluir ${entity}`,
      save: `Erro ao salvar ${entity}`,
      fetch: `Erro ao carregar ${entity}`
    }
    
    const baseMessage = messages[action] || `Erro ao executar ${action}`
    const fullMessage = error ? `${baseMessage}: ${error}` : baseMessage
    
    return showError(fullMessage)
  }
  
  const showValidationError = (errors) => {
    if (Array.isArray(errors)) {
      errors.forEach(error => showError(error))
    } else if (typeof errors === 'object') {
      Object.values(errors).forEach(error => {
        if (Array.isArray(error)) {
          error.forEach(e => showError(e))
        } else {
          showError(error)
        }
      })
    } else {
      showError(errors)
    }
  }
  
  // Network-related notifications
  const showNetworkError = () => {
    return showError('Erro de conexão. Verifique sua internet.', {
      duration: 10000
    })
  }
  
  const showOfflineWarning = () => {
    return showWarning('Você está offline. Algumas funcionalidades podem não estar disponíveis.', {
      persistent: true
    })
  }
  
  // Progress notifications
  const showProgress = (message, progress = 0) => {
    return notificationsStore.add({
      type: 'progress',
      message,
      progress,
      persistent: true
    })
  }
  
  const updateProgress = (id, progress, message) => {
    notificationsStore.updateProgress(id, progress, message)
  }
  
  return {
    // State
    notifications: notificationsStore.notifications,
    localNotifications,
    
    // Basic methods
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showLoading,
    showProgress,
    dismiss,
    dismissAll,
    updateProgress,
    
    // Specialized methods
    showActionSuccess,
    showActionError,
    showValidationError,
    showNetworkError,
    showOfflineWarning
  }
} 